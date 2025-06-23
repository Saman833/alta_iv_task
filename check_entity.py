"""


This file is used to check the entity table and print the content of the entity table
do not use it in production


"""

import sqlite3
from datetime import datetime
import html

def check_entity_table():
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables in database:")
    for table in tables:
        print(f"  - {table[0]}")
    
    print("\n" + "="*50)
    
    try:
        cursor.execute("SELECT COUNT(*) FROM entity;")
        count = cursor.fetchone()[0]
        print(f"Entity table has {count} records")
        
        if count > 0:
            cursor.execute("SELECT id, content_id, entity_type, entity_value, created_at FROM entity LIMIT 15;")
            rows = cursor.fetchall()
            print("\nRecent entity records:")
            for row in rows:
                print(f"  ID: {row[0]}")
                print(f"  Content ID: {row[1]}")
                print(f"  Entity Type: {row[2]}")
                # Decode HTML entities in entity_value
                decoded_value = html.unescape(row[3]) if row[3] else ""
                print(f"  Entity Value: '{decoded_value}'")
                print(f"  Created At: {row[4]}")
                print("  " + "-"*30)
        else:
            print("No records found in entity table")
            
    except sqlite3.OperationalError as e:
        print(f"Error reading entity table: {e}")
    
    conn.close()

if __name__ == "__main__":
    check_entity_table() 