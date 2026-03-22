# -*- coding: utf-8 -*-
"""
Test: Task Default Project
Verifies that project.task defaults to the "General" project record
"""
from odoo.tests.common import TransactionCase


class TestTaskDefaultProject(TransactionCase):
    """Test that new tasks default to General project"""

    def setUp(self):
        super().setUp()
        # Reuse the seeded General project so the test stays aligned with the Odoo 17 project configuration.
        self.general_project = self.env['project.project'].search([
            ('name', '=', 'General')
        ], limit=1)
        self.assertTrue(self.general_project, "The General project should exist for the test setup")
    
    def test_task_defaults_to_general_project(self):
        """Test that creating a new task defaults project_id to the General project."""
        # Create a new task without specifying project
        task = self.env['project.task'].create({
            'name': 'Test Task for Default Project'
        })
        
        # Assert that project_id is set to the General project record.
        self.assertTrue(task.project_id, "Task should have a default project")
        self.assertEqual(
            task.project_id,
            self.general_project,
            f"Task project should default to General, but got {task.project_id.name if task.project_id else 'None'}"
        )
