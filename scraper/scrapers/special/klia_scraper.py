"""
KLIA / klia2 airport parking scraper.
Source: https://www.klia.com.my/transport/parking/
KLIA is in Sepang, Selangor — within KL & Selangor scope.
"""

from typing import List, Dict, Any
from scrapers.base_scraper import BaseScraper, make_record

SOURCE_URL = "https://www.klia.com.my/transport/parking/"

FALLBACK_DATA: List[Dict[str, Any]] = [
    make_record(
        name="KLIA – Short-Term Car Park (Level 1)",
        operator="Malaysia Airports Holdings Berhad",
        type="airport",
        parking_class="normal",
        address="KL International Airport, 64000 Sepang, Selangor",
        city="Sepang",
        state="Selangor",
        latitude=2.7456,
        longitude=101.7099,
        rate_per_hour=4.00,
        motorcycle_rate=2.00,
        daily_max_cap=60.00,
        operating_hours="Mon–Sun 24hrs",
        payment_method="Cash, Touch 'n Go, Card, JomParking",
        is_online_bookable="YES",
        booking_platform="klia2.info / MAHB App",
        total_bays=800,
        ev_charging="YES",
        disabled_bays="YES",
        source_url=SOURCE_URL,
        notes="Covered short-stay directly connected to KLIA main terminal",
    ),
    make_record(
        name="KLIA – Long-Term Car Park (Remote Lot)",
        operator="Malaysia Airports Holdings Berhad",
        type="airport",
        parking_class="normal",
        address="KL International Airport, 64000 Sepang, Selangor",
        city="Sepang",
        state="Selangor",
        latitude=2.7400,
        longitude=101.7050,
        rate_per_hour=None,
        daily_max_cap=10.00,
        overnight_rate=10.00,
        motorcycle_rate=5.00,
        operating_hours="Mon–Sun 24hrs",
        payment_method="Cash, Touch 'n Go, Card",
        is_online_bookable="YES",
        booking_platform="MAHB App",
        total_bays=5000,
        ev_charging="NO",
        disabled_bays="YES",
        source_url=SOURCE_URL,
        notes="RM10/day; free shuttle to KLIA terminal",
    ),
    make_record(
        name="klia2 – Short-Term Car Park",
        operator="Malaysia Airports Holdings Berhad",
        type="airport",
        parking_class="normal",
        address="klia2, 64000 Sepang, Selangor",
        city="Sepang",
        state="Selangor",
        latitude=2.7447,
        longitude=101.6993,
        rate_per_hour=4.00,
        motorcycle_rate=2.00,
        daily_max_cap=60.00,
        operating_hours="Mon–Sun 24hrs",
        payment_method="Cash, Touch 'n Go, Card",
        is_online_bookable="YES",
        booking_platform="MAHB App",
        total_bays=1200,
        ev_charging="YES",
        disabled_bays="YES",
        source_url=SOURCE_URL,
        notes="Adjacent to klia2 budget terminal",
    ),
    make_record(
        name="klia2 – Long-Term Car Park (Remote Lot)",
        operator="Malaysia Airports Holdings Berhad",
        type="airport",
        parking_class="normal",
        address="klia2, 64000 Sepang, Selangor",
        city="Sepang",
        state="Selangor",
        latitude=2.7380,
        longitude=101.6980,
        rate_per_hour=None,
        daily_max_cap=8.00,
        overnight_rate=8.00,
        motorcycle_rate=4.00,
        operating_hours="Mon–Sun 24hrs",
        payment_method="Cash, Touch 'n Go, Card",
        is_online_bookable="YES",
        booking_platform="MAHB App",
        total_bays=3000,
        ev_charging="NO",
        disabled_bays="YES",
        source_url=SOURCE_URL,
        notes="RM8/day; shuttle to klia2",
    ),
    make_record(
        name="KLIA – Valet Parking (Departure Level)",
        operator="Malaysia Airports Holdings Berhad",
        type="valet",
        parking_class="valet",
        address="KL International Airport, 64000 Sepang, Selangor",
        city="Sepang",
        state="Selangor",
        latitude=2.7458,
        longitude=101.7102,
        valet_rate=None,
        daily_max_cap=80.00,
        operating_hours="Mon–Sun 24hrs",
        payment_method="Cash, Card",
        source_url=SOURCE_URL,
        notes="Premium valet at KLIA departure; ~RM80/day",
    ),
]


class KLIAScraper(BaseScraper):
    """Scrapes KLIA/klia2 airport parking rates."""

    def scrape(self) -> List[Dict[str, Any]]:
        self.logger.info("Starting KLIA scrape …")
        try:
            results = self._scrape_live()
            if results:
                self.logger.info("KLIA live scrape returned %d records", len(results))
                return results
        except Exception as exc:
            self.logger.warning("KLIA live scrape failed (%s) – using fallback", exc)
        self.logger.info("KLIA using %d fallback records", len(FALLBACK_DATA))
        return FALLBACK_DATA

    def _scrape_live(self) -> List[Dict[str, Any]]:
        if not self.can_fetch(SOURCE_URL):
            return []
        page = self.soup(SOURCE_URL)
        if page is None:
            return []
        records: List[Dict[str, Any]] = []
        for table in page.find_all("table"):
            for row in table.find_all("tr")[1:]:
                cells = [td.get_text(strip=True) for td in row.find_all("td")]
                if len(cells) < 2:
                    continue
                rec = make_record(
                    name=f"KLIA – {cells[0]}",
                    operator="Malaysia Airports Holdings Berhad",
                    type="airport",
                    city="Sepang",
                    state="Selangor",
                    latitude=2.7456,
                    longitude=101.7099,
                    rate_per_hour=self.safe_float(cells[1]) if len(cells) > 1 else None,
                    source_url=SOURCE_URL,
                )
                records.append(rec)
        return records
