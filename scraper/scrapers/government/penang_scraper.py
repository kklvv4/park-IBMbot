"""
Penang parking scraper (MBBI + MBPP).
Covers both Seberang Perai (MBBI) and Penang Island (MBPP).
Falls back to hardcoded Penang data.
"""

from typing import List, Dict, Any
from scrapers.base_scraper import BaseScraper, make_record

SOURCE_URL = "https://www.mbpp.gov.my"
SOURCE_URL_MBBI = "https://www.mbbi.gov.my"

FALLBACK_DATA: List[Dict[str, Any]] = [
    make_record(
        name="MBPP Street Parking – Georgetown Zone 1",
        operator="MBPP",
        type="street",
        parking_class="normal",
        address="Lebuh Chulia / Jalan Penang, Georgetown",
        city="George Town",
        state="Pulau Pinang",
        latitude=5.4164,
        longitude=100.3327,
        rate_per_hour=1.00,
        motorcycle_rate=0.30,
        daily_max_cap=8.00,
        operating_hours="Mon–Sat 08:00–18:00",
        payment_method="Coupon, Touch 'n Go, MyParking App",
        source_url=SOURCE_URL,
        notes="UNESCO World Heritage buffer zone – limited bays",
    ),
    make_record(
        name="MBPP Street Parking – Georgetown Zone 2",
        operator="MBPP",
        type="street",
        parking_class="normal",
        address="Jalan Burma / Jalan Air Itam, Georgetown",
        city="George Town",
        state="Pulau Pinang",
        latitude=5.4279,
        longitude=100.3196,
        rate_per_hour=0.60,
        motorcycle_rate=0.20,
        daily_max_cap=5.00,
        operating_hours="Mon–Sat 08:00–18:00",
        payment_method="Coupon, Touch 'n Go",
        source_url=SOURCE_URL,
    ),
    make_record(
        name="MBPP Multi-Storey Car Park – Prangin Mall",
        operator="MBPP",
        type="multistorey",
        parking_class="normal",
        address="Jalan Dr Lim Chwee Leong, Georgetown",
        city="George Town",
        state="Pulau Pinang",
        latitude=5.4142,
        longitude=100.3286,
        rate_per_hour=1.50,
        motorcycle_rate=0.50,
        daily_max_cap=15.00,
        total_bays=800,
        operating_hours="Mon–Sun 07:00–23:00",
        payment_method="Cash, Touch 'n Go, Card",
        source_url=SOURCE_URL,
    ),
    make_record(
        name="Gurney Plaza Parking",
        operator="Gurney Plaza",
        type="mall",
        parking_class="normal",
        address="170, Persiaran Gurney, Georgetown",
        city="George Town",
        state="Pulau Pinang",
        latitude=5.4367,
        longitude=100.3114,
        rate_per_hour=2.00,
        motorcycle_rate=0.50,
        first_hour_rate=2.00,
        daily_max_cap=20.00,
        total_bays=1200,
        operating_hours="Mon–Sun 10:00–22:00",
        payment_method="Cash, Touch 'n Go, Card",
        source_url="https://www.gurney.com.my",
        notes="First 2 hours RM2 each",
    ),
    make_record(
        name="Queensbay Mall Parking",
        operator="Queensbay Mall",
        type="mall",
        parking_class="normal",
        address="100, Persiaran Bayan Indah, Bayan Lepas",
        city="Bayan Lepas",
        state="Pulau Pinang",
        latitude=5.3316,
        longitude=100.3062,
        rate_per_hour=2.00,
        motorcycle_rate=0.50,
        first_hour_rate=2.00,
        daily_max_cap=18.00,
        total_bays=1500,
        operating_hours="Mon–Sun 10:00–22:00",
        payment_method="Cash, Touch 'n Go, Card",
        source_url="https://www.queensbay.com.my",
    ),
    make_record(
        name="MBBI Street Parking – Butterworth",
        operator="MBBI",
        type="street",
        parking_class="normal",
        address="Jalan Bagan Luar, Butterworth",
        city="Butterworth",
        state="Pulau Pinang",
        latitude=5.3996,
        longitude=100.3631,
        rate_per_hour=0.60,
        motorcycle_rate=0.20,
        daily_max_cap=5.00,
        operating_hours="Mon–Sat 08:00–18:00",
        payment_method="Coupon, Touch 'n Go",
        source_url=SOURCE_URL_MBBI,
    ),
]


class PenangScraper(BaseScraper):
    """
    Penang scraper — kept as a stub since the project scope is KL & Selangor only.
    Returns an empty list so no Penang data enters the dataset.
    """

    def scrape(self) -> List[Dict[str, Any]]:
        self.logger.info(
            "PenangScraper: out of KL/Selangor scope — returning 0 records."
        )
        return []

    def _scrape_live(self) -> List[Dict[str, Any]]:
        # MBPP often has parking info under their online services portal
        if not self.can_fetch(SOURCE_URL):
            return []
        page = self.soup(SOURCE_URL + "/en/parking-rates")
        if page is None:
            return []
        tables = page.find_all("table")
        records: List[Dict[str, Any]] = []
        for table in tables:
            for row in table.find_all("tr")[1:]:
                cells = [td.get_text(strip=True) for td in row.find_all("td")]
                if len(cells) < 2:
                    continue
                rec = make_record(
                    name=cells[0],
                    operator="MBPP",
                    type="street",
                    city="George Town",
                    state="Pulau Pinang",
                    rate_per_hour=self.safe_float(cells[1]) if len(cells) > 1 else None,
                    source_url=SOURCE_URL,
                )
                records.append(rec)
        return records
