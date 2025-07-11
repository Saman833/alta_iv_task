from db import SessionLocal
from services.autonomous_analytics_service import AutonomousAnalyticsService

def main():
    """
    Complete Analytics Flow Demo
    This demonstrates the entire analytics pipeline working with real data
    """
    print('🚀 COMPLETE ANALYTICS FLOW - REAL DATA PIPELINE')
    print('=' * 70)
    
    db = None
    try:
        # Initialize database and service
        print('🔧 Initializing autonomous analytics service...')
        db = SessionLocal()
        analytics_service = AutonomousAnalyticsService(db)
        print('✅ Autonomous analytics service ready!')
        print()
        
        # Example user query
        user_query = "Show me insights about my data and suggest analysis approaches"
        print(f'👤 USER QUERY: "{user_query}"')
        print('-' * 50)
        
        # Run the complete autonomous analytics flow
        print('🔄 Running complete autonomous analytics pipeline...')
        result = analytics_service.analyze_user_request_autonomously(user_query)
        
        print('\n📊 AUTONOMOUS ANALYTICS RESULTS:')
        print('=' * 50)

        print(f'📝 User Question: {result.get("user_question", "N/A")}')
        print()

        # Print research plan summary
        research_plan = result.get("research_plan", {})
        if research_plan:
            print('📋 Research Plan:')
            if isinstance(research_plan, str):
                print(f'   Analysis: {research_plan[:200]}')
            else:
                print(f'   Analysis: {str(research_plan)[:200]}')
            print()

        # Print execution details
        execution_details = result.get("execution_details", [])
        if execution_details:
            print('🔍 Execution Details:')
            for i, execution in enumerate(execution_details, 1):
                print(f'   Step {i}: {execution.get("step_name", "Unknown")}')
                print(f'      Purpose: {execution.get("purpose", "")[:120]}')
                print(f'      Query: {execution.get("query", "")[:120]}')
                print(f'      Success: {execution.get("success", False)}')
                if execution.get("result", {}).get("data", {}).get("rows"):
                    rows = execution["result"]["data"]["rows"]
                    print(f'      Results: {len(rows)} rows returned')
                print()

        # Print comprehensive insights
        insights = result.get("comprehensive_insights", [])
        if insights:
            print('💡 Comprehensive Insights:')
            for insight in insights:
                print(f'   • {insight[:200]}')
            print()

        # Print final user response
        final_response = result.get("final_user_response", "")
        if final_response:
            print('📝 Final User Response:')
            print(f'   {final_response[:500]}')
            print()

        print('\n' + '=' * 70)
        print('✨ AUTONOMOUS ANALYTICS FLOW SUCCESSFUL!')
        print('🎉 Comprehensive analysis completed with dynamic 5-step research and structured response!')
        print('=' * 70)

        return result
        
    except Exception as e:
        print(f'❌ Error in analytics flow: {e}')
        import traceback
        traceback.print_exc()
        return None
        
    finally:
        if db:
            db.close()

if __name__ == "__main__":
    main() 