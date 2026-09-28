"""
Interpark Malaysia scraper.
Targets: https://www.interpark.com.my
Falls back to hardcoded Interpark locations.
"""

from typing import List, Dict, Any
from scrapers.base_scraper import BaseScraper, make_record

SOURCE_URL = "https://www.interpark.com.my"

FALLBACK_DATA: List[Dict[str, Any]] = [
    make_record(
        name="Interpark – KL Sentral",
        operator="Interpark",
        type="multistorey",
        parking_class="normal",
        address="KL Sentral, Brickfields, Kuala Lumpur",
        city="Kuala Lumpur",
        state="Wilayah Persekutuan",
        latitude=3.1340,
        longitude=101.6861,
        rate_per_hour=3.00,
        first_hour_rate=3.00,
        motorcycle_rate=1.00,
        daily_max_cap=25.00,
        total_bays=600,
        operating_hours="Mon–Sun 24hrs",
        payment_method="Cash, Touch 'n Go, Card, Interpark App",
        is_online_bookable="YES",
        booking_platform="Interpark App",
        ev_charging="YES",
        disabled_bays="YES",
        source_url=SOURCE_URL + "/kl-sentral",
        notes="Integrated with KL Sentral transport hub",
    ),
    make_record(
        name="Interpark – Menara Shell",
        operator="Interpark",
        type="multistorey",
        parking_class="normal",
        address="211, Jalan Tun Razak, Kuala Lumpur",
        city="Kuala Lumpur",
        state="Wilayah Persekutuan",
        latitude=3.1620,
        longitude=101.7208,
        rate_per_hour=4.00,
        motorcycle_rate=1.50,
        daily_max_cap=28.00,
        total_bays=250,
        operating_hours="Mon–Fri 07:00–21:00, Sat 08:00–17:00",
        payment_method="Cash, Touch 'n Go, Card",
        ev_charging="NO",
        disabled_bays="YES",
        source_url=SOURCE_URL + "/menara-shell",
    ),
    make_record(
        name="Interpark – Menara TM",
        operator="Interpark",
        type="multistorey",
        parking_class="normal",
        address="Jalan Pantai Baharu, Pantai Hillpark, Kuala Lumpur",
        city="Kuala Lumpur",
        state="Wilayah Persekutuan",
        latitude=3.1198,
        longitude=101.6755,
        rate_per_hour=3.00,
        motorcycle_rate=1.00,
        daily_max_cap=22.00,
        total_bays=450,
        operating_hours="Mon–Sun 07:00–22:00",
        payment_method="Cash, Touch 'n Go, Card",
        ev_charging="NO",
        disabled_bays="YES",
        source_url=SOURCE_URL + "/menara-tm",
    ),
    make_record(
        name="Interpark – Nu Sentral",
        operator="Interpark",
        type="multistorey",
        parking_class="normal",
        address="Nu Sentral, KL Sentral, Kuala Lumpur",
        city="Kuala Lumpur",
        state="Wilayah Persekutuan",
        latitude=3.1320,
        longitude=101.6872,
        rate_per_hour=3.00,
        first_hour_rate=2.00,
        motorcycle_rate=1.00,
        daily_max_cap=22.00,
        total_bays=700,
        operating_hours="Mon–Sun 10:00–22:00",
        payment_method="Cash, Touch 'n Go, Card, Interpark App",
        is_online_bookable="YES",
        booking_platform="Interpark App",
        ev_charging="YES",
        disabled_bays="YES",
        source_url=SOURCE_URL + "/nu-sentral",
    ),
]


class InterparkScraper(BaseScraper):
    """Scrapes Interpark Malaysia locations."""

    def scrape(self) -> List[Dict[str, Any]]:
        self.logger.info("Starting Interpark scrape …")
        try:
            results = self._scrape_live()
            if results:
                self.logger.info("Interpark live scrape returned %d records", len(results))
                return results
        except Exception as exc:
            self.logger.warning("Interpark live scrape failed (%s) – using fallback", exc)
        self.logger.info("Interpark using %d fallback records", len(FALLBACK_DATA))
        return FALLBACK_DATA

    def _scrape_live(self) -> List[Dict[str, Any]]:
        if not self.can_fetch(SOURCE_URL):
            return []
        page = self.soup(SOURCE_URL + "/locations")
        if page is None:
            return []
        records: List[Dict[str, Any]] = []
        cards = page.find_all("div", class_=lambda c: c and "location" in c.lower())
        for card in cards:
            name_el = card.find(["h2", "h3"])
            if not name_el:
                continue
            rec = make_record(
                name=name_el.get_text(strip=True),
                operator="Interpark",
                type="multistorey",
                city="Kuala Lumpur",
                state="Wilayah Persekutuan",
                source_url=SOURCE_URL + "/locations",
            )
            records.append(rec)
        return records
