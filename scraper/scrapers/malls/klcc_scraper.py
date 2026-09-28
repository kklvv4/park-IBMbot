"""
KLCC / Suria KLCC parking scraper. KL & Selangor focus.
Source: https://www.klcc.com.my
"""

from typing import List, Dict, Any
from scrapers.base_scraper import BaseScraper, make_record

SOURCE_URL = "https://www.klcc.com.my"

FALLBACK_DATA: List[Dict[str, Any]] = [
    make_record(
        name="Suria KLCC Car Park",
        operator="KLCC (Holdings) Sdn Bhd",
        type="mall",
        parking_class="normal",
        address="Kuala Lumpur City Centre, 50088 Kuala Lumpur",
        city="Kuala Lumpur",
        state="Wilayah Persekutuan",
        latitude=3.1578,
        longitude=101.7123,
        rate_per_hour=3.00,
        first_hour_rate=2.00,
        first_hour_free="NO",
        motorcycle_rate=1.00,
        daily_max_cap=20.00,
        total_bays=5700,
        operating_hours="Mon–Sun 09:00–22:00",
        payment_method="Cash, Touch 'n Go, Card, JomParking",
        is_online_bookable="NO",
        ev_charging="YES",
        disabled_bays="YES",
        source_url=SOURCE_URL + "/visit/getting-here/parking",
        notes="First 2 hrs RM2 each; daily max RM20; basement B1–B3",
    ),
    make_record(
        name="Mandarin Oriental KL – Public Car Park",
        operator="KLCC (Holdings) Sdn Bhd",
        type="multistorey",
        parking_class="normal",
        address="Kuala Lumpur City Centre, 50088 Kuala Lumpur",
        city="Kuala Lumpur",
        state="Wilayah Persekutuan",
        latitude=3.1557,
        longitude=101.7148,
        rate_per_hour=4.00,
        motorcycle_rate=1.50,
        daily_max_cap=30.00,
        total_bays=500,
        operating_hours="Mon–Sun 24hrs",
        payment_method="Cash, Touch 'n Go, Card",
        ev_charging="YES",
        disabled_bays="YES",
        source_url=SOURCE_URL,
        notes="Adjacent to Mandarin Oriental hotel",
    ),
]


class KLCCScraper(BaseScraper):
    """Scrapes KLCC parking rates."""

    def scrape(self) -> List[Dict[str, Any]]:
        self.logger.info("Starting KLCC scrape …")
        try:
            results = self._scrape_live()
            if results:
                self.logger.info("KLCC live scrape returned %d records", len(results))
                return results
        except Exception as exc:
            self.logger.warning("KLCC live scrape failed (%s) – using fallback", exc)
        self.logger.info("KLCC using %d fallback records", len(FALLBACK_DATA))
        return FALLBACK_DATA

    def _scrape_live(self) -> List[Dict[str, Any]]:
        url = SOURCE_URL + "/visit/getting-here/parking"
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
                    name=f"KLCC – {cells[0]}",
                    operator="KLCC (Holdings) Sdn Bhd",
                    type="mall",
                    city="Kuala Lumpur",
                    state="Wilayah Persekutuan",
                    latitude=3.1578,
                    longitude=101.7123,
                    rate_per_hour=self.safe_float(cells[1]) if len(cells) > 1 else None,
                    source_url=url,
                )
                records.append(rec)
        return records
