#!/usr/bin/env python3
"""
Test script for the analytics/ask endpoint
"""

import requests
import json
import time

def test_analytics_ask():
    """Test the analytics/ask endpoint"""
    print("🧪 TESTING ANALYTICS/ASK ENDPOINT")
    print("=" * 50)
    
    # Test question
    test_question = "Show me information about the existing data tables"
    print(f"👤 Question: {test_question}")
    print()
    
    try:
        # Make request to the endpoint
        print("🔄 Making POST request to /analytics/ask...")
        start_time = time.time()
        
        response = requests.post(
            'http://localhost:8000/analytics/ask',
            json={'question': test_question},
            timeout=120  # 2 minute timeout
        )
        
        end_time = time.time()
        print(f"⏱️  Request completed in {end_time - start_time:.2f} seconds")
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Request successful!")
            
            try:
                result = response.json()
                print("\n📋 RESPONSE DETAILS:")
                print("=" * 40)
                
                # Check if we have the expected fields
                if "final_user_response" in result:
                    final_response = result["final_user_response"]
                    print(f"📝 Final Response (first 500 chars):")
                    print(f"   {final_response[:500]}...")
                    print()
                
                if "research_plan" in result:
                    research_plan = result["research_plan"]
                    print(f"📋 Research Plan (first 200 chars):")
                    print(f"   {str(research_plan)[:200]}...")
                    print()
                
                if "execution_details" in result:
                    execution_details = result["execution_details"]
                    print(f"🔍 Execution Details: {len(execution_details)} steps")
                    for i, step in enumerate(execution_details, 1):
                        print(f"   Step {i}: {step.get('step_name', 'Unknown')} - Success: {step.get('success', False)}")
                    print()
                
                print("✅ All expected fields present in response!")
                
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse JSON response: {e}")
                print(f"📄 Raw response: {response.text[:500]}")
        
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - Is the FastAPI server running?")
        print("💡 Make sure to run: uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        
    except requests.exceptions.Timeout:
        print("❌ Request timed out - the analytics process took too long")
        
    except Exception as e:
        print(f"❌ Error testing endpoint: {e}")

if __name__ == "__main__":
    test_analytics_ask() 