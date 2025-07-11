#!/usr/bin/env python3
"""
Test: JSON Export Functionality

Simple test to demonstrate the comprehensive JSON export capabilities.
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db import SessionLocal
from services.iterative_analytics_service import IterativeAnalyticsService

def test_json_export():
    """
    Test the JSON export functionality with a simple example
    """
    print("🧪 Testing JSON Export Functionality")
    print("=" * 50)
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Create analytics service
        analytics_service = IterativeAnalyticsService(db)
        
        print("📊 Running a simple analytics session...")
        
        # Run a simple autonomous analytics session
        results = analytics_service.run_autonomous_analytics(
            initial_user_input="Show me basic data overview",
            max_iterations=3,
            min_iterations=2
        )
        
        print("\n📋 Getting detailed query history...")
        detailed_history = analytics_service.get_detailed_query_history()
        
        # Create a comprehensive export manually for testing
        export_data = {
            "test_session": {
                "session_info": {
                    "total_iterations": len(detailed_history),
                    "successful_queries": sum(1 for h in detailed_history if h["exact_db_response"]["success"]),
                    "test_timestamp": "test_run"
                },
                "agent_calls": [],
                "sql_queries": [],
                "database_responses": []
            }
        }
        
        # Extract all agent interactions and SQL executions
        for i, history_entry in enumerate(detailed_history, 1):
            # Agent interaction
            agent_call = {
                "call_id": f"agent_call_{i}",
                "agent_name": "analytics_agent",
                "iteration": i,
                "input": {
                    "user_request": history_entry["user_input"],
                    "query_purpose": history_entry["query_purpose"]
                },
                "output": {
                    "sql_generated": history_entry["exact_sql_query"],
                    "reasoning": history_entry["query_purpose"]
                }
            }
            export_data["test_session"]["agent_calls"].append(agent_call)
            
            # SQL execution
            sql_execution = {
                "execution_id": f"sql_exec_{i}",
                "iteration": i,
                "sql_query": history_entry["exact_sql_query"],
                "execution_result": history_entry["exact_db_response"]
            }
            export_data["test_session"]["sql_queries"].append(sql_execution)
            
            # Database response
            db_response = {
                "response_id": f"db_response_{i}",
                "iteration": i,
                "success": history_entry["exact_db_response"]["success"],
                "data": history_entry["exact_db_response"]
            }
            export_data["test_session"]["database_responses"].append(db_response)
        
        # Export to JSON file
        test_filename = "test_comprehensive_export.json"
        with open(test_filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n✅ Test export created: {test_filename}")
        
        # Show what was captured
        print(f"\n📊 Export Summary:")
        print(f"   • Agent Calls: {len(export_data['test_session']['agent_calls'])}")
        print(f"   • SQL Queries: {len(export_data['test_session']['sql_queries'])}")
        print(f"   • Database Responses: {len(export_data['test_session']['database_responses'])}")
        
        # Show sample structure
        if export_data["test_session"]["agent_calls"]:
            print(f"\n📋 Sample Agent Call Structure:")
            sample_agent = export_data["test_session"]["agent_calls"][0]
            print(f"   • Agent Name: {sample_agent['agent_name']}")
            print(f"   • Input Keys: {list(sample_agent['input'].keys())}")
            print(f"   • Output Keys: {list(sample_agent['output'].keys())}")
        
        if export_data["test_session"]["sql_queries"]:
            print(f"\n📝 Sample SQL Query Structure:")
            sample_sql = export_data["test_session"]["sql_queries"][0]
            print(f"   • Execution ID: {sample_sql['execution_id']}")
            print(f"   • SQL Length: {len(sample_sql['sql_query'])} characters")
            print(f"   • Success: {sample_sql['execution_result']['success']}")
        
        return test_filename
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        db.close()

if __name__ == "__main__":
    result = test_json_export()
    if result:
        print(f"\n🎉 JSON export test completed successfully!")
        print(f"📁 Test file: {result}")
    else:
        print(f"\n❌ JSON export test failed!") 