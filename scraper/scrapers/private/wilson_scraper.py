"""
Wilson Parking Malaysia scraper.
Targets: https://www.wilsonparking.com.my
Falls back to hardcoded known Wilson locations.
"""

from typing import List, Dict, Any
from scrapers.base_scraper import BaseScraper, make_record

SOURCE_URL = "https://www.wilsonparking.com.my"

FALLBACK_DATA: List[Dict[str, Any]] = [
    make_record(
        name="Wilson Parking – Menara Citibank",
        operator="Wilson Parking",
        type="multistorey",
        parking_class="normal",
        address="165, Jalan Ampang, Kuala Lumpur",
        city="Kuala Lumpur",
        state="Wilayah Persekutuan",
        latitude=3.1569,
        longitude=101.7172,
        rate_per_hour=3.00,
        motorcycle_rate=1.00,
        daily_max_cap=25.00,
        total_bays=400,
        operating_hours="Mon–Sun 24hrs",
        payment_method="Cash, Touch 'n Go, Card, Wilson App",
        is_online_bookable="YES",
        booking_platform="Wilson App",
        ev_charging="NO",
        disabled_bays="YES",
        source_url=SOURCE_URL + "/car-parks/menara-citibank",
        notes="Corporate office tower parking",
    ),
    make_record(
        name="Wilson Parking – Bangunan Angkasa Raya",
        operator="Wilson Parking",
        type="multistorey",
        parking_class="normal",
        address="123, Jalan Ampang, Kuala Lumpur",
        city="Kuala Lumpur",
        state="Wilayah Persekutuan",
        latitude=3.1547,
        longitude=101.7138,
        rate_per_hour=4.00,
        motorcycle_rate=1.50,
        daily_max_cap=30.00,
        total_bays=350,
        operating_hours="Mon–Sun 24hrs",
        payment_method="Cash, Touch 'n Go, Card, Wilson App",
        is_online_bookable="YES",
        booking_platform="Wilson App",
        ev_charging="YES",
        disabled_bays="YES",
        source_url=SOURCE_URL + "/car-parks/angkasa-raya",
    ),
    make_record(
        name="Wilson Parking – Wisma Goldhill",
        operator="Wilson Parking",
        type="multistorey",
        parking_class="normal",
        address="67, Jalan Raja Chulan, Kuala Lumpur",
        city="Kuala Lumpur",
        state="Wilayah Persekutuan",
        latitude=3.1507,
        longitude=101.7076,
        rate_per_hour=3.00,
        motorcycle_rate=1.00,
        daily_max_cap=25.00,
        total_bays=280,
        operating_hours="Mon–Fri 07:00–22:00, Sat–Sun 08:00–20:00",
        payment_method="Cash, Touch 'n Go, Card, Wilson App",
        is_online_bookable="YES",
        booking_platform="Wilson App",
        ev_charging="NO",
        disabled_bays="YES",
        source_url=SOURCE_URL + "/car-parks/wisma-goldhill",
    ),
    make_record(
        name="Wilson Parking – Menara IMC",
        operator="Wilson Parking",
        type="multistorey",
        parking_class="normal",
        address="8, Jalan Sultan Ismail, Kuala Lumpur",
        city="Kuala Lumpur",
        state="Wilayah Persekutuan",
        latitude=3.1529,
        longitude=101.7068,
        rate_per_hour=4.00,
        motorcycle_rate=1.50,
        daily_max_cap=28.00,
        total_bays=320,
        operating_hours="Mon–Sun 24hrs",
        payment_method="Cash, Touch 'n Go, Card, Wilson App",
        is_online_bookable="YES",
        booking_platform="Wilson App",
        ev_charging="YES",
        disabled_bays="YES",
        source_url=SOURCE_URL + "/car-parks/menara-imc",
    ),
    make_record(
        name="Wilson Parking – Bangsar Village",
        operator="Wilson Parking",
        type="multistorey",
        parking_class="normal",
        address="1, Jalan Telawi 1, Bangsar Baru, Kuala Lumpur",
        city="Kuala Lumpur",
        state="Wilayah Persekutuan",
        latitude=3.1289,
        longitude=101.6735,
        rate_per_hour=3.00,
        first_hour_rate=2.00,
        motorcycle_rate=1.00,
        daily_max_cap=20.00,
        total_bays=500,
        operating_hours="Mon–Sun 10:00–22:00",
        payment_method="Cash, Touch 'n Go, Card, Wilson App",
        is_online_bookable="YES",
        booking_platform="Wilson App",
        ev_charging="YES",
        disabled_bays="YES",
        source_url=SOURCE_URL + "/car-parks/bangsar-village",
    ),
]


class WilsonScraper(BaseScraper):
    """Scrapes Wilson Parking Malaysia locations."""

    def scrape(self) -> List[Dict[str, Any]]:
        self.logger.info("Starting Wilson Parking scrape …")
        try:
            results = self._scrape_live()
            if results:
                self.logger.info("Wilson live scrape returned %d records", len(results))
                return results
        except Exception as exc:
            self.logger.warning("Wilson live scrape failed (%s) – using fallback", exc)
        self.logger.info("Wilson using %d fallback records", len(FALLBACK_DATA))
        return FALLBACK_DATA

    def _scrape_live(self) -> List[Dict[str, Any]]:
        if not self.can_fetch(SOURCE_URL + "/car-parks"):
            return []
        page = self.soup(SOURCE_URL + "/car-parks")
        if page is None:
            return []
        records: List[Dict[str, Any]] = []
        # Wilson uses card-based layouts; look for parking cards
        cards = page.find_all("div", class_=lambda c: c and "car-park" in c.lower())
        if not cards:
            cards = page.find_all("article")
        for card in cards:
            name_el = card.find(["h2", "h3", "h4"])
            if not name_el:
                continue
            name = name_el.get_text(strip=True)
            # Try to extract rate from card text
            text = card.get_text(" ", strip=True)
            rec = make_record(
                name=name,
                operator="Wilson Parking",
                type="multistorey",
                parking_class="normal",
                city="Kuala Lumpur",
                state="Wilayah Persekutuan",
                source_url=SOURCE_URL + "/car-parks",
                notes=text[:200] if text else "",
            )
            records.append(rec)
        return records
