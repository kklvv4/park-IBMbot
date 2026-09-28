"""
Stadium parking scraper — major stadiums in KL & Selangor.
All data hardcoded (no machine-readable parking rate pages on stadium websites).
"""

from typing import List, Dict, Any
from scrapers.base_scraper import BaseScraper, make_record

FALLBACK_DATA: List[Dict[str, Any]] = [
    make_record(
        name="Stadium Nasional Bukit Jalil – Car Park",
        operator="Perbadanan Stadium Malaysia",
        type="open_lot",
        parking_class="normal",
        address="Jalan Jalil Perkasa 1, Bukit Jalil, 57000 Kuala Lumpur",
        city="Kuala Lumpur",
        state="Wilayah Persekutuan",
        latitude=3.0576,
        longitude=101.6917,
        rate_per_hour=None,
        daily_max_cap=5.00,
        operating_hours="Event days only; 2hrs before kick-off until 1hr after",
        payment_method="Cash, Touch 'n Go",
        total_bays=12000,
        ev_charging="NO",
        disabled_bays="YES",
        source_url="https://www.stadiummalaysia.com.my",
        notes="RM5 flat on event days; free on non-event days",
    ),
    make_record(
        name="Stadium Shah Alam – Car Park",
        operator="Majlis Bandaraya Shah Alam",
        type="open_lot",
        parking_class="normal",
        address="Persiaran Olahraga, Seksyen 13, 40100 Shah Alam, Selangor",
        city="Shah Alam",
        state="Selangor",
        latitude=3.0636,
        longitude=101.5300,
        rate_per_hour=None,
        daily_max_cap=3.00,
        operating_hours="Event days; gates open 2hrs before",
        payment_method="Cash",
        total_bays=5000,
        ev_charging="NO",
        disabled_bays="YES",
        source_url="https://www.stadiumshahalam.com.my",
        notes="RM3 flat on event days",
    ),
    make_record(
        name="Stadium Merdeka – Car Park",
        operator="DBKL",
        type="open_lot",
        parking_class="normal",
        address="Jalan Stadium, 50460 Kuala Lumpur",
        city="Kuala Lumpur",
        state="Wilayah Persekutuan",
        latitude=3.1444,
        longitude=101.7025,
        rate_per_hour=2.00,
        daily_max_cap=15.00,
        operating_hours="Mon–Sun 07:00–22:00",
        payment_method="Cash, Touch 'n Go",
        total_bays=800,
        ev_charging="NO",
        disabled_bays="YES",
        source_url="https://www.dbkl.gov.my",
        notes="Heritage stadium; open lot adjacent",
    ),
    make_record(
        name="Axiata Arena (Stadium Putra) – Car Park",
        operator="Perbadanan Stadium Malaysia",
        type="open_lot",
        parking_class="normal",
        address="Jalan Jalil Perkasa 2, Bukit Jalil, 57000 Kuala Lumpur",
        city="Kuala Lumpur",
        state="Wilayah Persekutuan",
        latitude=3.0581,
        longitude=101.6905,
        rate_per_hour=None,
        daily_max_cap=5.00,
        operating_hours="Event days only",
        payment_method="Cash, Touch 'n Go",
        total_bays=3000,
        ev_charging="NO",
        disabled_bays="YES",
        source_url="https://www.axiataareana.com.my",
        notes="RM5 flat on event days; shares Bukit Jalil lot",
    ),
]


class StadiumScraper(BaseScraper):
    """Returns hardcoded stadium parking data for KL & Selangor."""

    def scrape(self) -> List[Dict[str, Any]]:
        self.logger.info(
            "Stadium scraper returning %d hardcoded records", len(FALLBACK_DATA)
        )
        return FALLBACK_DATA
