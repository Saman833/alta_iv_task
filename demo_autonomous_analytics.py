#!/usr/bin/env python3
"""
Autonomous Analytics Demo

This demo shows how the analytics system can run autonomously for several iterations,
automatically generating follow-up queries based on previous results.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db import SessionLocal
from services.autonomous_analytics_service import AutonomousAnalyticsService
import json

def main():
    """
    Demo of Autonomous Analytics Service
    Shows how the analytics agent autonomously executes multiple queries
    to provide comprehensive answers to user questions
    """
    print('🚀 AUTONOMOUS ANALYTICS DEMONSTRATION')
    print('=' * 60)
    print('This demo shows how the analytics agent works autonomously')
    print('to answer complex business questions with multiple queries')
    print()
    
    db = None
    try:
        # Initialize service
        print('🔧 Initializing Autonomous Analytics Service...')
        db = SessionLocal()
        analytics_service = AutonomousAnalyticsService(db)
        print('✅ Service ready!')
        print()
        
        # Example user questions (both English and Russian)
        example_questions = [
            "Which product shows high growth and a high share of total sales?",
            "Which product has a high share but a low growth rate of sales volume?",
            "Which product has a low share but high sales-growth rates?",
            "Which product has a low growth rate and a low market share?",
            "Which channels deliver the greatest reach for each euro spent?",
            "Where is the largest drop-off between impressions and clicks?",
            "Which campaigns convert clicks into sales the best?",
            "Who is our 'star' audience—high reach and high conversion?"
        ]
        
        print('📋 Example Questions:')
        for i, question in enumerate(example_questions, 1):
            print(f'   {i}. {question}')
        print()
        
        # Get user input
        print('Please enter your analytics question (or press Enter for demo):')
        user_input = input('👤 Your question: ').strip()
        
        if not user_input:
            user_input = "Which product shows high growth and a high share of total sales?"
            print(f'Using demo question: "{user_input}"')
        
        print(f'\n🎯 Processing: "{user_input}"')
        print('=' * 60)
        
        # Run autonomous analytics
        print('\n🔄 Running Autonomous Analytics...')
        result = analytics_service.analyze_user_request_autonomously(user_input, max_queries=5)
        
        # Display results
        print('\n📊 AUTONOMOUS ANALYTICS RESULTS')
        print('=' * 60)
        
        if "error" in result:
            print(f'❌ Error: {result["error"]}')
            return
        
        print(f'👤 User Question: {result["user_question"]}')
        print()
        
        print('📋 Analysis Plan:')
        plan = result["analysis_plan"]
        print(f'   Understanding: {plan["user_question_understanding"]}')
        print(f'   Strategy: {plan["analysis_strategy"]}')
        print(f'   Expected Outcome: {plan["expected_outcome"]}')
        print()
        
        print('🔍 Queries Executed:')
        print(f'   Total: {result["total_queries"]}')
        print(f'   Successful: {result["queries_executed"]}')
        print()
        
        print('💡 Insights Generated:')
        for i, insight in enumerate(result["comprehensive_insights"], 1):
            print(f'   {i}. {insight}')
        print()
        
        print('📝 Comprehensive Answer:')
        print(f'   {result["comprehensive_answer"]}')
        print()
        
        # Show execution details
        print('🔍 Execution Details:')
        for execution in result["execution_details"]:
            status = "✅" if execution.get("success") else "❌"
            print(f'   {status} Query {execution["query_number"]}: {execution["purpose"]}')
            if not execution.get("success"):
                print(f'      Error: {execution.get("error", "Unknown error")}')
        print()
        
        # Save results
        filename = f"autonomous_analytics_{int(time.time())}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f'💾 Results saved to: {filename}')
        
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc() 
    
    finally:
        if db:
            db.close()

if __name__ == "__main__":
    import time
    main() 