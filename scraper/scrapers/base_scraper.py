"""
Base scraper class that all scrapers inherit from.
Provides common utilities: HTTP session, rate limiting, logging, robots.txt check.
"""

import time
import logging
import urllib.robotparser
from datetime import datetime
from typing import List, Dict, Any, Optional

import requests
from bs4 import BeautifulSoup

# Configure module-level logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Standard column schema for all scrapers
RECORD_SCHEMA = {
    "id": None,
    "name": "",
    "operator": "",
    "type": "",                # street/mall/open_lot/multistorey/valet/park_and_ride/airport
    "parking_class": "normal", # normal/premium/valet
    "address": "",
    "city": "",
    "state": "",
    "latitude": None,
    "longitude": None,
    "rate_per_hour": None,
    "motorcycle_rate": None,
    "valet_rate": None,
    "first_hour_rate": None,
    "first_hour_free": "NO",
    "daily_max_cap": None,
    "overnight_rate": None,
    "operating_hours": "",
    "payment_method": "",
    "is_online_bookable": "NO",
    "booking_platform": "",
    "total_bays": None,
    "ev_charging": "NO",
    "disabled_bays": "NO",
    "source_url": "",
    "last_updated": datetime.now().strftime("%Y-%m-%d"),
    "notes": "",
}


def make_record(**kwargs) -> Dict[str, Any]:
    """Return a record dict with schema defaults, overridden by kwargs."""
    rec = dict(RECORD_SCHEMA)
    rec.update(kwargs)
    return rec


class BaseScraper:
    """
    Abstract base class for all Malaysia parking scrapers.

    Sub-classes must implement:
        scrape() -> List[Dict]
    """

    # Default request headers to avoid trivial bot blocks
    DEFAULT_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    def __init__(self, delay: float = 1.5):
        self.delay = delay  # seconds between requests
        self.logger = logging.getLogger(self.__class__.__name__)
        self.session = requests.Session()
        self.session.headers.update(self.DEFAULT_HEADERS)
        self._robots_cache: Dict[str, urllib.robotparser.RobotFileParser] = {}

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def scrape(self) -> List[Dict[str, Any]]:
        """Override in sub-class. Must return a list of record dicts."""
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def get(self, url: str, **kwargs) -> Optional[requests.Response]:
        """GET request with rate-limit delay and error handling."""
        time.sleep(self.delay)
        try:
            resp = self.session.get(url, timeout=15, **kwargs)
            resp.raise_for_status()
            self.logger.info("GET %s → %s", url, resp.status_code)
            return resp
        except requests.RequestException as exc:
            self.logger.warning("GET %s failed: %s", url, exc)
            return None

    def soup(self, url: str, **kwargs) -> Optional[BeautifulSoup]:
        """Return a BeautifulSoup object for the given URL, or None on failure."""
        resp = self.get(url, **kwargs)
        if resp is None:
            return None
        return BeautifulSoup(resp.text, "html.parser")

    def can_fetch(self, url: str) -> bool:
        """Return True if robots.txt allows fetching the URL."""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        if base not in self._robots_cache:
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(f"{base}/robots.txt")
            try:
                rp.read()
            except Exception:
                # If we can't read robots.txt, assume allowed
                rp = None
            self._robots_cache[base] = rp
        rp = self._robots_cache[base]
        if rp is None:
            return True
        return rp.can_fetch(self.DEFAULT_HEADERS["User-Agent"], url)

    def safe_float(self, value) -> Optional[float]:
        """Convert value to float, return None on failure."""
        try:
            return float(str(value).replace("RM", "").replace(",", "").strip())
        except (ValueError, TypeError):
            return None

    def safe_int(self, value) -> Optional[int]:
        """Convert value to int, return None on failure."""
        try:
            return int(str(value).strip())
        except (ValueError, TypeError):
            return None
