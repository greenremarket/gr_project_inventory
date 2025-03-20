import logging
import io
import base64
from odoo import models, api
import xlsxwriter

_logger = logging.getLogger(__name__)

class InternalInventoryReportXLSX(models.AbstractModel):
    _name = 'report.gr_project_inventory.internal_inventory_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Internal Inventory Report XLSX'

    @api.model
    def generate_xlsx_report(self, workbook, data, tasks):
        _logger.info("Génération du rapport XLSX commencée.")

        # Définir les formats
        header_merge_format = workbook.add_format({
            'bold': True,
            'font_color': '#FFFFFF',
            'bg_color': '#9BBB59',
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 20,  # Taille de la police augmentée
        })

        table_header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D3D3D3',
            'align': 'center',
            'valign': 'vcenter',
        })

        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})

        for task in tasks:
            _logger.info(f"Traitement de la tâche ID: {task.id}, Nom: {task.name}")

            report_name = f'Internal Inventory Report - {task.name}'
            sheet_name = report_name[:31]  # Limite à 31 caractères
            sheet = workbook.add_worksheet(sheet_name)

            # Ajuster la hauteur de la première ligne pour le logo et le titre
            sheet.set_row(0, 80)  # Hauteur ajustée à 80 px

            # Définir la largeur des colonnes
            sheet.set_column('A:A', 20)  # Colonne A pour le logo
            sheet.set_column('B:K', 25)  # Colonnes B à K pour le titre et autres données (élargi pour inclure les nouveaux champs)

            # Insérer le logo de l'entreprise avec des offsets et une échelle appropriée
            company = self.env.company
            if company.logo:
                try:
                    logo_bytes = base64.b64decode(company.logo)
                    sheet.insert_image('A1', 'logo.png', {
                        'image_data': io.BytesIO(logo_bytes),
                        'x_scale': 0.1,  # Réduction horizontale du logo
                        'y_scale': 0.1,  # Réduction verticale du logo
                        'x_offset': 5,     # Décalage horizontal
                        'y_offset': 10     # Décalage vertical pour aligner le logo avec le titre
                    })
                except Exception as e:
                    _logger.error(f"Échec de l'insertion du logo de l'entreprise : {e}")
            else:
                _logger.warning("Aucun logo trouvé pour l'entreprise.")

            # Écrire le texte du titre au centre de l'en-tête fusionné (colonnes B à K)
            sheet.merge_range('B1:K1', "INVENTAIRE ET SORTIE COMPTABLE".upper(), header_merge_format)

            # Passer à la ligne suivante pour les en-têtes de table
            current_row = 2

            headers = [
                'Serial Number', 'Asset Tag', 'Client Asset Tag', 'Name', 'Model', 'Manufacturer',
                'Product Type', 'Warehouse Location', 'Pallet Number', 'Status', 'Observation'
            ]
            for col, header in enumerate(headers):
                sheet.write(current_row, col, header, table_header_format)
            current_row += 1

            # Écrire les données des lignes d'inventaire
            for item in task.inventory_line_ids:
                sheet.write(current_row, 0, item.serial_number or '')
                sheet.write(current_row, 1, item.asset_tag or '')
                sheet.write(current_row, 2, item.client_asset_tag or '')
                sheet.write(current_row, 3, item.name or '')
                sheet.write(current_row, 4, item.part_number or '')  # Utiliser part_number pour Model
                sheet.write(current_row, 5, item.manufacturer_id.name if item.manufacturer_id else '')
                sheet.write(current_row, 6, item.product_type_id.name if item.product_type_id else '')
                sheet.write(current_row, 7, item.wareh_location or '')
                sheet.write(current_row, 8, item.pallet_number or '')
                sheet.write(current_row, 9, item.status or '')
                sheet.write(current_row, 10, item.observation_id.name if item.observation_id else '')
                current_row += 1

        _logger.info("Génération du rapport XLSX terminée avec succès.")
