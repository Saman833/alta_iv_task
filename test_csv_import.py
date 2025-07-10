#!/usr/bin/env python3
"""
Test script for CSV import functionality
"""

import requests
import json
from pathlib import Path

# API base URL
BASE_URL = "http://127.0.0.1:8000"

def test_csv_import():
    """Test the CSV import functionality"""
    
    # Read the sample CSV file
    csv_file_path = Path("sample_data.csv")
    if not csv_file_path.exists():
        print("❌ sample_data.csv not found!")
        return
    
    with open(csv_file_path, 'r', encoding='utf-8') as f:
        csv_content = f.read()
    
    print("📁 Sample CSV content preview:")
    print(csv_content[:500] + "..." if len(csv_content) > 500 else csv_content)
    print("\n" + "="*50)
    
    # Test 1: Upload CSV from content
    print("🔄 Testing CSV import from content...")
    
    data = {
        "csv_content": csv_content,
        "file_name": "sample_data.csv",
        "folder_id": "test-folder-123",
        "user_id": "test-user-456"
    }
    
    try:
        print(f"🔗 Connecting to: {BASE_URL}")
        
        # First, test if server is reachable
        health_response = requests.get(f"{BASE_URL}/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ Server is reachable!")
        else:
            print(f"⚠️  Server responded with status: {health_response.status_code}")
        
        response = requests.post(f"{BASE_URL}/files/upload-csv-from-content", data=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ CSV import successful!")
            print(f"📊 Table ID: {result['table_id']}")
            print(f"📋 Table Name: {result['table_name']}")
            print(f"📁 File ID: {result['file_id']}")
            
            table_id = result['table_id']
            
            # Test 2: Get table data
            print("\n🔄 Testing table data retrieval...")
            data_response = requests.get(f"{BASE_URL}/files/table/{table_id}/data?limit=5", timeout=10)
            
            if data_response.status_code == 200:
                table_data = data_response.json()
                print("✅ Table data retrieved successfully!")
                print(f"📊 Total rows: {table_data['total_count']}")
                print(f"📋 Columns: {table_data['columns']}")
                print(f"📄 Retrieved {len(table_data['data'])} rows")
                
                # Show first few rows
                print("\n📋 Sample data:")
                for i, row in enumerate(table_data['data'][:3]):
                    print(f"Row {i+1}: {row}")
            else:
                print(f"❌ Failed to retrieve table data: {data_response.status_code} - {data_response.text}")
            
            # Test 3: Search table data
            print("\n🔄 Testing table search...")
            search_response = requests.get(f"{BASE_URL}/files/table/{table_id}/search?search_term=meeting", timeout=10)
            
            if search_response.status_code == 200:
                search_data = search_response.json()
                print("✅ Table search successful!")
                print(f"🔍 Search term: 'meeting'")
                print(f"📊 Found {search_data['result_count']} results")
                
                if search_data['results']:
                    print("📋 Search results:")
                    for i, row in enumerate(search_data['results'][:2]):
                        print(f"Result {i+1}: {row}")
            else:
                print(f"❌ Failed to search table data: {search_response.status_code} - {search_response.text}")
            
            # Test 4: Clean up - delete table
            print("\n🔄 Testing table deletion...")
            delete_response = requests.delete(f"{BASE_URL}/files/table/{table_id}", timeout=10)
            
            if delete_response.status_code == 200:
                print("✅ Table deleted successfully!")
            else:
                print(f"❌ Failed to delete table: {delete_response.status_code} - {delete_response.text}")
                
        else:
            print(f"❌ CSV import failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to the API server at {BASE_URL}")
        print("💡 Try these alternatives:")
        print("   - http://localhost:8000")
        print("   - http://127.0.0.1:8000")
        print("   - http://0.0.0.0:8000")
        print("📝 Make sure the server is running with: uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    except requests.exceptions.Timeout:
        print(f"❌ Request timed out. Server might be slow to respond.")
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")

def test_file_upload():
    """Test file upload functionality (requires server to be running)"""
    print("\n" + "="*50)
    print("🔄 Testing file upload functionality...")
    print("📝 Note: This test requires the server to be running")
    print("📝 You can test this manually by uploading sample_data.csv via the API")
    print("📝 Endpoint: POST /files/upload-csv")

if __name__ == "__main__":
    print("🚀 Starting CSV Import Test")
    print("="*50)
    
    test_csv_import()
    test_file_upload()
    
    print("\n" + "="*50)
    print("✅ Test completed!")
    print("\n📝 To test manually:")
    print("1. Start the server: uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    print("2. Upload CSV: curl -X POST http://127.0.0.1:8000/files/upload-csv-from-content")
    print("3. View data: GET http://127.0.0.1:8000/files/table/{table_id}/data")
    print("4. Search data: GET http://127.0.0.1:8000/files/table/{table_id}/search?search_term=meeting")
    print("5. Visit API docs: http://127.0.0.1:8000/docs") 