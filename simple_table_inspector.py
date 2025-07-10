#!/usr/bin/env python3
"""
Simple SQLite Table Inspector
Shows tables, metadata, and sample data
"""

import sqlite3
from datetime import datetime
import json

def inspect_database():
    """Inspect the SQLite database"""
    print("🔍 SQLite Database Inspector")
    print("=" * 60)
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    print()
    
    try:
        # Connect to the database
        conn = sqlite3.connect("test.db")  # Based on your config
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"📊 Found {len(tables)} tables in database")
        print()
        
        # Separate tables by type
        csv_tables = []
        system_tables = []
        other_tables = []
        
        for (table_name,) in tables:
            if table_name.startswith('csv_table_'):
                csv_tables.append(table_name)
            elif table_name in ['file', 'folder', 'table', 'content', 'entity']:
                system_tables.append(table_name)
            else:
                other_tables.append(table_name)
        
        # Show CSV tables
        if csv_tables:
            print("📈 CSV TABLES (Analytics Data)")
            print("-" * 40)
            for table_name in csv_tables:
                inspect_table(cursor, table_name, show_sample=True)
        
        # Show system tables
        if system_tables:
            print("\n🏗️  SYSTEM TABLES (Application Data)")
            print("-" * 40)
            for table_name in system_tables:
                inspect_table(cursor, table_name, show_sample=False)
        
        # Show other tables
        if other_tables:
            print("\n📋 OTHER TABLES")
            print("-" * 40)
            for table_name in other_tables:
                inspect_table(cursor, table_name, show_sample=False)
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def inspect_table(cursor, table_name, show_sample=False):
    """Inspect a specific table"""
    print(f"📋 TABLE: {table_name}")
    print("-" * 30)
    
    try:
        # Get table info
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        
        print(f"📝 Columns ({len(columns)}):")
        column_names = []
        for col in columns:
            cid, name, type_name, notnull, default_value, pk = col
            column_names.append(name)
            nullable = "NOT NULL" if notnull else "NULL"
            primary_key = "🔑 PRIMARY KEY" if pk else ""
            default = f"DEFAULT {default_value}" if default_value else ""
            print(f"  • {name}: {type_name} {nullable} {primary_key} {default}")
        
        # Get row count
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            print(f"📊 Row Count: {row_count}")
        except Exception as e:
            print(f"⚠️  Could not get row count: {e}")
        
        # Show sample data for CSV tables
        if show_sample and column_names:
            try:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 2")
                rows = cursor.fetchall()
                
                if rows:
                    print(f"📄 Sample Data (first 2 rows):")
                    for i, row in enumerate(rows, 1):
                        print(f"  Row {i}:")
                        for j, value in enumerate(row):
                            if j < len(column_names):
                                # Truncate long values
                                display_value = str(value)[:60] + "..." if len(str(value)) > 60 else str(value)
                                print(f"    {column_names[j]}: {display_value}")
                        print()
            except Exception as e:
                print(f"⚠️  Could not get sample data: {e}")
        
        print()
        
    except Exception as e:
        print(f"❌ Error inspecting table {table_name}: {e}")
        print()

def show_table_summary():
    """Show a summary of all tables"""
    print("📊 DATABASE SUMMARY")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect("test.db")
        cursor = conn.cursor()
        
        # Get all tables with row counts
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        total_rows = 0
        table_stats = []
        
        for (table_name,) in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cursor.fetchone()[0]
                total_rows += row_count
                table_stats.append((table_name, row_count))
            except:
                table_stats.append((table_name, "Error"))
        
        # Sort by row count (descending)
        table_stats.sort(key=lambda x: x[1] if isinstance(x[1], int) else 0, reverse=True)
        
        print(f"📈 Total Tables: {len(tables)}")
        print(f"📊 Total Rows: {total_rows}")
        print()
        
        print("📋 Tables by Size:")
        for table_name, row_count in table_stats:
            table_type = "CSV" if table_name.startswith('csv_table_') else "System"
            print(f"  • {table_name}: {row_count} rows ({table_type})")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def inspect_latest_csv_table():
    """Inspect the most recently created CSV table"""
    print("🔍 LATEST CSV TABLE INSPECTOR")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect("test.db")
        cursor = conn.cursor()
        
        # Get CSV tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'csv_table_%';")
        csv_tables = cursor.fetchall()
        
        if not csv_tables:
            print("❌ No CSV tables found")
            return
        
        # Get the latest table (assuming the UUID contains timestamp info)
        latest_table = csv_tables[-1][0]  # Get the last one
        
        print(f"📋 Latest CSV Table: {latest_table}")
        print("-" * 40)
        
        # Get table info
        cursor.execute(f"PRAGMA table_info({latest_table});")
        columns = cursor.fetchall()
        
        column_names = []
        print(f"📝 Columns ({len(columns)}):")
        for col in columns:
            cid, name, type_name, notnull, default_value, pk = col
            column_names.append(name)
            nullable = "NOT NULL" if notnull else "NULL"
            primary_key = "🔑 PRIMARY KEY" if pk else ""
            print(f"  • {name}: {type_name} {nullable} {primary_key}")
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {latest_table}")
        row_count = cursor.fetchone()[0]
        print(f"📊 Total Rows: {row_count}")
        print()
        
        # Show sample data
        cursor.execute(f"SELECT * FROM {latest_table} LIMIT 3")
        rows = cursor.fetchall()
        
        if rows:
            print(f"📄 Sample Data (first 3 rows):")
            for i, row in enumerate(rows, 1):
                print(f"  Row {i}:")
                for j, value in enumerate(row):
                    if j < len(column_names):
                        # Truncate long values
                        display_value = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                        print(f"    {column_names[j]}: {display_value}")
                print()
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Starting SQLite Database Inspection")
    print("=" * 60)
    
    # Show summary first
    show_table_summary()
    print()
    
    # Inspect latest CSV table
    inspect_latest_csv_table()
    print()
    
    # Full inspection
    inspect_database()
    
    print("=" * 60)
    print("✅ Database inspection completed!")
    print()
    print("💡 Key Insights:")
    print("• CSV tables contain your imported analytics data")
    print("• Each CSV upload creates a new table with unique ID")
    print("• Use 'row_id' for unique row identification")
    print("• Original CSV 'id' column is preserved for analytics")
    print("• System tables manage files, folders, and metadata") 