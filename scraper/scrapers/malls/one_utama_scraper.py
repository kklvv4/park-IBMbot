"""
1 Utama Shopping Centre parking scraper. Selangor focus.
Source: https://www.1utama.com.my
"""

from typing import List, Dict, Any
from scrapers.base_scraper import BaseScraper, make_record

SOURCE_URL = "https://www.1utama.com.my"

FALLBACK_DATA: List[Dict[str, Any]] = [
    make_record(
        name="1 Utama Shopping Centre Car Park",
        operator="1 Utama",
        type="mall",
        parking_class="normal",
        address="1, Lebuh Bandar Utama, Bandar Utama, 47800 Petaling Jaya, Selangor",
        city="Petaling Jaya",
        state="Selangor",
        latitude=3.1515,
        longitude=101.6152,
        rate_per_hour=2.00,
        first_hour_rate=2.00,
        first_hour_free="NO",
        motorcycle_rate=0.50,
        daily_max_cap=18.00,
        total_bays=10000,
        operating_hours="Mon–Sun 10:00–22:00",
        payment_method="Cash, Touch 'n Go, Card, JomParking",
        is_online_bookable="NO",
        ev_charging="YES",
        disabled_bays="YES",
        source_url=SOURCE_URL + "/visitor-info/parking",
        notes="4th largest mall in Malaysia; rooftop + basement",
    ),
]


class OneUtamaScraper(BaseScraper):
    """Scrapes 1 Utama parking rates."""

    def scrape(self) -> List[Dict[str, Any]]:
        self.logger.info("Starting 1 Utama scrape …")
        try:
            results = self._scrape_live()
            if results:
                self.logger.info("1 Utama live scrape returned %d records", len(results))
                return results
        except Exception as exc:
            self.logger.warning("1 Utama live scrape failed (%s) – using fallback", exc)
        self.logger.info("1 Utama using %d fallback records", len(FALLBACK_DATA))
        return FALLBACK_DATA

    def _scrape_live(self) -> List[Dict[str, Any]]:
        url = SOURCE_URL + "/visitor-info/parking"
        if not self.can_fetch(url):
            return []
        page = self.soup(url)
        if page is None:
            return []
        records: List[Dict[str, Any]] = []
        for table in page.find_all("table"):
            for row in table.find_all("tr")[1:]:
                cells = [td.get_text(strip=True) for td in row.find_all("td")]
                if len(cells) < 2:
                    continue
                rec = make_record(
                    name=f"1 Utama – {cells[0]}",
                    operator="1 Utama",
                    type="mall",
                    city="Petaling Jaya",
                    state="Selangor",
                    latitude=3.1515,
                    longitude=101.6152,
                    rate_per_hour=self.safe_float(cells[1]) if len(cells) > 1 else None,
                    source_url=url,
                )
                records.append(rec)
        return records
