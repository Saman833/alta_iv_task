#!/usr/bin/env python3
"""
Script to delete a specific table
"""

from sqlalchemy import create_engine, text

def delete_specific_table(table_name: str):
    """Delete a specific table"""
    DATABASE_URL = "sqlite:///./test.db"
    engine = create_engine(DATABASE_URL)
    
    print(f"🗑️  Deleting table: {table_name}")
    print("=" * 40)
    
    with engine.connect() as conn:
        try:
            # Check if table exists
            check_query = text("SELECT name FROM sqlite_master WHERE type='table' AND name=:table_name")
            result = conn.execute(check_query, {"table_name": table_name})
            
            if result.fetchone():
                # Delete the table
                drop_query = text(f"DROP TABLE {table_name}")
                conn.execute(drop_query)
                conn.commit()
                print(f"✅ Successfully deleted table: {table_name}")
            else:
                print(f"⚠️  Table not found: {table_name}")
                
        except Exception as e:
            print(f"❌ Failed to delete {table_name}: {e}")

if __name__ == "__main__":
    table_name = "csv_table_360c7996_2e40_4aff_9618_441df0ff312a"
    delete_specific_table(table_name) 