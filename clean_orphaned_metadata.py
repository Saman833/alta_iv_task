from db import SessionLocal
from repository.table_respository import TableRepository
from sqlalchemy import text

def main():
    """
    Clean up orphaned table metadata records that point to deleted CSV tables
    This will remove metadata for CSV tables that no longer exist
    """
    print('🧹 CLEANING ORPHANED TABLE METADATA')
    print('=' * 60)
    
    db = None
    try:
        # Initialize database and repository
        print('🔧 Initializing database connection...')
        db = SessionLocal()
        table_repo = TableRepository(db)
        print('✅ Database connection ready!')
        print()
        
        # Get all table metadata records
        print('📂 Getting all table metadata records...')
        all_table_records = table_repo.get_all_tables_global()
        print(f'📋 Found {len(all_table_records)} table metadata records')
        
        # Get all actual CSV tables that exist in the database
        print('🔍 Checking which CSV tables actually exist...')
        result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'csv_table_%'"))
        existing_csv_tables = {row[0] for row in result.fetchall()}
        print(f'📊 Found {len(existing_csv_tables)} actual CSV tables in database')
        
        if existing_csv_tables:
            print('✅ Existing CSV tables:')
            for table in sorted(existing_csv_tables):
                print(f'   • {table}')
        print()
        
        # Check each metadata record
        print('🔍 Checking metadata records for orphaned entries...')
        orphaned_records = []
        valid_records = []
        
        for table_record in all_table_records:
            # Convert table ID to expected CSV table name
            expected_csv_table = f"csv_table_{table_record.id.replace('-', '_')}"
            
            if expected_csv_table in existing_csv_tables:
                valid_records.append(table_record)
                print(f'✅ VALID: {table_record.table_name} → {expected_csv_table}')
            else:
                orphaned_records.append(table_record)
                print(f'❌ ORPHANED: {table_record.table_name} → {expected_csv_table} (missing)')
        
        print()
        print(f'📊 Analysis Results:')
        print(f'   ✅ Valid metadata records: {len(valid_records)}')
        print(f'   ❌ Orphaned metadata records: {len(orphaned_records)}')
        
        if orphaned_records:
            print()
            print(f'🗑️  ORPHANED RECORDS TO DELETE:')
            for i, record in enumerate(orphaned_records, 1):
                print(f'   {i}. Table: {record.table_name}')
                print(f'      ID: {record.id}')
                print(f'      Expected CSV table: csv_table_{record.id.replace("-", "_")}')
                print(f'      Created: {record.table_created_at}')
                print()
            
            # Ask for confirmation
            print('⚠️  These orphaned metadata records will be permanently deleted!')
            confirm = input('❓ Are you sure you want to delete these orphaned records? (y/n): ').strip().lower()
            
            if confirm in ['y', 'yes']:
                print()
                print('🗑️  Deleting orphaned metadata records...')
                deleted_count = 0
                
                for record in orphaned_records:
                    try:
                        # Delete the record
                        db.delete(record)
                        deleted_count += 1
                        print(f'   ✅ Deleted: {record.table_name} (ID: {record.id})')
                    except Exception as e:
                        print(f'   ❌ Failed to delete {record.table_name}: {e}')
                
                # Commit all deletions
                db.commit()
                print()
                print(f'✅ Successfully deleted {deleted_count} orphaned metadata records!')
                
                # Also clean up orphaned file records
                print()
                print('🧹 Also checking for orphaned file records...')
                from repository.file_repository import FileRepository
                file_repo = FileRepository(db)
                
                # Get remaining valid folder IDs
                remaining_records = table_repo.get_all_tables_global()
                valid_folder_ids = {record.folder_id for record in remaining_records}
                
                # Get all file records
                all_files_result = db.execute(text("SELECT * FROM file"))
                orphaned_files = []
                
                for file_row in all_files_result.fetchall():
                    file_dict = dict(file_row._mapping) if hasattr(file_row, '_mapping') else dict(zip(file_row.keys(), file_row))
                    folder_id = file_dict['folder_id']
                    
                    if folder_id not in valid_folder_ids:
                        orphaned_files.append(file_dict)
                
                if orphaned_files:
                    print(f'🗑️  Found {len(orphaned_files)} orphaned file records')
                    for file_dict in orphaned_files:
                        try:
                            db.execute(text("DELETE FROM file WHERE id = :file_id"), {"file_id": file_dict['id']})
                            print(f'   ✅ Deleted orphaned file: {file_dict["file_name"]}')
                        except Exception as e:
                            print(f'   ❌ Failed to delete file {file_dict["file_name"]}: {e}')
                    
                    db.commit()
                    print(f'✅ Cleaned up {len(orphaned_files)} orphaned file records!')
                else:
                    print('✅ No orphaned file records found')
                
            else:
                print('❌ Operation cancelled - no records deleted')
        else:
            print('✅ No orphaned metadata records found - database is clean!')
        
        print()
        print('🎯 CLEANUP SUMMARY:')
        print(f'   📊 Total metadata records checked: {len(all_table_records)}')
        print(f'   ✅ Valid records remaining: {len(valid_records)}')
        print(f'   🗑️  Orphaned records cleaned: {len(orphaned_records) if orphaned_records and confirm in ["y", "yes"] else 0}')
        print('   💡 Analytics service should now work without hardcoded references!')
        
    except Exception as e:
        print(f'❌ Error cleaning orphaned metadata: {e}')
        if db:
            db.rollback()
        import traceback
        traceback.print_exc()
        
    finally:
        if db:
            db.close()

if __name__ == "__main__":
    main() 