#!/usr/bin/env python3
"""
Comprehensive test to verify all fixes work correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db import SessionLocal
from services.assistant_service import AssistantService

def test_comprehensive_fixes():
    """Test all the fixes comprehensively"""
    
    print("🧪 Comprehensive Test - All Fixes")
    print("=" * 60)
    
    # Initialize
    db = SessionLocal()
    assistant_service = AssistantService(db)
    
    # Test 1: Check initialization
    print("\n✅ Test 1: Service Initialization")
    try:
        assert hasattr(assistant_service, 'openai_client')
        assert hasattr(assistant_service, 'agent_service')
        assert hasattr(assistant_service, 'content_table_service')
        assert hasattr(assistant_service, 'function_loader')
        print("✅ All services initialized correctly")
    except Exception as e:
        print(f"❌ Initialization error: {e}")
    
    # Test 2: Check data availability
    print("\n✅ Test 2: Data Availability")
    try:
        messages = assistant_service.content_table_service.get_public_summary()
        print(f"📊 Total messages: {len(messages)}")
        if messages:
            print(f"📝 Sample message structure: {type(messages[0])}")
            print(f"🔍 Sample content_data: {messages[0].content_data[:50]}...")
    except Exception as e:
        print(f"❌ Data access error: {e}")
    
    # Test 3: Test search function with error handling
    print("\n✅ Test 3: Search Function (with error handling)")
    try:
        search_result = assistant_service.search_on_database("urgent messages")
        print(f"🔍 Search result type: {type(search_result)}")
        print(f"📋 Search result: {search_result}")
        
        if isinstance(search_result, list):
            print(f"✅ Search returned list with {len(search_result)} items")
        else:
            print(f"⚠️ Unexpected search result type: {type(search_result)}")
    except Exception as e:
        print(f"❌ Search error: {e}")
    
    # Test 4: Test summary function with error handling
    print("\n✅ Test 4: Summary Function (with error handling)")
    try:
        summary_result = assistant_service.get_summary_of_messages("urgent messages")
        print(f"📋 Summary result type: {type(summary_result)}")
        print(f"📝 Summary result: {summary_result}")
        
        if isinstance(summary_result, str):
            print("✅ Summary returned string correctly")
        else:
            print(f"⚠️ Unexpected summary result type: {type(summary_result)}")
    except Exception as e:
        print(f"❌ Summary error: {e}")
    
    # Test 5: Test function formatting
    print("\n✅ Test 5: Function Response Formatting")
    try:
        # Test with empty results
        empty_results = []
        formatted = assistant_service._format_function_response(empty_results, "test")
        print(f"📝 Empty results formatting: {formatted}")
        
        # Test with mock search results
        mock_results = [{
            "function_name": "search_on_database",
            "result": [],
            "reasoning": "test"
        }]
        formatted = assistant_service._format_function_response(mock_results, "test")
        print(f"📝 Mock search results formatting: {formatted}")
        
        # Test with mock summary results
        mock_results = [{
            "function_name": "get_summary_of_messages",
            "result": "Test summary",
            "reasoning": "test"
        }]
        formatted = assistant_service._format_function_response(mock_results, "test")
        print(f"📝 Mock summary results formatting: {formatted}")
        
    except Exception as e:
        print(f"❌ Formatting error: {e}")
    
    # Test 6: Test agent manager
    print("\n✅ Test 6: Agent Manager")
    try:
        # Test with a simple request
        result = assistant_service.agent_manager("hello")
        print(f"🤖 Agent manager result type: {type(result)}")
        print(f"📋 Agent manager result: {result}")
        
        if isinstance(result, dict) and "type" in result:
            print("✅ Agent manager returned proper dict structure")
        else:
            print(f"⚠️ Unexpected agent manager result: {result}")
            
    except Exception as e:
        print(f"❌ Agent manager error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Comprehensive test completed!")

if __name__ == "__main__":
    test_comprehensive_fixes() 