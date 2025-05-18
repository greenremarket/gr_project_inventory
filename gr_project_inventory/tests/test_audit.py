from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import UserError
from unittest.mock import patch, MagicMock
from datetime import datetime

@tagged('gr_project_inventory', 'audit')
class TestAudit(TransactionCase):
    def setUp(self):
        super().setUp()
        self.wizard_model = self.env['audit.report.xlsx.wizard']
        # self.erasure_service = self.env['gr.erasure.service']  # Not needed for patching at class level
        
        # Mock data for testing
        self.mock_data = [{
            'lot': 'AUDT1',
            'serial': 'SN123',
            'model': 'Test Model',
            'manufacturer': 'Test Manufacturer',
            'created': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'osrestored': 'Yes',
            'status': 'Completed'
        }]
        
        # Mock report action
        self.report_action = {
            'type': 'ir.actions.report',
            'report_name': 'gr_project_inventory.audit_report_xlsx',
            'report_type': 'xlsx',
            'report_file': 'gr_project_inventory.audit_report_xlsx',
            'name': 'Audit Report',
            'data': {'lot_name': 'AUDT1', 'lot': 'AUDT1'}
        }

    def test_audit_wizard_creation(self):
        """Test creation of audit report wizard"""
        wizard = self.wizard_model.create({
            'lot_name': 'AUDT1'
        })
        self.assertEqual(wizard.lot_name, 'AUDT1')

    def test_audit_database_connection_error(self):
        """Test handling of database connection error"""
        with patch('odoo.addons.gr_project_inventory.models.erasure_service.ErasureService.lot_exists', side_effect=Exception('Database connection failed')):
            wizard = self.wizard_model.create({
                'lot_name': 'AUDT1'
            })
            with self.assertRaises(Exception) as cm:
                wizard.export_xlsx_report()
            self.assertEqual(str(cm.exception), 'Database connection failed')

    def test_audit_report_generation(self):
        """Test successful audit report generation"""
        with patch('odoo.addons.gr_project_inventory.models.erasure_service.ErasureService.lot_exists', return_value=True), \
             patch('odoo.addons.gr_project_inventory.models.erasure_service.ErasureService.fetch_audit_for_lot', return_value=self.mock_data):
            
            wizard = self.wizard_model.create({
                'lot_name': 'AUDT1'
            })
            result = wizard.export_xlsx_report()
            
            self.assertEqual(result['type'], 'ir.actions.report')
            self.assertEqual(result['report_name'], 'gr_project_inventory.audit_report_xlsx')
            self.assertEqual(result['report_type'], 'xlsx')

    def test_audit_report_multiple_devices(self):
        """Test audit report generation with multiple devices"""
        multiple_devices = self.mock_data * 2
        with patch('odoo.addons.gr_project_inventory.models.erasure_service.ErasureService.lot_exists', return_value=True), \
             patch('odoo.addons.gr_project_inventory.models.erasure_service.ErasureService.fetch_audit_for_lot', return_value=multiple_devices):
            
            wizard = self.wizard_model.create({
                'lot_name': 'AUDT1'
            })
            result = wizard.export_xlsx_report()
            
            self.assertEqual(result['type'], 'ir.actions.report')
            self.assertEqual(result['report_name'], 'gr_project_inventory.audit_report_xlsx')
            self.assertEqual(result['report_type'], 'xlsx')

    def test_audit_report_no_data(self):
        """Test audit report generation when no data is found"""
        with patch('odoo.addons.gr_project_inventory.models.erasure_service.ErasureService.lot_exists', return_value=True), \
             patch('odoo.addons.gr_project_inventory.models.erasure_service.ErasureService.fetch_audit_for_lot', return_value=[]):
            
            wizard = self.wizard_model.create({
                'lot_name': 'NODT1'
            })
            with self.assertRaises(UserError) as cm:
                wizard.export_xlsx_report()
            self.assertIn('No data found', str(cm.exception)) 