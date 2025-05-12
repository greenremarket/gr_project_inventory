from odoo.tests.common import TransactionCase, tagged
from datetime import datetime, timedelta

@tagged('test_date_field')
class TestDateField(TransactionCase):
    """
    Test class for the date field functionality.
    
    This class contains tests for the date fields in project tasks,
    particularly the planned_date_begin field which is used to store
    the operation start date.
    """

    def setUp(self):
        """
        Set up test data before each test.
        
        Creates:
            - A test project
            - Test users
        """
        super().setUp()
        self.project = self.env['project.project'].create({
            'name': 'Test Project'
        })
        
        # Create a test user for assignments
        self.test_user = self.env['res.users'].create({
            'name': 'Test User',
            'login': 'test_user',
            'email': 'test@example.com',
        })

    def tearDown(self):
        """
        Clean up test data after each test.
        
        This method ensures that no test data persists between test runs.
        """
        super().tearDown()
        # Clean up created tasks
        self.env['project.task'].search([('name', 'like', 'Test Date%')]).unlink()
        print("Cleaned up test data")

    def test_planned_date_begin_setting(self):
        """
        Test that the planned_date_begin field can be set directly.
        
        This test verifies:
            - Direct setting of planned_date_begin works correctly
            - The value is stored properly
            - The date format is handled correctly
        """
        # Define a test date
        test_date = datetime.now().replace(microsecond=0) + timedelta(days=5)
        
        # Create a task with planned_date_begin
        task = self.env['project.task'].create({
            'name': 'Test Date Task Direct',
            'project_id': self.project.id,
            'planned_date_begin': test_date,
            'client_destination_name': 'Test Client'
        })
        
        # Verify the date was set correctly
        self.assertEqual(task.planned_date_begin, test_date, 
                         "planned_date_begin should be set to the specified date")
                         
        # Reload the task from the database to ensure it was stored correctly
        task = self.env['project.task'].browse(task.id)
        
        # Verify the date is still correct after reload
        self.assertEqual(task.planned_date_begin, test_date,
                         "planned_date_begin should be stored correctly in the database")
        
        # Check that  was also set via onchange
        self.assertTrue(task., " should be set when planned_date_begin is provided")
        
        # Verify the  format
        expected_text_format = test_date.strftime('%d/%m/%Y %H:%M:%S')
        self.assertEqual(task., expected_text_format,
                         " should be formatted as DD/MM/YYYY HH:MM:SS")

    def test__conversion(self):
        """
        Test that the  field correctly converts to planned_date_begin.
        
        This test verifies:
            - Setting  properly updates planned_date_begin
            - The conversion handles various date formats
            - Edge cases are handled appropriately
        """
        # Create a task with 
        task = self.env['project.task'].create({
            'name': 'Test Date Task Text',
            'project_id': self.project.id,
            '': '01/05/2025 14:30:00',
            'client_destination_name': 'Test Client'
        })
        
        # Verify planned_date_begin was set based on 
        self.assertTrue(task.planned_date_begin, 
                        "planned_date_begin should be set when  is provided")
        
        # Expected date (May 1, 2025, 14:30:00)
        expected_date = datetime(2025, 5, 1, 14, 30, 0)
        
        # Account for potential timezone differences using string comparison of the date part
        self.assertEqual(task.planned_date_begin.strftime('%Y-%m-%d %H:%M:%S'), 
                         expected_date.strftime('%Y-%m-%d %H:%M:%S'),
                         "planned_date_begin should match the date specified in ")

    def test_form_view_date_field(self):
        """
        Test that the date field in the form view works correctly.
        
        This is a simulated test of form view interaction by directly
        creating records as the form would, to ensure the UI behavior
        works correctly.
        """
        # Create a task as if from the task creation form
        # (simulating what happens when a user fills the form)
        task_vals = {
            'name': 'Test Date Form View',
            'project_id': self.project.id,
            'tag_ids': [(0, 0, {'name': 'Test Tag'})],
            'user_ids': [(4, self.test_user.id)],
            'client_destination_name': 'Test Client',
            '': '15/06/2025 09:15:00',
            'description': 'Test operation description'
        }
        
        task = self.env['project.task'].create(task_vals)
        
        # Verify planned_date_begin was set correctly from the form
        self.assertTrue(task.planned_date_begin, 
                        "planned_date_begin should be set when created via form")
        
        # Expected date (June 15, 2025, 09:15:00)
        expected_date = datetime(2025, 6, 15, 9, 15, 0)
        
        # Compare formatted dates to handle timezone differences
        self.assertEqual(task.planned_date_begin.strftime('%Y-%m-%d %H:%M:%S'), 
                         expected_date.strftime('%Y-%m-%d %H:%M:%S'),
                         "planned_date_begin should match the date specified in the form")
                         
    def test_bidirectional_date_update(self):
        """
        Test that updating either field correctly updates the other field.
        
        This test verifies:
            - Updating  updates planned_date_begin
            - Updating planned_date_begin updates 
            - The bidirectional relationship works correctly
        """
        # Create a task
        task = self.env['project.task'].create({
            'name': 'Test Bidirectional Update',
            'project_id': self.project.id,
            'client_destination_name': 'Test Client'
        })
        
        # Update 
        task.write({'': '10/07/2025 08:45:30'})
        
        # Verify planned_date_begin was updated
        expected_date = datetime(2025, 7, 10, 8, 45, 30)
        self.assertEqual(task.planned_date_begin.strftime('%Y-%m-%d %H:%M:%S'),
                         expected_date.strftime('%Y-%m-%d %H:%M:%S'),
                         "planned_date_begin should be updated when  is changed")
        
        # Now update planned_date_begin
        new_date = datetime(2025, 8, 20, 16, 30, 0)
        task.write({'planned_date_begin': new_date})
        
        # Verify  was updated
        expected_text = new_date.strftime('%d/%m/%Y %H:%M:%S')
        self.assertEqual(task., expected_text,
                         " should be updated when planned_date_begin is changed")
    
    def test_multiple_date_formats(self):
        """
        Test that different date formats are correctly converted.
        
        This test verifies:
            - Different date formats are correctly recognized and converted
            - Invalid formats are properly handled
        """
        # Test different date formats
        formats_to_test = [
            # Format, expected date
            ('01/05/2025 14:30:00', datetime(2025, 5, 1, 14, 30, 0)),  # Full format with seconds
            ('01/05/2025 14:30', datetime(2025, 5, 1, 14, 30, 0)),     # Without seconds
            ('01/05/2025', datetime(2025, 5, 1, 0, 0, 0)),             # Date only
            ('2025-05-01 14:30:00', datetime(2025, 5, 1, 14, 30, 0)),  # ISO format with time
            ('2025-05-01', datetime(2025, 5, 1, 0, 0, 0))              # ISO format date only
        ]
        
        for format_str, expected_date in formats_to_test:
            task = self.env['project.task'].create({
                'name': f'Test Format {format_str}',
                'project_id': self.project.id,
                '': format_str,
                'client_destination_name': 'Test Client'
            })
            
            self.assertEqual(
                task.planned_date_begin.strftime('%Y-%m-%d %H:%M:%S'),
                expected_date.strftime('%Y-%m-%d %H:%M:%S'),
                f"Date format {format_str} should be correctly converted"
            )
    
    def test_view_fields_visibility(self):
        """
        Test that the date fields are visible in the views.
        
        This test verifies that the fields are included in views
        and not inadvertently hidden by view inheritance.
        """
        # Get the task form view
        view = self.env['ir.ui.view'].search([
            ('model', '=', 'project.task'),
            ('name', '=', 'project.task.form.inherit.date.priority')
        ], limit=1)
        
        # Check that the view exists
        self.assertTrue(view, "The high-priority date field view should exist")
        
        # Check the view priority
        self.assertEqual(view.priority, 99, "The view should have high priority (99)")
        
        # Get the field from the view's arch
        field_in_view = '<field name="planned_date_begin"' in view.arch
        self.assertTrue(field_in_view, "planned_date_begin should be in the view arch")
        
        # Also check for the widget
        widget_in_view = 'widget="datetime"' in view.arch
        self.assertTrue(widget_in_view, "The datetime widget should be specified in the view")
    
    def test_invalid_date_format_handling(self):
        """
        Test that invalid date formats are handled gracefully.
        """
        # Try to create a task with an invalid date format
        task = self.env['project.task'].create({
            'name': 'Test Invalid Date Format',
            'project_id': self.project.id,
            '': 'not a date',  # Invalid format
            'client_destination_name': 'Test Client'
        })
        
        # The task should be created without error, but planned_date_begin should not be set
        self.assertTrue(task.id, "Task should be created successfully even with invalid date format")
        
        # planned_date_begin should not be set for invalid formats
        self.assertFalse(task.planned_date_begin, 
                        "planned_date_begin should not be set for invalid date formats") 