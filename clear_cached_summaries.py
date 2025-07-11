from db import SessionLocal
from repository.file_repository import FileRepository
from models.file import FileType
from sqlalchemy import text

def main():
    """
    Clear all cached file summaries from the database
    This will force regeneration of summaries on next analytics run
    """
    print('🗑️  CLEARING ALL CACHED FILE SUMMARIES')
    print('=' * 60)
    
    db = None
    try:
        # Initialize database and repository
        print('🔧 Initializing database connection...')
        db = SessionLocal()
        file_repo = FileRepository(db)
        print('✅ Database connection ready!')
        print()
        
        # Get all files in the database
        print('📂 Searching for files with cached summaries...')
        
        # Use proper SQLAlchemy text() for raw SQL
        all_files = db.execute(text("SELECT * FROM file")).fetchall()
        
        print(f'📋 Found {len(all_files)} total files in database')
        
        cleared_count = 0
        csv_files_count = 0
        
        for file_row in all_files:
            # Convert row to dict for easier access
            file_dict = dict(file_row._mapping) if hasattr(file_row, '_mapping') else dict(zip(file_row.keys(), file_row))
            
            file_id = file_dict['id']
            file_name = file_dict['file_name']
            file_type = file_dict['file_type']
            detail_summary = file_dict['detail_summary']
            
            # Count CSV files
            if file_type == 'CSV':
                csv_files_count += 1
                print(f'📄 CSV File: {file_name}')
                
                # Check if this file has a cached summary
                has_cached_summary = (
                    detail_summary and 
                    detail_summary != f"File created from {file_type}" and
                    not detail_summary.startswith("File") and
                    len(detail_summary) > 50  # Likely a real summary, not just default text
                )
                
                if has_cached_summary:
                    print(f'   🗑️  Clearing cached summary ({len(detail_summary)} characters)')
                    
                    # Clear the summary using proper text() syntax
                    db.execute(
                        text("UPDATE file SET detail_summary = NULL WHERE id = :file_id"),
                        {"file_id": file_id}
                    )
                    cleared_count += 1
                else:
                    print(f'   ⏭️  No cached summary found (keeping default)')
            else:
                print(f'📄 Other File: {file_name} (type: {file_type}) - skipping')
        
        # Commit all changes
        if cleared_count > 0:
            db.commit()
            print()
            print(f'✅ Successfully cleared {cleared_count} cached summaries!')
        else:
            print()
            print(f'ℹ️  No cached summaries found to clear')
        
        print()
        print(f'📊 Summary:')
        print(f'   📄 Total files: {len(all_files)}')
        print(f'   📊 CSV files: {csv_files_count}')
        print(f'   🗑️  Summaries cleared: {cleared_count}')
        print(f'   🔄 Files that will regenerate summaries: {cleared_count}')
        
        if cleared_count > 0:
            print()
            print('💡 Next time you run analytics, summaries will be regenerated!')
            print('   This ensures you get fresh summaries with the latest schema info.')
        
    except Exception as e:
        print(f'❌ Error clearing cached summaries: {e}')
        if db:
            db.rollback()
        import traceback
        traceback.print_exc()
        
    finally:
        if db:
            db.close()

if __name__ == "__main__":
    print('🧹 Cached Summary Cleaner')
    print('=' * 40)
    print('This will clear all cached file summaries and force regeneration')
    print()
    
    try:
        # Confirm with user
        confirm = input('❓ Are you sure you want to clear all cached summaries? (y/n): ').strip().lower()
        if confirm in ['y', 'yes']:
            main()
        else:
            print('❌ Operation cancelled')
            
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Operation interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc() 