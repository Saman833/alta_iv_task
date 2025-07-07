#!/usr/bin/env python3
"""
Debug script to test search functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db import SessionLocal
from services.assistant_service import AssistantService

def debug_search():
    """Debug the search functionality"""
    
    print("🔍 Debugging Search Functionality")
    print("=" * 50)
    
    # Initialize
    db = SessionLocal()
    assistant_service = AssistantService(db)
    
    # Test 1: Check what data we have
    print("\n📊 Checking available messages:")
    messages = assistant_service.content_table_service.get_public_summary()
    print(f"Total messages: {len(messages)}")
    
    for i, msg in enumerate(messages[:3]):  # Show first 3
        print(f"Message {i}:")
        print(f"  ID: {msg.id}")
        print(f"  Content: {msg.content_data[:100]}...")
        print(f"  Category: {msg.category}")
        print(f"  Source: {msg.source}")
        print(f"  Subject: {msg.subject}")
        print()
    
    # Test 2: Try search for urgent messages
    print("\n🔍 Testing search for urgent messages:")
    try:
        search_result = assistant_service.search_on_database("show me urgent messages")
        print(f"Search result type: {type(search_result)}")
        print(f"Search result: {search_result}")
        
        if isinstance(search_result, list):
            print(f"Found {len(search_result)} messages")
            for i, msg in enumerate(search_result):
                print(f"  {i+1}. {msg.content_data[:100]}...")
        else:
            print(f"Unexpected result: {search_result}")
            
    except Exception as e:
        print(f"❌ Search error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Try summary
    print("\n📋 Testing summary for urgent messages:")
    try:
        summary_result = assistant_service.get_summary_of_messages("give me a summary of urgent messages")
        print(f"Summary result: {summary_result}")
    except Exception as e:
        print(f"❌ Summary error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("✅ Debug completed!")

if __name__ == "__main__":
    debug_search() 