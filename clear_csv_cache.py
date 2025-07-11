#!/usr/bin/env python3
"""
Script to clear all cached data related to CSV tables and files
"""

import os
import glob
from sqlalchemy import create_engine, text
import json

def clear_csv_cache():
    """Clear all cached data related to CSV tables and files"""
    print("🧹 Clearing CSV and file cache...")
    print("=" * 50)
    
    # Clear database cache for CSV tables
    clear_database_cache()
    
    # Clear file system cache
    clear_filesystem_cache()
    
    # Clear any JSON cache files
    clear_json_cache()
    
    print("✅ Cache clearing complete!")

def clear_database_cache():
    """Clear database cache related to CSV tables"""
    print("\n🗄️  Clearing database cache...")
    
    DATABASE_URL = "sqlite:///./test.db"
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        try:
            # Clear any cached table metadata
            print("  • Clearing table metadata cache...")
            
            # Delete any remaining CSV table references
            csv_tables_query = text("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'csv_%'")
            result = conn.execute(csv_tables_query)
            csv_tables = [row[0] for row in result.fetchall()]
            
            if csv_tables:
                print(f"  • Found {len(csv_tables)} CSV tables to clean up")
                for table in csv_tables:
                    try:
                        drop_query = text(f"DROP TABLE {table}")
                        conn.execute(drop_query)
                        print(f"    ✅ Dropped table: {table}")
                    except Exception as e:
                        print(f"    ⚠️  Could not drop {table}: {e}")
            else:
                print("  • No CSV tables found in database")
            
            conn.commit()
            
        except Exception as e:
            print(f"  ❌ Database cache clear error: {e}")

def clear_filesystem_cache():
    """Clear file system cache files"""
    print("\n📁 Clearing filesystem cache...")
    
    # Common cache file patterns
    cache_patterns = [
        "*.cache",
        "*.tmp",
        "*.temp",
        "cache/*",
        "temp/*",
        "tmp/*",
        "*.json.bak",
        "*.csv.bak"
    ]
    
    cleared_files = []
    
    for pattern in cache_patterns:
        try:
            files = glob.glob(pattern, recursive=True)
            for file_path in files:
                if os.path.isfile(file_path):
                    try:
                        os.remove(file_path)
                        cleared_files.append(file_path)
                        print(f"  ✅ Deleted: {file_path}")
                    except Exception as e:
                        print(f"  ⚠️  Could not delete {file_path}: {e}")
        except Exception as e:
            print(f"  ⚠️  Error with pattern {pattern}: {e}")
    
    if cleared_files:
        print(f"  📊 Cleared {len(cleared_files)} cache files")
    else:
        print("  ℹ️  No cache files found")

def clear_json_cache():
    """Clear JSON cache files"""
    print("\n📄 Clearing JSON cache files...")
    
    # Look for JSON files that might be cache
    json_files = [
        "table_schema.json",
        "cache_data.json",
        "csv_cache.json",
        "file_cache.json"
    ]
    
    cleared_json = []
    
    for json_file in json_files:
        if os.path.exists(json_file):
            try:
                os.remove(json_file)
                cleared_json.append(json_file)
                print(f"  ✅ Deleted: {json_file}")
            except Exception as e:
                print(f"  ⚠️  Could not delete {json_file}: {e}")
    
    if cleared_json:
        print(f"  📊 Cleared {len(cleared_json)} JSON cache files")
    else:
        print("  ℹ️  No JSON cache files found")

def clear_memory_cache():
    """Clear any in-memory cache"""
    print("\n🧠 Clearing memory cache...")
    
    # Clear Python cache directories
    cache_dirs = [
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache"
    ]
    
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            try:
                import shutil
                shutil.rmtree(cache_dir)
                print(f"  ✅ Cleared: {cache_dir}")
            except Exception as e:
                print(f"  ⚠️  Could not clear {cache_dir}: {e}")

if __name__ == "__main__":
    clear_csv_cache()
    clear_memory_cache()
    print("\n🎉 All cache clearing operations completed!") 