"""
REST market-data helpers for Polymarket's public CLOB API.

Used as a fallback when the WebSocket feed is unavailable, for initial
market discovery, and for metadata such as market title and close time.
"""
import time
from typing import List, Optional

import requests

CLOB_API_URL = "https://clob.polymarket.com"


class MarketData:
    """Thin wrapper around the Polymarket public CLOB REST API."""

    def __init__(self, api_url: str = CLOB_API_URL, timeout: int = 10) -> None:
        self.api_url = api_url.rstrip("/")
        self.timeout = timeout

    def get_midpoint(self, token_id: str) -> float:
        """Return the current midpoint price (0–1) for *token_id*."""
        resp = requests.get(
            f"{self.api_url}/midpoint",
            params={"token_id": token_id},
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return float(resp.json()["mid"])

    def get_order_book(self, token_id: str) -> dict:
        """Return the current order book snapshot for *token_id*."""
        resp = requests.get(
            f"{self.api_url}/book",
            params={"token_id": token_id},
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()

    def get_markets(self) -> List[dict]:
        """Return a list of all active markets."""
        resp = requests.get(
            f"{self.api_url}/markets",
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json().get("data", [])

    def get_market(self, condition_id: str) -> dict:
        """Return metadata for a single market by its condition ID."""
        resp = requests.get(
            f"{self.api_url}/markets/{condition_id}",
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()


# ---------------------------------------------------------------------------
# Stateless helpers
# ---------------------------------------------------------------------------

def is_short_duration_market(title: str, keywords: List[str]) -> bool:
    """Return *True* if *title* contains any of the duration *keywords*.

    Comparison is case-insensitive.

    >>> is_short_duration_market("BTC 1-hour UP/DOWN", ["1-hour"])
    True
    >>> is_short_duration_market("BTC daily UP/DOWN", ["1-hour", "hourly"])
    False
    """
    title_lower = title.lower()
    return any(kw.lower() in title_lower for kw in keywords)


def is_market_active(close_time: Optional[float]) -> bool:
    """Return *True* when the market has not yet expired.

    Parameters
    ----------
    close_time:
        Unix timestamp (seconds) of market close.  If *None* the market is
        treated as still active.
    """
    if close_time is None:
        return True
    return time.time() < close_time
