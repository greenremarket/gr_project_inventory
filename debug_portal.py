#!/usr/bin/env python3

"""
Debug script to simulate admin accessing portal home
"""

import os
import sys

# Add Odoo to path
sys.path.append('./odoo')
sys.path.append('./enterprise')

os.environ['ODOO_CONFIG'] = 'odoo.conf'

def debug_portal_home():
    """Debug what happens when admin accesses /my/home"""
    
    try:
        import odoo
        from odoo import api, registry
        
        # Load database registry
        db_name = 'greenremarket_repro'
        registry = registry.Registry(db_name)
        
        with registry.cursor() as cr:
            env = api.Environment(cr, 1, {})  # Admin user (uid=1)
            
            # Find admin@greenremarket.fr user
            admin_user = env['res.users'].search([('login', '=', 'admin@greenremarket.fr')], limit=1)
            
            if not admin_user:
                print("❌ Admin user not found")
                return False
            
            print(f"✅ Found admin user: {admin_user.name}")
            print(f"   Task portal ok: {admin_user.partner_id.task_portal_ok}")
            
            # Simulate the controller logic
            user = admin_user
            partner = user.partner_id
            
            # Get tasks like the controller does
            tasks = env['project.task'].search([
                ('user_ids', 'in', [user.id]),
                ('active', '=', True),
            ], limit=10)
            
            print(f"📋 Found {len(tasks)} tasks for admin")
            
            # Check PD3E tag
            pd3e_tag = env['project.tags'].search([('name', '=', 'PD3E')], limit=1)
            if not pd3e_tag:
                print("❌ PD3E tag not found")
                return False
            
            print(f"✅ PD3E tag found: {pd3e_tag.id}")
            
            # Filter tasks with PD3E tag (like template does)
            pd3e_tasks = tasks.filtered(lambda t: pd3e_tag in t.tag_ids)
            print(f"🎯 Tasks with PD3E tag: {len(pd3e_tasks)}")
            
            if pd3e_tasks:
                print("📝 PD3E Operations:")
                for task in pd3e_tasks:
                    print(f"   - {task.name} (ID: {task.id})")
            else:
                print("❌ No tasks with PD3E tag found!")
                
                # Show all tasks without PD3E
                print("📋 All admin tasks:")
                for task in tasks:
                    tags = [t.name for t in task.tag_ids]
                    print(f"   - {task.name} (Tags: {tags})")
            
            return len(pd3e_tasks) > 0
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = debug_portal_home()
    print(f"\n🎯 Result: {'SUCCESS' if success else 'FAILED'}")
    sys.exit(0 if success else 1)
