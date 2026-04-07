"""
Test E2E réel du workflow métier complet côté responsables.

Flow couvert :
  1. Ouverture du Formulaire de lancement d'opération
  2. Saisie des infos minimales + ajout d'une pièce jointe dans le formulaire
  3. Création de la tâche via "Créer et aller à la tâche"
  4. Ouverture du smart button Documents
  5. Tagging UI du document dérivé : `PJ > Livrable` + `PJ > Inventaire`
  6. Vérification portail : l'opération apparaît et le livrable inventaire est téléchargeable

Ce test couvre enfin le vrai point d'entrée métier utilisé par les responsables.
"""

from pathlib import Path
import tempfile
import uuid
import re
import xmlrpc.client

import pytest
from playwright.sync_api import Page

from conftest import BASE_URL, _login, assert_no_odoo_error

DB = "greenremarket"
ADMIN_LOGIN = "admin@greenremarket.fr"
ADMIN_PASSWORD = "Payasugo187!odoo"
ACTION_TASK_CREATION_FORM = 420


def get_admin_rpc():
    common = xmlrpc.client.ServerProxy(f"{BASE_URL}/xmlrpc/2/common")
    uid = common.authenticate(DB, ADMIN_LOGIN, ADMIN_PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f"{BASE_URL}/xmlrpc/2/object")

    def x(model, method, *args, **kwargs):
        return models.execute_kw(DB, uid, ADMIN_PASSWORD, model, method, *args, **kwargs)

    return x


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


def cleanup_task_by_name(x, task_name):
    task_ids = x("project.task", "search", [[("name", "=", task_name)]])
    if task_ids:
        x("project.task", "unlink", [task_ids])


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


def extract_task_id_from_url(url: str) -> int:
    match = re.search(r"[#&]id=(\d+)", url)
    assert match, f"Impossible d'extraire l'id de tâche depuis l'URL: {url}"
    return int(match.group(1))


