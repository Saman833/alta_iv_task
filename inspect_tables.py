#!/usr/bin/env python3
"""
Database Table Inspector
Inspect all tables and their metadata in the database
"""

import sqlite3
from pathlib import Path
import json
from datetime import datetime
from sqlalchemy import create_engine, MetaData, inspect
from sqlalchemy.orm import sessionmaker
from config import config

def get_database_connection():
    """Get database connection"""
    try:
        # Try SQLAlchemy first
        engine = create_engine(config.SQL_URI)
        return engine, None
    except Exception as e:
        print(f"SQLAlchemy connection failed: {e}")
        # Fallback to direct SQLite connection
        try:
            conn = sqlite3.connect("database.db")
            return None, conn
        except Exception as e2:
            print(f"Direct SQLite connection failed: {e2}")
            return None, None

def inspect_database_tables():
    """Inspect all tables in the database"""
    print("🔍 Database Table Inspector")
    print("=" * 60)
    
    engine, conn = get_database_connection()
    
    if engine:
        inspect_with_sqlalchemy(engine)
    elif conn:
        inspect_with_sqlite(conn)
    else:
        print("❌ Could not connect to database")
        return

def inspect_with_sqlalchemy(engine):
    """Inspect database using SQLAlchemy"""
    print("🔧 Using SQLAlchemy Inspector")
    print("-" * 40)
    
    try:
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        
        print(f"📊 Found {len(table_names)} tables in database")
        print()
        
        for table_name in table_names:
            print(f"📋 TABLE: {table_name}")
            print("-" * 30)
            
            # Get columns
            columns = inspector.get_columns(table_name)
            print(f"📝 Columns ({len(columns)}):")
            for col in columns:
                nullable = "NULL" if col['nullable'] else "NOT NULL"
                primary_key = "PRIMARY KEY" if col.get('primary_key', False) else ""
                print(f"  • {col['name']}: {col['type']} {nullable} {primary_key}")
            
            # Get indexes
            indexes = inspector.get_indexes(table_name)
            if indexes:
                print(f"🔍 Indexes ({len(indexes)}):")
                for idx in indexes:
                    unique = "UNIQUE" if idx['unique'] else ""
                    print(f"  • {idx['name']}: {idx['column_names']} {unique}")
            
            # Get foreign keys
            foreign_keys = inspector.get_foreign_keys(table_name)
            if foreign_keys:
                print(f"🔗 Foreign Keys ({len(foreign_keys)}):")
                for fk in foreign_keys:
                    print(f"  • {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
            
            # Get row count
            try:
                with engine.connect() as connection:
                    result = connection.execute(f"SELECT COUNT(*) FROM {table_name}")
                    row_count = result.scalar()
                    print(f"📊 Row Count: {row_count}")
            except Exception as e:
                print(f"⚠️  Could not get row count: {e}")
            
            print()
            
    except Exception as e:
        print(f"❌ Error inspecting with SQLAlchemy: {e}")

def inspect_with_sqlite(conn):
    """Inspect database using direct SQLite connection"""
    print("🔧 Using Direct SQLite Connection")
    print("-" * 40)
    
    try:
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"📊 Found {len(tables)} tables in database")
        print()
        
        for (table_name,) in tables:
            print(f"📋 TABLE: {table_name}")
            print("-" * 30)
            
            # Get table info
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            print(f"📝 Columns ({len(columns)}):")
            for col in columns:
                cid, name, type_name, notnull, default_value, pk = col
                nullable = "NOT NULL" if notnull else "NULL"
                primary_key = "PRIMARY KEY" if pk else ""
                default = f"DEFAULT {default_value}" if default_value else ""
                print(f"  • {name}: {type_name} {nullable} {primary_key} {default}")
            
            # Get indexes
            cursor.execute(f"PRAGMA index_list({table_name});")
            indexes = cursor.fetchall()
            
            if indexes:
                print(f"🔍 Indexes ({len(indexes)}):")
                for idx in indexes:
                    seq, name, unique, origin, partial = idx
                    unique_str = "UNIQUE" if unique else ""
                    print(f"  • {name}: {unique_str}")
            
            # Get foreign keys
            cursor.execute(f"PRAGMA foreign_key_list({table_name});")
            foreign_keys = cursor.fetchall()
            
            if foreign_keys:
                print(f"🔗 Foreign Keys ({len(foreign_keys)}):")
                for fk in foreign_keys:
                    id, seq, table, from_col, to_col, on_update, on_delete, match = fk
                    print(f"  • {from_col} -> {table}.{to_col}")
            
            # Get row count
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cursor.fetchone()[0]
                print(f"📊 Row Count: {row_count}")
            except Exception as e:
                print(f"⚠️  Could not get row count: {e}")
            
            print()
            
    except Exception as e:
        print(f"❌ Error inspecting with SQLite: {e}")
    finally:
        conn.close()

