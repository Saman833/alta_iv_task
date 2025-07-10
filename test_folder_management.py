#!/usr/bin/env python3
"""
Test script for folder management functionality
"""

import requests
import json
from pathlib import Path

# API base URL
BASE_URL = "http://127.0.0.1:8000"

def test_folder_management():
    """Test the folder management functionality"""
    
    print("🚀 Starting Folder Management Test")
    print("="*50)
    
    try:
        # Test 1: Create a folder
        print("🔄 Testing folder creation...")
        
        folder_data = {
            "folder_name": "My Documents",
            "detail_summary": "A folder for storing important documents",
            "user_id": "test-user-123"
        }
        
        response = requests.post(f"{BASE_URL}/files/folders", json=folder_data, timeout=10)
        
        if response.status_code == 200:
            folder_result = response.json()
            print("✅ Folder created successfully!")
            print(f"📁 Folder ID: {folder_result['id']}")
            print(f"📋 Folder Name: {folder_result['folder_name']}")
            print(f"👤 User ID: {folder_result['user_id']}")
            
            folder_id = folder_result['id']
            user_id = folder_result['user_id']
            
            # Test 2: Get folder by ID
            print("\n🔄 Testing folder retrieval...")
            get_response = requests.get(f"{BASE_URL}/files/folders/{folder_id}", timeout=10)
            
            if get_response.status_code == 200:
                folder_data = get_response.json()
                print("✅ Folder retrieved successfully!")
                print(f"📁 Retrieved folder: {folder_data['folder_name']}")
            else:
                print(f"❌ Failed to retrieve folder: {get_response.status_code}")
            
            # Test 3: Get user folders
            print("\n🔄 Testing user folders retrieval...")
            user_folders_response = requests.get(f"{BASE_URL}/files/folders?user_id={user_id}", timeout=10)
            
            if user_folders_response.status_code == 200:
                user_folders = user_folders_response.json()
                print("✅ User folders retrieved successfully!")
                print(f"📊 Found {len(user_folders)} folders for user")
                for folder in user_folders:
                    print(f"  - {folder['folder_name']} (ID: {folder['id']})")
            else:
                print(f"❌ Failed to retrieve user folders: {user_folders_response.status_code}")
            
            # Test 4: Create a CSV file in the folder
            print("\n🔄 Testing CSV file creation in folder...")
            
            # Read sample CSV
            csv_file_path = Path("sample_data.csv")
            if csv_file_path.exists():
                with open(csv_file_path, 'r', encoding='utf-8') as f:
                    csv_content = f.read()
                
                file_data = {
                    "csv_content": csv_content,
                    "file_name": "test_data.csv",
                    "folder_id": folder_id,
                    "user_id": user_id
                }
                
                file_response = requests.post(f"{BASE_URL}/files/upload-csv-from-content", data=file_data, timeout=15)
                
                if file_response.status_code == 200:
                    file_result = file_response.json()
                    print("✅ CSV file created in folder successfully!")
                    print(f"📄 File ID: {file_result['file_id']}")
                    print(f"📊 Table ID: {file_result['table_id']}")
                    
                    # Test 5: Get folder files
                    print("\n🔄 Testing folder files retrieval...")
                    folder_files_response = requests.get(f"{BASE_URL}/files/folders/{folder_id}/files", timeout=10)
                    
                    if folder_files_response.status_code == 200:
                        folder_files = folder_files_response.json()
                        print("✅ Folder files retrieved successfully!")
                        print(f"📊 Found {len(folder_files)} files in folder")
                        for file in folder_files:
                            print(f"  - {file['file_name']} (Type: {file['file_type']}, Size: {file['file_size']} bytes)")
                    else:
                        print(f"❌ Failed to retrieve folder files: {folder_files_response.status_code}")
                        
                else:
                    print(f"❌ Failed to create CSV file: {file_response.status_code}")
                    print(f"Response: {file_response.text}")
            else:
                print("⚠️  sample_data.csv not found, skipping file creation test")
            
            # Test 6: Get user files
            print("\n🔄 Testing user files retrieval...")
            user_files_response = requests.get(f"{BASE_URL}/files/users/{user_id}/files", timeout=10)
            
            if user_files_response.status_code == 200:
                user_files = user_files_response.json()
                print("✅ User files retrieved successfully!")
                print(f"📊 Found {len(user_files)} files for user")
                for file in user_files:
                    print(f"  - {file['file_name']} in folder {file['folder_id']}")
            else:
                print(f"❌ Failed to retrieve user files: {user_files_response.status_code}")
            
            # Test 7: Try to delete folder (should fail if it has files)
            print("\n🔄 Testing folder deletion (should fail with files)...")
            delete_response = requests.delete(f"{BASE_URL}/files/folders/{folder_id}", timeout=10)
            
            if delete_response.status_code == 400:
                print("✅ Folder deletion correctly blocked due to files!")
                print("📝 This is expected behavior")
            else:
                print(f"⚠️  Unexpected response: {delete_response.status_code}")
            
            # Test 8: Force delete folder
            print("\n🔄 Testing force folder deletion...")
            force_delete_response = requests.delete(f"{BASE_URL}/files/folders/{folder_id}?force=true", timeout=10)
            
            if force_delete_response.status_code == 200:
                print("✅ Folder force deleted successfully!")
                print("📝 All files in the folder were also deleted")
            else:
                print(f"❌ Failed to force delete folder: {force_delete_response.status_code}")
                print(f"Response: {force_delete_response.text}")
                
        else:
            print(f"❌ Folder creation failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to the API server at {BASE_URL}")
        print("📝 Make sure the server is running with: uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    except requests.exceptions.Timeout:
        print(f"❌ Request timed out. Server might be slow to respond.")
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")

if __name__ == "__main__":
    test_folder_management()
    
    print("\n" + "="*50)
    print("✅ Folder Management Test completed!")
    print("\n📝 Available endpoints:")
    print("1. POST /files/folders - Create folder")
    print("2. GET /files/folders?user_id={user_id} - Get user folders")
    print("3. GET /files/folders/{folder_id} - Get specific folder")
    print("4. GET /files/folders/{folder_id}/files - Get folder files")
    print("5. DELETE /files/folders/{folder_id} - Delete folder")
    print("6. DELETE /files/folders/{folder_id}?force=true - Force delete folder")
    print("7. GET /files/users/{user_id}/files - Get user files")
    print("8. Visit API docs: http://127.0.0.1:8000/docs") 