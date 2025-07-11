#!/usr/bin/env python3
"""
Script to delete all records from the file table
"""

from sqlalchemy import create_engine, text

def delete_all_file_records():
    """Delete all records from the file table"""
    DATABASE_URL = "sqlite:///./test.db"
    engine = create_engine(DATABASE_URL)
    
    print("🗑️  Deleting all records from the file table...")
    print("=" * 50)
    
    with engine.connect() as conn:
        try:
            # First, check how many records exist
            count_query = text("SELECT COUNT(*) FROM file")
            result = conn.execute(count_query)
            record_count = result.scalar()
            
            print(f"Found {record_count} records in the file table")
            
            if record_count > 0:
                # Delete all records
                delete_query = text("DELETE FROM file")
                conn.execute(delete_query)
                conn.commit()
                
                print(f"✅ Successfully deleted {record_count} records from the file table")
            else:
                print("ℹ️  No records found in the file table")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    delete_all_file_records() 