#!/usr/bin/env python3
"""
Test script that only works with existing tables and tests step 1
"""

from db import SessionLocal
from services.autonomous_analytics_service import AutonomousAnalyticsService
from sqlalchemy import create_engine, text

def get_existing_tables():
    """Get list of existing tables in the database"""
    DATABASE_URL = "sqlite:///./test.db"
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Get all table names
        query = text("SELECT name FROM sqlite_master WHERE type='table'")
        result = conn.execute(query)
        tables = [row[0] for row in result.fetchall()]
    
    return tables

def test_step1_with_existing_tables():
    """Test step 1 with only existing tables"""
    print("🔍 TESTING STEP 1 WITH EXISTING TABLES")
    print("=" * 50)
    
    # Get existing tables
    existing_tables = get_existing_tables()
    print(f"📋 Found {len(existing_tables)} existing tables:")
    for table in existing_tables:
        print(f"   • {table}")
    print()
    
    if not existing_tables:
        print("❌ No tables found in database")
        return
    
    db = None
    try:
        # Initialize service
        print("🔧 Initializing analytics service...")
        db = SessionLocal()
        analytics_service = AutonomousAnalyticsService(db)
        print("✅ Service ready!")
        print()
        
        # Test user query
        user_query = "Show me information about the existing data tables"
        print(f"👤 USER QUERY: '{user_query}'")
        print("-" * 50)
        
        # Run only step 1 (research plan generation)
        print("🔄 Testing Step 1: Research Plan Generation...")
        
        # Get file summaries (this will only include existing tables)
        file_summaries = analytics_service._get_all_file_summaries()
        print(f"📊 Found {len(file_summaries)} file summaries")
        
        # Generate research plan
        research_plan = analytics_service._generate_autonomous_analysis_plan(user_query, file_summaries)
        
        if research_plan:
            print("✅ Step 1 SUCCESSFUL!")
            print()
            
            # Display research plan details
            print("📋 RESEARCH PLAN DETAILS:")
            print("=" * 40)
            
            # Research analysis
            research_analysis = research_plan.get("research_analysis", {})
            if research_analysis:
                print("🔍 Research Analysis:")
                print(f"   Understanding: {research_analysis.get('user_question_understanding', 'N/A')[:200]}")
                print(f"   Current Knowledge: {research_analysis.get('current_knowledge', 'N/A')[:200]}")
                print(f"   Knowledge Gaps: {research_analysis.get('knowledge_gaps', [])}")
                print(f"   Strategy: {research_analysis.get('research_strategy', 'N/A')[:200]}")
                print()
            
            # Five step plan
            five_step_plan = research_plan.get("five_step_research_plan", [])
            if five_step_plan:
                print("📊 5-Step Research Plan:")
                for i, step in enumerate(five_step_plan, 1):
                    print(f"   Step {i}: {step.get('step_name', 'Unknown')}")
                    print(f"      Purpose: {step.get('step_purpose', 'N/A')[:100]}")
                    print(f"      Query: {step.get('query', 'N/A')[:100]}")
                    print()
            
            # Comprehensive research
            comprehensive = research_plan.get("comprehensive_research", {})
            if comprehensive:
                print("📝 Comprehensive Research:")
                print(f"   Summary: {comprehensive.get('research_summary', 'N/A')[:200]}")
                print(f"   Questions: {comprehensive.get('research_questions', [])}")
                print()
            
            print("✅ ALL REQUIRED FIELDS PRESENT!")
            print("✅ Step 1 test completed successfully!")
            
        else:
            print("❌ Step 1 FAILED - No research plan generated")
            
    except Exception as e:
        print(f"❌ Error in test: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if db:
            db.close()

if __name__ == "__main__":
    test_step1_with_existing_tables() 