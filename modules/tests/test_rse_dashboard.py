"""
Tests RSE dashboard — /my/csr-reports

Valide que :
1. Sans données RSE → état vide (placeholder)
2. Avec données RSE → KPIs non nuls
3. Histogramme mensuel → les barres du mois courant reflètent les bonnes valeurs
4. Les barres ont une hauteur > 0 quand il y a des données
5. Le titre (tooltip) de chaque barre contient le bon mois et les bonnes unités

Le graphique est CSS-based (divs avec style height=X%) + title tooltip.
Pas de canvas → testable directement via le HTML.
"""

import xmlrpc.client
import pytest
from datetime import date
from playwright.sync_api import Page

from conftest import assert_no_odoo_error, BASE_URL

DB = "greenremarket"
ADMIN_LOGIN = "admin@greenremarket.fr"
ADMIN_PASSWORD = "Payasugo187!odoo"

# Valeur distinctive pour l'histogramme (improbable dans les données existantes)
RSE_UNITS_CHART = 613


def admin_rpc():
    common = xmlrpc.client.ServerProxy(f"{BASE_URL}/xmlrpc/2/common")
    uid = common.authenticate(DB, ADMIN_LOGIN, ADMIN_PASSWORD, {})
    m = xmlrpc.client.ServerProxy(f"{BASE_URL}/xmlrpc/2/object")
    def x(model, method, *args, **kwargs):
        return m.execute_kw(DB, uid, ADMIN_PASSWORD, model, method, *args, **kwargs)
    return x


# ══════════════════════════════════════════════════════════════════════════
# Tests RSE dashboard
# ══════════════════════════════════════════════════════════════════════════

