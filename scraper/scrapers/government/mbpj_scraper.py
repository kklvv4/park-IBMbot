"""
MBPJ (Majlis Bandaraya Petaling Jaya) parking scraper.
Targets: https://www.mbpj.gov.my
Falls back to hardcoded PJ data.
"""

from typing import List, Dict, Any
from scrapers.base_scraper import BaseScraper, make_record

SOURCE_URL = "https://www.mbpj.gov.my"

FALLBACK_DATA: List[Dict[str, Any]] = [
    make_record(
        name="MBPJ Street Parking – SS2",
        operator="MBPJ",
        type="street",
        parking_class="normal",
        address="Jalan SS2/72, SS2, Petaling Jaya",
        city="Petaling Jaya",
        state="Selangor",
        latitude=3.1147,
        longitude=101.6266,
        rate_per_hour=1.00,
        motorcycle_rate=0.30,
        daily_max_cap=8.00,
        operating_hours="Mon–Sat 08:00–18:00",
        payment_method="Coupon, Touch 'n Go, MBPJ App",
        source_url=SOURCE_URL,
        notes="Zone A – commercial streets",
    ),
    make_record(
        name="MBPJ Street Parking – PJ Old Town",
        operator="MBPJ",
        type="street",
        parking_class="normal",
        address="Jalan Kemajuan, PJ Old Town, Petaling Jaya",
        city="Petaling Jaya",
        state="Selangor",
        latitude=3.1046,
        longitude=101.6360,
        rate_per_hour=1.00,
        motorcycle_rate=0.30,
        daily_max_cap=8.00,
        operating_hours="Mon–Sat 08:00–18:00",
        payment_method="Coupon, Touch 'n Go, MBPJ App",
        source_url=SOURCE_URL,
    ),
    make_record(
        name="MBPJ Multi-Storey Car Park – Damansara Uptown",
        operator="MBPJ",
        type="multistorey",
        parking_class="normal",
        address="Jalan SS21/37, Damansara Utama, Petaling Jaya",
        city="Petaling Jaya",
        state="Selangor",
        latitude=3.1330,
        longitude=101.6237,
        rate_per_hour=2.00,
        motorcycle_rate=0.50,
        daily_max_cap=15.00,
        total_bays=400,
        operating_hours="Mon–Sun 07:00–23:00",
        payment_method="Cash, Touch 'n Go",
        source_url=SOURCE_URL,
    ),
    make_record(
        name="MBPJ Open Car Park – Section 14",
        operator="MBPJ",
        type="open_lot",
        parking_class="normal",
        address="Section 14, Petaling Jaya",
        city="Petaling Jaya",
        state="Selangor",
        latitude=3.1121,
        longitude=101.6431,
        rate_per_hour=1.00,
        motorcycle_rate=0.30,
        daily_max_cap=8.00,
        total_bays=200,
        operating_hours="Mon–Sun 06:00–24:00",
        payment_method="Cash, Coupon",
        source_url=SOURCE_URL,
    ),
    make_record(
        name="MBPJ Street Parking – Ara Damansara",
        operator="MBPJ",
        type="street",
        parking_class="normal",
        address="Jalan PJU 1A, Ara Damansara, Petaling Jaya",
        city="Petaling Jaya",
        state="Selangor",
        latitude=3.1218,
        longitude=101.5793,
        rate_per_hour=1.00,
        motorcycle_rate=0.30,
        daily_max_cap=8.00,
        operating_hours="Mon–Sat 08:00–18:00",
        payment_method="Coupon, MBPJ App",
        source_url=SOURCE_URL,
    ),
]


class MBPJScraper(BaseScraper):
    """Scrapes MBPJ parking data for Petaling Jaya."""

    def scrape(self) -> List[Dict[str, Any]]:
        self.logger.info("Starting MBPJ scrape …")
        try:
            results = self._scrape_live()
            if results:
                self.logger.info("MBPJ live scrape returned %d records", len(results))
                return results
        except Exception as exc:
            self.logger.warning("MBPJ live scrape failed (%s) – using fallback", exc)
        self.logger.info("MBPJ using %d fallback records", len(FALLBACK_DATA))
        return FALLBACK_DATA

    def _scrape_live(self) -> List[Dict[str, Any]]:
        if not self.can_fetch(SOURCE_URL):
            return []
        page = self.soup(SOURCE_URL + "/parking")
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
                    operator="MBPJ",
                    type="street",
                    parking_class="normal",
                    city="Petaling Jaya",
                    state="Selangor",
                    rate_per_hour=self.safe_float(cells[1]) if len(cells) > 1 else None,
                    source_url=SOURCE_URL,
                )
                records.append(rec)
        return records
