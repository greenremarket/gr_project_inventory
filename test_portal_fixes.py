#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup

def test_portal_task_page():
    """Test if documents appear in portal task page"""
    
    session = requests.Session()
    
    # Login
    login_data = {
        'login': 'admin@greenremarket.fr',
        'password': 'Payasugo187!odoo'
    }
    
    login_response = session.post('http://localhost:8069/web/login', data=login_data)
    print(f"Login status: {login_response.status_code}")
    
    if login_response.status_code != 200:
        print("❌ Login failed")
        return False
    
    # Access task page
    task_url = 'http://localhost:8069/my/tasks/691?'
    task_response = session.get(task_url)
    print(f"Task page status: {task_response.status_code}")
    
    if task_response.status_code != 200:
        print("❌ Cannot access task page")
        return False
    
    # Parse HTML
    soup = BeautifulSoup(task_response.text, 'html.parser')
    
    # Check for documents section
    documents_section = soup.find('h4', string='Documents')
    if documents_section:
        print("✅ Documents section found")
        
        # Count documents
        document_links = soup.find_all('a', class_='oe_documents')
        print(f"✅ Found {len(document_links)} documents in portal")
        
        for doc in document_links:
            doc_name = doc.find('div', class_='oe_document_name')
            if doc_name:
                print(f"  - {doc_name.get_text().strip()}")
        
        return len(document_links) > 0
    else:
        print("❌ No documents section found")
        
        # Check if page contains task info
        task_title = soup.find('h3')
        if task_title:
            print(f"Page title: {task_title.get_text().strip()}")
        
        # Look for any document-related content
        doc_mentions = soup.find_all(string=lambda text: text and 'document' in text.lower())
        if doc_mentions:
            print(f"Found document mentions: {len(doc_mentions)}")
        
        return False

def test_delivrables_download():
    """Test delivrables ZIP download"""
    
    session = requests.Session()
    
    # Login
    login_data = {
        'login': 'admin@greenremarket.fr',
        'password': 'Payasugo187!odoo'
    }
    
    session.post('http://localhost:8069/web/login', data=login_data)
    
    # Test delivrables download endpoint
    download_data = {
        'task_ids': '691'
    }
    
    download_response = session.post('http://localhost:8069/delivrable/download', data=download_data)
    print(f"Delivrables download status: {download_response.status_code}")
    
    if download_response.status_code == 200:
        content_type = download_response.headers.get('Content-Type', '')
        if 'zip' in content_type:
            print("✅ ZIP download successful")
            print(f"ZIP size: {len(download_response.content)} bytes")
            return True
        else:
            print(f"❌ Wrong content type: {content_type}")
            return False
    else:
        print(f"❌ Download failed: {download_response.status_code}")
        print(f"Response: {download_response.text[:200]}...")
        return False

if __name__ == "__main__":
    print("=== Testing Portal Documents Display ===")
    docs_ok = test_portal_task_page()
    
    print("\n=== Testing Delivrables Download ===")
    delivrables_ok = test_delivrables_download()
    
    print(f"\n=== SUMMARY ===")
    print(f"Documents in portal: {'✅' if docs_ok else '❌'}")
    print(f"Delivrables download: {'✅' if delivrables_ok else '❌'}")
    
    if docs_ok and delivrables_ok:
        print("🎉 ALL FIXES WORKING!")
    else:
        print("❌ Some fixes need work")
