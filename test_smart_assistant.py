#!/usr/bin/env python3
"""
Test script for the smart assistant integration
"""

import asyncio
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.conversational_ai_service import ConversationalAIService

async def test_smart_assistant():
    """Test the smart assistant with different types of requests"""
    
    print("🧪 Testing Smart Assistant Integration")
    print("=" * 50)
    
    # Initialize the service
    service = ConversationalAIService()
    
    # Test cases
    test_cases = [
        {
            "name": "Search Request",
            "input": "Find messages about meetings",
            "expected_type": "function_response"
        },
        {
            "name": "Summary Request", 
            "input": "Give me a summary of urgent messages",
            "expected_type": "function_response"
        },
        {
            "name": "Conversational Request",
            "input": "Hello, how are you today?",
            "expected_type": "conversational"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📝 Testing: {test_case['name']}")
        print(f"Input: '{test_case['input']}'")
        
        try:
            response = await service.generate_response(test_case['input'])
            print(f"✅ Response: '{response}'")
            
            # Check if it's a function response or conversational
            if "found" in response.lower() or "summary" in response.lower():
                print("🔧 Function response detected")
            else:
                print("💬 Conversational response detected")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Testing completed!")

if __name__ == "__main__":
    asyncio.run(test_smart_assistant()) 