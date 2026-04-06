import sqlite3

conn = sqlite3.connect("birds.db")
cursor = conn.cursor()

rows = cursor.execute("PRAGMA table_info(detections)").fetchall()
for row in rows:
    print(row)

conn.close()