#!/usr/bin/env python3
"""
Test script to verify the fast CSV upload process
"""

import requests
import json
import time

def test_csv_upload():
    """Test the fast CSV upload process"""
    print("🧪 TESTING FAST CSV UPLOAD")
    print("=" * 50)
    
    # Sample CSV content
    csv_content = """product_id,product_name,category,price,review_score,sales_month_1,sales_month_2,sales_month_3
1,Laptop Pro,Electronics,999.99,4.5,150,180,200
2,Smartphone X,Electronics,599.99,4.2,200,220,250
3,Desk Chair,Furniture,199.99,4.0,50,60,70
4,Wireless Headphones,Electronics,89.99,4.3,300,350,400
5,Office Desk,Furniture,299.99,4.1,30,35,40"""
    
    # Test data
    test_data = {
        'csv_content': csv_content,
        'file_name': 'test_products.csv',
        'folder_id': 'test-folder-123',
        'user_id': 'test-user-456'
    }
    
    try:
        print("🔄 Testing CSV upload from content...")
        start_time = time.time()
        
        response = requests.post(
            'http://localhost:8000/files/upload-csv-from-content',
            data=test_data,
            timeout=30  # 30 second timeout
        )
        
        end_time = time.time()
        print(f"⏱️  Upload completed in {end_time - start_time:.2f} seconds")
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Upload successful!")
            
            try:
                result = response.json()
                print("\n📋 UPLOAD RESULT:")
                print("=" * 40)
                print(f"   Message: {result.get('message', 'N/A')}")
                print(f"   File ID: {result.get('file_id', 'N/A')}")
                print(f"   Table ID: {result.get('table_id', 'N/A')}")
                print(f"   Table Name: {result.get('table_name', 'N/A')}")
                print()
                
                # Test retrieving the uploaded data
                table_id = result.get('table_id')
                if table_id:
                    print("🔄 Testing data retrieval...")
                    data_response = requests.get(
                        f'http://localhost:8000/files/table/{table_id}/data',
                        timeout=10
                    )
                    
                    if data_response.status_code == 200:
                        data_result = data_response.json()
                        print("✅ Data retrieval successful!")
                        print(f"   Columns: {data_result.get('columns', [])}")
                        print(f"   Total Rows: {data_result.get('total_count', 0)}")
                        print(f"   Retrieved Rows: {len(data_result.get('data', []))}")
                        
                        # Show first few rows
                        rows = data_result.get('data', [])
                        if rows:
                            print("\n📊 Sample Data:")
                            for i, row in enumerate(rows[:3], 1):
                                print(f"   Row {i}: {row}")
                    else:
                        print(f"❌ Data retrieval failed: {data_response.status_code}")
                        print(f"   Response: {data_response.text}")
                
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse JSON response: {e}")
                print(f"📄 Raw response: {response.text}")
        
        else:
            print(f"❌ Upload failed with status {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - Is the FastAPI server running?")
        print("💡 Make sure to run: python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        
    except requests.exceptions.Timeout:
        print("❌ Upload timed out - the process took too long")
        
    except Exception as e:
        print(f"❌ Error testing upload: {e}")

if __name__ == "__main__":
    test_csv_upload() 