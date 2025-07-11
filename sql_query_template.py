#!/usr/bin/env python3
"""
SQLite Query Template

Simple template for executing custom SQLite queries.
Just replace the query in the main() function with your own SQL.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db import SessionLocal
from services.sqlite_query_service import SQLiteQueryService

def execute_custom_query(query):
    """
    Execute a custom SQLite query
    
    Args:
        query (str): Your SQL query
    
    Returns:
        dict: Query result with success status and data
    """
    print("🔍 Executing Custom SQLite Query")
    print("=" * 50)
    print(f"📝 Query: {query}")
    print()
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Create query service
        query_service = SQLiteQueryService(db)
        
        # Execute the query
        result = query_service.query("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        
        if result["success"]:
            data = result["data"]
            print("✅ Query executed successfully!")
            print(f"📊 Rows returned: {data.get('row_count', len(data.get('rows', [])))}")
            print(f"🗂️  Columns: {data.get('columns', [])}")
            
            # Show results
            rows = data.get('rows', [])
            if rows:
                print(f"\n📋 Results:")
                print("-" * 60)
                
                # Show column headers
                columns = data.get('columns', [])
                if columns:
                    header = " | ".join(f"{col:<15}" for col in columns)
                    print(header)
                    print("-" * len(header))
                
                # Show data rows (limit to first 20 for readability)
                for i, row in enumerate(rows[:20], 1):
                    if isinstance(row, (list, tuple)):
                        row_str = " | ".join(f"{str(cell):<15}" for cell in row)
                    elif isinstance(row, dict):
                        row_str = " | ".join(f"{str(row.get(col, '')):<15}" for col in columns)
                    else:
                        row_str = str(row)
                    
                    print(f"{row_str}")
                
                if len(rows) > 20:
                    print(f"... and {len(rows) - 20} more rows")
            else:
                print(f"\n📋 No data returned (query may have been an UPDATE/DELETE/CREATE)")
            
            return result
            
        else:
            print(f"❌ Query failed!")
            print(f"🚨 Error: {result.get('error', 'Unknown error')}")
            return result
            
    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}
    finally:
        db.close()

def main():
    """
    Main function - PUT YOUR SQL QUERY HERE
    """
    
    # 🔥 DYNAMICALLY FIND AND DROP ALL CSV TABLES 🔥
    print("🔍 Finding all CSV tables in the database...")
    
    # First, get all existing CSV tables
    discovery_query = "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'csv_table_%' ORDER BY name"
    discovery_result = execute_custom_query(discovery_query)
    
    if not discovery_result["success"]:
        print(f"❌ Failed to discover CSV tables: {discovery_result.get('error', 'Unknown error')}")
        return
    
    tables_to_drop = []
    csv_tables = discovery_result["data"]["rows"]
    
    for table_row in csv_tables:
        # Handle both dict and tuple/list formats safely
        if isinstance(table_row, dict):
            table_name = table_row.get('name', 'Unknown')
        elif isinstance(table_row, (list, tuple)) and len(table_row) > 0:
            table_name = table_row[0]
        else:
            table_name = str(table_row)
        
        if table_name != 'Unknown' and table_name.startswith('csv_table_'):
            tables_to_drop.append(table_name)
    
    if not tables_to_drop:
        print("c✅ No CSV tables found to delete!")
        return
    
    print(f"🗑️  Found {len(tables_to_drop)} CSV tables to drop:")
    for i, table_name in enumerate(tables_to_drop, 1):
        print(f"   {i}. {table_name}")
    
    print()
    print(f"🗑️  Dropping {len(tables_to_drop)} CSV tables...")
    print("=" * 60)
    
    deleted_count = 0
    failed_count = 0
    
    for i, table_name in enumerate(tables_to_drop, 1):
        print(f"\n🗑️  [{i}/{len(tables_to_drop)}] Dropping table: {table_name}")
        your_query = f'DROP TABLE IF EXISTS "{table_name}"'
        result = execute_custom_query(your_query)
        
        if result["success"]:
            deleted_count += 1
            print(f"   ✅ Successfully dropped {table_name}")
        else:
            failed_count += 1
            print(f"   ❌ Failed to drop {table_name}: {result.get('error', 'Unknown error')}")
    
    # Summary
    print(f"\n📊 Deletion Summary:")
    print(f"   ✅ Successfully deleted: {deleted_count} tables")
    print(f"   ❌ Failed to delete: {failed_count} tables")
    print(f"   📈 Success rate: {(deleted_count / len(tables_to_drop) * 100):.1f}%")
    
    # Verify all tables are gone
    print(f"\n🔍 Verifying all tables are deleted...")
    table_names_quoted = "', '".join(tables_to_drop)
    verification_query = f"""
    SELECT name FROM sqlite_master 
    WHERE type='table' AND name IN ('{table_names_quoted}')
    """
    
    result = execute_custom_query(verification_query)
    if result["success"]:
        remaining_tables = result["data"]["rows"]
        if len(remaining_tables) == 0:
            print("✅ All specified tables have been successfully deleted!")
        else:
            print(f"⚠️  {len(remaining_tables)} tables still exist:")
            for table in remaining_tables:
                # Handle both dict and tuple/list formats safely
                if isinstance(table, dict):
                    table_name = table.get('name', 'Unknown')
                elif isinstance(table, (list, tuple)) and len(table) > 0:
                    table_name = table[0]
                else:
                    table_name = str(table)
                print(f"   • {table_name}")
    
    # Show all remaining CSV tables
    print(f"\n📊 Checking all remaining CSV tables...")
    remaining_csv_query = "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%csv%' ORDER BY name"
    result = execute_custom_query(remaining_csv_query)
    
    if result["success"]:
        remaining_csv = result["data"]["rows"]
        print(f"\n📋 Remaining CSV tables: {len(remaining_csv)}")
        if remaining_csv:
            for table in remaining_csv:
                # Handle both dict and tuple/list formats safely
                if isinstance(table, dict):
                    table_name = table.get('name', 'Unknown')
                elif isinstance(table, (list, tuple)) and len(table) > 0:
                    table_name = table[0]
                else:
                    table_name = str(table)
                print(f"   • {table_name}")
        else:
            print("🎉 No CSV tables remaining in database!")

# Example queries you can try:
def example_queries():
    """
    Some example queries you can use
    """
    examples = {
        "List all tables": "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name",
        
        "List CSV tables only": "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%csv%' ORDER BY name",
        
        "Count rows in content table": "SELECT COUNT(*) as total_rows FROM content",
        
        "Show table structure": "PRAGMA table_info(content)",
        
        "Delete all CSV tables": "DROP TABLE IF EXISTS csv_table_example",
        
        "Show recent content": "SELECT * FROM content ORDER BY timestamp DESC LIMIT 10",
        
        "Count by category": "SELECT category, COUNT(*) as count FROM content GROUP BY category",
        
        "Database size info": """
        SELECT 
            name as table_name,
            (SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name = m.name) as exists
        FROM sqlite_master m 
        WHERE type='table'
        """,
        
        "Show entities": "SELECT * FROM entity LIMIT 10"
    }
    
    print("\n💡 Example Queries You Can Try:")
    print("=" * 50)
    for description, query in examples.items():
        print(f"\n📝 {description}:")
        print(f"   {query}")

if __name__ == "__main__":
    print("🗃️  Custom SQLite Query Executor")
    print("=" * 50)
    print("💡 Edit the 'your_query' variable in main() to run your own SQL")
    print()
    
    try:
        # Run your query
        main()
        
        # Show examples
        show_examples = input(f"\n❓ Want to see example queries? (y/n): ").strip().lower()
        if show_examples in ['y', 'yes']:
            example_queries()
            
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Query execution interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc() 