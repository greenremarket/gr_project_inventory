from odoo import models
import io
import base64
import xlsxwriter
from datetime import datetime

class DiscrepancyReportXLSX(models.AbstractModel):
    _name = 'report.gr_project_inventory.discrepancy_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Discrepancy Report XLSX'
    _model = 'project.task'

    def _get_discrepancy_type_translation(self, discrepancy_type):
        translations = {
            'missing': 'Manquant',
            'extra': 'Surplus',
            'damaged': 'Endommagé',
            'incorrect': 'Incorrect'
        }
        return translations.get(discrepancy_type, discrepancy_type)

    def create_xlsx_report(self, ids, data):
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
        
        for task in tasks:
            if not task:
                _logger.error(f"Task {task.id} is None.")
                raise ValueError(f"Task {task.id} is None.")
            if not task.name:
                _logger.error(f"Task {task.id} has no name.")
                raise ValueError(f"Task {task.id} has no name.")
        
        self.generate_xlsx_report(workbook, data, tasks)
        workbook.close()
        report_content = output.getvalue()

        # Just return the content and let the report framework handle the attachment
        return report_content, 'xlsx'

    def generate_xlsx_report(self, workbook, data, tasks):
        _logger = models.logging.getLogger(__name__)
        _logger.info("Generating XLSX report.")
        
        if not tasks:
            _logger.error("No tasks provided for the report generation.")
            raise ValueError("No tasks provided for the report generation.")
        
        for task in tasks:
            # Create worksheet
            sheet = workbook.add_worksheet('Rapport Ecarts')

            # Define formats
            title_format = workbook.add_format({
                'bold': True,
                'font_size': 22,
                'align': 'center',
                'valign': 'vcenter',
                'bg_color': '#C5E0B4',  # Light pastel green from screenshot
                'font_color': 'white',
                'border': 0
            })

            header_format = workbook.add_format({
                'bold': True,
                'font_size': 10,
                'align': 'center',
                'valign': 'vcenter',
                'bg_color': 'white',  # White interior
                'font_color': '#92D050',  # Dark green text
                'top': 1,
                'bottom': 1,
                'top_color': '#92D050',    # Dark green top border
                'bottom_color': '#92D050',  # Dark green bottom border
                'text_wrap': True
            })

            cell_format = workbook.add_format({
                'align': 'left',
                'valign': 'vcenter',
                'border': 0,
                'bg_color': '#E2EFD9'  # Lighter pastel green for alternating rows
            })

            # Set column widths
            sheet.set_column('A:A', 20)  # Serial Number
            sheet.set_column('B:B', 15)  # Asset Tag
            sheet.set_column('C:C', 15)  # Client Asset Tag
            sheet.set_column('D:D', 35)  # Designation
            sheet.set_column('E:E', 15)  # Part Number
            sheet.set_column('F:F', 15)  # Manufacturer
            sheet.set_column('G:G', 15)  # Product Type
            sheet.set_column('H:H', 15)  # Pallet Number
            sheet.set_column('I:I', 2)   # Extra column for full green background

            # Set row heights
            sheet.set_row(0, 75)  # Title row height - increased for logo and title
            sheet.set_row(1, 30)  # Header row height

            # Write title - covering full width including extra column
            sheet.merge_range('A1:I1', "RAPPORT D'ÉCARTS", title_format)

            # Insert company logo
            company = self.env.company
            if company.logo:
                image_data = io.BytesIO(base64.b64decode(company.logo))
                sheet.insert_image('A1', 'logo.png', {
                    'image_data': image_data,
                    'x_scale': 0.125,
                    'y_scale': 0.125,
                    'x_offset': 5,
                    'y_offset': 5,
                    'positioning': 1
                })

            # Write headers - now center aligned
            headers = [
                'Numéro de série',
                'Asset Tag',
                'Client Asset Tag',
                'Désignation',
                'Type d\'écart',
                'Commentaire',
                'Pallet Number',
                'Date'
            ]
            
            # Write headers with white background and dark green borders/text
            for col, header in enumerate(headers):
                sheet.write(1, col, header, header_format)
            sheet.write(1, 8, '', header_format)  # Extra column to extend formatting

            # Write data starting from row 3
            row = 2
            for discrepancy in task.discrepancies_ids:
                row_format = cell_format if row % 2 else workbook.add_format({'bg_color': '#FFFFFF'})
                sheet.write(row, 0, discrepancy.serial_number or '', row_format)
                sheet.write(row, 1, discrepancy.asset_tag or '', row_format)
                sheet.write(row, 2, '', row_format)  # Client Asset Tag
                sheet.write(row, 3, discrepancy.name or '', row_format)
                sheet.write(row, 4, self._get_discrepancy_type_translation(discrepancy.discrepancy_type) or '', row_format)
                # Combine notes and resolution_notes if they exist
                comments = []
                if discrepancy.notes:
                    comments.append(discrepancy.notes)
                if discrepancy.resolution_notes:
                    comments.append(f"Résolution: {discrepancy.resolution_notes}")
                sheet.write(row, 5, '\n'.join(comments) if comments else '', row_format)
                sheet.write(row, 6, discrepancy.pallet_number or '', row_format)
                sheet.write(row, 7, discrepancy.create_date.strftime('%d/%m/%Y') if discrepancy.create_date else '', row_format)
                sheet.write(row, 8, '', row_format)  # Extra column
                row += 1

        _logger.info("XLSX report generation completed successfully.")
