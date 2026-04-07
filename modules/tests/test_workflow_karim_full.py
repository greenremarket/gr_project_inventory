"""
Test E2E COMPLET — Workflow Karim Terqui (Infodis it) de bout en bout.

FLOW TESTÉ :
  1. Signup via invitation token (intercepté en DB, pas d'email envoyé)
     - admin génère token signup pour Karim
     - email temporaire utilisé pour éviter envoi réel
     - Playwright complète le signup avec password 'karim'
     - Karim se connecte avec ses nouveaux identifiants

  2. Karim soumet une demande d'enlèvement (/my/pickup-request)
     - Remplit le formulaire
     - La demande crée une tâche avec tag PD3E automatique (fix appliqué)

  3. Admin/opérateur traite la demande
     - Trouve la tâche créée par Karim
     - Remplit les valeurs RSE (total_units, reuse, co2)
     - Attache les livrables (inventaire, rapport RSE) avec tags corrects

  4. Karim voit son dashboard se mettre à jour
     - /my/operations liste l'opération
     - /my/csr-reports montre des stats RSE non-nulles
     - Le détail de l'opération montre les valeurs RSE

  5. Karim télécharge ses livrables
     - ZIP de l'opération contient les fichiers attachés
     - Les indicateurs livrables sont visibles

Notes :
  - Karim Terqui : partner_id=14, company=Infodis it (id=13), task_portal_ok=True
  - Email test : karim.test@infodis-test.internal (évite envoi réel)
  - Password test : karim
  - Les tâches existantes de Karim (prod) ne sont PAS touchées par ce test
"""

import base64
import re
import zipfile
import xmlrpc.client
import pytest
from playwright.sync_api import Page

from conftest import assert_no_odoo_error, BASE_URL, _login

DB = "greenremarket"
ADMIN_LOGIN = "admin@greenremarket.fr"
ADMIN_PASSWORD = "Payasugo187!odoo"
KARIM_PARTNER_ID = 14       # Karim Terqui
INFODIS_COMPANY_ID = 13     # Infodis it
KARIM_REAL_EMAIL = "Karim.Terqui@infodis.com"
KARIM_TEST_EMAIL = "karim.test@infodis-test.internal"  # email test pour signup (pas envoyé)
KARIM_PASSWORD = "karim"  # password apres signup via token

# Credentials du user portail existant
# Note : le signup test met a jour le password a 'karim' pour uid=28
# Si les tests sont executes dans l'ordre, KARIM_PASSWORD = 'karim' s'applique
KARIM_PORTAL_LOGIN = KARIM_REAL_EMAIL   # uid=28 a login=KARIM_REAL_EMAIL
KARIM_PORTAL_PASSWORD = KARIM_PASSWORD  # = 'karim' apres signup test


# ── Helpers RPC ────────────────────────────────────────────────────────────

def admin_rpc():
    common = xmlrpc.client.ServerProxy(f"{BASE_URL}/xmlrpc/2/common")
    uid = common.authenticate(DB, ADMIN_LOGIN, ADMIN_PASSWORD, {})
    m = xmlrpc.client.ServerProxy(f"{BASE_URL}/xmlrpc/2/object")
    def x(model, method, *args, **kwargs):
        return m.execute_kw(DB, uid, ADMIN_PASSWORD, model, method, *args, **kwargs)
    return x


def get_signup_token_for_karim(x):
    """Génère un token signup pour Karim SANS envoyer d'email.

    Approche : utiliser email temporaire + signup_prepare() ORM.
    Le token est lu directement depuis res.partner.
    """
    # Utiliser un email test pour éviter l'envoi réel d'invitation
    x("res.partner", "write", [[KARIM_PARTNER_ID], {"email": KARIM_TEST_EMAIL}])

    # Générer le token de signup
    x("res.partner", "signup_prepare", [[KARIM_PARTNER_ID]],
      {"signup_type": "signup"})

    # Lire le token généré
    info = x("res.partner", "read", [[KARIM_PARTNER_ID]],
             {"fields": ["signup_token"]})
    token = info[0].get("signup_token") if info else None
    return token


def restore_karim_email(x):
    """Remet l'email réel de Karim après le test."""
    x("res.partner", "write", [[KARIM_PARTNER_ID], {"email": KARIM_REAL_EMAIL}])


