"""
convert.py — Converts the scraper Excel output to a SQLite database.

Usage:
    python convert.py [--excel PATH] [--db PATH]

Defaults:
    --excel ../scraper/output/malaysia_parking_data.xlsx
    --db     parking.db
"""

import argparse
import logging
import sqlite3
from pathlib import Path

import openpyxl

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("convert")

DEFAULT_EXCEL = Path(__file__).parent.parent / "scraper" / "output" / "malaysia_parking_data.xlsx"
DEFAULT_DB = Path(__file__).parent / "parking.db"

# ── DDL ────────────────────────────────────────────────────────────────────────

DDL_LOCATIONS = """
CREATE TABLE IF NOT EXISTS parking_locations (
    id              INTEGER PRIMARY KEY,
    name            TEXT    NOT NULL,
    operator        TEXT,
    type            TEXT,
    parking_class   TEXT    DEFAULT 'normal',
    address         TEXT,
    city            TEXT,
    state           TEXT,
    latitude        REAL,
    longitude       REAL,
    rate_per_hour   REAL,
    motorcycle_rate REAL,
    valet_rate      REAL,
    first_hour_rate REAL,
    first_hour_free TEXT    DEFAULT 'NO',
    daily_max_cap   REAL,
    overnight_rate  REAL,
    operating_hours TEXT,
    payment_method  TEXT,
    is_online_bookable TEXT DEFAULT 'NO',
    booking_platform   TEXT,
    total_bays      INTEGER,
    ev_charging     TEXT    DEFAULT 'NO',
    disabled_bays   TEXT    DEFAULT 'NO',
    source_url      TEXT,
    last_updated    TEXT,
    notes           TEXT
);
"""

DDL_RATE_TIERS = """
CREATE TABLE IF NOT EXISTS rate_tiers (
    tier_id         TEXT    PRIMARY KEY,
    location_name   TEXT,
    duration        TEXT,
    rate            REAL,
    currency        TEXT    DEFAULT 'MYR',
    notes           TEXT
);
"""

DDL_ZONES = """
CREATE TABLE IF NOT EXISTS zones (
    zone_id         TEXT    PRIMARY KEY,
    council         TEXT,
    zone_name       TEXT,
    rate_per_hour   REAL,
    city            TEXT,
    state           TEXT,
    notes           TEXT
);
"""

DDL_VALET = """
CREATE TABLE IF NOT EXISTS valet_services (
    id              INTEGER PRIMARY KEY,
    name            TEXT    NOT NULL,
    operator        TEXT,
    type            TEXT,
    parking_class   TEXT,
    address         TEXT,
    city            TEXT,
    state           TEXT,
    latitude        REAL,
    longitude       REAL,
    rate_per_hour   REAL,
    motorcycle_rate REAL,
    valet_rate      REAL,
    first_hour_rate REAL,
    first_hour_free TEXT,
    daily_max_cap   REAL,
    overnight_rate  REAL,
    operating_hours TEXT,
    payment_method  TEXT,
    is_online_bookable TEXT,
    booking_platform   TEXT,
    total_bays      INTEGER,
    ev_charging     TEXT,
    disabled_bays   TEXT,
    source_url      TEXT,
    last_updated    TEXT,
    notes           TEXT
);
"""

DDL_AIRPORT = """
CREATE TABLE IF NOT EXISTS airport_parking (
    id              INTEGER PRIMARY KEY,
    name            TEXT    NOT NULL,
    operator        TEXT,
    type            TEXT,
    parking_class   TEXT,
    address         TEXT,
    city            TEXT,
    state           TEXT,
    latitude        REAL,
    longitude       REAL,
    rate_per_hour   REAL,
    motorcycle_rate REAL,
    valet_rate      REAL,
    first_hour_rate REAL,
    first_hour_free TEXT,
    daily_max_cap   REAL,
    overnight_rate  REAL,
    operating_hours TEXT,
    payment_method  TEXT,
    is_online_bookable TEXT,
    booking_platform   TEXT,
    total_bays      INTEGER,
    ev_charging     TEXT,
    disabled_bays   TEXT,
    source_url      TEXT,
    last_updated    TEXT,
    notes           TEXT
);
"""

DDL_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_locations_lat_lng ON parking_locations (latitude, longitude);",
    "CREATE INDEX IF NOT EXISTS idx_locations_city    ON parking_locations (city);",
    "CREATE INDEX IF NOT EXISTS idx_locations_type    ON parking_locations (type);",
    "CREATE INDEX IF NOT EXISTS idx_locations_state   ON parking_locations (state);",
    "CREATE INDEX IF NOT EXISTS idx_valet_city        ON valet_services    (city);",
    "CREATE INDEX IF NOT EXISTS idx_airport_city      ON airport_parking   (city);",
]

# Column order must match Excel sheet headers
LOCATION_COLUMNS = [
    "id", "name", "operator", "type", "parking_class",
    "address", "city", "state",
    "latitude", "longitude",
    "rate_per_hour", "motorcycle_rate", "valet_rate",
    "first_hour_rate", "first_hour_free",
    "daily_max_cap", "overnight_rate",
    "operating_hours", "payment_method",
    "is_online_bookable", "booking_platform",
    "total_bays", "ev_charging", "disabled_bays",
    "source_url", "last_updated", "notes",
]


