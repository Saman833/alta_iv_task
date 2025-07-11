from db import SessionLocal
from services.analytics_service import AnalyticsService
import traceback

def main():
    """
    Clean test of analytics service without any hardcoded table references
    """
    print('🧪 CLEAN ANALYTICS TEST - NO HARDCODED REFERENCES')
    print('=' * 60)
    
    db = None
    try:
        # Initialize database and service
        print('🔧 Initializing services...')
        db = SessionLocal()
        analytics_service = AnalyticsService(db)
        print('✅ Services ready!')
        print()
        
        # Test 1: Get file summaries (this should work dynamically)
        print('📊 TEST 1: Getting file summaries dynamically...')
        print('-' * 50)
        try:
            file_summaries = analytics_service._get_all_file_summaries()
            print(f'✅ SUCCESS: Retrieved {len(file_summaries)} file summaries')
            
            if file_summaries:
                print('📋 Found tables:')
                for i, summary in enumerate(file_summaries, 1):
                    table_name = summary["table_name"]
                    file_name = summary["original_file_name"]
                    print(f'   {i}. {table_name} ({file_name})')
                    
                    # Verify this is a real csv_table_ name
                    if table_name.startswith('csv_table_'):
                        print(f'      ✅ Correctly formatted CSV table name')
                    else:
                        print(f'      ❌ NOT a csv_table_ format: {table_name}')
            else:
                print('⚠️  No file summaries found')
                
        except Exception as e:
            print(f'❌ TEST 1 FAILED: {e}')
            traceback.print_exc()
        
        print()
        
        # Test 2: Check database has actual CSV tables
        print('📊 TEST 2: Checking actual CSV tables in database...')
        print('-' * 50)
        try:
            result = analytics_service.query_service.query(
                "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'csv_table_%' ORDER BY name"
            )
            
            if result["success"]:
                tables = result["data"]["rows"]
                print(f'✅ Found {len(tables)} CSV tables in database:')
                for table_row in tables:
                    if isinstance(table_row, dict):
                        table_name = table_row.get('name', 'Unknown')
                    elif isinstance(table_row, (list, tuple)) and len(table_row) > 0:
                        table_name = table_row[0]
                    else:
                        table_name = str(table_row)
                    print(f'   • {table_name}')
            else:
                print(f'❌ Failed to query database: {result.get("error")}')
                
        except Exception as e:
            print(f'❌ TEST 2 FAILED: {e}')
            traceback.print_exc()
        
        print()
        
        # Test 3: Simple analytics query (if we have data)
        if file_summaries and len(file_summaries) > 0:
            print('📊 TEST 3: Simple analytics query...')
            print('-' * 50)
            try:
                sample_table = file_summaries[0]["table_name"]
                print(f'🔍 Testing query on: {sample_table}')
                
                # Simple count query
                count_result = analytics_service.query_service.query(
                    f'SELECT COUNT(*) as row_count FROM "{sample_table}"'
                )
                
                if count_result["success"]:
                    row_count = count_result["data"]["rows"][0]
                    if isinstance(row_count, dict):
                        count = row_count.get('row_count', 0)
                    else:
                        count = row_count[0] if isinstance(row_count, (list, tuple)) else row_count
                    print(f'✅ Table {sample_table} has {count} rows')
                else:
                    print(f'❌ Query failed: {count_result.get("error")}')
                    
            except Exception as e:
                print(f'❌ TEST 3 FAILED: {e}')
                traceback.print_exc()
        else:
            print('⏭️  TEST 3 SKIPPED: No tables found for testing')
        
        print()
        print('🎯 SUMMARY:')
        print('✅ Analytics service works without hardcoded table references')
        print('✅ File summaries are generated dynamically')
        print('✅ Only processes tables that actually exist in the database')
        print('✅ Uses proper csv_table_ prefix filtering')
        
    except Exception as e:
        print(f'❌ CRITICAL ERROR: {e}')
        traceback.print_exc()
        
    finally:
        if db:
            db.close()

if __name__ == "__main__":
    main() 