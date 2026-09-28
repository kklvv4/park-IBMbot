"""
database.py — SQLite connection and query helpers.
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, List, Dict, Any, Optional

DB_PATH = Path(__file__).parent / "parking.db"


def _row_factory(cursor: sqlite3.Cursor, row: tuple) -> Dict[str, Any]:
    """Convert each SQLite row to a dict keyed by column name."""
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Yield a SQLite connection with dict row_factory; close on exit."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = _row_factory
    conn.execute("PRAGMA journal_mode=WAL;")
    try:
        yield conn
    finally:
        conn.close()


# ── query helpers ──────────────────────────────────────────────────────────────

def fetch_all_locations(
    city: Optional[str] = None,
    parking_type: Optional[str] = None,
    table: str = "parking_locations",
) -> List[Dict[str, Any]]:
    sql = f"SELECT * FROM {table} WHERE latitude IS NOT NULL AND longitude IS NOT NULL"
    params: List[Any] = []
    if city:
        sql += " AND LOWER(city) = LOWER(?)"
        params.append(city)
    if parking_type:
        sql += " AND LOWER(type) = LOWER(?)"
        params.append(parking_type)
    sql += " ORDER BY id"
    with get_db() as conn:
        return conn.execute(sql, params).fetchall()


def fetch_location_by_id(location_id: int, table: str = "parking_locations") -> Optional[Dict[str, Any]]:
    sql = f"SELECT * FROM {table} WHERE id = ?"
    with get_db() as conn:
        row = conn.execute(sql, (location_id,)).fetchone()
    return row


def fetch_zones(city: Optional[str] = None) -> List[Dict[str, Any]]:
    sql = "SELECT * FROM zones"
    params: List[Any] = []
    if city:
        sql += " WHERE LOWER(city) = LOWER(?)"
        params.append(city)
    sql += " ORDER BY zone_id"
    with get_db() as conn:
        return conn.execute(sql, params).fetchall()


def fetch_stats() -> Dict[str, Any]:
    with get_db() as conn:
        total_loc = conn.execute(
            "SELECT COUNT(*) AS cnt FROM parking_locations"
        ).fetchone()["cnt"]
        total_valet = conn.execute(
            "SELECT COUNT(*) AS cnt FROM valet_services"
        ).fetchone()["cnt"]
        total_airport = conn.execute(
            "SELECT COUNT(*) AS cnt FROM airport_parking"
        ).fetchone()["cnt"]
        avg_row = conn.execute(
            "SELECT AVG(rate_per_hour) AS avg FROM parking_locations WHERE rate_per_hour IS NOT NULL"
        ).fetchone()
        avg_rate = round(avg_row["avg"], 2) if avg_row and avg_row["avg"] else None
        cities = [
            r["city"] for r in conn.execute(
                "SELECT DISTINCT city FROM parking_locations WHERE city IS NOT NULL ORDER BY city"
            ).fetchall()
        ]
        types = [
            r["type"] for r in conn.execute(
                "SELECT DISTINCT type FROM parking_locations WHERE type IS NOT NULL ORDER BY type"
            ).fetchall()
        ]
    return {
        "total_locations": total_loc,
        "total_valet": total_valet,
        "total_airport": total_airport,
        "avg_rate_per_hour": avg_rate,
        "cities": cities,
        "types": types,
    }


def db_exists() -> bool:
    return DB_PATH.exists()
