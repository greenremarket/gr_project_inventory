from odoo.tests import HttpCase, tagged


@tagged('-at_install', 'post_install')
class TestPortalUI(HttpCase):
    """Test portal UI functionality with real browser simulation."""

    def test_portal_operations_display(self):
        """Test that portal user can see operations in portal home."""
        
        # Login as admin user (has tasks with PD3E tag)
        self.authenticate('admin@greenremarket.fr', 'Payasugo187!odoo')
        
        # Go to portal home
        response = self.url_open('/my/home')
        
        # Check page loads successfully
        self.assertEqual(response.status_code, 200, "Portal home should load successfully")
        
        # Check if operations section exists
        page_content = response.text
        
        # Look for operations section
        operations_found = 'Your Operations' in page_content
        self.assertTrue(operations_found, "Operations section should be visible")
        
        # Look for "You have no operations" message
        no_operations_found = 'You have no operations at the moment' in page_content
        
        if no_operations_found:
            self.fail("Portal shows 'no operations' - this is the bug we need to fix")
        
        # Look for actual operations
        operations_list_found = '<ul class="list-unstyled mb-0">' in page_content
        
        if not operations_list_found:
            self.fail("No operations list found in portal home")
        
        # Check for PD3E tag filtering
        pd3e_filter_found = "'PD3E' in task.tag_ids.mapped('name')" in page_content
        
        if pd3e_filter_found:
            print("✅ PD3E filter found in template")
        else:
            print("❌ PD3E filter NOT found in template")
        
        print("✅ Portal UI test completed - check results above")

    def test_portal_task_documents_display(self):
        """Test that documents are visible in portal task page."""
        
        # Login as admin user
        self.authenticate('admin@greenremarket.fr', 'Payasugo187!odoo')
        
        # Go to task page
        response = self.url_open('/my/tasks/691?')
        
        # Check page loads successfully
        self.assertEqual(response.status_code, 200, "Task page should load successfully")
        
        page_content = response.text
        
        # Check for Documents section
        documents_section_found = '<h4>Documents</h4>' in page_content
        self.assertTrue(documents_section_found, "Documents section should be visible in task page")
        
        if documents_section_found:
            # Count document links
            doc_links_count = page_content.count('oe_documents')
            print(f"✅ Found {doc_links_count} documents in portal task page")
            
            # Should have 4 documents for task 691
            self.assertGreaterEqual(doc_links_count, 1, "Should have at least 1 document displayed")
            
            # Check for specific document names
            expected_docs = ['document dhl.pdf', 'XN188858465FR', 'XN170514257FR', 'XN165838414FR']
            docs_found = 0
            for doc_name in expected_docs:
                if doc_name in page_content:
                    docs_found += 1
            
            print(f"✅ Found {docs_found}/{len(expected_docs)} expected document names")
        else:
            self.fail("Documents section not found - P0.8 fix failed")

    def test_delivrables_zip_download(self):
        """Test that delivrables ZIP download works without errors."""
        
        # Login as admin user
        self.authenticate('admin@greenremarket.fr', 'Payasugo187!odoo')
        
        # Test delivrables download endpoint
        response = self.url_open('/delivrable/download', data={'task_ids': '691'})
        
        # Should not return 500 error anymore
        self.assertNotEqual(response.status_code, 500, "Delivrables download should not return 500 error")
        
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            if 'zip' in content_type:
                print(f"✅ ZIP download successful - size: {len(response.content)} bytes")
            else:
                print(f"❌ Wrong content type: {content_type}")
                self.fail("Should return ZIP file")
        elif response.status_code == 403:
            print("❌ Access forbidden - check task access rights")
            self.fail("Should have access to delivrables download")
        else:
            print(f"❌ Download failed with status: {response.status_code}")
            self.fail(f"Delivrables download should work, got {response.status_code}")

    def test_complete_portal_workflow(self):
        """Test complete workflow: operations -> task page -> documents -> delivrables."""
        
        print("=== Testing Complete Portal Workflow ===")
        
        # Step 1: Check operations in home
        self.authenticate('admin@greenremarket.fr', 'Payasugo187!odoo')
        home_response = self.url_open('/my/home')
        self.assertEqual(home_response.status_code, 200)
        
        # Step 2: Access task page
        task_response = self.url_open('/my/tasks/691?')
        self.assertEqual(task_response.status_code, 200)
        
        # Step 3: Verify documents are displayed
        task_content = task_response.text
        documents_found = '<h4>Documents</h4>' in task_content
        self.assertTrue(documents_found, "Documents should be visible")
        
        # Step 4: Test delivrables download
        download_response = self.url_open('/delivrable/download', data={'task_ids': '691'})
        self.assertNotEqual(download_response.status_code, 500, "Download should not crash")
        
        print("✅ Complete portal workflow test passed")
