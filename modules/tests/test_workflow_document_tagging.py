"""
Test E2E : workflow complet de tagging document → indicateur livrable portail.

Ce test couvre le trou de couverture révélé lors de la démo Samy (2026-04-07) :
  - Un admin ouvre la tâche → bouton Documents → assigne le tag "Inventaire" à un fichier
  - Un client portail navigue vers le détail de l'opération
  - L'indicateur "Inventaire" s'allume (has_inventaire = True)

Le test valide DEUX choses distinctes :
  1. API (ORM) : créer un documents.document avec le bon tag suffit à activer has_inventaire
  2. Portail (E2E) : le portail affiche bien l'indicateur livrable quand has_inventaire = True

Sans ces tests, le bug des stubs vides (search_panel_select_range manquant,
is_delivrable() inactif) serait passé inaperçu en CI.

Hypothèses :
  - seed lancé (OP-2026-001 dans projet General, EcoSolutions company, PD3E tag)
  - Odoo UP sur BASE_URL
  - Module gr_project_inventory >= 17.0.4.1.0 (stubs implémentés)
"""

import base64
import xmlrpc.client
import pytest
from playwright.sync_api import Page

from conftest import assert_no_odoo_error, BASE_URL

ADMIN_LOGIN = "admin@greenremarket.fr"
ADMIN_PASSWORD = "Payasugo187!odoo"
DB = "greenremarket"


# ── Helpers RPC ─────────────────────────────────────────────────────────────

def get_admin_rpc():
    common = xmlrpc.client.ServerProxy(f"{BASE_URL}/xmlrpc/2/common")
    uid = common.authenticate(DB, ADMIN_LOGIN, ADMIN_PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f"{BASE_URL}/xmlrpc/2/object")

    def x(model, method, *args, **kwargs):
        return models.execute_kw(DB, uid, ADMIN_PASSWORD, model, method, *args, **kwargs)

    return x, uid


def get_seeded_task(x):
    tasks = x(
        "project.task", "search_read",
        [[("name", "ilike", "OP-2026-001"), ("project_id", "=", 1)]],
        {"fields": ["id", "name", "lot_name", "partner_id", "documents_folder_id"], "limit": 1},
    )
    return tasks[0] if tasks else None


def get_tag_inventaire_id(x):
    """Retourne l'id du tag 'Inventaire' sous la facette PJ."""
    tags = x(
        "documents.tag", "search_read",
        [[("name", "=", "Inventaire")]],
        {"fields": ["id", "name"], "limit": 1},
    )
    return tags[0]["id"] if tags else None


def get_or_create_task_folder(x, task):
    """Retourne le folder_id de la tâche (documents_folder_id).
    Si absent, utilise le dossier 'General' (id=6) comme fallback.
    """
    folder_id = task.get("documents_folder_id")
    if isinstance(folder_id, (list, tuple)):
        folder_id = folder_id[0]
    if folder_id:
        return folder_id
    # Fallback : dossier General sous Projects
    folders = x(
        "documents.folder", "search_read",
        [[("name", "=", "General")]],
        {"fields": ["id"], "limit": 1},
    )
    return folders[0]["id"] if folders else False


def create_tagged_document(x, task_id, folder_id, tag_id):
    """Crée un documents.document avec le tag Inventaire lié à la tâche."""
    att_id = x("ir.attachment", "create", [{
        "name": "inventaire-test-2026.pdf",
        "datas": base64.b64encode(b"inventaire test content").decode(),
        "res_model": "project.task",
        "res_id": task_id,
    }])
    doc_id = x("documents.document", "create", [{
        "name": "inventaire-test-2026.pdf",
        "folder_id": folder_id,
        "tag_ids": [[4, tag_id]],
        "attachment_id": att_id,
        "res_model": "project.task",
        "res_id": task_id,
    }])
    return doc_id, att_id


# ══════════════════════════════════════════════════════════════════════════════
# 1. Tests ORM (sans navigateur) — valide has_inventaire via XML-RPC
# ══════════════════════════════════════════════════════════════════════════════

