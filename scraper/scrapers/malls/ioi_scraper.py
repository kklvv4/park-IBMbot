"""
IOI City Mall parking scraper. Selangor (Putrajaya fringe) focus.
Source: https://www.ioicitymall.com.my
"""

from typing import List, Dict, Any
from scrapers.base_scraper import BaseScraper, make_record

SOURCE_URL = "https://www.ioicitymall.com.my"

FALLBACK_DATA: List[Dict[str, Any]] = [
    make_record(
        name="IOI City Mall Car Park",
        operator="IOI Properties",
        type="mall",
        parking_class="normal",
        address="IOI Resort City, 62502 Putrajaya, Selangor",
        city="Putrajaya",
        state="Selangor",
        latitude=2.9706,
        longitude=101.7241,
        rate_per_hour=2.00,
        first_hour_rate=2.00,
        first_hour_free="NO",
        motorcycle_rate=0.50,
        daily_max_cap=16.00,
        total_bays=8000,
        operating_hours="Mon–Sun 10:00–22:00",
        payment_method="Cash, Touch 'n Go, Card, JomParking",
        is_online_bookable="NO",
        ev_charging="YES",
        disabled_bays="YES",
        source_url=SOURCE_URL + "/visitor-info",
        notes="IOI City Mall 1 & 2 combined; largest in south KL corridor",
    ),
    make_record(
        name="IOI Mall Puchong Car Park",
        operator="IOI Properties",
        type="mall",
        parking_class="normal",
        address="Jalan Puchong, 47100 Puchong, Selangor",
        city="Puchong",
        state="Selangor",
        latitude=3.0247,
        longitude=101.6195,
        rate_per_hour=2.00,
        first_hour_rate=2.00,
        motorcycle_rate=0.50,
        daily_max_cap=15.00,
        total_bays=3500,
        operating_hours="Mon–Sun 10:00–22:00",
        payment_method="Cash, Touch 'n Go, Card",
        ev_charging="NO",
        disabled_bays="YES",
        source_url=SOURCE_URL,
    ),
]


class IOIScraper(BaseScraper):
    """Scrapes IOI City Mall parking rates."""

    def scrape(self) -> List[Dict[str, Any]]:
        self.logger.info("Starting IOI City Mall scrape …")
        try:
            results = self._scrape_live()
            if results:
                self.logger.info("IOI live scrape returned %d records", len(results))
                return results
        except Exception as exc:
            self.logger.warning("IOI live scrape failed (%s) – using fallback", exc)
        self.logger.info("IOI using %d fallback records", len(FALLBACK_DATA))
        return FALLBACK_DATA

    def _scrape_live(self) -> List[Dict[str, Any]]:
        url = SOURCE_URL + "/visitor-info"
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
                    name=f"IOI City Mall – {cells[0]}",
                    operator="IOI Properties",
                    type="mall",
                    city="Putrajaya",
                    state="Selangor",
                    latitude=2.9706,
                    longitude=101.7241,
                    rate_per_hour=self.safe_float(cells[1]) if len(cells) > 1 else None,
                    source_url=url,
                )
                records.append(rec)
        return records
