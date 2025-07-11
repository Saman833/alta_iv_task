#!/usr/bin/env python3
"""
Script to delete specific tables from the database
"""

import sqlite3
from sqlalchemy import create_engine, text, MetaData, inspect
from sqlalchemy.orm import sessionmaker
import json
from typing import Dict, List, Any

def get_database_connection():
    """Get database connection"""
    DATABASE_URL = "sqlite:///./test.db"
    engine = create_engine(DATABASE_URL)
    return engine

def list_all_tables():
    """List all tables in the database"""
    engine = get_database_connection()
    inspector = inspect(engine)
    
    table_names = inspector.get_table_names()
    
    print("📋 All tables in database:")
    print("=" * 50)
    for i, table_name in enumerate(table_names, 1):
        print(f"{i:2d}. {table_name}")
    
    return table_names

def delete_tables(table_names: List[str], confirm: bool = True):
    """Delete specified tables"""
    engine = get_database_connection()
    
    print(f"\n🗑️  Deleting {len(table_names)} tables...")
    print("=" * 50)
    
    if confirm:
        print("Tables to delete:")
        for table_name in table_names:
            print(f"  • {table_name}")
        
        response = input("\n❓ Are you sure you want to delete these tables? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("❌ Operation cancelled.")
            return False
    
    deleted_tables = []
    failed_tables = []
    
    with engine.connect() as conn:
        for table_name in table_names:
            try:
                # Check if table exists
                check_query = text("SELECT name FROM sqlite_master WHERE type='table' AND name=:table_name")
                result = conn.execute(check_query, {"table_name": table_name})
                
                if result.fetchone():
                    # Delete the table
                    drop_query = text(f"DROP TABLE {table_name}")
                    conn.execute(drop_query)
                    conn.commit()
                    
                    print(f"✅ Deleted table: {table_name}")
                    deleted_tables.append(table_name)
                else:
                    print(f"⚠️  Table not found: {table_name}")
                    failed_tables.append(table_name)
                    
            except Exception as e:
                print(f"❌ Failed to delete {table_name}: {e}")
                failed_tables.append(table_name)
    
    # Summary
    print(f"\n📊 Summary:")
    print(f"  ✅ Successfully deleted: {len(deleted_tables)} tables")
    print(f"  ❌ Failed to delete: {len(failed_tables)} tables")
    
    if deleted_tables:
        print(f"  📝 Deleted tables: {', '.join(deleted_tables)}")
    
    if failed_tables:
        print(f"  ⚠️  Failed tables: {', '.join(failed_tables)}")
    
    return len(failed_tables) == 0

def delete_csv_tables():
    """Delete all CSV tables (tables starting with 'csv_table_')"""
    engine = get_database_connection()
    
    with engine.connect() as conn:
        # Find all CSV tables
        query = text("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'csv_table_%'")
        result = conn.execute(query)
        csv_tables = [row[0] for row in result.fetchall()]
    
    if csv_tables:
        print(f"🗑️  Found {len(csv_tables)} CSV tables to delete:")
        for table in csv_tables:
            print(f"  • {table}")
        
        return delete_tables(csv_tables)
    else:
        print("ℹ️  No CSV tables found.")
        return True

def delete_by_pattern(pattern: str):
    """Delete tables matching a pattern"""
    engine = get_database_connection()
    
    with engine.connect() as conn:
        # Find tables matching pattern
        query = text("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE :pattern")
        result = conn.execute(query, {"pattern": pattern})
        matching_tables = [row[0] for row in result.fetchall()]
    
    if matching_tables:
        print(f"🗑️  Found {len(matching_tables)} tables matching pattern '{pattern}':")
        for table in matching_tables:
            print(f"  • {table}")
        
        return delete_tables(matching_tables)
    else:
        print(f"ℹ️  No tables found matching pattern '{pattern}'.")
        return True

def main():
    """Main function"""
    print("🗑️  Database Table Deletion Tool")
    print("=" * 50)
    
    # List all tables first
    all_tables = list_all_tables()
    
    if not all_tables:
        print("ℹ️  No tables found in database.")
        return
    
    print(f"\nOptions:")
    print("1. Delete specific tables (enter table names)")
    print("2. Delete all CSV tables (csv_table_*)")
    print("3. Delete tables by pattern")
    print("4. Exit")
    
    choice = input("\nSelect option (1-4): ").strip()
    
    if choice == "1":
        print("\nEnter table names to delete (separated by commas):")
        table_input = input("Tables: ").strip()
        if table_input:
            table_names = [name.strip() for name in table_input.split(",")]
            delete_tables(table_names)
    
    elif choice == "2":
        delete_csv_tables()
    
    elif choice == "3":
        pattern = input("Enter pattern (e.g., 'csv_%' or '%temp%'): ").strip()
        if pattern:
            delete_by_pattern(pattern)
    
    elif choice == "4":
        print("👋 Exiting...")
    
    else:
        print("❌ Invalid option.")

if __name__ == "__main__":
    main() 