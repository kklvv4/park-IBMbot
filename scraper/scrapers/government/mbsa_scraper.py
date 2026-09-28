"""
MBSA (Majlis Bandaraya Shah Alam) parking scraper.
Targets: https://www.mbsa.gov.my
Falls back to hardcoded Shah Alam data.
"""

from typing import List, Dict, Any
from scrapers.base_scraper import BaseScraper, make_record

SOURCE_URL = "https://www.mbsa.gov.my"

FALLBACK_DATA: List[Dict[str, Any]] = [
    make_record(
        name="MBSA Street Parking – Shah Alam City Centre",
        operator="MBSA",
        type="street",
        parking_class="normal",
        address="Persiaran Perbandaran, Shah Alam City Centre",
        city="Shah Alam",
        state="Selangor",
        latitude=3.0738,
        longitude=101.5183,
        rate_per_hour=1.00,
        motorcycle_rate=0.30,
        daily_max_cap=8.00,
        operating_hours="Mon–Sat 08:00–18:00",
        payment_method="Coupon, Touch 'n Go, ParkMate App",
        source_url=SOURCE_URL,
        notes="Shah Alam City Centre zone",
    ),
    make_record(
        name="MBSA Multi-Storey Car Park – Plaza Masalam",
        operator="MBSA",
        type="multistorey",
        parking_class="normal",
        address="Persiaran Masjid, Section 14, Shah Alam",
        city="Shah Alam",
        state="Selangor",
        latitude=3.0762,
        longitude=101.5156,
        rate_per_hour=1.00,
        motorcycle_rate=0.30,
        daily_max_cap=10.00,
        total_bays=500,
        operating_hours="Mon–Sun 07:00–23:00",
        payment_method="Cash, Touch 'n Go",
        source_url=SOURCE_URL,
    ),
    make_record(
        name="MBSA Open Car Park – Section 7",
        operator="MBSA",
        type="open_lot",
        parking_class="normal",
        address="Section 7, Shah Alam",
        city="Shah Alam",
        state="Selangor",
        latitude=3.0825,
        longitude=101.5290,
        rate_per_hour=1.00,
        motorcycle_rate=0.30,
        daily_max_cap=8.00,
        total_bays=180,
        operating_hours="Mon–Sun 06:00–24:00",
        payment_method="Cash, Coupon",
        source_url=SOURCE_URL,
    ),
    make_record(
        name="MBSA Street Parking – Seksyen 9",
        operator="MBSA",
        type="street",
        parking_class="normal",
        address="Jalan Seksyen 9/1, Shah Alam",
        city="Shah Alam",
        state="Selangor",
        latitude=3.0930,
        longitude=101.5430,
        rate_per_hour=0.50,
        motorcycle_rate=0.20,
        daily_max_cap=5.00,
        operating_hours="Mon–Sat 08:00–18:00",
        payment_method="Coupon, ParkMate App",
        source_url=SOURCE_URL,
    ),
]


class MBSAScraper(BaseScraper):
    """Scrapes MBSA parking data for Shah Alam."""

    def scrape(self) -> List[Dict[str, Any]]:
        self.logger.info("Starting MBSA scrape …")
        try:
            results = self._scrape_live()
            if results:
                self.logger.info("MBSA live scrape returned %d records", len(results))
                return results
        except Exception as exc:
            self.logger.warning("MBSA live scrape failed (%s) – using fallback", exc)
        self.logger.info("MBSA using %d fallback records", len(FALLBACK_DATA))
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
                    operator="MBSA",
                    type="street",
                    city="Shah Alam",
                    state="Selangor",
                    rate_per_hour=self.safe_float(cells[1]) if len(cells) > 1 else None,
                    source_url=SOURCE_URL,
                )
                records.append(rec)
        return records
