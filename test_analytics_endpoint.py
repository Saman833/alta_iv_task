#!/usr/bin/env python3

import requests
import json

def test_analytics_endpoint():
    """Test the /analytics/ask endpoint"""
    
    url = "http://localhost:8000/analytics/ask"
    
    # Test data
    test_data = {
        "question": "Show me insights about my data and suggest analysis approaches"
    }
    
    print("🧪 Testing analytics endpoint...")
    print(f"📤 Sending request to: {url}")
    print(f"📋 Question: {test_data['question']}")
    
    try:
        # Send POST request
        response = requests.post(url, json=test_data)
        
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Request successful!")
            
            # Check if we got a final response
            if "final_user_response" in result:
                print(f"📝 Final response length: {len(result['final_user_response'])}")
                print(f"📝 Final response preview: {result['final_user_response'][:200]}...")
            else:
                print("⚠️ No final_user_response in result")
                print(f"📊 Available keys: {list(result.keys())}")
                
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"📄 Response text: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure FastAPI is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_analytics_endpoint() 