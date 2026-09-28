"""
MPSJ (Majlis Perbandaran Subang Jaya) parking scraper.
Targets: https://www.mpsj.gov.my
Falls back to hardcoded Subang Jaya data.
"""

from typing import List, Dict, Any
from scrapers.base_scraper import BaseScraper, make_record

SOURCE_URL = "https://www.mpsj.gov.my"

FALLBACK_DATA: List[Dict[str, Any]] = [
    make_record(
        name="MPSJ Street Parking – SS15 Subang Jaya",
        operator="MPSJ",
        type="street",
        parking_class="normal",
        address="Jalan SS15/4, SS15, Subang Jaya",
        city="Subang Jaya",
        state="Selangor",
        latitude=3.0758,
        longitude=101.5857,
        rate_per_hour=1.00,
        motorcycle_rate=0.30,
        daily_max_cap=8.00,
        operating_hours="Mon–Sat 08:00–18:00",
        payment_method="Coupon, Touch 'n Go, ParkMate App",
        source_url=SOURCE_URL,
    ),
    make_record(
        name="MPSJ Multi-Storey Car Park – Taipan USJ",
        operator="MPSJ",
        type="multistorey",
        parking_class="normal",
        address="Jalan USJ 10/1, Taipan, Subang Jaya",
        city="Subang Jaya",
        state="Selangor",
        latitude=3.0544,
        longitude=101.5829,
        rate_per_hour=1.50,
        motorcycle_rate=0.40,
        daily_max_cap=12.00,
        total_bays=350,
        operating_hours="Mon–Sun 07:00–23:00",
        payment_method="Cash, Touch 'n Go",
        source_url=SOURCE_URL,
    ),
    make_record(
        name="MPSJ Open Car Park – USJ 21",
        operator="MPSJ",
        type="open_lot",
        parking_class="normal",
        address="Jalan USJ 21/5, Subang Jaya",
        city="Subang Jaya",
        state="Selangor",
        latitude=3.0378,
        longitude=101.5965,
        rate_per_hour=1.00,
        motorcycle_rate=0.30,
        daily_max_cap=8.00,
        total_bays=200,
        operating_hours="Mon–Sun 06:00–24:00",
        payment_method="Cash, Coupon",
        source_url=SOURCE_URL,
    ),
    make_record(
        name="MPSJ Street Parking – Putra Heights",
        operator="MPSJ",
        type="street",
        parking_class="normal",
        address="Jalan Putra Perdana 3, Putra Heights, Subang Jaya",
        city="Subang Jaya",
        state="Selangor",
        latitude=3.0178,
        longitude=101.5638,
        rate_per_hour=0.50,
        motorcycle_rate=0.20,
        daily_max_cap=5.00,
        operating_hours="Mon–Sat 08:00–18:00",
        payment_method="Coupon, ParkMate App",
        source_url=SOURCE_URL,
    ),
]


class MPSJScraper(BaseScraper):
    """Scrapes MPSJ parking data for Subang Jaya."""

    def scrape(self) -> List[Dict[str, Any]]:
        self.logger.info("Starting MPSJ scrape …")
        try:
            results = self._scrape_live()
            if results:
                self.logger.info("MPSJ live scrape returned %d records", len(results))
                return results
        except Exception as exc:
            self.logger.warning("MPSJ live scrape failed (%s) – using fallback", exc)
        self.logger.info("MPSJ using %d fallback records", len(FALLBACK_DATA))
        return FALLBACK_DATA

    def _scrape_live(self) -> List[Dict[str, Any]]:
        if not self.can_fetch(SOURCE_URL):
            return []
        page = self.soup(SOURCE_URL + "/en/parking")
        if page is None:
            return []
        tables = page.find_all("table")
        records: List[Dict[str, Any]] = []
        for table in tables:
            for row in table.find_all("tr")[1:]:
                cells = [td.get_text(strip=True) for td in row.find_all("td")]
                if len(cells) < 2:
                    continue
                rec = make_record(
                    name=cells[0],
                    operator="MPSJ",
                    type="street",
                    city="Subang Jaya",
                    state="Selangor",
                    rate_per_hour=self.safe_float(cells[1]) if len(cells) > 1 else None,
                    source_url=SOURCE_URL,
                )
                records.append(rec)
        return records
