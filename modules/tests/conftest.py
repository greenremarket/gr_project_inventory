"""
Fixtures Playwright pour les tests E2E du portail Green Remarket.

Variables d'environnement requises :
    ODOO_BASE_URL   (défaut : http://localhost:8069)
    PORTAL_USER     (login utilisateur portal)
    PORTAL_PASSWORD (mot de passe utilisateur portal)
    ODOO_DB         (TOUJOURS greenremarket)
    OPERATOR_USER   (login opérateur backend)
    SUPERVISOR_USER (login superviseur backend)

Usage :
    pytest --headed                       # debug visuel
    pytest --screenshot=only-on-failure   # CI
"""

import os
import re

import pytest
from playwright.sync_api import Page, expect

BASE_URL = os.environ.get("ODOO_BASE_URL", "http://localhost:8069")
# Users seedés par scripts/seed-test-data.py (idempotent)
# Ces defaults évitent de dépendre de l'utilisateur admin (qui peut rediriger vers helpdesk)
PORTAL_USER = os.environ.get("PORTAL_USER", "client@ecosolutions.fr")
PORTAL_PASSWORD = os.environ.get("PORTAL_PASSWORD", "TestGrm2026!")
ODOO_DB = os.environ.get("ODOO_DB", "greenremarket")

# Rôles backend — defaults = admin (toujours actif sur CT201 et CT202).
# operateur@ et superviseur@ sont archivés sur les deux instances pour
# ne pas consommer de sièges licence Odoo Enterprise.
# Pour tester un rôle spécifique, passer OPERATOR_USER/SUPERVISOR_USER en env.
INTERNAL_USER = os.environ.get("INTERNAL_USER", "admin@greenremarket.fr")
INTERNAL_PASSWORD = os.environ.get("INTERNAL_PASSWORD", "Payasugo187!odoo")
OPERATOR_USER = os.environ.get("OPERATOR_USER", "admin@greenremarket.fr")
OPERATOR_PASSWORD = os.environ.get("OPERATOR_PASSWORD", "Payasugo187!odoo")
SUPERVISOR_USER = os.environ.get("SUPERVISOR_USER", "admin@greenremarket.fr")
SUPERVISOR_PASSWORD = os.environ.get("SUPERVISOR_PASSWORD", "Payasugo187!odoo")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def assert_no_odoo_error(page: Page):
    """Vérifie qu'il n'y a pas de traceback Odoo / erreur 500 dans le body."""
    body = page.content()
    assert "Internal Server Error" not in body, "Erreur 500 détectée"
    assert "Traceback (most recent call last)" not in body, "Traceback Python détecté"
    assert "odoo.exceptions" not in body, "Exception Odoo détectée"


def assert_gr_layout(page: Page):
    """Vérifie que le layout GR portal est chargé (sidebar ou header GR)."""
    page.wait_for_selector("body", timeout=10_000)
    assert_no_odoo_error(page)


def _login(page: Page, base_url: str, login: str, password: str) -> Page:
    """Login générique via /web/login.
    
    Gère le nouveau login GR portal (hero en premier plan, form caché par défaut).
    Si le champ login n'est pas visible, cliquer sur le bouton CTA d'abord.
    """
    page.goto(f"{base_url}/web/login")
    page.wait_for_load_state("networkidle")

    db_select = page.locator("select[name='db']")
    if db_select.is_visible():
        db_select.select_option(ODOO_DB)

    # Nouveau login GR : manipulation DOM directe pour tests headless.
    # Le widget Odoo peut ne pas être initialisé sur la page login.
    # On force l'affichage du formulaire en JS.
    page.evaluate("""
        () => {
            const loader = document.getElementById('gr_login_loader');
            if (loader) loader.remove();
            const hero = document.querySelector('.o_login_hero');
            const card = document.querySelector('.o_login_card');
            const back = document.querySelector('.o_login_back');
            if (hero) hero.style.display = 'none';
            if (card) { card.style.display = 'block'; card.style.opacity = '1'; }
            if (back) { back.style.display = 'block'; back.style.opacity = '1'; }
        }
    """)
    page.wait_for_selector("input[name='login']", state="visible", timeout=5_000)

    page.fill("input[name='login']", login)
    page.fill("input[name='password']", password)
    page.click("button[type='submit']")
    # 'load' au lieu de 'networkidle' : le backend Odoo 17 (SPA) fait
    # de nombreux appels API qui empêchent networkidle dans les 30s.
    page.wait_for_load_state("load")
    assert_no_odoo_error(page)
    return page


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture(scope="session")
def browser_context_args():
    return {
        "viewport": {"width": 1280, "height": 800},
        "locale": "fr-FR",
        "ignore_https_errors": True,
    }


