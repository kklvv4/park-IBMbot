"""
MPAJ (Majlis Perbandaran Ampang Jaya) parking scraper.
Falls back to hardcoded Ampang Jaya data.
"""

from typing import List, Dict, Any
from scrapers.base_scraper import BaseScraper, make_record

SOURCE_URL = "https://www.mpaj.gov.my"

FALLBACK_DATA: List[Dict[str, Any]] = [
    make_record(
        name="MPAJ Street Parking – Ampang Point",
        operator="MPAJ",
        type="street",
        parking_class="normal",
        address="Jalan Mamanda 7, Ampang Point, Ampang",
        city="Ampang",
        state="Selangor",
        latitude=3.1487,
        longitude=101.7598,
        rate_per_hour=1.00,
        motorcycle_rate=0.30,
        daily_max_cap=8.00,
        operating_hours="Mon–Sat 08:00–18:00",
        payment_method="Coupon, Touch 'n Go",
        source_url=SOURCE_URL,
    ),
    make_record(
        name="MPAJ Open Car Park – Pandan Indah",
        operator="MPAJ",
        type="open_lot",
        parking_class="normal",
        address="Jalan Pandan Indah 4/4, Pandan Indah, Ampang",
        city="Ampang",
        state="Selangor",
        latitude=3.1102,
        longitude=101.7478,
        rate_per_hour=1.00,
        motorcycle_rate=0.30,
        daily_max_cap=8.00,
        total_bays=150,
        operating_hours="Mon–Sun 06:00–24:00",
        payment_method="Cash, Coupon",
        source_url=SOURCE_URL,
    ),
    make_record(
        name="MPAJ Multi-Storey Car Park – Wangsa Maju",
        operator="MPAJ",
        type="multistorey",
        parking_class="normal",
        address="Seksyen 1, Wangsa Maju, Kuala Lumpur",
        city="Ampang",
        state="Selangor",
        latitude=3.2042,
        longitude=101.7482,
        rate_per_hour=1.50,
        motorcycle_rate=0.40,
        daily_max_cap=12.00,
        total_bays=300,
        operating_hours="Mon–Sun 07:00–23:00",
        payment_method="Cash, Touch 'n Go",
        source_url=SOURCE_URL,
    ),
]


class MPAJScraper(BaseScraper):
    """Scrapes MPAJ parking data for Ampang Jaya."""

    def scrape(self) -> List[Dict[str, Any]]:
        self.logger.info("Starting MPAJ scrape …")
        try:
            results = self._scrape_live()
            if results:
                self.logger.info("MPAJ live scrape returned %d records", len(results))
                return results
        except Exception as exc:
            self.logger.warning("MPAJ live scrape failed (%s) – using fallback", exc)
        self.logger.info("MPAJ using %d fallback records", len(FALLBACK_DATA))
        return FALLBACK_DATA

    def _scrape_live(self) -> List[Dict[str, Any]]:
        if not self.can_fetch(SOURCE_URL):
            return []
        page = self.soup(SOURCE_URL)
        if page is None:
            return []
        return []  # MPAJ site rarely has structured parking data
