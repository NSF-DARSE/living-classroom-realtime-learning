from flask import Flask, jsonify, render_template_string, request
from datetime import datetime, timedelta # flask framework
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

def get_filter_condition(filter_value):
    if filter_value == "1h":
        cutoff = (datetime.now().astimezone() - timedelta(hours=1)).isoformat()
        return "WHERE timestamp >= ?", (cutoff,)
    elif filter_value == "today":
        start_of_day = datetime.now().astimezone().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        return "WHERE timestamp >= ?", (start_of_day,)
    else:
        return "", ()

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
  #cards { margin-top: 14px; max-width: 720px; padding: 10px 12px; }
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
  .two-col {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 24px;
    align-items: stretch;
    max-width: 1200px;
  }

  .side-list .dcard {
    margin-bottom: 10px;
  }
  

  .side-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-top: 10px;
  }

  h3 {
    margin-bottom: 10px;
  }

  button.active {
    background-color: #00539f;
    color: white;
    border: none;
  }
</style>
</head>

<body>
  <h2>UD Farm Bird Monitoring Dashboard</h2>
  <p style="color:#666; margin-top:-10px;">
    Real-time bird detections with historical analytics
  </p>

  <div style="margin: 16px 0 18px 0;">
    <button onclick="setFilter('1h')" id="btn-1h">Last 1 Hour</button>
    <button onclick="setFilter('today')" id="btn-today">Today</button>
    <button onclick="setFilter('all')" id="btn-all">All Time</button>
  </div>

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
  
  
  <div class="two-col">

    <!-- LEFT -->
    <div>
      <div class="big">Recent Bird Activity</div>
      <div id="cards"></div>
      <div class="muted" id="updated"></div>
    </div>

    <!-- RIGHT -->
    <div class="side-list">
      <div class="big">Top 5 Species</div>
      <div id="topSpeciesList"></div>
    </div>

  </div>

  









  <script>
    let currentFilter = "all";
    function setFilter(filter) {
      currentFilter = filter;

      // remove active from all buttons
      document.getElementById("btn-1h").classList.remove("active");
      document.getElementById("btn-today").classList.remove("active");
      document.getElementById("btn-all").classList.remove("active");

      // add active to selected button
      document.getElementById(`btn-${filter}`).classList.add("active");

      refresh();
      loadSummary();
      loadTopSpecies();
    }

    async function refresh() {
      try {
        const res = await fetch(`/latest?filter=${currentFilter}`);
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
        const res = await fetch(`/summary?filter=${currentFilter}`);
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

    async function loadTopSpecies() {
      try {
        const res = await fetch(`/top-species?filter=${currentFilter}`);
        const data = await res.json();

        if (data.ok) {
          const html = data.rows.map((x, i) => `
            <div style="margin-bottom: 8px; font-size: 16px; font-weight: 500;">
              ${i + 1}. ${x.species} - ${x.count}
            </div>
          `).join("");

          document.getElementById("topSpeciesList").innerHTML = html;
        }
      } catch (e) {
        console.error("Top species error:", e);
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
    setFilter("all");

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

        filter_value = request.args.get("filter", "all")
        where_clause, params = get_filter_condition(filter_value)

        query = f"""
            SELECT species, timestamp, confidence
            FROM detections
            {where_clause}
            ORDER BY timestamp DESC
            LIMIT 5
        """
        rows = cursor.execute(query, params).fetchall()

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

        filter_value = request.args.get("filter", "all")
        where_clause, params = get_filter_condition(filter_value)

        total_detections = cursor.execute(
            f"SELECT COUNT(*) FROM detections {where_clause}",
            params
        ).fetchone()[0]

        unique_species = cursor.execute(
            f"SELECT COUNT(DISTINCT species) FROM detections {where_clause}",
            params
        ).fetchone()[0]

        top_species_row = cursor.execute(
            f"""
            SELECT species, COUNT(*) as cnt
            FROM detections
            {where_clause}
            GROUP BY species
            ORDER BY cnt DESC
            LIMIT 1
            """,
            params
        ).fetchone()

        latest_timestamp_row = cursor.execute(
            f"SELECT MAX(timestamp) FROM detections {where_clause}",
            params
        ).fetchone()

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
    
@app.get("/top-species")
def top_species():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        filter_value = request.args.get("filter", "all")
        where_clause, params = get_filter_condition(filter_value)

        rows = cursor.execute(
            f"""
            SELECT species, COUNT(*) as cnt
            FROM detections
            {where_clause}
            GROUP BY species
            ORDER BY cnt DESC
            LIMIT 5
            """,
            params
        ).fetchall()

        conn.close()

        result = []
        for r in rows:
            result.append({
                "species": r[0],
                "count": r[1]
            })

        return jsonify(ok=True, rows=result)

    except Exception as e:
        return jsonify(ok=False, error=str(e))    

if __name__ == "__main__":
    app.run(debug=True)