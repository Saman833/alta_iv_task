"""


This file is used to check the database and print the content of the database
do not use it in production


"""

import sqlite3
from datetime import datetime
import html

def check_database():
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables in database:")
    for table in tables:
        print(f"  - {table[0]}")
    
    print("\n" + "="*50)
    
    try:
        cursor.execute("SELECT COUNT(*) FROM content;")
        count = cursor.fetchone()[0]
        print(f"Content table has {count} records")
        
        if count > 0:
            cursor.execute("SELECT id, source_id, content_type, content_data, content_html, source,category, timestamp FROM content LIMIT 12;")
            rows = cursor.fetchall()
            print("\nRecent content records:")
            for row in rows:
                print(f"  ID: {row[0]}")
                print(f"  Source ID: {row[1]}")
                print(f"  Type: {row[2]}")
                # Decode HTML entities in content_data
                decoded_content = html.unescape(row[3]) if row[3] else ""
                print(f"  Content Data: '{decoded_content}'")
                # Decode HTML entities in content_html
                decoded_html = html.unescape(row[4]) if row[4] else ""
                print(f"  Content HTML: '{decoded_html}'")
                print(f"  Source: {row[5]}")
                print(f"  Category: {row[6]}")
                print(f"  Timestamp: {row[7]}")
                print("  " + "-"*30)
    except sqlite3.OperationalError as e:
        print(f"Error reading content table: {e}")
    
    conn.close()

if __name__ == "__main__":
    check_database() 