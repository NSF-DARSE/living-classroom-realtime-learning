import sqlite3

conn = sqlite3.connect("birds.db")
cursor = conn.cursor()

rows = cursor.execute("SELECT * FROM detections LIMIT 10").fetchall()

for r in rows:
    print(f"""
ID: {r[0]}
Station: {r[1]}
Species: {r[2]}
Time: {r[3]}
Confidence: {r[4]}
------------------------
""")

conn.close()