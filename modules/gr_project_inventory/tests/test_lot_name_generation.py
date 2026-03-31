# -*- coding: utf-8 -*-
"""Tests for lot name auto-generation functionality."""

from odoo.tests import TransactionCase, tagged
from odoo.exceptions import ValidationError


@tagged('-at_install', 'post_install')
class TestLotNameAutoGeneration(TransactionCase):
    """Test lot name auto-generation features."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        # Create test partner
        cls.test_partner = cls.env['res.partner'].create({
            'name': 'Test Client InfoDisk',
            'email': 'test@example.com',
        })

        # Create test project
        cls.test_project = cls.env['project.project'].create({
            'name': 'Test Project',
            'privacy_visibility': 'portal',
        })

    def test_lot_name_length_constraint_6_chars(self):
        """Test that lot name length constraint is 6 characters."""
        # Should accept 6 chars
        task = self.env['project.task'].create({
            'name': 'Test Task',
            'project_id': self.test_project.id,
            'lot_name': 'ABC123',
        })
        self.assertEqual(task.lot_name, 'ABC123')

        # Should reject 7 chars
        with self.assertRaises(ValidationError) as cm:
            self.env['project.task'].create({
                'name': 'Test Task 2',
                'project_id': self.test_project.id,
                'lot_name': 'ABC1234',
            })
        self.assertIn("ne doit pas dépasser 6 caractères", str(cm.exception))

    def test_lot_name_unique_constraint(self):
        """Test that lot name unique constraint works."""
        # Create first task
        task1 = self.env['project.task'].create({
            'name': 'Test Task 1',
            'project_id': self.test_project.id,
            'lot_name': 'UNIQ01',
        })

        # Should reject duplicate lot name with proper ValidationError
        with self.assertRaises(ValidationError) as cm:
            self.env['project.task'].create({
                'name': 'Test Task 2',
                'project_id': self.test_project.id,
                'lot_name': 'UNIQ01',
            })
        self.assertIn("existe déjà", str(cm.exception))

    def test_auto_generation_when_empty(self):
        """Test auto-generation when lot_name is empty."""
        task = self.env['project.task'].create({
            'name': 'Test Task',
            'project_id': self.test_project.id,
            'partner_id': self.test_partner.id,
            # lot_name not provided
        })

        # Should auto-generate lot_name
        self.assertTrue(task.lot_name, "Lot name should be auto-generated")
        self.assertEqual(len(task.lot_name), 6, "Generated lot name should be 6 characters")
        self.assertTrue(task.lot_name.isalnum(), "Generated lot name should be alphanumeric")
        self.assertTrue(task.lot_name.isupper(), "Generated lot name should be uppercase")

    def test_no_overwrite_when_manually_set(self):
        """Test that manual lot_name is not overwritten."""
        manual_lot_name = 'MANUAL'
        task = self.env['project.task'].create({
            'name': 'Test Task',
            'project_id': self.test_project.id,
            'partner_id': self.test_partner.id,
            'lot_name': manual_lot_name,
        })

        # Should keep manual lot_name
        self.assertEqual(task.lot_name, manual_lot_name)

    def test_client_hint_from_client_destination_name(self):
        """client_destination_name is highest priority for lot hint."""
        task = self.env['project.task'].create({
            'name': 'Test Task',
            'project_id': self.test_project.id,
            'client_destination_name': 'INFODIS',
            'partner_id': self.test_partner.id,  # should be ignored
        })
        hint = task._generate_client_hint()
        # INFODIS → 'INF'
        self.assertEqual(hint, 'INF')

    def test_client_hint_generation(self):
        """Falls back to partner_id.name when client_destination_name is empty."""
        task = self.env['project.task'].create({
            'name': 'Test Task',
            'project_id': self.test_project.id,
            'partner_id': self.test_partner.id,
            # client_destination_name intentionally not set
        })

        client_hint = task._generate_client_hint()
        self.assertEqual(len(client_hint), 3, "Client hint should be 3 characters")
        self.assertTrue(client_hint.isalnum(), "Client hint should be alphanumeric")
        self.assertTrue(client_hint.isupper(), "Client hint should be uppercase")
        # Should extract "TES" from "Test Client InfoDisk"
        self.assertIn('TES', client_hint)

    def test_year_hint_generation(self):
        """Test year hint generation."""
        task = self.env['project.task'].create({
            'name': 'Test Task',
            'project_id': self.test_project.id,
        })

        year_hint = task._generate_year_hint()
        self.assertEqual(len(year_hint), 1, "Year hint should be 1 character")
        self.assertTrue(year_hint.isdigit(), "Year hint should be a digit")

    def test_sequence_generation_collision_handling(self):
        """Test sequence generation with collision handling."""
        # Create multiple tasks to test collision handling
        tasks = []
        for i in range(3):
            task = self.env['project.task'].create({
                'name': f'Test Task {i}',
                'project_id': self.test_project.id,
                'partner_id': self.test_partner.id,
            })
            tasks.append(task)

        # All should have unique lot names
        lot_names = [task.lot_name for task in tasks]
        self.assertEqual(len(set(lot_names)), len(lot_names), "All lot names should be unique")

        # Should have same prefix (client + year) but different sequences
        prefixes = [lot_name[:4] for lot_name in lot_names]
        self.assertEqual(len(set(prefixes)), 1, "All should have same prefix")

        # Sequences should be different
        sequences = [lot_name[4:6] for lot_name in lot_names]
        self.assertEqual(len(set(sequences)), len(sequences), "All should have different sequences")

    def test_fallback_to_unknown(self):
        """Test fallback to UNK when no partner/order_giver."""
        task = self.env['project.task'].create({
            'name': 'Test Task',
            'project_id': self.test_project.id,
            # No partner_id or order_giver_id
        })

        # Should use UNK as client hint
        self.assertTrue(task.lot_name.startswith('UNK'), "Should use UNK as fallback client hint")

    def test_order_giver_fallback(self):
        """Falls back to order_giver_id when client_destination_name and partner are both empty."""
        test_order_giver = self.env['res.partner'].create({
            'name': 'Order Giver Corp',
            'email': 'order@example.com',
        })

        task = self.env['project.task'].create({
            'name': 'Test Task',
            'project_id': self.test_project.id,
            'order_giver_id': test_order_giver.id,
            # No client_destination_name, no partner_id
        })

        client_hint = task._generate_client_hint()
        self.assertIn('ORD', client_hint)  # From "Order Giver Corp"

    def test_client_destination_overrides_order_giver(self):
        """client_destination_name beats order_giver_id."""
        test_order_giver = self.env['res.partner'].create({
            'name': 'Order Giver Corp',
            'email': 'order2@example.com',
        })

        task = self.env['project.task'].create({
            'name': 'Test Task',
            'project_id': self.test_project.id,
            'client_destination_name': 'ACME',
            'order_giver_id': test_order_giver.id,
        })

        hint = task._generate_client_hint()
        # ACME → 'ACM', not 'ORD'
        self.assertEqual(hint, 'ACM')

    def test_edge_cases_special_characters(self):
        """Test edge cases with special characters and accents."""
        # Create partner with accents
        special_partner = self.env['res.partner'].create({
            'name': 'Été Client & Co!',
            'email': 'special@example.com',
        })
        
        task = self.env['project.task'].create({
            'name': 'Test Task',
            'project_id': self.test_project.id,
            'partner_id': special_partner.id,
        })

        # Should handle accents and special chars properly
        client_hint = task._generate_client_hint()
        self.assertEqual(len(client_hint), 3)
        self.assertTrue(client_hint.isalnum())
        self.assertTrue(client_hint.isupper())

    def test_sequence_collision_real_scenario(self):
        """Test real collision scenario with forced duplicate."""
        # Create first task
        task1 = self.env['project.task'].create({
            'name': 'Test Task 1',
            'project_id': self.test_project.id,
            'partner_id': self.test_partner.id,
        })
        first_lot_name = task1.lot_name
        
        # Force create second task with same lot_name to test collision
        task2 = self.env['project.task'].create({
            'name': 'Test Task 2',
            'project_id': self.test_project.id,
            'partner_id': self.test_partner.id,
        })
        
        # Should have different sequence
        self.assertNotEqual(task1.lot_name, task2.lot_name)
        self.assertEqual(task1.lot_name[:4], task2.lot_name[:4])  # Same prefix
        self.assertNotEqual(task1.lot_name[4:], task2.lot_name[4:])  # Different sequence

    def test_format_compatibility(self):
        """Test generated format: XXXYY (3+1+2)."""
        task = self.env['project.task'].create({
            'name': 'Test Task',
            'project_id': self.test_project.id,
            'partner_id': self.test_partner.id,
        })

        lot_name = task.lot_name
        self.assertEqual(len(lot_name), 6, "Lot name should be exactly 6 characters")
        
        # First 3 chars: client hint (letters)
        client_hint = lot_name[:3]
        self.assertTrue(client_hint.isalpha(), "First 3 chars should be letters (client hint)")
        
        # 4th char: year hint (digit)
        year_hint = lot_name[3]
        self.assertTrue(year_hint.isdigit(), "4th char should be digit (year hint)")
        
        # Last 2 chars: sequence (digits)
        sequence = lot_name[4:6]
        self.assertTrue(sequence.isdigit(), "Last 2 chars should be digits (sequence)")
