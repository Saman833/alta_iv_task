import sqlite3

def drop_all_tables():
    try:
        # Connect to the database
        conn = sqlite3.connect('test.db')
        cursor = conn.cursor()
        
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        # Drop each table
        for table in tables:
            table_name = table[0]
            cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
            print(f"Dropped table: {table_name}")
        
        # Commit the changes
        conn.commit()
        print("Successfully dropped all tables")
        
    except Exception as e:
        print(f"Error: {e}")
        
    finally:
        # Close the connection
        if conn:
            conn.close()

if __name__ == "__main__":
    drop_all_tables() 