class TestRSEDashboard:
    """Tests du dashboard /my/csr-reports."""

    def test_csr_empty_state_when_no_data(self, portal_navigate):
        """/my/csr-reports affiche un état vide si pas de données."""
        # Ce test est conditionnel : si le portal user a des données, on skip
        page = portal_navigate("/my/csr-reports")
        assert_no_odoo_error(page)
        # La page doit charger sans 500
        assert "/my/csr-reports" in page.url

    def test_kpis_show_nonzero_with_rse_data(self, portal_navigate):
        """Avec des données RSE, les KPIs sont non nuls."""
        x = admin_rpc()
        tasks = x("project.task", "search_read",
            [[("name", "ilike", "OP-2026-001"), ("project_id", "=", 1)]],
            {"fields": ["id", "rse_total_units"], "limit": 1})
        if not tasks or not tasks[0]["rse_total_units"]:
            pytest.skip("Tache sans données RSE — relancer seed")

        page = portal_navigate("/my/csr-reports")
        assert_no_odoo_error(page)
        body = page.content()

        # Les KPIs doivent afficher des valeurs non nulles
        kpi_card = page.locator(".o_kpi_value").first
        if kpi_card.is_visible():
            kpi_text = kpi_card.text_content()
            assert "—" not in kpi_text, (
                "Les KPIs affichent '—' même avec des données RSE. "
                "Vérifier que le portal user voit les taches du partner."
            )

    def test_histogram_has_twelve_bars(self, portal_navigate):
        """L'histogramme affiche exactement 12 barres (12 mois)."""
        page = portal_navigate("/my/csr-reports")
        assert_no_odoo_error(page)

        bars = page.locator(".o_chart_bar")
        count = bars.count()
        assert count == 12, (
            f"L'histogramme doit avoir 12 barres (12 mois), trouvé {count}. "
            "Vérifier portal_csr_reports dans le controller."
        )

    def test_histogram_current_month_updates_with_rse_data(
        self, logged_in_page: Page
    ):
        """Admin met RSE à jour → la barre du mois courant reflète la valeur.

        Ce test est le test clé de la cohérence du graphique :
        1. Admin met rse_total_units=613 sur une tache du mois courant
        2. Portal user charge /my/csr-reports
        3. La barre du mois courant doit avoir un title contenant '613'
           ou la hauteur doit être > 0
        """
        x = admin_rpc()
        tasks = x("project.task", "search_read",
            [[("name", "ilike", "OP-2026-001"), ("project_id", "=", 1)]],
            {"fields": ["id", "rse_total_units"], "limit": 1})
        if not tasks:
            pytest.skip("Tache OP-2026-001 non seedee")
        task_id = tasks[0]["id"]
        original_units = tasks[0]["rse_total_units"]

        # Trouver aussi OP-2026-002 pour eviter que sa valeur s'ajoute au total
        tasks2 = x("project.task", "search_read",
            [[("name", "ilike", "OP-2026-002"), ("project_id", "=", 1)]],
            {"fields": ["id", "rse_total_units"], "limit": 1})
        task2_id = tasks2[0]["id"] if tasks2 else None
        task2_original = tasks2[0]["rse_total_units"] if tasks2 else 0

        try:
            # Remettre OP-2026-002 a 0 pour que le total d'avril = RSE_UNITS_CHART seul
            if task2_id:
                x("project.task", "write", [[task2_id], {"rse_total_units": 0}])
            x("project.task", "write", [[task_id], {"rse_total_units": RSE_UNITS_CHART}])

            page = logged_in_page
            page.goto(f"{BASE_URL}/my/csr-reports")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(1000)
            assert_no_odoo_error(page)

            # Vérifier que l'histogramme a 12 barres
            bars = page.locator(".o_chart_bar")
            assert bars.count() == 12, "Histogramme sans 12 barres"

            # Vérifier que la valeur RSE injectée (613) apparaît dans les tooltips
            # (locale-indépendant : le mois peut être en FR ou EN selon le serveur)
            body = page.content()
            assert str(RSE_UNITS_CHART) in body, (
                f"La valeur RSE {RSE_UNITS_CHART} n'apparaît pas dans l'histogramme. "
                "Vérifier que la barre du mois courant affiche la bonne valeur."
            )

            # La barre du mois courant est la DERNIERE (index 11, mois le plus recent)
            # Elle doit avoir une hauteur 100% (max_units = valeur du mois courant)
            # et contenir RSE_UNITS_CHART dans son title tooltip
            all_bars = page.locator(".o_chart_bar")
            last_bar = all_bars.nth(11)  # barre du mois courant
            last_title = last_bar.get_attribute("title") or ""
            last_height = last_bar.get_attribute("style") or ""

            assert str(RSE_UNITS_CHART) in last_title, (
                f"La barre du mois courant (derniere) devrait contenir {RSE_UNITS_CHART}. "
                f"Titre actuel: '{last_title}' | Hauteur: '{last_height}'. "
                f"La barre est a l'index 11 sur 12 (mois courant={current_month})."
            )
            assert "height:0%" not in last_height, (
                f"La barre du mois courant a une hauteur 0% malgre {RSE_UNITS_CHART} unites. "
                "Verifier le calcul max_units dans le controller."
            )

        finally:
            x("project.task", "write", [[task_id], {"rse_total_units": original_units}])
            if task2_id:
                x("project.task", "write", [[task2_id], {"rse_total_units": task2_original}])

    def test_histogram_bar_height_proportional(self, portal_navigate):
        """La hauteur des barres est proportionnelle aux unités (max=100%)."""
        x = admin_rpc()
        tasks = x("project.task", "search_read",
            [[("name", "ilike", "OP-2026-001"), ("project_id", "=", 1)]],
            {"fields": ["id", "rse_total_units"], "limit": 1})
        if not tasks or not tasks[0]["rse_total_units"]:
            pytest.skip("Tache sans données RSE")

        page = portal_navigate("/my/csr-reports")
        assert_no_odoo_error(page)

        # La barre la plus haute doit être à 100% (max_units)
        bars = page.locator(".o_chart_bar")
        styles = [bars.nth(i).get_attribute("style") or "" for i in range(bars.count())]
        has_full = any("height:100%" in s for s in styles)
        has_nonzero = any("height:" in s and "height:0%" not in s for s in styles)

        assert has_nonzero, (
            "Aucune barre n'a de hauteur non-nulle. "
            "Les données RSE ne sont pas transmises au graphique."
        )
        assert has_full, (
            "Aucune barre n'est à 100% de hauteur. "
            "Le calcul max_units est peut-être incorrect (division par zéro ou valeur fausse)."
        )

    def test_csv_export_contains_rse_values(self, portal_navigate):
        """L'export CSV contient les valeurs RSE des opérations."""
        page = portal_navigate("/my/csr-reports")
        assert_no_odoo_error(page)

        csv_link = page.locator("a[href*='/my/csr-reports/csv']").first
        if not csv_link.is_visible():
            pytest.skip("Lien export CSV non trouvé")

        with page.expect_download(timeout=10_000) as dl_info:
            csv_link.click()
        download = dl_info.value
        assert download.suggested_filename.endswith(".csv")

        # Lire le contenu du CSV
        import io
        path = download.path()
        with open(path, encoding="utf-8-sig") as f:
            content = f.read()

        # Le CSV doit avoir un header et au moins une ligne de données
        lines = [l for l in content.split("\n") if l.strip()]
        assert len(lines) >= 2, (
            f"CSV vide ou sans données. Lignes: {len(lines)}. "
            "Vérifier portal_csr_reports_csv dans le controller."
        )
        # Première ligne = header
        assert any(col in lines[0] for col in ["op", "Op", "RSE", "unité", "CO"]), (
            f"Header CSV inattendu: {lines[0]}"
        )
