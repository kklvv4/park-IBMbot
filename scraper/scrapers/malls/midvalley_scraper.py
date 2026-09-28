"""
Mid Valley Megamall parking scraper. KL focus.
Source: https://www.midvalley.com.my
"""

from typing import List, Dict, Any
from scrapers.base_scraper import BaseScraper, make_record

SOURCE_URL = "https://www.midvalley.com.my"

FALLBACK_DATA: List[Dict[str, Any]] = [
    make_record(
        name="Mid Valley Megamall Car Park",
        operator="IGB Corporation",
        type="mall",
        parking_class="normal",
        address="Mid Valley City, Lingkaran Syed Putra, 59200 Kuala Lumpur",
        city="Kuala Lumpur",
        state="Wilayah Persekutuan",
        latitude=3.1183,
        longitude=101.6779,
        rate_per_hour=2.00,
        first_hour_rate=2.00,
        first_hour_free="NO",
        motorcycle_rate=0.50,
        daily_max_cap=20.00,
        total_bays=6500,
        operating_hours="Mon–Sun 10:00–22:00",
        payment_method="Cash, Touch 'n Go, Card, JomParking",
        is_online_bookable="NO",
        ev_charging="YES",
        disabled_bays="YES",
        source_url=SOURCE_URL + "/visitor-info/parking",
        notes="Largest parking in Mid Valley City; B1–B5 + rooftop",
    ),
    make_record(
        name="The Gardens Mall Car Park",
        operator="IGB Corporation",
        type="mall",
        parking_class="premium",
        address="Mid Valley City, Lingkaran Syed Putra, 59200 Kuala Lumpur",
        city="Kuala Lumpur",
        state="Wilayah Persekutuan",
        latitude=3.1190,
        longitude=101.6768,
        rate_per_hour=3.00,
        first_hour_rate=3.00,
        motorcycle_rate=1.00,
        daily_max_cap=25.00,
        total_bays=2500,
        operating_hours="Mon–Sun 10:00–22:00",
        payment_method="Cash, Touch 'n Go, Card",
        ev_charging="YES",
        disabled_bays="YES",
        source_url=SOURCE_URL + "/visitor-info/parking",
        notes="Premium annexe; shared with Mid Valley",
    ),
]


class MidValleyScraper(BaseScraper):
    """Scrapes Mid Valley parking rates."""

    def scrape(self) -> List[Dict[str, Any]]:
        self.logger.info("Starting Mid Valley scrape …")
        try:
            results = self._scrape_live()
            if results:
                self.logger.info("Mid Valley live scrape returned %d records", len(results))
                return results
        except Exception as exc:
            self.logger.warning("Mid Valley live scrape failed (%s) – using fallback", exc)
        self.logger.info("Mid Valley using %d fallback records", len(FALLBACK_DATA))
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
                    name=f"Mid Valley – {cells[0]}",
                    operator="IGB Corporation",
                    type="mall",
                    city="Kuala Lumpur",
                    state="Wilayah Persekutuan",
                    latitude=3.1183,
                    longitude=101.6779,
                    rate_per_hour=self.safe_float(cells[1]) if len(cells) > 1 else None,
                    source_url=url,
                )
                records.append(rec)
        return records