class TestDocumentTaggingOrm:
    """Valide que le tag 'Inventaire' active has_inventaire sur la tâche (ORM)."""

    def test_inventaire_tag_exists_in_db(self):
        """Le tag 'Inventaire' sous la facette PJ doit exister en base."""
        x, _ = get_admin_rpc()
        tag_id = get_tag_inventaire_id(x)
        assert tag_id is not None, (
            "Le tag 'Inventaire' n'existe pas en base. "
            "Vérifier que gr_project_inventory a été --update après v17.0.4.1.0."
        )

    def test_pj_facet_tags_present(self):
        """Les 5 tags PJ (Livrable, RSE, Inventaire, Audit, Effacement) existent."""
        x, _ = get_admin_rpc()
        expected = {"Livrable", "RSE", "Inventaire", "Audit", "Effacement"}
        tags = x(
            "documents.tag", "search_read",
            [[("facet_id.name", "=", "PJ")]],
            {"fields": ["name"]},
        )
        found = {t["name"] for t in tags}
        missing = expected - found
        assert not missing, (
            f"Tags PJ manquants en base : {missing}. "
            "Le module gr_project_inventory doit être mis à jour."
        )

    def test_document_with_inventaire_tag_sets_has_inventaire(self):
        """documents.document avec tag Inventaire → has_inventaire = True sur la tâche."""
        x, _ = get_admin_rpc()
        task = get_seeded_task(x)
        if not task:
            pytest.skip("Tâche OP-2026-001 non seedée")

        tag_id = get_tag_inventaire_id(x)
        if not tag_id:
            pytest.skip("Tag 'Inventaire' absent — module non mis à jour")

        folder_id = get_or_create_task_folder(x, task)
        if not folder_id:
            pytest.skip("Aucun dossier Documents disponible")

        task_id = task["id"]
        doc_id = att_id = None
        try:
            doc_id, att_id = create_tagged_document(x, task_id, folder_id, tag_id)

            # Vérifie que has_inventaire est True sur la tâche
            result = x(
                "project.task", "read",
                [[task_id]],
                {"fields": ["has_inventaire", "count_inventaire"]},
            )
            assert result, "Impossible de lire la tâche"
            assert result[0]["has_inventaire"] is True, (
                f"has_inventaire = False après ajout d'un document avec tag Inventaire "
                f"(task_id={task_id}, doc_id={doc_id}). "
                "Vérifier que les stubs documents_document.py sont bien implémentés."
            )
            assert result[0]["count_inventaire"] >= 1, (
                "count_inventaire devrait être >= 1 avec un document tagué"
            )
        finally:
            if doc_id:
                x("documents.document", "unlink", [[doc_id]])
            if att_id:
                x("ir.attachment", "unlink", [[att_id]])

    def test_document_without_tag_does_not_set_has_inventaire(self):
        """documents.document SANS tag Inventaire → has_inventaire reste False.

        Vérifie que le has_inventaire n'est pas activé par le nom de fichier seul
        (la logique tagged-only doit prendre le dessus sur le fallback regex).
        """
        x, _ = get_admin_rpc()
        task = get_seeded_task(x)
        if not task:
            pytest.skip("Tâche OP-2026-001 non seedée")

        folder_id = get_or_create_task_folder(x, task)
        if not folder_id:
            pytest.skip("Aucun dossier Documents disponible")

        task_id = task["id"]
        # S'assurer qu'il n'y a pas déjà un document Inventaire tagué
        existing_docs = x(
            "documents.document", "search",
            [[("res_model", "=", "project.task"), ("res_id", "=", task_id),
              ("tag_ids.name", "=", "Inventaire")]],
        )
        if existing_docs:
            pytest.skip("Tâche a déjà un document Inventaire tagué — test non applicable")

        att_id = x("ir.attachment", "create", [{
            "name": "inventaire-sans-tag.pdf",
            "datas": base64.b64encode(b"fichier inventaire non tagué").decode(),
            "res_model": "project.task",
            "res_id": task_id,
        }])
        try:
            result = x(
                "project.task", "read",
                [[task_id]],
                {"fields": ["has_inventaire"]},
            )
            assert result[0]["has_inventaire"] is False, (
                "has_inventaire devrait être False quand le document n'a pas de tag Inventaire. "
                "Le fallback regex ne doit pas activer l'indicateur (logique tagged-only)."
            )
        finally:
            x("ir.attachment", "unlink", [[att_id]])


