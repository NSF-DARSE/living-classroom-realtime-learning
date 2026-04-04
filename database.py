import sqlite3 # imports SQLite library - used to create and manage local DB

DB_NAME = "birds.db"

# function to open a connection to the DB
def get_connection():
    return sqlite3.connect(DB_NAME)

# function to create table if not already present
def create_table():
    conn = get_connection()
    cursor = conn.cursor() # cursor lets you run SQL queries

    # SQL command to create table only if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS detections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        station_id INTEGER,
        species TEXT,
        timestamp TEXT UNIQUE,
        confidence REAL
    )
    """)

    conn.commit() #saves changes to DB
    conn.close() #closes DB connection

if __name__ == "__main__":
    create_table()
    print("Database and table created.")