"""
Test E2E réel du workflow Documents sur une tâche backend.

Flow couvert :
  1. Un utilisateur backend attache un fichier en pièce jointe à la tâche
  2. Il clique sur le smart button "Documents"
  3. Il sélectionne le document dérivé de cette pièce jointe
  4. Il applique les tags `PJ > Livrable` et `PJ > Inventaire`
  5. Un utilisateur portail voit l'indicateur Inventaire sur l'opération
  6. Le téléchargement portail du livrable Inventaire fonctionne

Ce test vise explicitement le trou de couverture remonté après la démo Samy :
le backend pouvait attacher des fichiers, mais le workflow de tagging via la
vue Documents n'était pas vérifié de bout en bout.
"""

from pathlib import Path
import tempfile
import uuid
import xmlrpc.client

import pytest
from playwright.sync_api import Page

from conftest import BASE_URL, _login, assert_no_odoo_error

DB = "greenremarket"
ADMIN_LOGIN = "admin@greenremarket.fr"
ADMIN_PASSWORD = "Payasugo187!odoo"


def get_admin_rpc():
    common = xmlrpc.client.ServerProxy(f"{BASE_URL}/xmlrpc/2/common")
    uid = common.authenticate(DB, ADMIN_LOGIN, ADMIN_PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f"{BASE_URL}/xmlrpc/2/object")

    def x(model, method, *args, **kwargs):
        return models.execute_kw(DB, uid, ADMIN_PASSWORD, model, method, *args, **kwargs)

    return x


def get_seeded_task(x):
    tasks = x(
        "project.task",
        "search_read",
        [[("name", "ilike", "OP-2026-001"), ("project_id", "=", 1)]],
        {"fields": ["id", "name", "lot_name"], "limit": 1},
    )
    return tasks[0] if tasks else None


def cleanup_documents_by_filename(x, task_id, filename):
    doc_ids = x(
        "documents.document",
        "search",
        [[("res_model", "=", "project.task"), ("res_id", "=", task_id), ("name", "=", filename)]],
    )
    if doc_ids:
        x("documents.document", "unlink", [doc_ids])

    att_ids = x(
        "ir.attachment",
        "search",
        [[("res_model", "=", "project.task"), ("res_id", "=", task_id), ("name", "=", filename)]],
    )
    if att_ids:
        x("ir.attachment", "unlink", [att_ids])


def get_document_tags(x, task_id, filename):
    docs = x(
        "documents.document",
        "search_read",
        [[("res_model", "=", "project.task"), ("res_id", "=", task_id), ("name", "=", filename)]],
        {"fields": ["id", "name", "tag_ids"], "limit": 1},
    )
    if not docs:
        return None, set()
    doc = docs[0]
    tag_ids = doc.get("tag_ids", [])
    if not tag_ids:
        return doc["id"], set()
    tags = x("documents.tag", "read", [tag_ids], {"fields": ["name"]})
    return doc["id"], {tag["name"] for tag in tags}


def open_task_form(page: Page, task_id: int):
    page.goto(f"{BASE_URL}/web")
    page.wait_for_load_state("load")
    page.wait_for_timeout(2000)
    page.evaluate(
        f"window.location.hash = '#id={task_id}&model=project.task&view_type=form'"
    )
    page.wait_for_timeout(6000)
    assert_no_odoo_error(page)
    assert "/web#" in page.url and f"id={task_id}" in page.url, (
        f"Impossible d'ouvrir la tâche {task_id}, URL actuelle: {page.url}"
    )


def add_document_tag(page: Page, query: str, expected_label: str):
    tag_input = page.locator(".o-autocomplete--input").last
    tag_input.click()
    tag_input.fill(query)
    page.wait_for_timeout(1200)
    suggestion = page.locator(".o-autocomplete--dropdown-item").filter(
        has_text=expected_label
    ).first
    assert suggestion.is_visible(), (
        f"Suggestion de tag introuvable pour '{expected_label}'"
    )
    suggestion.click()
    page.wait_for_timeout(1200)