def _safe(val):
    """Return None for empty strings so SQLite stores NULL."""
    if val is None:
        return None
    s = str(val).strip()
    return None if s == "" else s


def _safe_float(val):
    try:
        return float(str(val).replace("RM", "").replace(",", "").strip())
    except (ValueError, TypeError):
        return None


def _safe_int(val):
    try:
        return int(str(val).strip())
    except (ValueError, TypeError):
        return None


def _sheet_rows(ws):
    """Yield rows from a worksheet as dicts, using the first row as header."""
    headers = [str(cell.value).strip() if cell.value else f"col_{i}"
               for i, cell in enumerate(next(ws.iter_rows(min_row=1, max_row=1)))]
    for row in ws.iter_rows(min_row=2, values_only=True):
        if all(v is None for v in row):
            continue
        yield dict(zip(headers, row))


def load_excel(path: Path) -> dict:
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    sheets = {}
    for name in wb.sheetnames:
        sheets[name] = list(_sheet_rows(wb[name]))
    wb.close()
    logger.info(
        "Loaded Excel: %s  sheets=%s",
        path,
        {k: len(v) for k, v in sheets.items()},
    )
    return sheets


def create_schema(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    for ddl in [DDL_LOCATIONS, DDL_RATE_TIERS, DDL_ZONES, DDL_VALET, DDL_AIRPORT]:
        cur.executescript(ddl)
    for idx in DDL_INDEXES:
        cur.execute(idx)
    conn.commit()
    logger.info("Schema created / verified.")


def _insert_location_rows(conn, table: str, rows: list) -> int:
    placeholders = ", ".join(["?"] * len(LOCATION_COLUMNS))
    sql = f"INSERT OR REPLACE INTO {table} ({', '.join(LOCATION_COLUMNS)}) VALUES ({placeholders})"
    count = 0
    cur = conn.cursor()
    for row in rows:
        vals = []
        for col in LOCATION_COLUMNS:
            raw = row.get(col)
            if col in ("latitude", "longitude", "rate_per_hour", "motorcycle_rate",
                       "valet_rate", "first_hour_rate", "daily_max_cap", "overnight_rate"):
                vals.append(_safe_float(raw))
            elif col in ("total_bays", "id"):
                vals.append(_safe_int(raw))
            else:
                vals.append(_safe(raw))
        cur.execute(sql, vals)
        count += 1
    conn.commit()
    return count


def populate(conn: sqlite3.Connection, sheets: dict) -> None:
    # ── parking_locations ──────────────────────────────────────────────────────
    loc_rows = sheets.get("parking_locations", [])
    n = _insert_location_rows(conn, "parking_locations", loc_rows)
    logger.info("Inserted %d rows → parking_locations", n)

    # ── rate_tiers ─────────────────────────────────────────────────────────────
    tier_rows = sheets.get("rate_tiers", [])
    cur = conn.cursor()
    tier_count = 0
    for row in tier_rows:
        cur.execute(
            "INSERT OR REPLACE INTO rate_tiers "
            "(tier_id, location_name, duration, rate, currency, notes) VALUES (?,?,?,?,?,?)",
            (
                _safe(row.get("tier_id")),
                _safe(row.get("location_name")),
                _safe(row.get("duration")),
                _safe_float(row.get("rate")),
                _safe(row.get("currency")) or "MYR",
                _safe(row.get("notes")),
            ),
        )
        tier_count += 1
    conn.commit()
    logger.info("Inserted %d rows → rate_tiers", tier_count)

    # ── zones ──────────────────────────────────────────────────────────────────
    zone_rows = sheets.get("zones", [])
    zone_count = 0
    for row in zone_rows:
        cur.execute(
            "INSERT OR REPLACE INTO zones "
            "(zone_id, council, zone_name, rate_per_hour, city, state, notes) VALUES (?,?,?,?,?,?,?)",
            (
                _safe(row.get("zone_id")),
                _safe(row.get("council")),
                _safe(row.get("zone_name")),
                _safe_float(row.get("rate_per_hour")),
                _safe(row.get("city")),
                _safe(row.get("state")),
                _safe(row.get("notes")),
            ),
        )
        zone_count += 1
    conn.commit()
    logger.info("Inserted %d rows → zones", zone_count)

    # ── valet_services ─────────────────────────────────────────────────────────
    valet_rows = sheets.get("valet_services", [])
    n = _insert_location_rows(conn, "valet_services", valet_rows)
    logger.info("Inserted %d rows → valet_services", n)

    # ── airport_parking ────────────────────────────────────────────────────────
    airport_rows = sheets.get("airport_parking", [])
    n = _insert_location_rows(conn, "airport_parking", airport_rows)
    logger.info("Inserted %d rows → airport_parking", n)


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert parking Excel → SQLite")
    parser.add_argument("--excel", type=Path, default=DEFAULT_EXCEL,
                        help="Path to malaysia_parking_data.xlsx")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB,
                        help="Output SQLite database path")
    args = parser.parse_args()

    if not args.excel.exists():
        logger.error("Excel file not found: %s — run the scraper first.", args.excel)
        raise SystemExit(1)

    sheets = load_excel(args.excel)

    conn = sqlite3.connect(args.db)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")

    create_schema(conn)
    populate(conn, sheets)

    conn.close()
    logger.info("Database saved → %s", args.db)


if __name__ == "__main__":
    main()
