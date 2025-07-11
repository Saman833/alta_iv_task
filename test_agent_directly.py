#!/usr/bin/env python3

from services.agent_service import AgentService
from db import SessionLocal

def test_analytics_agent():
    """Test the analytics agent directly to see what's happening"""
    print("🧪 Testing Analytics Agent Directly")
    print("=" * 50)
    
    # Initialize agent service
    agent_service = AgentService()
    
    # Prepare test input
    test_input = {
        "original_user_input": "Which product shows high growth and a high share of total sales?",
        "file_summaries": [
            {
                "table_name": "csv_table_231cd743_c616_40f6_b0c4_deae52051078",
                "original_file_name": "ecommerce_sales_analysis.csv",
                "file_summary": {
                    "overview": "Product sales data with monthly sales figures, product categories, pricing, and customer reviews",
                    "business_domain": "E-commerce Sales"
                }
            },
            {
                "table_name": "csv_table_85cc25ed_5b1a_41dc_bdfe_f89fe7832fb0",
                "original_file_name": "Social_Media_Advertising.csv",
                "file_summary": {
                    "overview": "Social media advertising campaign data with performance metrics, targeting, and ROI analysis",
                    "business_domain": "Digital Marketing"
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
        print("🤖 Calling analytics agent...")
        result = agent_service.run_agent("analytics_agent", test_input)
        print("✅ Agent call successful!")
        print("📊 Result type:", type(result))
        print("📊 Result keys:", list(result.keys()) if isinstance(result, dict) else "Not a dict")
        print("📊 Result preview:", str(result)[:500] + "..." if result else "None")
        
    except Exception as e:
        print(f"❌ Error calling analytics agent: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_analytics_agent() 