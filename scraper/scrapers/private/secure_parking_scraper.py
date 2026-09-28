"""
Secure Parking Malaysia scraper.
Focused on Kuala Lumpur and Selangor locations.
Falls back to hardcoded Secure Parking locations.
"""

from typing import List, Dict, Any
from scrapers.base_scraper import BaseScraper, make_record

SOURCE_URL = "https://www.secureparking.com.my"

FALLBACK_DATA: List[Dict[str, Any]] = [
    make_record(
        name="Secure Parking – Menara Maxis",
        operator="Secure Parking",
        type="multistorey",
        parking_class="normal",
        address="Kuala Lumpur City Centre (KLCC), Kuala Lumpur",
        city="Kuala Lumpur",
        state="Wilayah Persekutuan",
        latitude=3.1577,
        longitude=101.7116,
        rate_per_hour=5.00,
        motorcycle_rate=2.00,
        daily_max_cap=35.00,
        total_bays=300,
        operating_hours="Mon–Sun 24hrs",
        payment_method="Cash, Touch 'n Go, Card",
        ev_charging="YES",
        disabled_bays="YES",
        source_url=SOURCE_URL,
        notes="Premium KLCC fringe location",
    ),
    make_record(
        name="Secure Parking – Menara Standard Chartered",
        operator="Secure Parking",
        type="multistorey",
        parking_class="normal",
        address="30, Jalan Sultan Ismail, Kuala Lumpur",
        city="Kuala Lumpur",
        state="Wilayah Persekutuan",
        latitude=3.1534,
        longitude=101.7095,
        rate_per_hour=4.00,
        motorcycle_rate=1.50,
        daily_max_cap=28.00,
        total_bays=280,
        operating_hours="Mon–Fri 07:00–22:00, Sat–Sun 08:00–18:00",
        payment_method="Cash, Touch 'n Go, Card",
        ev_charging="NO",
        disabled_bays="YES",
        source_url=SOURCE_URL,
    ),
    make_record(
        name="Secure Parking – Kompleks Dayabumi",
        operator="Secure Parking",
        type="multistorey",
        parking_class="normal",
        address="Jalan Sultan Hishamudin, Kuala Lumpur",
        city="Kuala Lumpur",
        state="Wilayah Persekutuan",
        latitude=3.1447,
        longitude=101.6942,
        rate_per_hour=3.00,
        motorcycle_rate=1.00,
        daily_max_cap=22.00,
        total_bays=400,
        operating_hours="Mon–Sun 07:00–22:00",
        payment_method="Cash, Touch 'n Go, Card",
        ev_charging="NO",
        disabled_bays="YES",
        source_url=SOURCE_URL,
    ),
    make_record(
        name="Secure Parking – Jalan P. Ramlee",
        operator="Secure Parking",
        type="multistorey",
        parking_class="normal",
        address="Jalan P. Ramlee, Kuala Lumpur",
        city="Kuala Lumpur",
        state="Wilayah Persekutuan",
        latitude=3.1557,
        longitude=101.7078,
        rate_per_hour=4.00,
        motorcycle_rate=1.50,
        daily_max_cap=30.00,
        total_bays=350,
        operating_hours="Mon–Sun 24hrs",
        payment_method="Cash, Touch 'n Go, Card",
        ev_charging="YES",
        disabled_bays="YES",
        source_url=SOURCE_URL,
    ),
    make_record(
        name="Secure Parking – Subang Jaya Medical Centre",
        operator="Secure Parking",
        type="multistorey",
        parking_class="normal",
        address="1, Jalan SS12/1A, Subang Jaya, Selangor",
        city="Subang Jaya",
        state="Selangor",
        latitude=3.0737,
        longitude=101.5813,
        rate_per_hour=3.00,
        motorcycle_rate=1.00,
        daily_max_cap=20.00,
        total_bays=250,
        operating_hours="Mon–Sun 24hrs",
        payment_method="Cash, Touch 'n Go, Card",
        ev_charging="NO",
        disabled_bays="YES",
        source_url=SOURCE_URL,
        notes="Hospital adjacent – 24hr access",
    ),
    make_record(
        name="Secure Parking – Empire Damansara",
        operator="Secure Parking",
        type="multistorey",
        parking_class="normal",
        address="Jalan PJU 8/8A, Damansara Perdana, Petaling Jaya, Selangor",
        city="Petaling Jaya",
        state="Selangor",
        latitude=3.1520,
        longitude=101.5990,
        rate_per_hour=2.00,
        motorcycle_rate=0.50,
        daily_max_cap=15.00,
        total_bays=300,
        operating_hours="Mon–Sun 10:00–22:00",
        payment_method="Cash, Touch 'n Go, Card",
        ev_charging="YES",
        disabled_bays="YES",
        source_url=SOURCE_URL,
    ),
]


class SecureParkingScraper(BaseScraper):
    """Scrapes Secure Parking Malaysia locations in KL and Selangor."""

    def scrape(self) -> List[Dict[str, Any]]:
        self.logger.info("Starting Secure Parking scrape …")
        try:
            results = self._scrape_live()
            if results:
                self.logger.info("Secure Parking live scrape returned %d records", len(results))
                return results
        except Exception as exc:
            self.logger.warning("Secure Parking live scrape failed (%s) – using fallback", exc)
        self.logger.info("Secure Parking using %d fallback records", len(FALLBACK_DATA))
        return FALLBACK_DATA

    def _scrape_live(self) -> List[Dict[str, Any]]:
        if not self.can_fetch(SOURCE_URL):
            return []
        page = self.soup(SOURCE_URL + "/locations")
        if page is None:
            return []
        records: List[Dict[str, Any]] = []
        for card in page.find_all("div", class_=lambda c: c and "location" in c.lower()):
            name_el = card.find(["h2", "h3"])
            if not name_el:
                continue
            rec = make_record(
                name=name_el.get_text(strip=True),
                operator="Secure Parking",
                type="multistorey",
                city="Kuala Lumpur",
                state="Wilayah Persekutuan",
                source_url=SOURCE_URL,
            )
            records.append(rec)
        return records
