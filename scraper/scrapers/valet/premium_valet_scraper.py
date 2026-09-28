"""
Premium valet parking scraper — standalone valet operators in KL & Selangor.
Covers restaurant/event valet services at key locations.
All data is hardcoded.
"""

from typing import List, Dict, Any
from scrapers.base_scraper import BaseScraper, make_record

FALLBACK_DATA: List[Dict[str, Any]] = [
    make_record(
        name="Valet Parking – Pavilion KL (Main Entrance)",
        operator="Pavilion KL Valet",
        type="valet",
        parking_class="valet",
        address="168, Jalan Bukit Bintang, 55100 Kuala Lumpur",
        city="Kuala Lumpur",
        state="Wilayah Persekutuan",
        latitude=3.1487,
        longitude=101.7131,
        valet_rate=20.00,
        operating_hours="Mon–Sun 10:00–22:00",
        payment_method="Cash, Card",
        source_url="https://www.pavilion-kl.com",
        notes="Valet at main entrance Drop-off; RM20 flat",
    ),
    make_record(
        name="Valet Parking – Mid Valley Megamall (North Court)",
        operator="Mid Valley Valet",
        type="valet",
        parking_class="valet",
        address="Mid Valley City, Lingkaran Syed Putra, 59200 Kuala Lumpur",
        city="Kuala Lumpur",
        state="Wilayah Persekutuan",
        latitude=3.1186,
        longitude=101.6775,
        valet_rate=15.00,
        operating_hours="Mon–Sun 10:00–22:00",
        payment_method="Cash, Card",
        source_url="https://www.midvalley.com.my",
        notes="RM15 flat valet at North Court entrance",
    ),
    make_record(
        name="Valet Parking – Jalan Ampang Restaurant Strip",
        operator="Ampang Valet Services",
        type="valet",
        parking_class="valet",
        address="Jalan Ampang, 50450 Kuala Lumpur",
        city="Kuala Lumpur",
        state="Wilayah Persekutuan",
        latitude=3.1594,
        longitude=101.7235,
        valet_rate=15.00,
        operating_hours="Mon–Sun 11:00–23:00",
        payment_method="Cash",
        source_url="",
        notes="Shared valet for restaurants along Jalan Ampang; typical RM15",
    ),
    make_record(
        name="Valet Parking – Bangsar Village II",
        operator="Bangsar Village Valet",
        type="valet",
        parking_class="valet",
        address="2, Jalan Telawi 1, Bangsar Baru, 59100 Kuala Lumpur",
        city="Kuala Lumpur",
        state="Wilayah Persekutuan",
        latitude=3.1282,
        longitude=101.6730,
        valet_rate=12.00,
        operating_hours="Mon–Sun 10:00–22:00",
        payment_method="Cash, Card",
        source_url="https://www.bangsarvillage.com",
        notes="RM12 flat valet",
    ),
    make_record(
        name="Valet Parking – Jalan Telawi Bangsar (Restaurants)",
        operator="Bangsar Restaurant Valet",
        type="valet",
        parking_class="valet",
        address="Jalan Telawi 2/3, Bangsar, Kuala Lumpur",
        city="Kuala Lumpur",
        state="Wilayah Persekutuan",
        latitude=3.1277,
        longitude=101.6720,
        valet_rate=10.00,
        operating_hours="Mon–Sun 18:00–01:00",
        payment_method="Cash",
        source_url="",
        notes="Evening dining valet; typical RM10–RM15",
    ),
    make_record(
        name="Valet Parking – Empire Damansara (Event)",
        operator="Empire Damansara Valet",
        type="valet",
        parking_class="valet",
        address="Jalan PJU 8/8A, Damansara Perdana, 47820 Petaling Jaya, Selangor",
        city="Petaling Jaya",
        state="Selangor",
        latitude=3.1520,
        longitude=101.5990,
        valet_rate=15.00,
        operating_hours="Mon–Sun 10:00–22:00",
        payment_method="Cash, Card",
        source_url="https://www.empiredamansara.com",
        notes="RM15 flat valet at event/F&B entrance",
    ),
    make_record(
        name="Valet Parking – Sunway Pyramid (Main Entrance)",
        operator="Sunway Pyramid Valet",
        type="valet",
        parking_class="valet",
        address="3, Jalan PJS 11/15, Bandar Sunway, 47500 Subang Jaya, Selangor",
        city="Subang Jaya",
        state="Selangor",
        latitude=3.0730,
        longitude=101.6065,
        valet_rate=15.00,
        operating_hours="Mon–Sun 10:00–22:00",
        payment_method="Cash, Card",
        source_url="https://www.sunwaypyramid.com",
        notes="RM15 flat valet at main entrance",
    ),
]


class PremiumValetScraper(BaseScraper):
    """Returns hardcoded premium/standalone valet data for KL & Selangor."""

    def scrape(self) -> List[Dict[str, Any]]:
        self.logger.info(
            "Premium valet scraper returning %d hardcoded records (KL & Selangor)",
            len(FALLBACK_DATA),
        )
        return FALLBACK_DATA
