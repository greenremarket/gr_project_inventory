from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import ValidationError
from odoo.fields import Date

@tagged('test_discrepancy')
class TestDiscrepancyReport(TransactionCase):
    """
    Test class for the discrepancy report functionality.
    
    This class contains tests for creating, validating, and managing discrepancy reports
    in the project inventory system. It tests both successful operations and error cases.
    """

    @classmethod
    def setUpClass(cls):
        """
        Set up test data before running any tests.
        
        Creates:
            - A test project
            - A test task associated with the project
        """
        super().setUpClass()
        print("SETTING UP TEST CLASS")
        cls.project = cls.env['project.project'].create({
            'name': 'Test Project'
        })
        print(f"Created project: {cls.project.name}")
        cls.task = cls.env['project.task'].create({
            'name': 'Test Task',
            'project_id': cls.project.id,
            'lot_name': 'TESTLOT'
        })
        print(f"Created task: {cls.task.name}")

    def tearDown(self):
        """
        Clean up test data after each test.
        
        This method ensures that no test data persists between test runs by:
            - Calling the parent class's tearDown method
            - Deleting all created discrepancy records
        """
        super().tearDown()
        # Clean up any created discrepancies
        self.env['gr.discrepancy'].search([]).unlink()
        print("Cleaned up test data")

    def test_discrepancy(self):
        """
        Test the creation and resolution of a discrepancy.
        """
        # Create a discrepancy
        discrepancy = self.env['gr.discrepancy'].create({
            'name': 'Test Discrepancy',
            'task_id': self.task.id,
            'discrepancy_type': 'missing',
            'notes': 'Test notes'
        })
        
        # Verify the discrepancy was created correctly
        self.assertEqual(discrepancy.name, 'Test Discrepancy')
        self.assertEqual(discrepancy.task_id, self.task)
        self.assertEqual(discrepancy.discrepancy_type, 'missing')
        self.assertEqual(discrepancy.notes, 'Test notes')
        self.assertFalse(discrepancy.resolved)
        
        # Mark the discrepancy as resolved
        discrepancy.action_mark_resolved()
        
        # Verify the resolution
        self.assertTrue(discrepancy.resolved)
        self.assertTrue(discrepancy.resolution_date) 