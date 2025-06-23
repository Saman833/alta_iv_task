import sqlite3

def clear_alembic_version():
    try:
        # Connect to the database
        conn = sqlite3.connect('test.db')
        cursor = conn.cursor()
        
        # Drop the alembic_version table if it exists
        cursor.execute("DROP TABLE IF EXISTS alembic_version;")
        
        # Commit the changes
        conn.commit()
        print("Successfully cleared alembic_version table")
        
    except Exception as e:
        print(f"Error: {e}")
        
    finally:
        # Close the connection
        if conn:
            conn.close()

if __name__ == "__main__":
    clear_alembic_version() 