# ——————————————————————————————————————————————————————————————————————
# Contextes partagés par session — login UNE SEULE FOIS par rôle
# ——————————————————————————————————————————————————————————————————————

@pytest.fixture(scope="session")
def portal_context(browser, base_url):
    """Contexte Playwright authentifié portail — partagé sur toute la session."""
    ctx = browser.new_context(
        viewport={"width": 1280, "height": 800},
        locale="fr-FR",
        ignore_https_errors=True,
    )
    page = ctx.new_page()
    _login(page, base_url, PORTAL_USER, PORTAL_PASSWORD)
    # /web/login contient '/web' -> ne pas accepter comme login reussi
    assert "/my" in page.url or ("/web" in page.url and "/login" not in page.url), (
        f"Login portal echoue (reste sur login page) — URL : {page.url}"
    )
    page.close()
    yield ctx
    ctx.close()


@pytest.fixture(scope="session")
def internal_context(browser, base_url):
    """Contexte Playwright authentifié interne — partagé sur toute la session."""
    login = OPERATOR_USER or INTERNAL_USER
    password = OPERATOR_PASSWORD or INTERNAL_PASSWORD
    ctx = browser.new_context(
        viewport={"width": 1280, "height": 800},
        locale="fr-FR",
        ignore_https_errors=True,
    )
    page = ctx.new_page()
    _login(page, base_url, login, password)
    assert "/web" in page.url or "/my" in page.url, (
        f"Login interne échoué — URL : {page.url}"
    )
    page.close()
    yield ctx
    ctx.close()


@pytest.fixture(scope="session")
def supervisor_context(browser, base_url):
    """Contexte Playwright authentifié superviseur — partagé sur toute la session."""
    login = SUPERVISOR_USER or INTERNAL_USER
    password = SUPERVISOR_PASSWORD or INTERNAL_PASSWORD
    ctx = browser.new_context(
        viewport={"width": 1280, "height": 800},
        locale="fr-FR",
        ignore_https_errors=True,
    )
    page = ctx.new_page()
    _login(page, base_url, login, password)
    assert "/web" in page.url or "/my" in page.url, (
        f"Login superviseur échoué — URL : {page.url}"
    )
    page.close()
    yield ctx
    ctx.close()


# ——————————————————————————————————————————————————————————————————————
# Fixtures par test — page fraîche depuis le contexte partagé (pas de re-login)
# ——————————————————————————————————————————————————————————————————————

@pytest.fixture()
def logged_in_page(portal_context):
    """Page portal fraîche — session déjà authentifiée (pas de re-login)."""
    page = portal_context.new_page()
    yield page
    page.close()


@pytest.fixture()
def portal_navigate(logged_in_page: Page, base_url: str):
    """Factory fixture pour naviguer vers une route portail."""

    def _navigate(path: str) -> Page:
        logged_in_page.goto(f"{base_url}{path}")
        logged_in_page.wait_for_load_state("networkidle")
        assert_no_odoo_error(logged_in_page)
        return logged_in_page

    return _navigate


@pytest.fixture()
def internal_page(internal_context):
    """Page interne fraîche — session déjà authentifiée."""
    page = internal_context.new_page()
    yield page
    page.close()


@pytest.fixture()
def internal_navigate(internal_page: Page, base_url: str):
    """Factory fixture pour naviguer vers une route backend."""

    def _navigate(path: str) -> Page:
        internal_page.goto(f"{base_url}{path}")
        # 'load' pour le backend Odoo SPA — networkidle ne se stabilise jamais < 30s
        internal_page.wait_for_load_state("load")
        assert_no_odoo_error(internal_page)
        return internal_page

    return _navigate


@pytest.fixture()
def supervisor_page(supervisor_context):
    """Page superviseur fraîche — session déjà authentifiée."""
    page = supervisor_context.new_page()
    yield page
    page.close()


@pytest.fixture()
def supervisor_navigate(supervisor_page: Page, base_url: str):
    """Factory fixture pour naviguer en tant que superviseur."""

    def _navigate(path: str) -> Page:
        supervisor_page.goto(f"{base_url}{path}")
        supervisor_page.wait_for_load_state("load")
        assert_no_odoo_error(supervisor_page)
        return supervisor_page

    return _navigate
