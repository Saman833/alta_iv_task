#!/usr/bin/env python3
"""
Script to inspect column types for all tables in the database
"""

import sqlite3
from sqlalchemy import create_engine, text, MetaData, inspect
from sqlalchemy.orm import sessionmaker
import json
from typing import Dict, List, Any

def get_database_connection():
    """Get database connection"""
    # Use the same database URL as in your main application
    DATABASE_URL = "sqlite:///./test.db"
    engine = create_engine(DATABASE_URL)
    return engine

def inspect_all_tables():
    """Inspect all tables and their column types"""
    engine = get_database_connection()
    inspector = inspect(engine)
    
    # Get all table names
    table_names = inspector.get_table_names()
    
    print(f"Found {len(table_names)} tables in database:")
    print("=" * 60)
    
    all_tables_info = {}
    
    for table_name in table_names:
        print(f"\n📋 Table: {table_name}")
        print("-" * 40)
        
        # Get columns for this table
        columns = inspector.get_columns(table_name)
        
        table_info = {
            "table_name": table_name,
            "columns": []
        }
        
        for column in columns:
            col_name = column['name']
            col_type = str(column['type'])
            nullable = column.get('nullable', True)
            primary_key = column.get('primary_key', False)
            
            print(f"  • {col_name}: {col_type} {'(PK)' if primary_key else ''} {'(NULL)' if nullable else '(NOT NULL)'}")
            
            table_info["columns"].append({
                "name": col_name,
                "type": col_type,
                "nullable": nullable,
                "primary_key": primary_key
            })
        
        all_tables_info[table_name] = table_info
    
    return all_tables_info

def get_sample_data_for_tables():
    """Get sample data for each table"""
    engine = get_database_connection()
    
    print(f"\n📊 Sample Data (first 3 rows):")
    print("=" * 60)
    
    with engine.connect() as conn:
        # Get all table names
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        table_names = [row[0] for row in result.fetchall()]
        
        for table_name in table_names:
            print(f"\n📋 Table: {table_name}")
            print("-" * 40)
            
            try:
                # Get sample data
                sample_query = text(f"SELECT * FROM {table_name} LIMIT 3")
                sample_result = conn.execute(sample_query)
                
                # Get column names
                columns = sample_result.keys()
                print(f"Columns: {', '.join(columns)}")
                
                # Get sample rows
                rows = sample_result.fetchall()
                if rows:
                    print("Sample data:")
                    for i, row in enumerate(rows, 1):
                        print(f"  Row {i}: {dict(zip(columns, row))}")
                else:
                    print("  (No data)")
                    
            except Exception as e:
                print(f"  Error reading table: {e}")

def save_table_info_to_json(all_tables_info: Dict[str, Any], filename: str = "table_schema.json"):
    """Save table information to JSON file"""
    with open(filename, 'w') as f:
        json.dump(all_tables_info, f, indent=2)
    print(f"\n💾 Table schema saved to: {filename}")

def main():
    """Main function"""
    print("🔍 Database Column Type Inspector")
    print("=" * 60)
    
    try:
        # Inspect all tables
        all_tables_info = inspect_all_tables()
        
        # Get sample data
        get_sample_data_for_tables()
        
        # Save to JSON file
        save_table_info_to_json(all_tables_info)
        
        print(f"\n✅ Inspection complete! Found {len(all_tables_info)} tables.")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 