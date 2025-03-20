from odoo import models
import io
import base64
import xlsxwriter

class DiscrepancyReportXLSX(models.AbstractModel):
    _name = 'report.gr_project_inventory.discrepancy_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Discrepancy Report XLSX'
    _model = 'project.task'  # Specify the model associated with the report

    def create_xlsx_report(self, ids, data):
        # Ajout de journaux pour vérifier les données et les IDs
        _logger = models.logging.getLogger(__name__)
        _logger.info(f"create_xlsx_report called with ids: {ids} and data: {data}")

        if not ids:
            _logger.error("No IDs provided for the report generation.")
            raise ValueError("No IDs provided for the report generation.")
        if not data:
            _logger.error("No data provided for the report generation.")
            raise ValueError("No data provided for the report generation.")
        
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        tasks = self.env[self._model].browse(ids)
        
        if not tasks:
            _logger.error("No tasks found for the provided IDs.")
            raise ValueError("No tasks found for the provided IDs.")
        
        # Ajout de vérifications pour les tâches
        for task in tasks:
            if not task:
                _logger.error(f"Task {task.id} is None.")
                raise ValueError(f"Task {task.id} is None.")
            if not task.name:
                _logger.error(f"Task {task.id} has no name.")
                raise ValueError(f"Task {task.id} has no name.")
            if not task.discrepancies_ids:
                _logger.error(f"Task {task.id} has no discrepancies.")
                raise ValueError(f"Task {task.id} has no discrepancies.")
        
        self.generate_xlsx_report(workbook, data, tasks)
        workbook.close()
        report_content = output.getvalue()

        # Create attachments for tasks
        for task in tasks:
            report_name = 'Discrepancy Report - %s.xlsx' % task.name
            attachment = self.env['ir.attachment'].create({
                'name': report_name,
                'type': 'binary',
                'datas': base64.b64encode(report_content),
                'res_model': self._model,
                'res_id': task.id,
                'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'public': True,
            })
            task.message_post(body="Discrepancy report generated", attachment_ids=[attachment.id])

        return report_content, 'xlsx'

    def generate_xlsx_report(self, workbook, data, tasks):
        _logger = models.logging.getLogger(__name__)
        _logger.info("Generating XLSX report.")
        
        # Vérification initiale des tâches
        if not tasks:
            _logger.error("No tasks provided for the report generation.")
            raise ValueError("No tasks provided for the report generation.")
        
        sheet = workbook.add_worksheet('Discrepancy Report')

        # Définir les formats pour l'en-tête
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
            'bg_color': '#F9DA04',
            'align': 'center',
            'valign': 'vcenter',
        })

        # Définir les formats pour les données
        data_format = workbook.add_format({
            'align': 'left',
            'valign': 'vcenter',
            'text_wrap': True,
        })

        # Ajuster la hauteur de la première ligne pour le logo et le titre
        sheet.set_row(0, 80)  # Hauteur ajustée à 80 px

        # Définir la largeur des colonnes
        sheet.set_column('A:A', 20)  # Colonne A pour le logo
        sheet.set_column('B:G', 25)  # Colonnes B à G pour le titre et autres données

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

        # Écrire le texte du titre au centre de l'en-tête fusionné (colonnes B à G)
        sheet.merge_range('B1:G1', "RAPPORT D'ECARTS D'INVENTAIRE".upper(), header_merge_format)

        # Passer à la ligne suivante pour les en-têtes de table
        current_row = 2

        # Définir les en-têtes des colonnes
        headers = ['Item Name', 'Item Type', 'Discrepancy Name', 'Discrepancy Type', 'Serial Number', 'Internal Asset Tag', 'Client Asset Tag', 'Pallet Number']
        for col, header in enumerate(headers):
            sheet.write(current_row, col, header, table_header_format)
        
        current_row += 1

        # Écrire les données des lignes de disparité
        for task in tasks:
            _logger.info(f"Processing task {task.id} with name {task.name}.")
            for discrepancy in task.discrepancies_ids:
                col = 0
                item_name = discrepancy.internal_inventory_id.name if discrepancy.internal_inventory_id else (discrepancy.client_inventory_id.name if discrepancy.client_inventory_id else '')
                item_type = discrepancy.internal_inventory_id.product_type_id.name if discrepancy.internal_inventory_id and discrepancy.internal_inventory_id.product_type_id else ''
                sheet.write(current_row, col, item_name or '', data_format)
                col += 1
                sheet.write(current_row, col, item_type or '', data_format)
                col += 1
                sheet.write(current_row, col, discrepancy.name or '', data_format)
                col += 1
                sheet.write(current_row, col, discrepancy.discrepancy_type or '', data_format)
                col += 1
                sheet.write(current_row, col, discrepancy.serial_number or '', data_format)
                col += 1
                # Write internal asset tag
                sheet.write(current_row, col, discrepancy.internal_inventory_id.asset_tag if discrepancy.internal_inventory_id else '', data_format)
                col += 1
                # Write client asset tag
                sheet.write(current_row, col, discrepancy.client_inventory_id.asset_tag if discrepancy.client_inventory_id else '', data_format)
                col += 1
                sheet.write(current_row, col, discrepancy.pallet_number or '', data_format)
                current_row += 1

        _logger.info("Génération du rapport XLSX terminée avec succès.")
