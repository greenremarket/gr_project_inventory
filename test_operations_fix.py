#!/usr/bin/env python3

"""
Quick test to verify operations display fix
"""

import requests
import sys

def test_operations_display():
    """Test if operations are displayed in portal home"""
    
    # Login and get session
    session = requests.Session()
    
    # Get login page
    login_url = "http://localhost:8069/web/login"
    response = session.get(login_url)
    
    if response.status_code != 200:
        print("❌ Cannot reach login page")
        return False
    
    # Login (assuming admin user exists)
    login_data = {
        'login': 'admin@greenremarket.fr',
        'password': 'admin',  # This might be wrong
        'csrf_token': response.cookies.get('csrf_token', ''),
    }
    
    response = session.post(login_url, data=login_data)
    
    # Check portal home
    home_url = "http://localhost:8069/my/home"
    response = session.get(home_url)
    
    if response.status_code != 200:
        print(f"❌ Cannot reach portal home (status: {response.status_code})")
        return False
    
    page_content = response.text
    
    # Check for operations
    has_operations = 'Your Operations' in page_content
    has_no_operations = 'You have no operations at the moment' in page_content
    
    if has_operations and not has_no_operations:
        print("✅ Operations section found and not empty")
        return True
    elif has_no_operations:
        print("❌ Portal shows 'no operations'")
        return False
    else:
        print("❌ Operations section not found")
        return False

if __name__ == "__main__":
    try:
        success = test_operations_display()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        sys.exit(1)
