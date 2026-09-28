"""
FastAPI backend — Malaysia Parking Map (KL & Selangor).

Endpoints:
  GET /health
  GET /api/parking            → GeoJSON FeatureCollection (all + filter by city/type)
  GET /api/parking/{id}       → single parking location detail
  GET /api/parking/type/{type}→ filter by type
  GET /api/parking/city/{city}→ filter by city
  GET /api/zones              → all council zones
  GET /api/stats              → summary statistics

Also serves the frontend static files from ../frontend/
"""

from pathlib import Path
from typing import Optional, List

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from database import (
    fetch_all_locations,
    fetch_location_by_id,
    fetch_zones,
    fetch_stats,
    db_exists,
)
from models import (
    ParkingLocation,
    GeoJSONFeature,
    GeoJSONFeatureCollection,
    Zone,
    Stats,
)

# ── App setup ──────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Malaysia Parking Map API",
    description="Parking fee data for Kuala Lumpur and Selangor",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"


# ── Helpers ────────────────────────────────────────────────────────────────────

def _to_geojson(rows: list) -> GeoJSONFeatureCollection:
    features = []
    for row in rows:
        lat = row.get("latitude")
        lng = row.get("longitude")
        if lat is None or lng is None:
            continue
        feature = GeoJSONFeature(
            geometry={"type": "Point", "coordinates": [lng, lat]},
            properties={
                "id": row.get("id"),
                "name": row.get("name"),
                "operator": row.get("operator"),
                "type": row.get("type"),
                "parking_class": row.get("parking_class"),
                "address": row.get("address"),
                "city": row.get("city"),
                "state": row.get("state"),
                "rate_per_hour": row.get("rate_per_hour"),
                "motorcycle_rate": row.get("motorcycle_rate"),
                "valet_rate": row.get("valet_rate"),
                "first_hour_rate": row.get("first_hour_rate"),
                "first_hour_free": row.get("first_hour_free"),
                "daily_max_cap": row.get("daily_max_cap"),
                "overnight_rate": row.get("overnight_rate"),
                "operating_hours": row.get("operating_hours"),
                "payment_method": row.get("payment_method"),
                "is_online_bookable": row.get("is_online_bookable"),
                "booking_platform": row.get("booking_platform"),
                "total_bays": row.get("total_bays"),
                "ev_charging": row.get("ev_charging"),
                "disabled_bays": row.get("disabled_bays"),
                "source_url": row.get("source_url"),
                "last_updated": row.get("last_updated"),
                "notes": row.get("notes"),
            },
        )
        features.append(feature)
    return GeoJSONFeatureCollection(features=features)


def _check_db():
    if not db_exists():
        raise HTTPException(
            status_code=503,
            detail="Database not found. Run: python convert.py",
        )


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "db_ready": db_exists()}


@app.get("/api/parking", response_model=GeoJSONFeatureCollection)
def get_all_parking(
    city: Optional[str] = Query(None, description="Filter by city name"),
    type: Optional[str] = Query(None, description="Filter by parking type"),
    include_valet: bool = Query(True, description="Include valet locations"),
    include_airport: bool = Query(True, description="Include airport parking"),
):
    """
    Returns a GeoJSON FeatureCollection of all parking locations.
    Optionally filter by city or type. Includes valet and airport by default.
    """
    _check_db()
    rows = fetch_all_locations(city=city, parking_type=type)
    if include_valet:
        rows += fetch_all_locations(city=city, table="valet_services")
    if include_airport:
        rows += fetch_all_locations(city=city, table="airport_parking")
    return _to_geojson(rows)


@app.get("/api/parking/type/{parking_type}", response_model=GeoJSONFeatureCollection)
def get_parking_by_type(parking_type: str):
    """Returns all parking locations matching a specific type."""
    _check_db()
    rows = fetch_all_locations(parking_type=parking_type)
    return _to_geojson(rows)


@app.get("/api/parking/city/{city}", response_model=GeoJSONFeatureCollection)
def get_parking_by_city(city: str):
    """Returns all parking locations in a specific city."""
    _check_db()
    rows = fetch_all_locations(city=city)
    rows += fetch_all_locations(city=city, table="valet_services")
    rows += fetch_all_locations(city=city, table="airport_parking")
    return _to_geojson(rows)


@app.get("/api/parking/{location_id}", response_model=ParkingLocation)
def get_parking_detail(location_id: int):
    """Returns full detail for a single parking location by ID."""
    _check_db()
    # Search across all tables
    row = fetch_location_by_id(location_id, "parking_locations")
    if row is None:
        row = fetch_location_by_id(location_id, "valet_services")
    if row is None:
        row = fetch_location_by_id(location_id, "airport_parking")
    if row is None:
        raise HTTPException(status_code=404, detail=f"Parking location {location_id} not found")
    return ParkingLocation(**row)


@app.get("/api/zones", response_model=List[Zone])
def get_zones(city: Optional[str] = Query(None)):
    """Returns all council parking zones, optionally filtered by city."""
    _check_db()
    rows = fetch_zones(city=city)
    return [Zone(**r) for r in rows]


@app.get("/api/stats", response_model=Stats)
def get_stats():
    """Returns summary statistics for the parking database."""
    _check_db()
    data = fetch_stats()
    return Stats(**data)


# ── Static frontend ────────────────────────────────────────────────────────────

if FRONTEND_DIR.exists():
    # Serve JS/CSS sub-folders
    app.mount("/css", StaticFiles(directory=str(FRONTEND_DIR / "css")), name="css")
    app.mount("/js",  StaticFiles(directory=str(FRONTEND_DIR / "js")),  name="js")

    @app.get("/", response_class=FileResponse)
    def serve_index():
        return FileResponse(str(FRONTEND_DIR / "index.html"))
else:
    @app.get("/")
    def root():
        return {"message": "Frontend not found. Place it in ../frontend/"}