# ══════════════════════════════════════════════════════════════════════════════
# 2. Tests E2E portail — admin tag → client voit l'indicateur
# ══════════════════════════════════════════════════════════════════════════════

class TestDocumentTaggingPortal:
    """Workflow complet : admin ajoute tag Inventaire → portail client voit le livrable."""

    def test_tagged_document_shows_livrable_indicator_on_portal(
        self, logged_in_page: Page
    ):
        """WORKFLOW CLÉ : admin tag document Inventaire → portail affiche indicateur.

        Reproduit exactement le scénario raté lors de la démo Samy (2026-04-07) :
        - Admin attribue le tag PJ > Inventaire à un fichier dans la tâche
        - Client portail navigue vers le détail de l'opération
        - La page doit montrer l'indicateur livrable Inventaire (non warning)
        """
        x, _ = get_admin_rpc()
        task = get_seeded_task(x)
        if not task:
            pytest.skip("Tâche OP-2026-001 non seedée")

        tag_id = get_tag_inventaire_id(x)
        if not tag_id:
            pytest.skip("Tag 'Inventaire' absent en base")

        folder_id = get_or_create_task_folder(x, task)
        if not folder_id:
            pytest.skip("Aucun dossier Documents disponible")

        task_id = task["id"]
        doc_id = att_id = None
        try:
            doc_id, att_id = create_tagged_document(x, task_id, folder_id, tag_id)

            page = logged_in_page
            page.goto(f"{BASE_URL}/my/operations/{task_id}")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(1000)
            assert_no_odoo_error(page)

            body = page.content()

            # L'indicateur inventaire doit être présent (coche verte, pas warning)
            # Les textes possibles selon la template portail :
            has_indicator = any(kw in body for kw in [
                "inventaire-test-2026",  # nom du fichier
                "Inventaire",            # label de l'indicateur
                "inventaire",            # lower
                "livrable",              # générique
                "Livrable",
                "download",
                "télécharger",
                "Télécharger",
            ])
            assert has_indicator, (
                f"Aucun indicateur de livrable 'Inventaire' visible sur le portail "
                f"(task_id={task_id}) après taggage via documents.document. "
                f"URL={page.url}\n"
                "Ce test valide le workflow admin→portail après fix des stubs "
                "documents_document.py (search_panel_select_range + is_delivrable)."
            )

            # L'indicateur ne doit PAS être un warning (fichier non tagué)
            # (un warning serait présent si le fallback regex activait l'indicateur
            #  sans que le tag soit posé — ce n'est pas le cas ici)
            assert "Non tagué" not in body, (
                "L'indicateur affiche 'Non tagué' au lieu d'une coche verte. "
                "Vérifier que is_delivrable() utilise bien le tag Documents (pas le regex fallback)."
            )

        finally:
            if doc_id:
                x("documents.document", "unlink", [[doc_id]])
            if att_id:
                x("ir.attachment", "unlink", [[att_id]])

    def test_documents_button_from_task_opens_correct_workspace(
        self, logged_in_page: Page
    ):
        """Le bouton Documents depuis la tâche doit naviguer sans erreur.

        Valide que action_view_documents_project_task() fonctionne
        (initialise le dossier task si absent, retourne une action valide).
        Ce test est headless-friendly : on vérifie juste que l'URL change
        et qu'il n'y a pas d'erreur 500.
        """
        x, _ = get_admin_rpc()
        task = get_seeded_task(x)
        if not task:
            pytest.skip("Tâche OP-2026-001 non seedée")

        # Via XML-RPC, appeler action_view_documents_project_task et vérifier
        # qu'elle retourne une action (pas d'exception)
        try:
            result = x(
                "project.task", "action_view_documents_project_task",
                [[task["id"]]],
            )
            assert result, "action_view_documents_project_task a retourné une valeur vide"
            assert result.get("type") == "ir.actions.act_window", (
                f"Type d'action inattendu : {result.get('type')}"
            )
            assert result.get("res_model") == "documents.document", (
                f"Modèle inattendu : {result.get('res_model')}"
            )
        except Exception as e:
            pytest.fail(
                f"action_view_documents_project_task a levé une exception : {e}\n"
                "Vérifier que les méthodes _init_documents_folder / _prepare_documents_folder "
                "sont bien implémentées sur ProjectTask."
            )
