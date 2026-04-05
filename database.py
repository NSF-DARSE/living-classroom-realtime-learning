import sqlite3

DB_NAME = "birds.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def create_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS detections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        station_id INTEGER,
        species TEXT,
        timestamp TEXT UNIQUE,
        confidence REAL
    )
    """)

    try:
        cursor.execute("ALTER TABLE detections ADD COLUMN lat REAL")
        print("Added lat column")
    except sqlite3.OperationalError as e:
        print("lat column:", e)

    try:
        cursor.execute("ALTER TABLE detections ADD COLUMN lon REAL")
        print("Added lon column")
    except sqlite3.OperationalError as e:
        print("lon column:", e)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_table()
    print("Database and table created.")