class TestRealDocumentsWorkflow:
    def test_attach_then_tag_in_documents_then_portal_downloads_inventaire(
        self, page: Page, logged_in_page: Page
    ):
        """Vrai flow backend → Documents → portail client.

        Note pratique :
        - sur CT202, le compte `operateur@greenremarket.fr` ne rejoint pas
          actuellement le backend `/web` de façon stable en headless ;
        - on exécute donc le flow avec `admin@greenremarket.fr`, qui traverse
          exactement la même UI backend Documents.
        """
        x = get_admin_rpc()
        task = get_seeded_task(x)
        if not task:
            pytest.skip("Tâche seed OP-2026-001 introuvable")

        task_id = task["id"]
        unique = uuid.uuid4().hex[:8]
        filename = f"inventaire-ui-e2e-{unique}.pdf"

        tmpdir = Path(tempfile.gettempdir())
        filepath = tmpdir / filename
        filepath.write_bytes(b"%PDF-1.4\n% fake pdf for playwright e2e\n")

        cleanup_documents_by_filename(x, task_id, filename)

        try:
            _login(page, BASE_URL, ADMIN_LOGIN, ADMIN_PASSWORD)
            open_task_form(page, task_id)

            attach_btn = page.locator(".o-mail-Chatter-attachFiles").first
            assert attach_btn.is_visible(), "Bouton pièces jointes du chatter introuvable"
            attach_btn.click()
            page.wait_for_timeout(800)

            file_input = page.locator("input[type='file']").last
            file_input.set_input_files(str(filepath))
            page.wait_for_timeout(5000)

            body_after_upload = page.locator("body").inner_text()
            assert filename in body_after_upload, (
                f"Le fichier {filename} n'apparaît pas après upload dans la tâche"
            )

            docs_button = page.locator(".oe_stat_button").filter(has_text="Documents").first
            assert docs_button.is_visible(), "Smart button Documents introuvable"
            docs_button.click()
            page.wait_for_timeout(7000)
            assert "model=documents.document" in page.url, (
                f"La vue Documents ne s'est pas ouverte, URL: {page.url}"
            )
            assert_no_odoo_error(page)

            doc_card = page.locator(".o_kanban_record").filter(has_text=filename).first
            assert doc_card.is_visible(), (
                f"Document {filename} introuvable dans la vue Documents"
            )
            doc_card.click()
            page.wait_for_timeout(2500)

            add_document_tag(page, "Livr", "PJ > Livrable")
            add_document_tag(page, "Invent", "PJ > Inventaire")

            doc_id, tag_names = get_document_tags(x, task_id, filename)
            assert doc_id, f"Document {filename} introuvable en base après tagging UI"
            assert "Inventaire" in tag_names, (
                f"Tag Inventaire absent après tagging UI, tags présents: {tag_names}"
            )
            assert ("Livrable" in tag_names) or ("Delivrable" in tag_names), (
                f"Tag Livrable/Delivrable absent après tagging UI, tags présents: {tag_names}"
            )

            portal = logged_in_page
            portal.goto(f"{BASE_URL}/my/operations/{task_id}")
            portal.wait_for_load_state("load")
            portal.wait_for_timeout(2000)
            assert_no_odoo_error(portal)

            portal_body = portal.locator("body").inner_text()
            assert "Inventaire" in portal_body or "inventaire" in portal_body.lower(), (
                f"L'indicateur portail Inventaire n'est pas visible pour la tâche {task_id}"
            )
            assert "Non tagué" not in portal_body, (
                "Le portail montre encore un warning 'Non tagué' après tagging UI"
            )

            with portal.expect_download(timeout=15000) as dl_info:
                try:
                    portal.goto(f"{BASE_URL}/my/operations/{task_id}/deliverable/inventaire")
                except Exception:
                    # Playwright lève "Download is starting" quand la route
                    # répond directement par un flux fichier. C'est attendu ici.
                    pass
            download = dl_info.value
            assert download.suggested_filename, "Aucun téléchargement reçu pour le livrable inventaire"

        finally:
            cleanup_documents_by_filename(x, task_id, filename)
            try:
                filepath.unlink(missing_ok=True)
            except Exception:
                pass