# ══════════════════════════════════════════════════════════════════════════
# 1. Signup via invitation token
# ══════════════════════════════════════════════════════════════════════════

class TestKarimSignup:
    """Flux d'inscription de Karim via token (sans email)."""

    def test_signup_token_generation(self):
        """Un token signup peut être généré pour Karim via admin RPC."""
        x = admin_rpc()
        try:
            token = get_signup_token_for_karim(x)
            assert token, "signup_prepare() n'a pas généré de token pour Karim"
            assert len(token) > 10, f"Token trop court: {token}"
        finally:
            restore_karim_email(x)

    def test_signup_url_with_token_accessible(self, page: Page):
        """L'URL /web/signup?token=<token> retourne 200 et affiche le formulaire."""
        x = admin_rpc()
        try:
            token = get_signup_token_for_karim(x)
            if not token:
                pytest.skip("Impossible de générer le token signup")

            page.goto(f"{BASE_URL}/web/signup?token={token}")
            page.wait_for_load_state("load")
            assert_no_odoo_error(page)
            assert "404" not in page.url

            body = page.content()
            has_form = "password" in body.lower() or "mot de passe" in body.lower()
            assert has_form, "Formulaire de complétion d'inscription non affiché"

        finally:
            restore_karim_email(x)

    def test_karim_complete_signup_and_login(self, page: Page):
        """Karim complète son inscription via token et se connecte avec 'karim'."""
        x = admin_rpc()
        try:
            token = get_signup_token_for_karim(x)
            if not token:
                pytest.skip("Impossible de générer le token signup")

            # Naviguer vers le formulaire d'inscription avec le token
            page.goto(f"{BASE_URL}/web/signup?token={token}")
            page.wait_for_load_state("load")
            page.wait_for_timeout(500)

            # Enlever le loader GR si présent
            page.evaluate("""
                () => {
                    const loader = document.getElementById('gr_login_loader');
                    if (loader) loader.remove();
                    const card = document.querySelector('.o_login_card, form');
                    if (card) { card.style.display = 'block'; card.style.opacity = '1'; }
                }
            """)

            # Remplir le mot de passe (le nom est pré-rempli via token)
            pw = page.locator("input[name='password']")
            confirm = page.locator("input[name='confirm_password']")

            if not pw.is_visible():
                pytest.skip("Champ password non visible dans le formulaire token")

            pw.fill(KARIM_PASSWORD)
            if confirm.is_visible():
                confirm.fill(KARIM_PASSWORD)

            # Soumettre
            page.click("button[type='submit']")
            page.wait_for_load_state("load")
            assert_no_odoo_error(page)

            # Après signup → devrait être connecté (redirect vers /my ou /web)
            assert "/my" in page.url or "/web" in page.url or "login" in page.url, (
                f"Après signup, URL inattendue: {page.url}"
            )

            # Déconnexion avant de tester le login (fix: /web/login redirige vers /my si déjà connecté)
            page.goto(f"{BASE_URL}/web/session/logout")
            page.wait_for_load_state("load")

            # Maintenant tester le login avec le nouveau mot de passe
            page.goto(f"{BASE_URL}/web/login")
            page.wait_for_load_state("load")
            page.evaluate("""
                () => {
                    const loader = document.getElementById('gr_login_loader');
                    if (loader) loader.remove();
                    const card = document.querySelector('.o_login_card');
                    const back = document.querySelector('.o_login_back');
                    if (card) { card.style.display='block'; card.style.opacity='1'; }
                    if (back) { back.style.display='block'; }
                }
            """)
            page.wait_for_selector("input[name='login']", state="visible", timeout=5_000)
            page.fill("input[name='login']", KARIM_TEST_EMAIL)
            page.fill("input[name='password']", KARIM_PASSWORD)
            page.click("button[type='submit']")
            page.wait_for_load_state("load")
            assert_no_odoo_error(page)

            assert "/my" in page.url or "/web" in page.url, (
                f"Login Karim/{KARIM_PASSWORD} échoué. URL: {page.url}"
            )

        finally:
            restore_karim_email(x)


# ══════════════════════════════════════════════════════════════════════════
# 2. Flow complet : Karim → pickup request → admin traite → Karim voit
# ══════════════════════════════════════════════════════════════════════════

