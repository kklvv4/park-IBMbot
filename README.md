# 🅿 Malaysia Parking Map — KL & Selangor

An interactive web map showing parking fees across **Kuala Lumpur and Selangor**, built entirely with free, open-source tools — no private API keys required.

---

## Features

| Feature | Technology |
|---|---|
| Interactive map | Leaflet.js + OpenStreetMap tiles |
| Location search | Nominatim (OSM Geocoding) |
| Marker clustering | Leaflet.MarkerCluster |
| Backend API | FastAPI (Python) |
| Database | SQLite |
| Data collection | Python scraper → Excel → SQLite |

### Map capabilities
- 🟢 Green markers = RM1–2/hr · 🟡 Amber = RM2–4/hr · 🔴 Red = RM4+/hr · 🟣 Violet = Valet · 🔵 Teal = Park & Ride · ⚫ Grey = Free/flat
- Marker clusters when zoomed out
- Click any marker for full parking details (rate, hours, payment, EV, OKU, etc.)
- Filter sidebar: by type, price range, payment method, features
- Search bar powered by Nominatim geocoding

### Data coverage (KL & Selangor)
- **Government / council** — DBKL (3 zones), MBPJ, MBSA, MPSJ, MPAJ
- **Malls** — KLCC/Suria, Pavilion KL, Mid Valley + Gardens, Sunway Pyramid + Velocity, 1 Utama, IOI City Mall + IOI Puchong, The Curve / IPC / IKEA
- **Private operators** — Wilson Parking, Interpark, MyParking, Secure Parking
- **Hotel valet** — Mandarin Oriental, Ritz-Carlton, Grand Hyatt, InterContinental, Hilton, Le Meridien, St. Regis, Sheraton PJ, Sunway Resort
- **Premium/standalone valet** — Pavilion, Mid Valley, Bangsar, Jalan Ampang, Sunway, Empire Damansara
- **Airport** — KLIA short/long-stay, klia2 short/long-stay, KLIA valet
- **Park & Ride** — RapidKL at 8 LRT/MRT/KTM/BRT stations (Pasar Seni, Titiwangsa, Kelana Jaya, Subang Jaya KTM, Chow Kit MRT, Sunway BRT, Shah Alam KTM, Pandan Jaya LRT)
- **Stadiums** — Stadium Nasional Bukit Jalil, Stadium Shah Alam, Stadium Merdeka, Axiata Arena

---

## Prerequisites

- **Python 3.9+**
- **pip**

---

## Project Structure

```
malaysia-parking-map/
├── scraper/
│   ├── main.py                 ← Runs all scrapers, writes Excel
│   ├── requirements.txt
│   ├── output/
│   │   └── malaysia_parking_data.xlsx  ← generated
│   └── scrapers/
│       ├── base_scraper.py
│       ├── government/         ← DBKL, MBPJ, MBSA, MPSJ, MPAJ
│       ├── private/            ← Wilson, Interpark, MyParking, Secure Parking
│       ├── malls/              ← KLCC, Pavilion, Mid Valley, Sunway, 1U, IOI, Curve
│       ├── valet/              ← hotel_valet, premium_valet
│       └── special/            ← KLIA, RapidKL, Stadium
├── backend/
│   ├── main.py                 ← FastAPI app
│   ├── convert.py              ← Excel → SQLite
│   ├── models.py
│   ├── database.py
│   ├── requirements.txt
│   └── parking.db              ← generated
└── frontend/
    ├── index.html
    ├── css/style.css
    └── js/
        ├── api.js
        ├── map.js
        ├── markers.js
        ├── filters.js
        └── popup.js
```

---

## Quick Start

### 1. Clone / download the project

```bash
git clone https://github.com/yourname/malaysia-parking-map.git
cd malaysia-parking-map
```

### 2. Run the scraper

```bash
cd scraper
pip install -r requirements.txt

# (Optional) Install Playwright browsers if any scraper uses them
python -m playwright install chromium

python main.py
```

This creates `scraper/output/malaysia_parking_data.xlsx`.

### 3. Convert Excel → SQLite

```bash
cd ../backend
pip install -r requirements.txt

python convert.py
```

This creates `backend/parking.db`.

### 4. Start the backend

```bash
# still inside backend/
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Open the map

Visit **http://localhost:8000** in your browser.

The FastAPI backend serves the frontend static files automatically.

---

## API Reference

| Endpoint | Description |
|---|---|
| `GET /health` | Health check; reports whether DB is ready |
| `GET /api/parking` | All parking locations as GeoJSON; query params: `city`, `type`, `include_valet`, `include_airport` |
| `GET /api/parking/{id}` | Single location detail |
| `GET /api/parking/type/{type}` | Filter by type (`street`, `mall`, `multistorey`, `open_lot`, `valet`, `park_and_ride`, `airport`) |
| `GET /api/parking/city/{city}` | Filter by city |
| `GET /api/zones` | Council street zones; optional `city` query param |
| `GET /api/stats` | Summary statistics |

Interactive docs: **http://localhost:8000/docs**

---

## Scraper Notes

- Every scraper has a `scrape()` method that **first attempts to scrape live** then falls back to hardcoded data if the site is unavailable or blocks the request.
- Requests respect `robots.txt`, use a browser-like User-Agent, and add 1.5-second delays between requests.
- Hardcoded fallback data ensures the app always has content even if all live scrapes fail.
- To add a new location, edit the `FALLBACK_DATA` list in the relevant scraper file — no other changes needed.

---

## Deploying for Free on Render.com

1. **Push the project to GitHub.**
2. Go to [render.com](https://render.com) → New → **Web Service**.
3. Connect your GitHub repo.
4. Set:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add an environment variable: *(none required — SQLite is bundled)*
6. **Before deploying**, run the scraper and converter locally, then commit `parking.db` to the repo (or use Render's Disk for persistence).

> **Tip:** The free Render tier spins down after 15 minutes of inactivity. The first request after spin-up may take ~30 seconds.

---

## Updating Data

```bash
# Re-scrape
cd scraper && python main.py

# Re-convert
cd ../backend && python convert.py

# Restart server (auto-reload if --reload flag is set)
```

---

## License

MIT — free for personal and commercial use.

---

## Acknowledgements

- [OpenStreetMap](https://www.openstreetmap.org/) — map tiles and geocoding
- [Leaflet.js](https://leafletjs.com/) — open-source mapping library
- [Nominatim](https://nominatim.org/) — free geocoding API
- [FastAPI](https://fastapi.tiangolo.com/) — modern Python web framework
