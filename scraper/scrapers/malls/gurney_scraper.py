"""
Gurney Plaza / Queensbay Mall scraper stub — kept minimal since
focus is KL & Selangor. Gurney is included as a reference but will
produce no records (Penang is out of scope).
"""

from typing import List, Dict, Any
from scrapers.base_scraper import BaseScraper, make_record

SOURCE_URL = "https://www.gurney.com.my"


class GurneyScraper(BaseScraper):
    """Stub scraper — Gurney Plaza is in Penang (out of KL/Selangor scope)."""

    def scrape(self) -> List[Dict[str, Any]]:
        self.logger.info(
            "Gurney Plaza is outside KL/Selangor scope — skipping."
        )
        return []
