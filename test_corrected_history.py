from db import SessionLocal
from services.iterative_analytics_service import IterativeAnalyticsService
import json

def main():
    """
    Test the corrected history tracking for SQL queries and their results
    """
    print('🧪 TESTING CORRECTED QUERY HISTORY TRACKING')
    print('=' * 60)
    
    db = None
    try:
        # Initialize database and service
        print('🔧 Initializing services...')
        db = SessionLocal()
        iterative_service = IterativeAnalyticsService(db)
        print('✅ Services ready!')
        print()
        
        # Test 1: Start analytics conversation
        print('📊 TEST 1: Starting analytics conversation...')
        print('-' * 50)
        initial_result = iterative_service.start_analytics_conversation("Show me the data overview")
        
        print(f'✅ Initial query executed successfully: {initial_result["query_result"]["success"]}')
        print(f'📝 Query generated: {initial_result["generated_query"][:100]}...')
        print()
        
        # Test 2: Check history format
        print('📋 TEST 2: Checking query history format...')
        print('-' * 50)
        
        if iterative_service.query_history:
            first_entry = iterative_service.query_history[0]
            print(f'✅ History has {len(iterative_service.query_history)} entries')
            print(f'📝 Entry format check:')
            print(f'   - Has "query": {"query" in first_entry}')
            print(f'   - Has "result": {"result" in first_entry}')
            print(f'   - Has "purpose": {"purpose" in first_entry}')
            print(f'   - Result has success: {"success" in first_entry.get("result", {})}')
            print(f'   - Result has rows: {"rows" in first_entry.get("result", {})}')
            print(f'   - Result has columns: {"columns" in first_entry.get("result", {})}')
            print(f'   - Result has row_count: {"row_count" in first_entry.get("result", {})}')
            print()
            
            # Show the actual history structure
            print('📖 Sample history entry:')
            print(json.dumps(first_entry, indent=2)[:500] + '...')
        else:
            print('❌ No history entries found')
        print()
        
        # Test 3: Continue conversation
        print('📊 TEST 3: Continuing analytics conversation...')
        print('-' * 50)
        follow_up_result = iterative_service.continue_analytics_conversation("Show me more details")
        
        print(f'✅ Follow-up query executed: {follow_up_result["query_result"]["success"]}')
        print(f'📝 Total queries in history: {len(iterative_service.query_history)}')
        print()
        
        # Test 4: Verify analytics agent format compatibility
        print('📋 TEST 4: Verifying analytics agent format compatibility...')
        print('-' * 50)
        
        context = iterative_service._get_conversation_context()
        previous_queries = context.get("previous_queries", [])
        
        if previous_queries:
            print(f'✅ Context has {len(previous_queries)} previous queries')
            print(f'📝 Format matches analytics agent examples: ')
            sample_query = previous_queries[0]
            required_fields = ["query", "result", "purpose"]
            required_result_fields = ["success", "rows", "columns", "row_count"]
            
            for field in required_fields:
                present = field in sample_query
                print(f'   - {field}: {"✅" if present else "❌"}')
            
            if "result" in sample_query:
                for field in required_result_fields:
                    present = field in sample_query["result"]
                    print(f'   - result.{field}: {"✅" if present else "❌"}')
            
            print()
            print('📖 Sample previous_queries entry:')
            print(json.dumps(sample_query, indent=2)[:400] + '...')
        else:
            print('❌ No previous queries found in context')
        
        print()
        print('🎉 All tests completed!')
        
        # Test 5: Export conversation to saman_test1.json
        print('💾 TEST 5: Exporting conversation data...')
        print('-' * 50)
        
        export_filename = iterative_service.export_conversation()
        print(f'✅ Conversation exported to: {export_filename}')
        
        # Verify the file was created and show its size
        import os
        if os.path.exists(export_filename):
            file_size = os.path.getsize(export_filename)
            print(f'📊 File size: {file_size} bytes')
            print(f'📁 File location: {os.path.abspath(export_filename)}')
        else:
            print('❌ Export file was not created')
        
    except Exception as e:
        print(f'❌ Error: {str(e)}')
        import traceback
        traceback.print_exc()
    
    finally:
        if db:
            db.close()

if __name__ == "__main__":
    main() 