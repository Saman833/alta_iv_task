#!/usr/bin/env python3
"""
Simple test script for CSV upload functionality
"""

import requests
import json
from pathlib import Path

# API base URL
BASE_URL = "http://127.0.0.1:8000"

def test_csv_upload():
    """Test the CSV upload functionality"""
    
    print("🚀 Starting CSV Upload Test")
    print("="*50)
    
    try:
        # Step 1: Create a folder first
        print("🔄 Creating folder...")
        folder_data = {
            "folder_name": "CSV Test Folder",
            "detail_summary": "Folder for testing CSV uploads",
            "user_id": "csv-test-user"
        }
        
        folder_response = requests.post(f"{BASE_URL}/files/folders", json=folder_data, timeout=10)
        
        if folder_response.status_code == 200:
            folder_result = folder_response.json()
            folder_id = folder_result['id']
            user_id = folder_result['user_id']
            print(f"✅ Folder created: {folder_result['folder_name']} (ID: {folder_id})")
            
            # Step 2: Upload CSV file
            print("\n🔄 Uploading CSV file...")
            
            # Read sample CSV
            csv_file_path = Path("sample_data.csv")
            if csv_file_path.exists():
                with open(csv_file_path, 'r', encoding='utf-8') as f:
                    csv_content = f.read()
                
                file_data = {
                    "csv_content": csv_content,
                    "file_name": "sample_data.csv",
                    "folder_id": folder_id,
                    "user_id": user_id
                }
                
                upload_response = requests.post(f"{BASE_URL}/files/upload-csv-from-content", data=file_data, timeout=15)
                
                if upload_response.status_code == 200:
                    upload_result = upload_response.json()
                    print("✅ CSV uploaded successfully!")
                    print(f"📄 File ID: {upload_result['file_id']}")
                    print(f"📊 Table ID: {upload_result['table_id']}")
                    print(f"📋 Table Name: {upload_result['table_name']}")
                    
                    table_id = upload_result['table_id']
                    
                    # Step 3: Test data retrieval
                    print("\n🔄 Testing data retrieval...")
                    data_response = requests.get(f"{BASE_URL}/files/table/{table_id}/data?limit=5", timeout=10)
                    
                    if data_response.status_code == 200:
                        data_result = data_response.json()
                        print("✅ Data retrieved successfully!")
                        print(f"📊 Total rows: {data_result['total_count']}")
                        print(f"📋 Columns: {len(data_result['columns'])}")
                        print(f"🔍 Sample columns: {data_result['columns'][:5]}")
                        print(f"📄 Retrieved {len(data_result['data'])} rows")
                        
                        # Show first row
                        if data_result['data']:
                            first_row = data_result['data'][0]
                            print(f"📝 First row sample:")
                            for key, value in list(first_row.items())[:3]:
                                print(f"  - {key}: {value}")
                        
                        # Step 4: Test search functionality
                        print("\n🔄 Testing search functionality...")
                        search_response = requests.get(f"{BASE_URL}/files/table/{table_id}/search?search_term=EMAIL", timeout=10)
                        
                        if search_response.status_code == 200:
                            search_result = search_response.json()
                            print("✅ Search completed successfully!")
                            print(f"🔍 Found {len(search_result['data'])} matching rows")
                        else:
                            print(f"⚠️  Search failed: {search_response.status_code}")
                        
                    else:
                        print(f"❌ Failed to retrieve data: {data_response.status_code}")
                        print(f"Response: {data_response.text}")
                    
                else:
                    print(f"❌ CSV upload failed: {upload_response.status_code}")
                    print(f"Response: {upload_response.text}")
                    
            else:
                print("❌ sample_data.csv not found!")
                
        else:
            print(f"❌ Folder creation failed: {folder_response.status_code}")
            print(f"Response: {folder_response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to the API server at {BASE_URL}")
        print("📝 Make sure the server is running with: uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")

if __name__ == "__main__":
    test_csv_upload()
    
    print("\n" + "="*50)
    print("✅ CSV Upload Test completed!")
    print("\n📝 The CSV upload system now supports:")
    print("• All columns stored as String type")
    print("• All columns are nullable (except primary key)")
    print("• SQLite-compatible SQL generation")
    print("• Automatic table creation from CSV headers")
    print("• Bulk data import with proper error handling")
    print("• Full CRUD operations on dynamic tables")
    print("• Search functionality across table data") 