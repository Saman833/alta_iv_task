from db import SessionLocal
from services.iterative_analytics_service import IterativeAnalyticsService

def print_query_result(result, query_number):
    """
    Print formatted query result
    """
    print(f'\n📊 QUERY #{query_number} RESULTS:')
    print('=' * 50)
    
    print(f'📝 Input: {result["original_input"]}')
    print(f'🎯 Purpose: {result["query_purpose"][:80]}...')
    print(f'🔍 SQL: {result["generated_query"][:100]}...')
    
    query_result = result["query_result"]
    if query_result["success"]:
        data = query_result["data"]
        print(f'✅ SUCCESS: Found {data.get("row_count", 0)} rows')
        
        if data.get("rows") and len(data["rows"]) > 0:
            print(f'📋 Columns: {", ".join(data.get("columns", [])[:5])}...')
            print('📄 Sample Results:')
            for i, row in enumerate(data["rows"][:3], 1):
                if isinstance(row, dict):
                    row_summary = {k: str(v)[:30] + "..." if len(str(v)) > 30 else v 
                                 for k, v in list(row.items())[:3]}
                    print(f'   Row {i}: {row_summary}')
    else:
        print(f'❌ FAILED: {query_result.get("error", "Unknown error")[:100]}...')
    
    # Show conversation context
    if "conversation_context" in result:
        ctx = result["conversation_context"]
        print(f'\n📈 Conversation Progress: {ctx["successful_queries"]}/{ctx["total_queries"]} successful queries')
        
        if ctx["insights_discovered"]:
            print(f'💡 Recent Insights: {len(ctx["insights_discovered"])} discovered')
            for insight in ctx["insights_discovered"][-2:]:  # Show last 2 insights
                print(f'   • {insight}')

def main():
    """
    Demo of Iterative Analytics Service
    Shows how previous query results inform next queries
    """
    print('🔄 ITERATIVE ANALYTICS DEMO')
    print('Using previous query results to generate follow-up queries')
    print('=' * 70)
    
    db = None
    try:
        # Initialize the iterative analytics service
        print('🔧 Initializing iterative analytics service...')
        db = SessionLocal()
        analytics_service = IterativeAnalyticsService(db)
        print('✅ Service ready!')
        
        # Start the analytics conversation
        print('\n🚀 STARTING ANALYTICS CONVERSATION')
        print('-' * 50)
        
        initial_query = "Show me the distribution of categories in my communication data"
        print(f'👤 Initial Query: "{initial_query}"')
        
        # Query 1: Initial analysis
        result1 = analytics_service.start_analytics_conversation(initial_query)
        print_query_result(result1, 1)
        
        # Query 2: Auto-generated follow-up based on Query 1 results
        print('\n🤖 AUTO-GENERATING FOLLOW-UP QUERY...')
        result2 = analytics_service.continue_analytics_conversation()
        print_query_result(result2, 2)
        
        # Query 3: Another auto-generated follow-up
        print('\n🤖 AUTO-GENERATING SECOND FOLLOW-UP...')
        result3 = analytics_service.continue_analytics_conversation()
        print_query_result(result3, 3)
        
        # Query 4: User-specified follow-up
        print('\n👤 USER-SPECIFIED FOLLOW-UP...')
        user_follow_up = "Compare the results with visitor data from Airbnb table"
        result4 = analytics_service.continue_analytics_conversation(user_follow_up)
        print_query_result(result4, 4)
        
        # Show conversation summary
        print('\n📋 CONVERSATION SUMMARY:')
        print('=' * 50)
        summary = analytics_service.get_conversation_summary()
        
        print(f'📊 Total Queries: {summary["total_queries"]}')
        print(f'✅ Successful Queries: {summary["successful_queries"]}')
        print(f'💡 Insights Discovered: {len(summary["insights_discovered"])}')
        
        print('\n📝 Query History:')
        for i, query_info in enumerate(summary["query_history"], 1):
            status = "✅" if query_info["success"] else "❌"
            print(f'   {i}. {status} "{query_info["query"][:50]}..."')
            print(f'      Purpose: {query_info["purpose"][:60]}...')
        
        if summary["insights_discovered"]:
            print('\n💡 Discovered Insights:')
            for insight in summary["insights_discovered"]:
                print(f'   • {insight}')
        
        # Export conversation
        print('\n💾 EXPORTING CONVERSATION...')
        filename = analytics_service.export_conversation("iterative_analytics_demo.json")
        
        print('\n' + '=' * 70)
        print('🎉 ITERATIVE ANALYTICS DEMO COMPLETE!')
        print('✨ Key Features Demonstrated:')
        print('   ✅ Auto-generation of follow-up queries based on previous results')
        print('   ✅ Context preservation across multiple queries')
        print('   ✅ Insight extraction and accumulation')
        print('   ✅ Mixed auto/manual query progression')
        print('   ✅ Conversation export for analysis')
        print('=' * 70)
        
        # Test with a fresh conversation
        if summary["successful_queries"] > 0:
            print('\n🔄 TESTING FRESH CONVERSATION START...')
            new_query = "Analyze user sessions in my Airbnb data"
            fresh_result = analytics_service.start_analytics_conversation(new_query)
            print(f'✅ Fresh conversation started successfully!')
            print(f'📊 New query: "{fresh_result["original_input"]}"')
            print(f'🎯 Purpose: {fresh_result["query_purpose"][:60]}...')
        
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()
        
    finally:
        if db:
            db.close()

if __name__ == "__main__":
    main() 