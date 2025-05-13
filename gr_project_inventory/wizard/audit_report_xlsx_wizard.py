# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class AuditReportXlsxWizard(models.TransientModel):
    _name = 'audit.report.xlsx.wizard'
    _description = 'Audit Report XLSX Export Wizard'

    lot_name = fields.Char(
        string='Lot Name', 
        required=True, 
        help="Enter the project lot name (as used in ProjectTask.lot_name)",
        default=lambda self: self._default_lot_name()
    )

    def _default_lot_name(self):
        """Get the default lot name from the context"""
        return self.env.context.get('default_lot_name', '').strip().upper()

    def action_export_xlsx(self):
        """
        Export the Audit Report as XLSX.
        Validates the lot name and triggers the report generation.
        """
        self.ensure_one()
        lot_name = (self.lot_name or '').strip().upper()
        if not lot_name:
            raise UserError('Please enter a valid Lot Name.')
            
        # Log the report generation for auditing
        _logger.info("Generating Audit XLSX Report for lot: %s", lot_name)
        
        # Pass the lot_name to the report
        data = {'lot_name': lot_name}
        
        # Return the report action
        return self.env.ref('gr_project_inventory.action_audit_report_xlsx').report_action(
            self, 
            data=data
        )

