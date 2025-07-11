from db import SessionLocal
from services.analytics_service import AnalyticsService

def main():
    """
    Complete Analytics Flow Demo with Accurate Column Information
    This demonstrates the entire analytics pipeline working with real data and correct schema info
    """
    print('🚀 COMPLETE ANALYTICS FLOW - WITH ACCURATE COLUMN SCHEMA')
    print('=' * 70)
    
    db = None
    try:
        # Initialize database and service
        print('🔧 Initializing analytics service...')
        db = SessionLocal()
        analytics_service = AnalyticsService(db)
        print('✅ Analytics service ready!')
        print()
        
        # Show available tables and their columns first
        print('📊 AVAILABLE DATA TABLES:')
        print('-' * 50)
        file_summaries = analytics_service._get_all_file_summaries()
        
        for i, summary in enumerate(file_summaries, 1):
            print(f'{i}. {summary["original_file_name"]} ({summary["table_name"]})')
            file_summary = summary["file_summary"]
            data_structure = file_summary.get("data_structure", {})
            if data_structure and data_structure.get("key_columns"):
                key_columns = data_structure["key_columns"][:5]  # First 5 columns
                col_names = [col.get("name", "") for col in key_columns]
                print(f'   📋 Columns: {", ".join(col_names)}...')
            print(f'   🏢 Domain: {file_summary.get("business_domain", "N/A")}')
            print()
        
        # Example user queries that should work with the actual data
        user_queries = [
            "Show me the distribution of content types in my communication data",
            "Analyze the Airbnb user session patterns",
            "What are the main categories in my data?"
        ]
        
        # Run analytics for the first query
        user_query = user_queries[0]
        print(f'👤 USER QUERY: "{user_query}"')
        print('-' * 50)
        
        # Run the complete analytics flow
        print('🔄 Running complete analytics pipeline...')
        result = analytics_service.analyze_user_request(user_query)
        
        print('\n📊 ANALYTICS RESULTS:')
        print('=' * 50)
        
        print(f'📝 Original Input: {result["original_input"]}')
        print()
        
        print('🎯 Enhanced Prompt:')
        enhanced_prompt = result["enhanced_prompt"]
        if isinstance(enhanced_prompt, dict):
            for key, value in enhanced_prompt.items():
                if key == 'context_summary' and value:
                    print(f'   📋 Context: {value[:100]}...')
                elif key == 'analysis_objectives' and value:
                    print(f'   🎯 Objectives: {", ".join(value[:3])}')
                elif key == 'enhanced_user_request':
                    print(f'   🔍 Enhanced Request: {value[:100]}...')
        else:
            print(f'   {str(enhanced_prompt)[:150]}...')
        print()
        
        print('🔍 Generated SQL Query:')
        query = result["generated_query"]
        print(f'   {query}')
        print()
        
        print('💡 Query Purpose:')
        print(f'   {result["query_purpose"]}')
        print()
        
        print('📈 Query Results:')
        query_result = result["query_result"]
        if query_result["success"]:
            data = query_result["data"]
            print(f'   ✅ Success: Found {data.get("row_count", 0)} rows')
            if data.get("rows"):
                print(f'   📊 Sample data: {len(data["rows"])} records retrieved')
                if data["rows"]:
                    first_row = data["rows"][0]
                    print(f'   🔍 First record keys: {list(first_row.keys())[:5]}...')
                    print(f'   📄 Sample values: {list(first_row.values())[:3]}...')
        else:
            print(f'   ❌ Query failed: {query_result.get("error", "Unknown error")}')
            print(f'   💡 This might be because the AI generated SQL with non-existent columns')
        print()
        
        print('🚀 Next Steps:')
        next_steps = result["next_steps"]
        if isinstance(next_steps, list):
            for i, step in enumerate(next_steps[:3], 1):
                if isinstance(step, dict):
                    if_result = step.get('if_result', str(step))[:60] + "..."
                    print(f'   {i}. {if_result}')
                else:
                    print(f'   {i}. {str(step)[:80]}...')
        else:
            print(f'   {next_steps}')
        
        print('\n' + '=' * 70)
        if query_result["success"]:
            print('✨ COMPLETE ANALYTICS FLOW SUCCESSFUL!')
            print('🎉 Real data processed, AI insights generated, SQL executed successfully!')
        else:
            print('⚠️  ANALYTICS FLOW COMPLETED WITH SQL ISSUE')
            print('🔧 The pipeline works but AI agent needs column schema information')
            print('💡 File summaries now contain real data - just need schema awareness')
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