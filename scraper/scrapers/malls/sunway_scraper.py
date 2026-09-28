"""
Sunway Pyramid parking scraper. Selangor focus.
Source: https://www.sunwaypyramid.com
"""

from typing import List, Dict, Any
from scrapers.base_scraper import BaseScraper, make_record

SOURCE_URL = "https://www.sunwaypyramid.com"

FALLBACK_DATA: List[Dict[str, Any]] = [
    make_record(
        name="Sunway Pyramid Car Park",
        operator="Sunway Malls",
        type="mall",
        parking_class="normal",
        address="3, Jalan PJS 11/15, Bandar Sunway, 47500 Subang Jaya, Selangor",
        city="Subang Jaya",
        state="Selangor",
        latitude=3.0732,
        longitude=101.6070,
        rate_per_hour=2.00,
        first_hour_rate=2.00,
        first_hour_free="NO",
        motorcycle_rate=0.50,
        daily_max_cap=15.00,
        total_bays=7000,
        operating_hours="Mon–Sun 10:00–22:00",
        payment_method="Cash, Touch 'n Go, Card, JomParking",
        is_online_bookable="NO",
        ev_charging="YES",
        disabled_bays="YES",
        source_url=SOURCE_URL + "/visitor-guide/car-park",
        notes="One of the largest malls in Selangor; B1–B4 + open lot",
    ),
    make_record(
        name="Sunway Velocity Car Park",
        operator="Sunway Malls",
        type="mall",
        parking_class="normal",
        address="Lingkaran SV, Sunway Velocity, 55100 Kuala Lumpur",
        city="Kuala Lumpur",
        state="Wilayah Persekutuan",
        latitude=3.1141,
        longitude=101.7282,
        rate_per_hour=2.00,
        first_hour_rate=2.00,
        motorcycle_rate=0.50,
        daily_max_cap=18.00,
        total_bays=3200,
        operating_hours="Mon–Sun 10:00–22:00",
        payment_method="Cash, Touch 'n Go, Card",
        ev_charging="YES",
        disabled_bays="YES",
        source_url=SOURCE_URL,
        notes="Cheras location",
    ),
]


class SunwayScraper(BaseScraper):
    """Scrapes Sunway mall parking rates."""

    def scrape(self) -> List[Dict[str, Any]]:
        self.logger.info("Starting Sunway scrape …")
        try:
            results = self._scrape_live()
            if results:
                self.logger.info("Sunway live scrape returned %d records", len(results))
                return results
        except Exception as exc:
            self.logger.warning("Sunway live scrape failed (%s) – using fallback", exc)
        self.logger.info("Sunway using %d fallback records", len(FALLBACK_DATA))
        return FALLBACK_DATA

    def _scrape_live(self) -> List[Dict[str, Any]]:
        url = SOURCE_URL + "/visitor-guide/car-park"
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
                    name=f"Sunway – {cells[0]}",
                    operator="Sunway Malls",
                    type="mall",
                    city="Subang Jaya",
                    state="Selangor",
                    latitude=3.0732,
                    longitude=101.6070,
                    rate_per_hour=self.safe_float(cells[1]) if len(cells) > 1 else None,
                    source_url=url,
                )
                records.append(rec)
        return records
