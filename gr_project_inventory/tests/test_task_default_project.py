# -*- coding: utf-8 -*-
"""
Test: Task Default Project
Verifies that project.task defaults to "General" project (ID 1)
"""
from odoo.tests.common import TransactionCase


class TestTaskDefaultProject(TransactionCase):
    """Test that new tasks default to General project"""
    
    def test_task_defaults_to_general_project(self):
        """Test that creating a new task defaults project_id to General (ID 1)"""
        # Create a new task without specifying project
        task = self.env['project.task'].create({
            'name': 'Test Task for Default Project'
        })
        
        # Assert that project_id is set to General project (ID 1)
        self.assertTrue(task.project_id, "Task should have a default project")
        self.assertEqual(
            task.project_id.id, 
            1,
            f"Task project should be General (ID 1), but got {task.project_id.name if task.project_id else 'None'} (ID {task.project_id.id if task.project_id else 'None'})"
        )
