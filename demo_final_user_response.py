#!/usr/bin/env python3
"""
Demo script showing the exact final response users will see
This demonstrates the complete analytics flow with proof and metrics
"""

from db import SessionLocal
from services.autonomous_analytics_service import AutonomousAnalyticsService

def main():
    """
    Demo the final user response - this is what users will actually see
    """
    print('🎯 FINAL USER RESPONSE DEMO')
    print('=' * 60)
    print('This shows the EXACT response users will see with proof and metrics')
    print('=' * 60)
    
    db = None
    try:
        # Initialize service
        print('🔧 Initializing autonomous analytics service...')
        db = SessionLocal()
        analytics_service = AutonomousAnalyticsService(db)
        print('✅ Service ready!')
        print()
        
        # Example user questions
        user_questions = [
            "What are the main trends in my sales data?",
            "How are my customer satisfaction scores performing?",
            "What insights can you find about my business performance?"
        ]
        
        for i, question in enumerate(user_questions, 1):
            print(f'\n📝 USER QUESTION {i}: "{question}"')
            print('-' * 50)
            
            # Run autonomous analysis
            print('🔄 Running autonomous analysis...')
            result = analytics_service.analyze_user_request_autonomously(question, max_queries=3)
            
            if result and "final_user_response" in result:
                print('\n🎯 FINAL USER RESPONSE:')
                print('=' * 50)
                print(result["final_user_response"])
                print('=' * 50)
                
                # Show metadata
                print('\n📊 Response Metadata:')
                print(f'   Queries executed: {result.get("queries_executed", 0)}')
                print(f'   Total queries: {result.get("total_queries", 0)}')
                print(f'   Insights generated: {len(result.get("comprehensive_insights", []))}')
                
            else:
                print('❌ No final user response generated')
            
            print('\n' + '=' * 60)
        
        print('\n✨ DEMO COMPLETE!')
        print('🎉 Users will see comprehensive responses with proof and metrics')
        
    except Exception as e:
        print(f'❌ Error in demo: {e}')
        import traceback
        traceback.print_exc()
        
    finally:
        if db:
            db.close()

if __name__ == "__main__":
    main() 