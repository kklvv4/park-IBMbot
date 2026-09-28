"""
Pavilion KL parking scraper. KL focus.
Source: https://www.pavilion-kl.com
"""

from typing import List, Dict, Any
from scrapers.base_scraper import BaseScraper, make_record

SOURCE_URL = "https://www.pavilion-kl.com"

FALLBACK_DATA: List[Dict[str, Any]] = [
    make_record(
        name="Pavilion Kuala Lumpur Car Park",
        operator="Pavilion KL",
        type="mall",
        parking_class="normal",
        address="168, Jalan Bukit Bintang, 55100 Kuala Lumpur",
        city="Kuala Lumpur",
        state="Wilayah Persekutuan",
        latitude=3.1488,
        longitude=101.7133,
        rate_per_hour=3.00,
        first_hour_rate=3.00,
        first_hour_free="NO",
        motorcycle_rate=1.00,
        daily_max_cap=25.00,
        total_bays=5000,
        operating_hours="Mon–Sun 10:00–22:00",
        payment_method="Cash, Touch 'n Go, Card, JomParking",
        is_online_bookable="NO",
        ev_charging="YES",
        disabled_bays="YES",
        source_url=SOURCE_URL + "/visitor-info/car-park",
        notes="Basement B1–B5; 1st hr RM3, daily max RM25",
    ),
    make_record(
        name="Pavilion Elite Car Park",
        operator="Pavilion KL",
        type="mall",
        parking_class="premium",
        address="170, Jalan Bukit Bintang, 55100 Kuala Lumpur",
        city="Kuala Lumpur",
        state="Wilayah Persekutuan",
        latitude=3.1482,
        longitude=101.7140,
        rate_per_hour=4.00,
        first_hour_rate=4.00,
        motorcycle_rate=1.50,
        daily_max_cap=30.00,
        total_bays=800,
        operating_hours="Mon–Sun 10:00–22:00",
        payment_method="Cash, Touch 'n Go, Card",
        is_online_bookable="NO",
        ev_charging="YES",
        disabled_bays="YES",
        source_url=SOURCE_URL + "/visitor-info/car-park",
        notes="Connected to Pavilion Elite extension",
    ),
]


class PavilionScraper(BaseScraper):
    """Scrapes Pavilion KL parking rates."""

    def scrape(self) -> List[Dict[str, Any]]:
        self.logger.info("Starting Pavilion KL scrape …")
        try:
            results = self._scrape_live()
            if results:
                self.logger.info("Pavilion live scrape returned %d records", len(results))
                return results
        except Exception as exc:
            self.logger.warning("Pavilion live scrape failed (%s) – using fallback", exc)
        self.logger.info("Pavilion using %d fallback records", len(FALLBACK_DATA))
        return FALLBACK_DATA

    def _scrape_live(self) -> List[Dict[str, Any]]:
        url = SOURCE_URL + "/visitor-info/car-park"
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
                    name=f"Pavilion KL – {cells[0]}",
                    operator="Pavilion KL",
                    type="mall",
                    city="Kuala Lumpur",
                    state="Wilayah Persekutuan",
                    latitude=3.1488,
                    longitude=101.7133,
                    rate_per_hour=self.safe_float(cells[1]) if len(cells) > 1 else None,
                    source_url=url,
                )
                records.append(rec)
        return records
