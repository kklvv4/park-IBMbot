"""
DBKL (Dewan Bandaraya Kuala Lumpur) parking scraper.
Targets: https://www.dbkl.gov.my (parking section)
Falls back to hardcoded KL street zone data if scraping fails.
"""

from typing import List, Dict, Any
from scrapers.base_scraper import BaseScraper, make_record

SOURCE_URL = "https://www.dbkl.gov.my/index.php?option=com_content&view=article&id=296&Itemid=376"

FALLBACK_DATA: List[Dict[str, Any]] = [
    make_record(
        name="DBKL Street Parking Zone 1 – City Centre",
        operator="DBKL",
        type="street",
        parking_class="normal",
        address="Jalan Raja Chulan / Jalan P. Ramlee / Jalan Ampang, KL City Centre",
        city="Kuala Lumpur",
        state="Wilayah Persekutuan",
        latitude=3.1478,
        longitude=101.6953,
        rate_per_hour=2.00,
        motorcycle_rate=0.50,
        daily_max_cap=20.00,
        operating_hours="Mon–Sat 08:00–18:00",
        payment_method="Coupon, E-Parking App, Touch 'n Go",
        source_url=SOURCE_URL,
        notes="Zone 1 – highest density commercial area",
    ),
    make_record(
        name="DBKL Street Parking Zone 2 – Surrounding City",
        operator="DBKL",
        type="street",
        parking_class="normal",
        address="Jalan Pudu / Jalan Chow Kit / Jalan Tuanku Abdul Halim",
        city="Kuala Lumpur",
        state="Wilayah Persekutuan",
        latitude=3.1430,
        longitude=101.6987,
        rate_per_hour=1.00,
        motorcycle_rate=0.30,
        daily_max_cap=10.00,
        operating_hours="Mon–Sat 08:00–18:00",
        payment_method="Coupon, E-Parking App, Touch 'n Go",
        source_url=SOURCE_URL,
        notes="Zone 2 – lower density surrounding areas",
    ),
    make_record(
        name="DBKL Street Parking Zone 3 – Outer City",
        operator="DBKL",
        type="street",
        parking_class="normal",
        address="Jalan Kepong / Jalan Gombak / Jalan Cheras",
        city="Kuala Lumpur",
        state="Wilayah Persekutuan",
        latitude=3.1550,
        longitude=101.6850,
        rate_per_hour=0.50,
        motorcycle_rate=0.20,
        daily_max_cap=5.00,
        operating_hours="Mon–Sat 08:00–18:00",
        payment_method="Coupon, E-Parking App",
        source_url=SOURCE_URL,
        notes="Zone 3 – outer residential/commercial",
    ),
    make_record(
        name="DBKL Masjid India Open Car Park",
        operator="DBKL",
        type="open_lot",
        parking_class="normal",
        address="Jalan Masjid India, Kuala Lumpur",
        city="Kuala Lumpur",
        state="Wilayah Persekutuan",
        latitude=3.1494,
        longitude=101.6935,
        rate_per_hour=2.00,
        motorcycle_rate=0.50,
        daily_max_cap=15.00,
        total_bays=200,
        operating_hours="Mon–Sun 07:00–22:00",
        payment_method="Cash, Touch 'n Go",
        source_url=SOURCE_URL,
    ),
    make_record(
        name="DBKL Chow Kit Open Car Park",
        operator="DBKL",
        type="open_lot",
        parking_class="normal",
        address="Jalan Chow Kit, Kuala Lumpur",
        city="Kuala Lumpur",
        state="Wilayah Persekutuan",
        latitude=3.1616,
        longitude=101.6974,
        rate_per_hour=1.00,
        motorcycle_rate=0.30,
        daily_max_cap=10.00,
        total_bays=150,
        operating_hours="Mon–Sun 07:00–22:00",
        payment_method="Cash, Touch 'n Go",
        source_url=SOURCE_URL,
    ),
]


class DBKLScraper(BaseScraper):
    """Scrapes DBKL street parking zones."""

    def scrape(self) -> List[Dict[str, Any]]:
        self.logger.info("Starting DBKL scrape …")
        try:
            results = self._scrape_live()
            if results:
                self.logger.info("DBKL live scrape returned %d records", len(results))
                return results
        except Exception as exc:
            self.logger.warning("DBKL live scrape failed (%s) – using fallback", exc)
        self.logger.info("DBKL using %d fallback records", len(FALLBACK_DATA))
        return FALLBACK_DATA

    def _scrape_live(self) -> List[Dict[str, Any]]:
        if not self.can_fetch(SOURCE_URL):
            self.logger.info("DBKL robots.txt disallows fetch – skipping live scrape")
            return []
        page = self.soup(SOURCE_URL)
        if page is None:
            return []
        # The DBKL parking page is mostly static text/tables; try to find a table
        tables = page.find_all("table")
        if not tables:
            return []
        records: List[Dict[str, Any]] = []
        for table in tables:
            rows = table.find_all("tr")
            for row in rows[1:]:  # skip header
                cells = [td.get_text(strip=True) for td in row.find_all(["td", "th"])]
                if len(cells) < 3:
                    continue
                rec = make_record(
                    name=cells[0] if cells[0] else "DBKL Parking",
                    operator="DBKL",
                    type="street",
                    parking_class="normal",
                    city="Kuala Lumpur",
                    state="Wilayah Persekutuan",
                    rate_per_hour=self.safe_float(cells[2]) if len(cells) > 2 else None,
                    source_url=SOURCE_URL,
                )
                records.append(rec)
        return records
