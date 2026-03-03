from flask import Flask, jsonify, render_template_string # flask framework
# flask - main app object
# jsonify - returns json response
# render_template_string - renders HTML stored as a string (?)

import requests #for API calling
 
STATION_ID = 14218
API_URL = f"https://app.birdweather.com/api/v1/stations/{STATION_ID}/detections"


#Creating  the Flask application instance.
app = Flask(__name__) #__name__ tells Flask where this file is located.

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
</style>
</head>
<body>
  <h2>BirdWeather Live Dashboard</h2>
  <div class="big">Latest 5 detections</div>
    <div id="cards"></div>
    <div class="muted" id="updated"></div>
    <div class="muted">Auto-refresh: <code>10s</code></div>
  </div>

  <script>
    async function refresh() {
      try {
        const res = await fetch("/latest");
        const data = await res.json();
        if (data.ok) {
        const cardsHtml = data.rows.map((x, i) => `
            <div class="dcard">
            <div class="dtitle">${i + 1}. ${x.species}</div>
            <div class="dmeta">Time: ${x.timestamp}</div>
            <div class="dmeta">Confidence: ${x.confidence}</div>
            </div>
        `).join("");

        document.getElementById("cards").innerHTML = cardsHtml;

        document.getElementById("updated").textContent =
            `Last updated (your time): ${new Date().toLocaleTimeString()}`;
        } else {
        document.getElementById("cards").innerHTML =
            `<div class="dcard"><div class="dtitle">API error</div><div class="dmeta">${data.error}</div></div>`;
        }
      } catch (e) {
        document.getElementById("species").textContent = "Network error";
        document.getElementById("meta").textContent = e.toString();
      }
    }

    refresh();
    setInterval(refresh, 10000);
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
        r = requests.get(API_URL, timeout=20)
        r.raise_for_status()
        data = r.json()

        detections = data.get("detections", [])[:5]  # top 5 (newest first)
        rows = []
        for d in detections:
            species = (d.get("species") or {}).get("commonName") or "Unknown"
            ts = d.get("timestamp") or ""
            conf = d.get("confidence")
            conf_str = f"{conf:.3f}" if isinstance(conf, (int, float)) else ""
            rows.append({"species": species, "timestamp": ts, "confidence": conf_str})

        return jsonify(ok=True, rows=rows)

    except Exception as e:
        return jsonify(ok=False, error=str(e))

if __name__ == "__main__":
    app.run(debug=True)