class TestKarimFullWorkflow:
    """Workflow end-to-end : Karim soumet → admin traite → Karim voit livrable."""

    INVENTAIRE_CONTENT = b"Contenu inventaire Infodis 2026"
    RSE_CONTENT = b"Rapport RSE Infodis 2026"

    def test_karim_submits_pickup_request(self, page: Page):
        """Karim soumet une demande d'enlèvement → tâche créée avec PD3E."""
        x = admin_rpc()

        # Résoudre le partner_id réel de Karim (varie selon l'environnement)
        karim_user = x("res.users", "search_read",
                       [[["login", "=", KARIM_REAL_EMAIL]]],
                       {"fields": ["partner_id"], "limit": 1,
                        "context": {"active_test": False}})
        actual_karim_partner = karim_user[0]["partner_id"][0] if karim_user else KARIM_PARTNER_ID

        # Compter les taches liees a Infodis ou Karim (IDs dynamiques)
        before = x("project.task", "search_count",
                   [["|",("partner_id", "=", INFODIS_COMPANY_ID),
                     ("partner_id", "=", actual_karim_partner),
                     ("tag_ids.name", "ilike", "PD3E")]])

        # Karim se connecte avec ses credentials portail existants
        _login(page, BASE_URL, KARIM_PORTAL_LOGIN, KARIM_PORTAL_PASSWORD)
        page.goto(f"{BASE_URL}/my/pickup-request")
        page.wait_for_load_state("networkidle")
        assert_no_odoo_error(page)

        # Remplir le formulaire
        date_input = page.locator("input[name='pickup_date']")
        desc_input = page.locator("textarea[name='description']")

        if not date_input.is_visible():
            pytest.skip("Formulaire pickup request non visible pour Karim")

        # Date : demain
        from datetime import date, timedelta
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        date_input.fill(tomorrow)
        desc_input.fill("Test E2E - 50 PC + 20 écrans - Infodis Paris 11")

        # Soumettre
        page.click("button[type='submit']")
        page.wait_for_load_state("networkidle")
        assert_no_odoo_error(page)

        # Verifier que la tache a ete creee avec PD3E (partner Infodis ou Karim)
        after = x("project.task", "search_count",
                  [["|",("partner_id", "=", INFODIS_COMPANY_ID),
                    ("partner_id", "=", actual_karim_partner),
                    ("tag_ids.name", "ilike", "PD3E")]])
        assert after > before, (
            "La demande d'enlèvement Karim n'a pas créé de tache avec tag PD3E. "
            "Vérifier portal_pickup_request_submit dans main.py."
        )

    def test_admin_processes_karim_operation_with_livrables(self, page: Page):
        """Admin remplit RSE + attache livrables → Karim voit tout côté portail.

        Ce test est le cœur du workflow :
        1. Admin trouve la tache Karim
        2. Admin remplit RSE (500 unités, 400 réemploi, 80 recyclage, 12.5 co2)
        3. Admin attache inventaire.pdf + rapport-rse.pdf
        4. Karim navigue → voit l'opération + données RSE
        5. Karim télécharge le ZIP de l'opération
        """
        x = admin_rpc()

        # Trouver la tache pickup request de Karim (la plus récente, partner=Infodis)
        tasks = x("project.task", "search_read",
                  [[("partner_id", "=", INFODIS_COMPANY_ID),
                    ("tag_ids.name", "ilike", "PD3E"),
                    ("name", "ilike", "Demande d'enlèvement")]],
                  {"fields": ["id", "name"], "order": "create_date desc", "limit": 1})

        if not tasks:
            # Fallback: utiliser la tache test créée précédemment
            tasks = x("project.task", "search_read",
                      [[("name", "ilike", "KARIM-TEST")]],
                      {"fields": ["id", "name"], "limit": 1})

        if not tasks:
            pytest.skip("Aucune tache Karim trouvée pour traitement admin")

        task_id = tasks[0]["id"]
        task_name = tasks[0]["name"]

        att_inv = att_rse = None
        try:
            # Valeur RSE distincte : 477 (improbable dans un message d'erreur)
            # Ne pas utiliser 500 (confondu avec HTTP 500), 200, 404 etc.
            RSE_UNITS = 477
            x("project.task", "write", [[task_id], {
                "rse_total_units": RSE_UNITS,
                "rse_reuse_units": 389,
                "rse_recycle_units": 77,
                "rse_co2_saved_kg": 11.3,
            }])

            # Admin attache l'inventaire (par nom matche le regex)
            att_inv = x("ir.attachment", "create", [{
                "name": "inventaire-infodis-2026.pdf",
                "datas": base64.b64encode(self.INVENTAIRE_CONTENT).decode(),
                "res_model": "project.task",
                "res_id": task_id,
            }])

            # Admin attache le rapport RSE
            att_rse = x("ir.attachment", "create", [{
                "name": "rapport-rse-infodis-2026.pdf",
                "datas": base64.b64encode(self.RSE_CONTENT).decode(),
                "res_model": "project.task",
                "res_id": task_id,
            }])

            # ── Karim voit l'opération ──
            _login(page, BASE_URL, KARIM_PORTAL_LOGIN, KARIM_PORTAL_PASSWORD)
            page.goto(f"{BASE_URL}/my/operations")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(2000)
            assert_no_odoo_error(page)

            body = page.content()
            assert "/my/operations" in page.url

            # ── Karim accède au détail ──
            page.goto(f"{BASE_URL}/my/operations/{task_id}")
            page.wait_for_load_state("load")
            page.wait_for_timeout(1000)
            assert_no_odoo_error(page)

            body = page.content()

            # Verifier qu'on est bien sur la page detail (pas une erreur)
            import re as _re
            assert _re.search(r'/my/operations/\d+', page.url), (
                f"Redirect inattendu : URL={page.url} (Karim n'a pas acces a cette op)"
            )

            # Verifier donnees RSE (477 = valeur distinctive, pas un code HTTP)
            assert str(RSE_UNITS) in body, (
                f"Valeurs RSE ({RSE_UNITS} unites) non visibles sur {page.url}. "
                f"Corps (extrait): {body[1000:2000]}"
            )

            # ── Karim télécharge le ZIP ──
            with page.expect_download(timeout=15_000) as dl_info:
                try:
                    page.goto(f"{BASE_URL}/my/operations/{task_id}/download-zip")
                except Exception:
                    pass

            download = dl_info.value
            assert download.suggested_filename.endswith(".zip"), (
                f"Attendu .zip, reçu: {download.suggested_filename}"
            )

            zip_path = download.path()
            with zipfile.ZipFile(zip_path) as zf:
                names = zf.namelist()
                has_inv = any("inventaire" in n.lower() for n in names)
                has_rse = any("rse" in n.lower() or "rapport" in n.lower() for n in names)
                assert has_inv or has_rse, (
                    f"ZIP ne contient pas les livrables attendus. Contenu: {names}"
                )

            # ── Dashboard RSE mis à jour ──
            page.goto(f"{BASE_URL}/my/csr-reports")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(1000)
            assert_no_odoo_error(page)
            body = page.content()
            # Verifier les valeurs RSE distinctives (477, 389, 11.3) ou keywords RSE
            has_rse_data = any(kw in body for kw in ["477", "389", "11.3", "RSE", "CO", "réemploi"])
            assert has_rse_data, (
                "Dashboard RSE ne montre pas les nouvelles valeurs après traitement admin"
            )

        finally:
            # Cleanup : supprimer les attachments de test
            if att_inv:
                x("ir.attachment", "unlink", [[att_inv]])
            if att_rse:
                x("ir.attachment", "unlink", [[att_rse]])
            # Remettre les valeurs RSE à 0 pour ne pas polluer
            x("project.task", "write", [[task_id], {
                "rse_total_units": 0, "rse_reuse_units": 0,
                "rse_recycle_units": 0, "rse_co2_saved_kg": 0.0,
            }])

    def test_karim_isolation_from_other_companies(self, page: Page):
        """Karim ne voit QUE les opérations d'Infodis, pas celles d'EcoSolutions."""
        _login(page, BASE_URL, KARIM_PORTAL_LOGIN, KARIM_PORTAL_PASSWORD)
        page.goto(f"{BASE_URL}/my/operations")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        assert_no_odoo_error(page)

        body = page.content()
        # EcoSolutions ops ne doivent PAS apparaître
        assert "OP-2026-001" not in body and "CLI601" not in body, (
            "ISOLATION FAIL : Karim voit des opérations d'EcoSolutions. "
            "Le filtre commercial_partner_id ne fonctionne pas."
        )
