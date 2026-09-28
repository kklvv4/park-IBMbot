"""
Scraper orchestrator — runs all scrapers and writes output to Excel.

Output: output/malaysia_parking_data.xlsx
  Sheet 1: parking_locations
  Sheet 2: rate_tiers
  Sheet 3: zones
  Sheet 4: valet_services
  Sheet 5: airport_parking

Usage:
    python main.py
"""

import sys
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

# ── add scraper root to path so sibling imports work ─────────────────────────
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

# Government
from scrapers.government.dbkl_scraper import DBKLScraper
from scrapers.government.mbpj_scraper import MBPJScraper
from scrapers.government.mbsa_scraper import MBSAScraper
from scrapers.government.mpsj_scraper import MPSJScraper
from scrapers.government.mpaj_scraper import MPAJScraper
from scrapers.government.penang_scraper import PenangScraper  # produces 0 records now

# Private / commercial
from scrapers.private.wilson_scraper import WilsonScraper
from scrapers.private.interpark_scraper import InterparkScraper
from scrapers.private.myparking_scraper import MyParkingScraper
from scrapers.private.secure_parking_scraper import SecureParkingScraper

# Malls
from scrapers.malls.klcc_scraper import KLCCScraper
from scrapers.malls.pavilion_scraper import PavilionScraper
from scrapers.malls.midvalley_scraper import MidValleyScraper
from scrapers.malls.sunway_scraper import SunwayScraper
from scrapers.malls.one_utama_scraper import OneUtamaScraper
from scrapers.malls.ioi_scraper import IOIScraper
from scrapers.malls.the_curve_scraper import TheCurveScraper
from scrapers.malls.gurney_scraper import GurneyScraper  # stub – 0 records

# Valet
from scrapers.valet.hotel_valet_scraper import HotelValetScraper
from scrapers.valet.premium_valet_scraper import PremiumValetScraper

# Special
from scrapers.special.klia_scraper import KLIAScraper
from scrapers.special.rapidkl_scraper import RapidKLScraper
from scrapers.special.stadium_scraper import StadiumScraper

# ── logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("main")

# ── column order for Sheet 1 ──────────────────────────────────────────────────
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

OUTPUT_DIR = ROOT / "output"
OUTPUT_FILE = OUTPUT_DIR / "malaysia_parking_data.xlsx"

# ── header style ───────────────────────────────────────────────────────────────
HEADER_FILL = PatternFill("solid", fgColor="1F4E79")
HEADER_FONT = Font(bold=True, color="FFFFFF", size=11)
HEADER_ALIGN = Alignment(horizontal="center", vertical="center", wrap_text=True)


def _style_sheet_header(ws, columns: List[str]) -> None:
    """Write and style the header row for a worksheet."""
    for col_idx, col_name in enumerate(columns, start=1):
        cell = ws.cell(row=1, column=col_idx, value=col_name)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = HEADER_ALIGN
    ws.row_dimensions[1].height = 28


def _auto_width(ws) -> None:
    """Set reasonable column widths based on content."""
    for col in ws.columns:
        max_len = max(
            (len(str(cell.value)) if cell.value is not None else 0) for cell in col
        )
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = min(max_len + 4, 50)


