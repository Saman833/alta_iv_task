
"""


This file is used to check the database and print the content of the database
do not use it in production


"""

import sqlite3
from datetime import datetime

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
            cursor.execute("SELECT id, source_id, content_type, content_data, content_html, source, timestamp FROM content LIMIT 5;")
            rows = cursor.fetchall()
            print("\nRecent content records:")
            for row in rows:
                print(f"  ID: {row[0]}")
                print(f"  Source ID: {row[1]}")
                print(f"  Type: {row[2]}")
                print(f"  Content Data: '{row[3]}'")
                print(f"  Content HTML: '{row[4]}'")
                print(f"  Source: {row[5]}")
                print(f"  Timestamp: {row[6]}")
                print("  " + "-"*30)
    except sqlite3.OperationalError as e:
        print(f"Error reading content table: {e}")
    
    conn.close()

if __name__ == "__main__":
    check_database() 