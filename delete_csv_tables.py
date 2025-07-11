#!/usr/bin/env python3
"""
Simple script to delete all CSV tables without confirmation
"""

from sqlalchemy import create_engine, text

def delete_all_csv_tables():
    """Delete all CSV tables (tables starting with 'csv_table_')"""
    DATABASE_URL = "sqlite:///./test.db"
    engine = create_engine(DATABASE_URL)
    
    print("🗑️  Deleting all CSV tables...")
    print("=" * 40)
    
    with engine.connect() as conn:
        # Find all CSV tables
        query = text("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'csv_table_%'")
        result = conn.execute(query)
        csv_tables = [row[0] for row in result.fetchall()]
    
    if csv_tables:
        print(f"Found {len(csv_tables)} CSV tables to delete:")
        for table in csv_tables:
            print(f"  • {table}")
        
        # Delete each table
        deleted_count = 0
        with engine.connect() as conn:
            for table_name in csv_tables:
                try:
                    drop_query = text(f"DROP TABLE {table_name}")
                    conn.execute(drop_query)
                    conn.commit()
                    print(f"✅ Deleted: {table_name}")
                    deleted_count += 1
                except Exception as e:
                    print(f"❌ Failed to delete {table_name}: {e}")
        
        print(f"\n📊 Summary: Successfully deleted {deleted_count}/{len(csv_tables)} tables")
    else:
        print("ℹ️  No CSV tables found.")

if __name__ == "__main__":
    delete_all_csv_tables() 