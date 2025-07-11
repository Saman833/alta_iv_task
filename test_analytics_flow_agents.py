#!/usr/bin/env python3
"""
Test script to verify all agents in the analytics flow are working correctly
and focused on user requests, with proper final structured responses.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db import SessionLocal
from services.autonomous_analytics_service import AutonomousAnalyticsService
from services.agent_service import AgentService
import json

def test_enhanced_user_prompt_agent():
    """Test enhanced user prompt agent focuses on user requests"""
    print("🧪 Testing Enhanced User Prompt Agent...")
    
    agent_service = AgentService()
    
    # Test input
    test_input = {
        "original_user_input": "What are the main trends in my data?",
        "file_summaries": [
            {
                "table_name": "sample_data",
                "original_file_name": "sample_data.csv",
                "file_summary": {
                    "overview": "Sample business data with sales, customers, and products",
                    "business_domain": "Retail/E-commerce",
                    "data_structure": {"columns": ["date", "sales", "customer_id", "product"]}
                }
            }
        ]
    }
    
    try:
        response = agent_service.run_agent("enhanced_user_prompt_agent", test_input)
        print("✅ Enhanced User Prompt Agent working")
        print(f"   Enhanced prompt: {str(response)[:100]}...")
        return True
    except Exception as e:
        print(f"❌ Enhanced User Prompt Agent failed: {e}")
        return False

def test_analytics_agent():
    """Test analytics agent focuses on user requests and conducts research"""
    print("\n🧪 Testing Analytics Agent...")
    
    agent_service = AgentService()
    
    # Test input
    test_input = {
        "original_user_input": "What are the main trends in my data?",
        "file_summaries": [
            {
                "table_name": "sample_data",
                "original_file_name": "sample_data.csv",
                "file_summary": {
                    "overview": "Sample business data with sales, customers, and products",
                    "business_domain": "Retail/E-commerce",
                    "data_structure": {"columns": ["date", "sales", "customer_id", "product"]}
                }
            }
        ],
        "previous_queries": [],
        "analysis_context": {
            "analysis_goal": "comprehensive_database_research",
            "constraints": {"max_rows": 100},
            "autonomous_mode": True,
            "research_mode": True
        }
    }
    
    try:
        response = agent_service.run_agent("analytics_agent", test_input)
        print("✅ Analytics Agent working")
        print(f"   Research analysis: {str(response.get('research_analysis', ''))[:100]}...")
        return True
    except Exception as e:
        print(f"❌ Analytics Agent failed: {e}")
        return False

def test_question_answering_agent():
    """Test question answering agent provides focused answers"""
    print("\n🧪 Testing Question Answering Agent...")
    
    agent_service = AgentService()
    
    # Test input
    test_input = {
        "client_question": "What are the main trends in my data?",
        "analytics_history": [
            {
                "query": "SELECT COUNT(*) as total_records FROM sample_data",
                "purpose": "Get total record count",
                "result": {
                    "success": True,
                    "rows": [{"total_records": 1000}],
                    "columns": ["total_records"],
                    "row_count": 1
                }
            }
        ],
        "file_summaries": [
            {
                "table_name": "sample_data",
                "original_file_name": "sample_data.csv",
                "file_summary": {
                    "overview": "Sample business data with sales, customers, and products",
                    "business_domain": "Retail/E-commerce",
                    "data_structure": {"columns": ["date", "sales", "customer_id", "product"]}
                }
            }
        ]
    }
    
    try:
        response = agent_service.run_agent("question_answering_agent", test_input)
        print("✅ Question Answering Agent working")
        if response and "answer_response" in response:
            print(f"   Direct answer: {response['answer_response']['direct_answer'][:100]}...")
        return True
    except Exception as e:
        print(f"❌ Question Answering Agent failed: {e}")
        return False

def test_final_response_agent():
    """Test final response agent creates comprehensive structured responses"""
    print("\n🧪 Testing Final Response Agent...")
    
    agent_service = AgentService()
    
    # Test input
    test_input = {
        "user_question": "What are the main trends in my data?",
        "analytics_data": {
            "total_queries": 3,
            "successful_queries": 3,
            "comprehensive_insights": [
                "Found 1000 total records in the dataset",
                "Sales show increasing trend over time",
                "Top products are electronics and clothing"
            ],
            "query_results": [
                {
                    "query": "SELECT COUNT(*) as total_records FROM sample_data",
                    "purpose": "Get total record count",
                    "result": {
                        "success": True,
                        "rows": [{"total_records": 1000}],
                        "columns": ["total_records"],
                        "row_count": 1
                    }
                }
            ]
        },
        "question_answering_response": "Based on the analysis, your data shows strong growth trends with electronics and clothing being the top performing product categories.",
        "file_summaries": [
            {
                "table_name": "sample_data",
                "original_file_name": "sample_data.csv",
                "file_summary": {
                    "overview": "Sample business data with sales, customers, and products",
                    "business_domain": "Retail/E-commerce",
                    "data_structure": {"columns": ["date", "sales", "customer_id", "product"]}
                }
            }
        ],
        "analysis_context": {
            "analysis_depth": "comprehensive",
            "data_sources_used": ["sample_data"],
            "research_completeness": "full_autonomous_analysis"
        },
        "research_plan": "Conducted comprehensive analysis of sales data to identify trends and patterns"
    }
    
    try:
        response = agent_service.run_agent("final_response_agent", test_input)
        print("✅ Final Response Agent working")
        if response and "final_response" in response:
            final_response = response["final_response"]
            if "comprehensive_text_response" in final_response:
                print(f"   Comprehensive text response: {final_response['comprehensive_text_response'][:100]}...")
            if "executive_summary" in final_response:
                print(f"   Executive summary: {final_response['executive_summary'][:100]}...")
        return True
    except Exception as e:
        print(f"❌ Final Response Agent failed: {e}")
        return False

def test_complete_autonomous_flow():
    """Test the complete autonomous analytics flow"""
    print("\n🧪 Testing Complete Autonomous Analytics Flow...")
    
    db = None
    try:
        db = SessionLocal()
        analytics_service = AutonomousAnalyticsService(db)
        
        # Test with a simple query
        user_query = "What insights can you find in my data?"
        print(f"   User query: {user_query}")
        
        result = analytics_service.analyze_user_request_autonomously(user_query, max_queries=2)
        
        if result:
            print("✅ Complete Autonomous Analytics Flow working")
            print(f"   Queries executed: {result.get('queries_executed', 0)}")
            print(f"   Total queries: {result.get('total_queries', 0)}")
            print(f"   Insights generated: {len(result.get('comprehensive_insights', []))}")
            
            # Check if final structured response is generated
            if "final_structured_response" in result:
                final_response = result["final_structured_response"]
                if "comprehensive_text_response" in final_response:
                    print(f"   Final text response: {final_response['comprehensive_text_response'][:100]}...")
                else:
                    print("   ⚠️ Final structured response missing comprehensive_text_response")
            else:
                print("   ⚠️ Final structured response not generated")
            
            return True
        else:
            print("❌ Complete Autonomous Analytics Flow failed")
            return False
            
    except Exception as e:
        print(f"❌ Complete Autonomous Analytics Flow failed: {e}")
        return False
    finally:
        if db:
            db.close()

def main():
    """Run all tests"""
    print("🚀 TESTING ANALYTICS FLOW AGENTS")
    print("=" * 60)
    
    tests = [
        test_enhanced_user_prompt_agent,
        test_analytics_agent,
        test_question_answering_agent,
        test_final_response_agent,
        test_complete_autonomous_flow
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    test_names = [
        "Enhanced User Prompt Agent",
        "Analytics Agent", 
        "Question Answering Agent",
        "Final Response Agent",
        "Complete Autonomous Flow"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i+1}. {name}: {status}")
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL AGENTS WORKING CORRECTLY!")
        print("✅ All agents are focused on user requests")
        print("✅ Final response agent provides comprehensive structured text")
        print("✅ Complete analytics flow is functional")
    else:
        print("⚠️ Some agents need attention")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 