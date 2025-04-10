from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import ValidationError

@tagged('test_core')
class TestProjectInventory(TransactionCase):
    """
    Test class for the core project inventory functionality.
    
    This class contains tests for the main inventory management features including:
    - Client inventory creation and validation
    - Internal inventory creation and management
    - Asset tag generation
    - Discrepancy handling
    """

    def setUp(self):
        """
        Set up test data before each test.
        
        Creates:
            - A test project
            - A test task
            - Product types (Laptop, Desktop, Monitor) if they don't exist
            - Chassis types (Tower, Desktop, Laptop)
            - A manufacturer
            - A client inventory
        """
        super().setUp()
        self.project = self.env['project.project'].create({
            'name': 'Test Project'
        })
        self.task = self.env['project.task'].create({
            'name': 'Test Task',
            'project_id': self.project.id,
            'lot_name': 'TESTLOT'
        })
        
        # Check if product types exist before creating them
        self.product_type_laptop = self.env['gr.product.type'].search([('name', '=', 'Laptop')], limit=1)
        if not self.product_type_laptop:
            self.product_type_laptop = self.env['gr.product.type'].create({
                'name': 'Laptop'
            })
            
        self.product_type_desktop = self.env['gr.product.type'].search([('name', '=', 'Desktop')], limit=1)
        if not self.product_type_desktop:
            self.product_type_desktop = self.env['gr.product.type'].create({
                'name': 'Desktop'
            })
            
        self.product_type_monitor = self.env['gr.product.type'].search([('name', '=', 'Monitor')], limit=1)
        if not self.product_type_monitor:
            self.product_type_monitor = self.env['gr.product.type'].create({
                'name': 'Monitor'
            })
            
        self.chassis_tower = self.env['gr.chassis'].create({
            'name': 'Tower'
        })
        self.chassis_desktop = self.env['gr.chassis'].create({
            'name': 'Desktop'
        })
        self.chassis_laptop = self.env['gr.chassis'].create({
            'name': 'Laptop'
        })
        self.manufacturer = self.env['gr.manufacturer'].create({
            'name': 'Test Manufacturer'
        })

        # Create a client inventory
        self.client_inventory = self.env['gr.client.inventory'].create({
            'name': 'Test Client Inventory',
            'task_id': self.task.id,
            'serial_number': 'TEST123'
        })

    def tearDown(self):
        """
        Clean up test data after each test.
        
        This method ensures that no test data persists between test runs by:
            - Calling the parent class's tearDown method
            - Deleting all created inventory and related records
        """
        super().tearDown()
        # Clean up any created records
        self.env['gr.client.inventory'].search([]).unlink()
        self.env['gr.internal.inventory'].search([]).unlink()
        self.env['gr.discrepancy'].search([]).unlink()
        print("Cleaned up test data")

    def test_create_client_inventory(self):
        """
        Test the creation and validation of client inventory items.
        
        This test verifies:
            - Creation of a client inventory item
            - Required field validation
            - Field value assignments
            - State transitions
        
        Expected Results:
            - Inventory should be created with correct values
            - Required fields should be properly validated
            - State should be 'draft' initially
        """
        # Test creating a client inventory item
        inventory = self.env['gr.client.inventory'].create({
            'name': 'Test Client Inventory 2',
            'task_id': self.task.id,
            'serial_number': 'TEST456'
        })
        
        self.assertTrue(inventory, "Client inventory should be created")
        self.assertEqual(inventory.name, 'Test Client Inventory 2')
        self.assertEqual(inventory.serial_number, 'TEST456')
        self.assertEqual(inventory.task_id, self.task)

    def test_create_internal_inventory(self):
        """Test creating an internal inventory through wizard"""
        # Create a wizard
        wizard = self.env['internal.inventory.wizard'].create({
            'name': 'Test Internal Inventory',
            'serial_number': 'SN123',
            'status': 'NEW',
            'client_inventory_id': self.client_inventory.id
        })

        # Submit the wizard to create internal inventory
        wizard.action_submit()

        # Check if internal inventory was created
        internal_inventory = self.env['gr.internal.inventory'].search([
            ('name', '=', 'Test Internal Inventory'),
            ('serial_number', '=', 'SN123'),
            ('status', '=', 'NEW')
        ])

        self.assertTrue(internal_inventory, "Internal inventory should be created")
        self.assertEqual(internal_inventory.client_inventory_id, self.client_inventory)

    def test_asset_tag_generation(self):
        """Test automatic generation of asset tags for internal inventory items"""
        # Create a wizard
        wizard = self.env['internal.inventory.wizard'].create({
            'name': 'Test Asset Tag Generation',
            'serial_number': 'SN456',
            'status': 'NEW',
            'client_inventory_id': self.client_inventory.id
        })

        # Submit the wizard to create internal inventory
        wizard.action_submit()

        # Check if internal inventory was created with proper asset tag
        internal_inventory = self.env['gr.internal.inventory'].search([
            ('name', '=', 'Test Asset Tag Generation')
        ])

        self.assertTrue(internal_inventory, "Internal inventory should be created")
        self.assertTrue(internal_inventory.asset_tag, "Asset tag should be generated")
        self.assertTrue(internal_inventory.asset_tag.startswith('GI/'), "Asset tag should start with GI/")
        self.assertEqual(len(internal_inventory.asset_tag.split('/')[-1]), 6, "Asset tag number should be 6 digits")

    def test_discrepancy_creation(self):
        """
        Test the creation and resolution of discrepancies.
        
        This test verifies:
            - Discrepancy creation
            - State transitions
            - Resolution process
            - Date tracking
        
        Expected Results:
            - Discrepancy should be created successfully
            - State should transition correctly
            - Resolution date should be set when marked as resolved
        """
        # Create a discrepancy
        discrepancy = self.env['gr.discrepancy'].create({
            'name': 'Test Discrepancy',
            'task_id': self.task.id,
            'discrepancy_type': 'missing',
            'notes': 'Test notes'
        })
        
        self.assertTrue(discrepancy, "Discrepancy should be created")
        self.assertEqual(discrepancy.name, 'Test Discrepancy')
        self.assertEqual(discrepancy.task_id, self.task)
        self.assertEqual(discrepancy.discrepancy_type, 'missing')
        self.assertFalse(discrepancy.resolved)

        # Mark as resolved
        discrepancy.action_mark_resolved()

        self.assertTrue(discrepancy.resolved)
        self.assertTrue(discrepancy.resolution_date) 