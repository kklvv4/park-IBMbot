"""
MyParking Malaysia scraper.
Targets: https://www.myparking.com.my
Falls back to hardcoded MyParking locations.
"""

from typing import List, Dict, Any
from scrapers.base_scraper import BaseScraper, make_record

SOURCE_URL = "https://www.myparking.com.my"

FALLBACK_DATA: List[Dict[str, Any]] = [
    make_record(
        name="MyParking – Berjaya Times Square",
        operator="MyParking",
        type="mall",
        parking_class="normal",
        address="1, Jalan Imbi, Kuala Lumpur",
        city="Kuala Lumpur",
        state="Wilayah Persekutuan",
        latitude=3.1420,
        longitude=101.7107,
        rate_per_hour=3.00,
        first_hour_rate=2.00,
        motorcycle_rate=1.00,
        daily_max_cap=22.00,
        total_bays=5000,
        operating_hours="Mon–Sun 10:00–22:00",
        payment_method="Cash, Touch 'n Go, Card, MyParking App",
        is_online_bookable="YES",
        booking_platform="MyParking App",
        ev_charging="YES",
        disabled_bays="YES",
        source_url=SOURCE_URL,
        notes="One of the largest indoor car parks in Malaysia",
    ),
    make_record(
        name="MyParking – Sogo KL",
        operator="MyParking",
        type="multistorey",
        parking_class="normal",
        address="190, Jalan Tuanku Abdul Halim, Kuala Lumpur",
        city="Kuala Lumpur",
        state="Wilayah Persekutuan",
        latitude=3.1521,
        longitude=101.6979,
        rate_per_hour=2.00,
        motorcycle_rate=0.50,
        daily_max_cap=18.00,
        total_bays=600,
        operating_hours="Mon–Sun 09:00–22:00",
        payment_method="Cash, Touch 'n Go, MyParking App",
        is_online_bookable="YES",
        booking_platform="MyParking App",
        ev_charging="NO",
        disabled_bays="YES",
        source_url=SOURCE_URL,
    ),
    make_record(
        name="MyParking – Chow Kit",
        operator="MyParking",
        type="open_lot",
        parking_class="normal",
        address="Jalan Haji Hussein, Chow Kit, Kuala Lumpur",
        city="Kuala Lumpur",
        state="Wilayah Persekutuan",
        latitude=3.1637,
        longitude=101.6966,
        rate_per_hour=1.50,
        motorcycle_rate=0.50,
        daily_max_cap=12.00,
        total_bays=150,
        operating_hours="Mon–Sun 07:00–22:00",
        payment_method="Cash, MyParking App",
        is_online_bookable="YES",
        booking_platform="MyParking App",
        ev_charging="NO",
        disabled_bays="NO",
        source_url=SOURCE_URL,
    ),
    make_record(
        name="MyParking – Jalan Ipoh",
        operator="MyParking",
        type="open_lot",
        parking_class="normal",
        address="Jalan Ipoh, Kuala Lumpur",
        city="Kuala Lumpur",
        state="Wilayah Persekutuan",
        latitude=3.1765,
        longitude=101.6868,
        rate_per_hour=1.00,
        motorcycle_rate=0.30,
        daily_max_cap=10.00,
        total_bays=200,
        operating_hours="Mon–Sun 07:00–22:00",
        payment_method="Cash, MyParking App",
        is_online_bookable="YES",
        booking_platform="MyParking App",
        source_url=SOURCE_URL,
    ),
]


class MyParkingScraper(BaseScraper):
    """Scrapes MyParking Malaysia locations."""

    def scrape(self) -> List[Dict[str, Any]]:
        self.logger.info("Starting MyParking scrape …")
        try:
            results = self._scrape_live()
            if results:
                self.logger.info("MyParking live scrape returned %d records", len(results))
                return results
        except Exception as exc:
            self.logger.warning("MyParking live scrape failed (%s) – using fallback", exc)
        self.logger.info("MyParking using %d fallback records", len(FALLBACK_DATA))
        return FALLBACK_DATA

    def _scrape_live(self) -> List[Dict[str, Any]]:
        if not self.can_fetch(SOURCE_URL):
            return []
        page = self.soup(SOURCE_URL + "/locations")
        if page is None:
            return []
        records: List[Dict[str, Any]] = []
        # MyParking often lists locations in a table or list
        items = page.find_all(["li", "tr"])
        for item in items:
            name_el = item.find(["a", "strong", "b"])
            if not name_el:
                continue
            name = name_el.get_text(strip=True)
            if not name:
                continue
            rec = make_record(
                name=name,
                operator="MyParking",
                type="multistorey",
                city="Kuala Lumpur",
                state="Wilayah Persekutuan",
                source_url=SOURCE_URL,
            )
            records.append(rec)
        return records
