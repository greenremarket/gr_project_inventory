# -*- coding: utf-8 -*-
from odoo import models, _
from odoo.exceptions import UserError
import io
import xlsxwriter
from datetime import datetime

class AuditReportXLSX(models.AbstractModel):
    _name = 'report.gr_project_inventory.audit_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Audit Report XLSX'
    _model = 'project.task'

    def create_xlsx_report(self, ids, data):
        _logger = models.logging.getLogger(__name__)
        _logger.info(f"create_xlsx_report called with ids: {ids} and data: {data}")

        if not data:
            _logger.error("No data provided for the report generation.")
            raise ValueError("No data provided for the report generation.")
        
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        # No need to fetch tasks for this report, as all data comes from the wizard/context
        self.generate_xlsx_report(workbook, data, None)
        workbook.close()
        report_content = output.getvalue()

        return report_content, 'xlsx'

    def generate_xlsx_report(self, workbook, data, tasks):
        _logger = models.logging.getLogger(__name__)
        _logger.info("Generating Audit XLSX report.")
        
        lot_name = data.get('lot_name', '').strip().upper()
        if not lot_name:
            raise UserError(_('No Lot Name provided for the audit report.'))

        # Fetch all audit device data for the lot_name
        try:
            audit_rows = self.env['gr.erasure.service'].fetch_audit_for_lot(lot_name)
        except Exception as e:
            _logger.error(f"Error fetching audit data: {str(e)}")
            raise UserError(_('Could not fetch Aiken/Workbench audit data for lot %s: %s') % (lot_name, str(e)))

        if not audit_rows:
            raise UserError(_('No such lot "%s" exists in Aiken/Workbench.') % lot_name)

        # Create worksheet
        sheet = workbook.add_worksheet('Rapport Audit')

        # Define formats
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 22,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#C5E0B4',  # Light pastel green
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
            'border': 1,
            'border_color': '#D9D9D9',  # Light gray border
            'bg_color': '#E2EFD9',  # Lighter pastel green for alternating rows
            'text_wrap': True
        })

        # Define column headers and widths
        columns = [
            ('UnitID', 15),
            ('LotID', 15),
            ('AssetTag', 20),
            ('Created', 15),
            ('ProductType', 20),
            ('Manufacturer', 20),
            ('Model', 25),
            ('Chassis', 15),
            ('PartNumber', 20),
            ('SerialNumber', 20),
            ('DisplaySize', 15),
            ('Resolution', 15),
            ('Processor', 20),
            ('ProcSpeed', 15),
            ('ProcGen', 15),
            ('RAM', 15),
            ('Storage1Size', 15),
            ('Storage1Type', 15),
            ('Storage1Model', 25),
            ('Storage1Serial', 20),
            ('Optical', 15),
            ('Keyb', 10),
            ('Webcam', 10),
            ('Videocard', 20),
            ('OSRestored', 15),
            ('ObservCodes', 20),
            ('ObservNotes', 30),
            ('Grade', 10)
        ]

        # Set column widths
        for col_idx, (_, width) in enumerate(columns):
            sheet.set_column(col_idx, col_idx, width)

        # Set row heights
        sheet.set_row(0, 75)  # Title row height
        sheet.set_row(1, 30)  # Header row height

        # Write title - merge cells for the full width
        sheet.merge_range(0, 0, 0, len(columns) - 1, 
                         f"RAPPORT D'AUDIT - LOT: {lot_name}", 
                         title_format)

        # Write headers
        for col_idx, (header, _) in enumerate(columns):
            sheet.write(1, col_idx, header, header_format)

        # Write data rows
        for row_idx, audit_row in enumerate(audit_rows, start=2):
            row_format = cell_format
            if row_idx % 2 == 0:  # Alternate row colors
                row_format = cell_format
            else:
                row_format = workbook.add_format({
                    'align': 'left',
                    'valign': 'vcenter',
                    'border': 1,
                    'border_color': '#D9D9D9',
                    'bg_color': 'white',
                    'text_wrap': True
                })
            
            # Map the audit row data to our columns
            for col_idx, (field, _) in enumerate(columns):
                # The SQL returns keys with exact case as in the SELECT, so use the field name as-is
                value = audit_row.get(field, '')
                # Defensive: fallback to lower-case if not found
                if value == '' and field.lower() in audit_row:
                    value = audit_row.get(field.lower(), '')
                sheet.write(row_idx, col_idx, value, row_format)

        # Add a footer with generation info
        sheet.set_footer(f"&L&G&CDocument généré le {datetime.now().strftime('%d/%m/%Y %H:%M')} par Odoo")

        # Set print settings
        sheet.set_landscape()
        sheet.set_paper(9)  # A4
        sheet.fit_to_pages(1, 0)  # Fit to 1 page wide
        sheet.print_area(0, 0, row_idx, len(columns) - 1)  # Set print area