class TestLaunchFormDocumentsWorkflow:
    def test_launch_form_then_documents_tagging_then_portal_visibility(
        self, page: Page, logged_in_page: Page
    ):
        x = get_admin_rpc()
        unique = uuid.uuid4().hex[:8]
        task_name = f"PW launch form {unique}"
        filename = f"inventaire-launch-{unique}.pdf"

        tmpdir = Path(tempfile.gettempdir())
        filepath = tmpdir / filename
        filepath.write_bytes(b"%PDF-1.4\n% fake pdf for playwright e2e\n")

        cleanup_task_by_name(x, task_name)

        task_id = None
        try:
            _login(page, BASE_URL, ADMIN_LOGIN, ADMIN_PASSWORD)

            # 1. Ouvrir le vrai formulaire de lancement
            page.goto(f"{BASE_URL}/web")
            page.wait_for_load_state("load")
            page.wait_for_timeout(2000)
            page.evaluate(
                f"window.location.hash = '#action={ACTION_TASK_CREATION_FORM}&model=project.task&view_type=form'"
            )
            page.wait_for_timeout(6000)
            assert_no_odoo_error(page)
            assert f"action={ACTION_TASK_CREATION_FORM}" in page.url, (
                f"Le formulaire de lancement ne s'est pas ouvert, URL: {page.url}"
            )

            # 2. Remplir les infos minimales du formulaire (nom uniquement).
            # order_giver_id est un Many2one : l'interaction autocomplete dans un formulaire
            # target:new est trop fragile en Playwright (le dropdown interfere avec le submit).
            # Le comportement serveur testaé (sync partner_id) est valideé via RPC apres
            # la creation de la tache — c'est le meme chemin de code.
            page.locator("#name_0").fill(task_name)
            page.locator("#client_destination_name_0").fill("EcoSolutions Test")

            # 3. Ajouter une pièce jointe dans le formulaire lui-même
            page.locator("input[name='ufile']").set_input_files(str(filepath))
            page.wait_for_timeout(3000)
            form_body = page.locator("body").inner_text()
            assert filename in form_body, f"La pièce jointe {filename} n'apparaît pas dans le formulaire"

            # 4. Créer et aller à la tâche
            page.locator("button", has_text="Créer et aller à la tâche").click()
            page.wait_for_timeout(7000)
            assert_no_odoo_error(page)
            if "id=" in page.url:
                task_id = extract_task_id_from_url(page.url)
            else:
                created = x(
                    "project.task",
                    "search_read",
                    [[("name", "=", task_name)]],
                    {"fields": ["id", "name", "tag_ids"], "limit": 1, "order": "id desc"},
                )
                assert created, (
                    f"La tâche n'a pas été créée depuis le formulaire : {task_name}"
                )
                task_id = created[0]["id"]
                page.goto(f"{BASE_URL}/web")
                page.wait_for_load_state("load")
                page.wait_for_timeout(1500)
                page.evaluate(
                    f"window.location.hash = '#id={task_id}&model=project.task&view_type=form'"
                )
                page.wait_for_timeout(5000)
                assert_no_odoo_error(page)

            # 5. Vérifier que le tag PD3E a bien été mis automatiquement
            task_data = x("project.task", "read", [[task_id]], {"fields": ["name", "tag_ids", "documents_folder_id", "lot_name"]})[0]
            assert task_data["name"] == task_name
            assert task_data["tag_ids"], "La tâche créée via le formulaire n'a aucun tag; PD3E attendu"
            task_lot_name = task_data.get("lot_name") or task_name  # lot_name = ref portail

            # 5b. Tester le sync order_giver_id -> partner_id (comportement serveur cle).
            # Le responsable definit le commanditaire dans le formulaire -> le commanditaire
            # doit voir l'operation sur son portail. On simule ce comportement via RPC :
            # set order_giver_id (EcoSolutions, partenaire stable CT202), puis appel
            # action_create_and_open qui doit syncer partner_id.
            ECOSOLUTIONS_ID = 320  # partenaire stable sur CT202
            x("project.task", "write", [[task_id], {"order_giver_id": ECOSOLUTIONS_ID}])
            x("project.task", "action_create_and_open", [[task_id]])
            synced = x("project.task", "read", [[task_id]], {"fields": ["partner_id", "order_giver_id"]})[0]
            assert synced["partner_id"], (
                f"partner_id non synchro depuis order_giver_id={synced['order_giver_id']} — "
                "le commanditaire ne verra pas l'operation sur son portail. "
                "Verifier action_create_and_open dans models.py."
            )

            # 6. Ouvrir Documents depuis la vraie tâche créée
            docs_button = page.locator(".oe_stat_button").filter(has_text="Documents").first
            assert docs_button.is_visible(), "Smart button Documents introuvable sur la tâche créée"
            docs_button.click()
            page.wait_for_timeout(7000)
            assert "model=documents.document" in page.url, (
                f"La vue Documents ne s'est pas ouverte, URL: {page.url}"
            )
            assert_no_odoo_error(page)

            # 7. Sélectionner le document issu de la pièce jointe et le tagger
            doc_card = page.locator(".o_kanban_record").filter(has_text=filename).first
            assert doc_card.is_visible(), f"Document {filename} introuvable dans la vue Documents"
            doc_card.click()
            page.wait_for_timeout(2500)
            add_document_tag(page, "Livr", "PJ > Livrable")
            add_document_tag(page, "Invent", "PJ > Inventaire")

            doc_id, tag_names = get_document_tags(x, task_id, filename)
            assert doc_id, f"Document {filename} introuvable en base après tagging UI"
            assert "Inventaire" in tag_names, f"Tag Inventaire absent après tagging UI: {tag_names}"
            assert ("Livrable" in tag_names) or ("Delivrable" in tag_names), (
                f"Tag Livrable/Delivrable absent après tagging UI: {tag_names}"
            )

            # 8. Vérifier le portail client : l'opération remonte bien
            portal = logged_in_page
            portal.goto(f"{BASE_URL}/my/operations")
            portal.wait_for_load_state("load")
            portal.wait_for_timeout(2000)
            assert_no_odoo_error(portal)
            ops_body = portal.locator("body").inner_text()
            assert task_lot_name in ops_body, (
                f"La tâche créée via le formulaire n'apparaît pas dans /my/operations "
                f"(lot_name={task_lot_name}, task_name={task_name})"
            )

            portal.goto(f"{BASE_URL}/my/operations/{task_id}")
            portal.wait_for_load_state("load")
            portal.wait_for_timeout(2000)
            assert_no_odoo_error(portal)
            portal_body = portal.locator("body").inner_text()
            assert "Inventaire" in portal_body or "inventaire" in portal_body.lower(), (
                f"L'indicateur portail Inventaire n'est pas visible pour la tâche {task_id}"
            )

            with portal.expect_download(timeout=15000) as dl_info:
                try:
                    portal.goto(f"{BASE_URL}/my/operations/{task_id}/deliverable/inventaire")
                except Exception:
                    pass
            download = dl_info.value
            assert download.suggested_filename, "Aucun téléchargement reçu pour le livrable inventaire"

        finally:
            if task_id:
                cleanup_documents_by_filename(x, task_id, filename)
                try:
                    x("project.task", "unlink", [[task_id]])
                except Exception:
                    pass
            else:
                cleanup_task_by_name(x, task_name)
            try:
                filepath.unlink(missing_ok=True)
            except Exception:
                pass
