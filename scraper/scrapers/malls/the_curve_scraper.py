"""
The Curve / IPC Shopping Centre parking scraper. Selangor focus.
Source: https://www.thecurve.com.my
"""

from typing import List, Dict, Any
from scrapers.base_scraper import BaseScraper, make_record

SOURCE_URL = "https://www.thecurve.com.my"

FALLBACK_DATA: List[Dict[str, Any]] = [
    make_record(
        name="The Curve Shopping Centre Car Park",
        operator="The Curve",
        type="mall",
        parking_class="normal",
        address="6, Jalan PJU 7/3, Mutiara Damansara, 47810 Petaling Jaya, Selangor",
        city="Petaling Jaya",
        state="Selangor",
        latitude=3.1572,
        longitude=101.6100,
        rate_per_hour=2.00,
        first_hour_rate=2.00,
        first_hour_free="NO",
        motorcycle_rate=0.50,
        daily_max_cap=16.00,
        total_bays=3800,
        operating_hours="Mon–Sun 10:00–22:00",
        payment_method="Cash, Touch 'n Go, Card, JomParking",
        is_online_bookable="NO",
        ev_charging="YES",
        disabled_bays="YES",
        source_url=SOURCE_URL + "/getting-here",
        notes="Shared lot with IPC Shopping Centre and IKEA Damansara",
    ),
    make_record(
        name="IPC Shopping Centre Car Park",
        operator="IPC Shopping Centre",
        type="mall",
        parking_class="normal",
        address="2, Jalan PJU 7/2, Mutiara Damansara, 47810 Petaling Jaya, Selangor",
        city="Petaling Jaya",
        state="Selangor",
        latitude=3.1565,
        longitude=101.6085,
        rate_per_hour=2.00,
        first_hour_rate=2.00,
        motorcycle_rate=0.50,
        daily_max_cap=16.00,
        total_bays=2500,
        operating_hours="Mon–Sun 10:00–22:00",
        payment_method="Cash, Touch 'n Go, Card",
        ev_charging="YES",
        disabled_bays="YES",
        source_url="https://www.ipcshopping.com.my",
        notes="Adjacent to The Curve; shares parking zone",
    ),
    make_record(
        name="Ikano Power Centre (IKEA Damansara) Car Park",
        operator="Ikano",
        type="mall",
        parking_class="normal",
        address="2, Jalan PJU 7/2, Mutiara Damansara, 47810 Petaling Jaya, Selangor",
        city="Petaling Jaya",
        state="Selangor",
        latitude=3.1580,
        longitude=101.6094,
        rate_per_hour=2.00,
        first_hour_free="YES",
        motorcycle_rate=0.50,
        daily_max_cap=16.00,
        total_bays=1500,
        operating_hours="Mon–Sun 10:00–22:00",
        payment_method="Cash, Touch 'n Go, Card",
        ev_charging="YES",
        disabled_bays="YES",
        source_url="https://www.ikea.com/my/en/stores/damansara/",
        notes="1st hour free with IKEA purchase validation",
    ),
]


class TheCurveScraper(BaseScraper):
    """Scrapes The Curve / IPC parking rates."""

    def scrape(self) -> List[Dict[str, Any]]:
        self.logger.info("Starting The Curve scrape …")
        try:
            results = self._scrape_live()
            if results:
                self.logger.info("The Curve live scrape returned %d records", len(results))
                return results
        except Exception as exc:
            self.logger.warning("The Curve live scrape failed (%s) – using fallback", exc)
        self.logger.info("The Curve using %d fallback records", len(FALLBACK_DATA))
        return FALLBACK_DATA

    def _scrape_live(self) -> List[Dict[str, Any]]:
        url = SOURCE_URL + "/getting-here"
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
                    name=f"The Curve – {cells[0]}",
                    operator="The Curve",
                    type="mall",
                    city="Petaling Jaya",
                    state="Selangor",
                    latitude=3.1572,
                    longitude=101.6100,
                    rate_per_hour=self.safe_float(cells[1]) if len(cells) > 1 else None,
                    source_url=url,
                )
                records.append(rec)
        return records
