import requests # for API calls
import sqlite3
import time

STATION_ID = 14218
URL = f"https://app.birdweather.com/api/v1/stations/{STATION_ID}/detections"

DB_NAME = "birds.db"

def save_detection(species, timestamp, confidence):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        cursor.execute("""
        INSERT INTO detections (station_id, species, timestamp, confidence)
        VALUES (?, ?, ?, ?)
        """, (STATION_ID, species, timestamp, confidence))

        conn.commit()
        print("Saved:", species, timestamp)

    except sqlite3.IntegrityError:
        # duplicate timestamp → skip
        print("Duplicate skipped:", timestamp)

    conn.close()


while True:
    try:
        r = requests.get(URL, timeout=20)
        r.raise_for_status()
        data = r.json()

        detections = data.get("detections", [])

        for d in detections:
            species = (d.get("species") or {}).get("commonName") or "Unknown"
            ts = d.get("timestamp")
            conf = d.get("confidence")

            save_detection(species, ts, conf)

    except Exception as e:
        print("Error:", e)

    time.sleep(10)