def inspect_csv_tables():
    """Specifically inspect CSV-generated tables"""
    print("📊 CSV Tables Inspector")
    print("=" * 60)
    
    engine, conn = get_database_connection()
    
    if engine:
        try:
            inspector = inspect(engine)
            table_names = inspector.get_table_names()
            
            # Filter CSV tables
            csv_tables = [name for name in table_names if name.startswith('csv_table_')]
            
            print(f"📈 Found {len(csv_tables)} CSV tables")
            print()
            
            for table_name in csv_tables:
                print(f"📋 CSV TABLE: {table_name}")
                print("-" * 40)
                
                # Get columns
                columns = inspector.get_columns(table_name)
                print(f"📝 Columns ({len(columns)}):")
                for col in columns:
                    print(f"  • {col['name']}: {col['type']}")
                
                # Get sample data
                try:
                    with engine.connect() as connection:
                        result = connection.execute(f"SELECT * FROM {table_name} LIMIT 3")
                        rows = result.fetchall()
                        
                        if rows:
                            print(f"📄 Sample Data (first 3 rows):")
                            column_names = [col['name'] for col in columns]
                            for i, row in enumerate(rows, 1):
                                print(f"  Row {i}:")
                                for j, value in enumerate(row):
                                    if j < len(column_names):
                                        # Truncate long values
                                        display_value = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                                        print(f"    {column_names[j]}: {display_value}")
                                print()
                        
                        # Get total count
                        result = connection.execute(f"SELECT COUNT(*) FROM {table_name}")
                        row_count = result.scalar()
                        print(f"📊 Total Rows: {row_count}")
                        
                except Exception as e:
                    print(f"⚠️  Could not get sample data: {e}")
                
                print()
                
        except Exception as e:
            print(f"❌ Error inspecting CSV tables: {e}")
    
    elif conn:
        try:
            cursor = conn.cursor()
            
            # Get CSV tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'csv_table_%';")
            csv_tables = cursor.fetchall()
            
            print(f"📈 Found {len(csv_tables)} CSV tables")
            print()
            
            for (table_name,) in csv_tables:
                print(f"📋 CSV TABLE: {table_name}")
                print("-" * 40)
                
                # Get columns
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                
                print(f"📝 Columns ({len(columns)}):")
                column_names = []
                for col in columns:
                    cid, name, type_name, notnull, default_value, pk = col
                    column_names.append(name)
                    print(f"  • {name}: {type_name}")
                
                # Get sample data
                try:
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
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
                    
                    # Get total count
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    row_count = cursor.fetchone()[0]
                    print(f"📊 Total Rows: {row_count}")
                    
                except Exception as e:
                    print(f"⚠️  Could not get sample data: {e}")
                
                print()
                
        except Exception as e:
            print(f"❌ Error inspecting CSV tables: {e}")
        finally:
            conn.close()

def inspect_system_tables():
    """Inspect system tables (files, folders, tables)"""
    print("🏗️  System Tables Inspector")
    print("=" * 60)
    
    engine, conn = get_database_connection()
    
    system_tables = ['file', 'folder', 'table']
    
    if engine:
        try:
            inspector = inspect(engine)
            table_names = inspector.get_table_names()
            
            for table_name in system_tables:
                if table_name in table_names:
                    print(f"📋 SYSTEM TABLE: {table_name}")
                    print("-" * 30)
                    
                    # Get columns
                    columns = inspector.get_columns(table_name)
                    print(f"📝 Columns ({len(columns)}):")
                    for col in columns:
                        nullable = "NULL" if col['nullable'] else "NOT NULL"
                        primary_key = "PRIMARY KEY" if col.get('primary_key', False) else ""
                        print(f"  • {col['name']}: {col['type']} {nullable} {primary_key}")
                    
                    # Get row count
                    try:
                        with engine.connect() as connection:
                            result = connection.execute(f"SELECT COUNT(*) FROM {table_name}")
                            row_count = result.scalar()
                            print(f"📊 Row Count: {row_count}")
                    except Exception as e:
                        print(f"⚠️  Could not get row count: {e}")
                    
                    print()
                else:
                    print(f"⚠️  System table '{table_name}' not found")
                    
        except Exception as e:
            print(f"❌ Error inspecting system tables: {e}")

if __name__ == "__main__":
    print("🚀 Starting Database Inspection")
    print("=" * 60)
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Inspect all tables
    inspect_database_tables()
    print()
    
    # Inspect CSV tables specifically
    inspect_csv_tables()
    print()
    
    # Inspect system tables
    inspect_system_tables()
    print()
    
    print("=" * 60)
    print("✅ Database inspection completed!")
    print()
    print("💡 Usage Tips:")
    print("• CSV tables store your imported data")
    print("• System tables manage files, folders, and metadata")
    print("• Use row_id for unique identification in CSV tables")
    print("• Original CSV id column is preserved for analytics") 