# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class AuditReportXlsxWizard(models.TransientModel):
    _name = 'audit.report.xlsx.wizard'
    _description = 'Audit Report XLSX Export Wizard'

    lot_name = fields.Char(
        string='Lot', 
        required=True, 
        help="Enter the lot name to generate the audit report for"
    )
    
    # Alias field for compatibility with old code/views
    lot = fields.Char(
        string='Lot (deprecated)', 
        compute='_compute_lot',
        inverse='_inverse_lot',
        help="Compatibility field - use lot_name instead"
    )
    
    @api.depends('lot_name')
    def _compute_lot(self):
        for record in self:
            record.lot = record.lot_name
    
    def _inverse_lot(self):
        for record in self:
            record.lot_name = record.lot

    def export_xlsx_report(self):
        """
        Export the Audit Report as XLSX.
        Validates the lot name and triggers the report generation.
        """
        self.ensure_one()
        lot = (self.lot_name or '').strip().upper()
        if not lot:
            raise UserError('Please enter a valid Lot Name.')
            
        # Log the report generation for auditing
        _logger.info("Generating Audit XLSX Report for lot: %s", lot)
        
        # Check if lot exists and get data
        erasure_service = self.env['gr.erasure.service']
        if not erasure_service.lot_exists(lot):
            raise UserError(f'Lot {lot} not found in the database.')
            
        data = erasure_service.fetch_audit_for_lot(lot)
        if not data:
            raise UserError(f'No data found for lot {lot}.')
        
        # Return the report action
        return self.env.ref('gr_project_inventory.action_audit_report_xlsx').report_action(
            self, 
            data={'lot_name': lot, 'lot': lot}  # Pass both for maximum compatibility
        )

