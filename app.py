from flask import Flask, jsonify, render_template_string # flask framework
import sqlite3
# flask - main app object
# jsonify - returns json response
# render_template_string - renders HTML stored as a string (?)



# --- this is doing api calling ---
# import requests #for API calling
# STATION_ID = 14218
# API_URL = f"https://app.birdweather.com/api/v1/stations/{STATION_ID}/detections"


#Creating  the Flask application instance.
app = Flask(__name__) #__name__ tells Flask where this file is located.

DB_NAME = "birds.db"

# Simple HTML page (dashboard)
HTML = """
<!doctype html>
<html>
<head>
  <title>BirdWeather Live Dashboard</title>
  <meta charset="utf-8" />
  <style>
  body { font-family: Arial, sans-serif; margin: 24px; }
  .big { font-size: 22px; font-weight: 700; }
  .muted { color: #666; margin-top: 6px; }
  code { background: #f6f6f6; padding: 2px 6px; border-radius: 6px; }

  /* NEW: cards */
  #cards { margin-top: 14px; max-width: 720px; }
  .dcard { padding: 12px 14px; border: 1px solid #ddd; border-radius: 12px; margin-bottom: 10px; }
  .dtitle { font-weight: 700; font-size: 16px; }
  .dmeta { color: #666; margin-top: 4px; font-size: 13px; }

  .summary-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(150px, 1fr));
  gap: 12px;
  max-width: 900px;
  margin-top: 16px;
  margin-bottom: 18px;
  }
  .scard {
    padding: 14px;
    border: 1px solid #ddd;
    border-radius: 12px;
    background: #fafafa;
  }
  .slabel {
    font-size: 13px;
    color: #666;
    margin-bottom: 6px;
  }
  .svalue {
    font-size: 20px;
    font-weight: 700;
    white-space: nowrap;
  }
</style>
</head>
<body>
  <h2>BirdWeather Live Dashboard</h2>
  <div class="summary-grid">
    <div class="scard">
      <div class="slabel">Total Detections</div>
      <div class="svalue" id="totalDetections">-</div>
    </div>
    <div class="scard">
      <div class="slabel">Unique Species</div>
      <div class="svalue" id="uniqueSpecies">-</div>
    </div>
    <div class="scard">
      <div class="slabel">Top Species</div>
      <div class="svalue" id="topSpecies">-</div>
    </div>
    <div class="scard">
      <div class="slabel">Latest Detection</div>
      <div class="svalue" id="latestTimestamp">-</div>
    </div>
  </div>

  <div class="big">Latest 5 detections</div>
    <div id="cards"></div>
    <div class="muted" id="updated"></div>
  </div>

  <script>
    async function refresh() {
      try {
        const res = await fetch("/latest");
        const data = await res.json();
        if (data.ok) {
        const cardsHtml = data.rows.map((x, i) => `
            <div class="dcard">
            <div class="dtitle">${x.species}</div>
            <div class="dmeta">${formatTime(x.timestamp)}</div>
            </div>
        `).join("");

        document.getElementById("cards").innerHTML = cardsHtml;

        document.getElementById("updated").textContent =
            `Last updated: ${new Date().toLocaleTimeString()}`;
        } else {
        document.getElementById("cards").innerHTML =
            `<div class="dcard"><div class="dtitle">API error</div><div class="dmeta">${data.error}</div></div>`;
        }
      } catch (e) {
        document.getElementById("species").textContent = "Network error";
        document.getElementById("meta").textContent = e.toString();
      }
    }


    async function loadSummary() {
      try {
        const res = await fetch("/summary");
        const data = await res.json();

        if (data.ok) {
          document.getElementById("totalDetections").textContent = data.total_detections;
          document.getElementById("uniqueSpecies").textContent = data.unique_species;
          document.getElementById("topSpecies").textContent = data.top_species;
          document.getElementById("latestTimestamp").textContent = formatTime(data.latest_timestamp);
        }
      } catch (e) {
        console.error("Summary error:", e);
      }
    }

    function formatTime(ts) {
      if (!ts) return "";

      const date = new Date(ts);

      return date.toLocaleString(undefined, {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "numeric",
        minute: "2-digit"
      });
    }
    refresh();
    loadSummary();

    setInterval(() => {
      refresh();
      loadSummary();
    }, 10000);

  </script>
</body>
</html>
"""

@app.get("/")
def home():
    return render_template_string(HTML)

@app.get("/latest")
def latest():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        rows = cursor.execute("""
            SELECT species, timestamp, confidence
            FROM detections
            ORDER BY timestamp DESC
            LIMIT 5
        """).fetchall()

        result = []
        for r in rows:
            result.append({
                "species": r[0],
                "timestamp": r[1],
                "confidence": f"{r[2]:.3f}" if r[2] else ""
            })

        conn.close()

        return jsonify(ok=True, rows=result)

    except Exception as e:
        return jsonify(ok=False, error=str(e))
        

    # --- this is for direct api calling ---
    #     r = requests.get(API_URL, timeout=20)
    #     r.raise_for_status()
    #     data = r.json()

    #     detections = data.get("detections", [])[:5]  # top 5 (newest first)
    #     rows = []
    #     for d in detections:
    #         species = (d.get("species") or {}).get("commonName") or "Unknown"
    #         ts = d.get("timestamp") or ""
    #         conf = d.get("confidence")
    #         conf_str = f"{conf:.3f}" if isinstance(conf, (int, float)) else ""
    #         rows.append({"species": species, "timestamp": ts, "confidence": conf_str})

    #     return jsonify(ok=True, rows=rows)

    # except Exception as e:
    #     return jsonify(ok=False, error=str(e))

@app.get("/summary")
def summary():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        total_detections = cursor.execute("""
            SELECT COUNT(*) FROM detections
        """).fetchone()[0]

        unique_species = cursor.execute("""
            SELECT COUNT(DISTINCT species) FROM detections
        """).fetchone()[0]

        top_species_row = cursor.execute("""
            SELECT species, COUNT(*) as cnt
            FROM detections
            GROUP BY species
            ORDER BY cnt DESC
            LIMIT 1
        """).fetchone()

        latest_timestamp_row = cursor.execute("""
            SELECT MAX(timestamp) FROM detections
        """).fetchone()

        conn.close()

        top_species = top_species_row[0] if top_species_row else "N/A"
        latest_timestamp = latest_timestamp_row[0] if latest_timestamp_row and latest_timestamp_row[0] else "N/A"

        return jsonify(
            ok=True,
            total_detections=total_detections,
            unique_species=unique_species,
            top_species=top_species,
            latest_timestamp=latest_timestamp
        )

    except Exception as e:
        return jsonify(ok=False, error=str(e))

if __name__ == "__main__":
    app.run(debug=True)