def _assign_ids(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Assign sequential IDs to records that don't have one."""
    for i, rec in enumerate(records, start=1):
        if not rec.get("id"):
            rec["id"] = i
    return records


# ── zone data ─────────────────────────────────────────────────────────────────
ZONES = [
    {"zone_id": "DBKL-Z1", "council": "DBKL", "zone_name": "Zone 1 – City Centre",
     "rate_per_hour": 2.00, "city": "Kuala Lumpur", "state": "Wilayah Persekutuan",
     "notes": "Jalan Raja Chulan, Jalan Ampang, Jalan P. Ramlee"},
    {"zone_id": "DBKL-Z2", "council": "DBKL", "zone_name": "Zone 2 – Surrounding City",
     "rate_per_hour": 1.00, "city": "Kuala Lumpur", "state": "Wilayah Persekutuan",
     "notes": "Jalan Pudu, Chow Kit, KLCC fringe"},
    {"zone_id": "DBKL-Z3", "council": "DBKL", "zone_name": "Zone 3 – Outer Areas",
     "rate_per_hour": 0.50, "city": "Kuala Lumpur", "state": "Wilayah Persekutuan",
     "notes": "Kepong, Gombak, Cheras"},
    {"zone_id": "MBPJ-A", "council": "MBPJ", "zone_name": "Zone A – PJ Commercial",
     "rate_per_hour": 1.00, "city": "Petaling Jaya", "state": "Selangor",
     "notes": "SS2, Damansara Uptown, Ara Damansara"},
    {"zone_id": "MBPJ-B", "council": "MBPJ", "zone_name": "Zone B – PJ Residential",
     "rate_per_hour": 0.50, "city": "Petaling Jaya", "state": "Selangor",
     "notes": "Section 14, Section 17"},
    {"zone_id": "MBSA-A", "council": "MBSA", "zone_name": "Zone A – Shah Alam City Centre",
     "rate_per_hour": 1.00, "city": "Shah Alam", "state": "Selangor",
     "notes": "Persiaran Perbandaran, Plaza Masalam"},
    {"zone_id": "MPSJ-A", "council": "MPSJ", "zone_name": "Zone A – Subang Jaya",
     "rate_per_hour": 1.00, "city": "Subang Jaya", "state": "Selangor",
     "notes": "SS15, USJ, Taipan"},
    {"zone_id": "MPAJ-A", "council": "MPAJ", "zone_name": "Zone A – Ampang",
     "rate_per_hour": 1.00, "city": "Ampang", "state": "Selangor",
     "notes": "Ampang Point, Wangsa Maju, Pandan"},
]

# ── rate tier data ────────────────────────────────────────────────────────────
RATE_TIERS = [
    {"tier_id": "KLCC-T1", "location_name": "Suria KLCC", "duration": "1st hour",
     "rate": 2.00, "currency": "MYR", "notes": ""},
    {"tier_id": "KLCC-T2", "location_name": "Suria KLCC", "duration": "2nd hour",
     "rate": 2.00, "currency": "MYR", "notes": ""},
    {"tier_id": "KLCC-T3", "location_name": "Suria KLCC", "duration": "3rd hour onwards",
     "rate": 3.00, "currency": "MYR", "notes": "Per hour"},
    {"tier_id": "KLCC-T4", "location_name": "Suria KLCC", "duration": "Daily max",
     "rate": 20.00, "currency": "MYR", "notes": ""},
    {"tier_id": "PAV-T1", "location_name": "Pavilion KL", "duration": "Per hour",
     "rate": 3.00, "currency": "MYR", "notes": ""},
    {"tier_id": "PAV-T2", "location_name": "Pavilion KL", "duration": "Daily max",
     "rate": 25.00, "currency": "MYR", "notes": ""},
    {"tier_id": "MV-T1", "location_name": "Mid Valley Megamall", "duration": "Per hour",
     "rate": 2.00, "currency": "MYR", "notes": ""},
    {"tier_id": "MV-T2", "location_name": "Mid Valley Megamall", "duration": "Daily max",
     "rate": 20.00, "currency": "MYR", "notes": ""},
    {"tier_id": "SP-T1", "location_name": "Sunway Pyramid", "duration": "Per hour",
     "rate": 2.00, "currency": "MYR", "notes": ""},
    {"tier_id": "SP-T2", "location_name": "Sunway Pyramid", "duration": "Daily max",
     "rate": 15.00, "currency": "MYR", "notes": ""},
    {"tier_id": "1U-T1", "location_name": "1 Utama", "duration": "Per hour",
     "rate": 2.00, "currency": "MYR", "notes": ""},
    {"tier_id": "1U-T2", "location_name": "1 Utama", "duration": "Daily max",
     "rate": 18.00, "currency": "MYR", "notes": ""},
    {"tier_id": "KLIA-T1", "location_name": "KLIA Short-Term", "duration": "Per hour",
     "rate": 4.00, "currency": "MYR", "notes": ""},
    {"tier_id": "KLIA-T2", "location_name": "KLIA Short-Term", "duration": "Daily max",
     "rate": 60.00, "currency": "MYR", "notes": ""},
    {"tier_id": "KLIA2-LT", "location_name": "KLIA Long-Term", "duration": "Per day",
     "rate": 10.00, "currency": "MYR", "notes": ""},
]


def run_all_scrapers() -> List[Dict[str, Any]]:
    scrapers = [
        DBKLScraper(), MBPJScraper(), MBSAScraper(), MPSJScraper(), MPAJScraper(),
        PenangScraper(),
        WilsonScraper(), InterparkScraper(), MyParkingScraper(), SecureParkingScraper(),
        KLCCScraper(), PavilionScraper(), MidValleyScraper(), SunwayScraper(),
        OneUtamaScraper(), IOIScraper(), TheCurveScraper(), GurneyScraper(),
        HotelValetScraper(), PremiumValetScraper(),
        KLIAScraper(), RapidKLScraper(), StadiumScraper(),
    ]
    all_records: List[Dict[str, Any]] = []
    for scraper in scrapers:
        try:
            records = scraper.scrape()
            logger.info(
                "%-35s → %d records",
                scraper.__class__.__name__,
                len(records),
            )
            all_records.extend(records)
        except Exception as exc:
            logger.error("Scraper %s crashed: %s", scraper.__class__.__name__, exc)
    return all_records


def separate_special(records: List[Dict[str, Any]]):
    """Split records into main, valet, and airport sheets."""
    main, valet, airport = [], [], []
    for rec in records:
        t = (rec.get("type") or "").lower()
        if t == "airport":
            airport.append(rec)
        elif t == "valet":
            valet.append(rec)
        else:
            main.append(rec)
    return main, valet, airport


def write_excel(all_records: List[Dict[str, Any]]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    all_records = _assign_ids(all_records)
    main, valet, airport = separate_special(all_records)

    wb = openpyxl.Workbook()

    # ── Sheet 1: parking_locations ─────────────────────────────────────────────
    ws1 = wb.active
    ws1.title = "parking_locations"
    _style_sheet_header(ws1, LOCATION_COLUMNS)
    for rec in main:
        row = [rec.get(col) for col in LOCATION_COLUMNS]
        ws1.append(row)
    _auto_width(ws1)
    ws1.freeze_panes = "A2"

    # ── Sheet 2: rate_tiers ────────────────────────────────────────────────────
    ws2 = wb.create_sheet("rate_tiers")
    tier_cols = ["tier_id", "location_name", "duration", "rate", "currency", "notes"]
    _style_sheet_header(ws2, tier_cols)
    for tier in RATE_TIERS:
        ws2.append([tier.get(c) for c in tier_cols])
    _auto_width(ws2)
    ws2.freeze_panes = "A2"

    # ── Sheet 3: zones ─────────────────────────────────────────────────────────
    ws3 = wb.create_sheet("zones")
    zone_cols = ["zone_id", "council", "zone_name", "rate_per_hour", "city", "state", "notes"]
    _style_sheet_header(ws3, zone_cols)
    for zone in ZONES:
        ws3.append([zone.get(c) for c in zone_cols])
    _auto_width(ws3)
    ws3.freeze_panes = "A2"

    # ── Sheet 4: valet_services ────────────────────────────────────────────────
    ws4 = wb.create_sheet("valet_services")
    _style_sheet_header(ws4, LOCATION_COLUMNS)
    for rec in valet:
        ws4.append([rec.get(col) for col in LOCATION_COLUMNS])
    _auto_width(ws4)
    ws4.freeze_panes = "A2"

    # ── Sheet 5: airport_parking ───────────────────────────────────────────────
    ws5 = wb.create_sheet("airport_parking")
    _style_sheet_header(ws5, LOCATION_COLUMNS)
    for rec in airport:
        ws5.append([rec.get(col) for col in LOCATION_COLUMNS])
    _auto_width(ws5)
    ws5.freeze_panes = "A2"

    wb.save(OUTPUT_FILE)
    logger.info(
        "Excel saved → %s  (%d main, %d valet, %d airport)",
        OUTPUT_FILE,
        len(main),
        len(valet),
        len(airport),
    )


def main() -> None:
    logger.info("=" * 60)
    logger.info("Malaysia Parking Map Scraper — KL & Selangor")
    logger.info("Started at %s", datetime.now().isoformat(timespec="seconds"))
    logger.info("=" * 60)

    records = run_all_scrapers()
    logger.info("Total records collected: %d", len(records))
    write_excel(records)

    logger.info("Done.")


if __name__ == "__main__":
    main()
