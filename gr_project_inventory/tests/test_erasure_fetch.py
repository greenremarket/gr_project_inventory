from unittest.mock import patch
from odoo.tests import TransactionCase
from odoo.exceptions import UserError

class ErasureFetch(TransactionCase):

    def setUp(self):
        super().setUp()
        self.task = self.env['project.task'].create({
            'name': 'Demo',
            'lot_name': 'BADLOT',
        })

    @patch('odoo.addons.gr_project_inventory.models.erasure_service.pymysql.connect')
    def test_mysql_unreachable(self, mock_conn):
        mock_conn.side_effect = Exception("boom")
        with self.assertRaises(UserError):
            self.task.action_generate_erasure_certificate()
