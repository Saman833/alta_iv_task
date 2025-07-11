from db import SessionLocal
from services.analytics_service import AnalyticsService
from repository.file_repository import FileRepository

def main():
    """
    Regenerate file summaries with accurate column schema information
    """
    print('🔄 REGENERATING FILE SUMMARIES WITH ACCURATE SCHEMA INFO')
    print('=' * 70)
    
    db = None
    try:
        # Initialize database and service
        print('🔧 Initializing services...')
        db = SessionLocal()
        analytics_service = AnalyticsService(db)
        file_repo = FileRepository(db)
        print('✅ Services ready!')
        print()
        
        # Get all files and force regeneration of summaries
        print('📂 Getting all files to regenerate summaries...')
        tables = analytics_service.table_repository.get_all_tables_global()
        
        files_updated = 0
        for table in tables:
            try:
                # Get the file associated with this table
                files = file_repo.get_folder_files(table.folder_id)
                csv_files = [f for f in files if f.file_name == table.table_name]
                
                if not csv_files:
                    continue
                    
                file = csv_files[0]
                print(f'🔄 Regenerating summary for: {file.file_name}')
                
                # Clear existing summary to force regeneration
                file.detail_summary = None
                db.commit()
                
                # Generate new summary with enhanced schema
                new_summary = analytics_service._generate_file_summary(table.id, file.file_name)
                
                if new_summary and isinstance(new_summary, dict):
                    # Check if it has the new schema information
                    if "database_schema" in new_summary:
                        print(f'✅ Enhanced summary generated with schema info')
                        schema = new_summary["database_schema"]
                        print(f'   📋 Table: {schema["table_name"]}')
                        print(f'   🔢 Columns: {len(schema["available_columns"])}')
                        print(f'   📊 Column details: {len(schema["column_details"])} analyzed')
                        files_updated += 1
                    else:
                        print(f'⚠️  Summary generated but missing schema info')
                else:
                    print(f'❌ Failed to generate summary')
                
                print()
                
            except Exception as e:
                print(f'❌ Error processing {table.table_name}: {e}')
                continue
        
        print(f'📊 REGENERATION COMPLETE: {files_updated} files updated with schema info')
        print()
        
        # Test the analytics flow with the new summaries
        print('🧪 TESTING ANALYTICS FLOW WITH NEW SUMMARIES:')
        print('-' * 50)
        
        user_query = "Show me the different categories in my communication data"
        print(f'👤 Test Query: "{user_query}"')
        
        result = analytics_service.analyze_user_request(user_query)
        
        print('📊 Results:')
        query_result = result["query_result"]
        if query_result["success"]:
            print(f'   ✅ SUCCESS: Query executed successfully!')
            print(f'   📈 Found {query_result["data"].get("row_count", 0)} results')
        else:
            print(f'   ❌ Query failed: {query_result.get("error", "Unknown error")}')
            print(f'   🔍 Generated SQL: {result["generated_query"]}')
        
        print('\n' + '=' * 70)
        if query_result["success"]:
            print('🎉 ENHANCED ANALYTICS PIPELINE WORKING!')
            print('✨ File summaries now include accurate database schema')
            print('🚀 AI agents can generate correct SQL queries!')
        else:
            print('⚠️  Analytics pipeline needs further schema refinement')
        print('=' * 70)
        
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()
        
    finally:
        if db:
            db.close()

if __name__ == "__main__":
    main() 