from unittest.mock import patch
from odoo.tests import TransactionCase

DUMMY_ROW = [{
    'ProductType': 'DESKTOP', 'Manufacturer': 'HP',
    'Model': 'TouchSmart', 'hd_size': '500 GB',
    'hd_model': 'ST500DM002', 'hd_sn': 'ABC123', 'ts': '2024-01-05 11:59:03'
}]

class ErasureHappy(TransactionCase):

    def setUp(self):
        super().setUp()
        self.task = self.env['project.task'].create({'name': 'Demo', 'lot_name': '1029'})

    @patch('odoo.addons.gr_project_inventory.models.erasure_service.ErasureService.fetch_for_lot', return_value=DUMMY_ROW)
    def test_report_generated(self, mock_fetch):
        action = self.task.action_generate_erasure_certificate()
        self.assertEqual(action['type'], 'ir.actions.report')
