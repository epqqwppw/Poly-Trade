"""Polymarket API client — fetches real order book data (public, no auth)."""

from __future__ import annotations

import logging
import time
from typing import List, Optional

import requests

from .config import Config
from .models import MarketInfo, OrderBook, OrderLevel

logger = logging.getLogger(__name__)


class MarketDataClient:
    """Reads live market data from Polymarket public APIs."""

    def __init__(self, config: Config):
        self.cfg = config.api
        self.filter_cfg = config.market_filter
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})
        self._market_cache: Optional[List[MarketInfo]] = None
        self._cache_time: float = 0

    # ------------------------------------------------------------------
    # Market discovery (Gamma API)
    # ------------------------------------------------------------------

    def find_active_markets(self, force: bool = False) -> List[MarketInfo]:
        """Find active BTC 15-minute markets via the Gamma API."""
        now = time.time()
        if (
            not force
            and self._market_cache is not None
            and now - self._cache_time < self.cfg.market_scan_interval_seconds
        ):
            return self._market_cache

        markets: List[MarketInfo] = []
        try:
            # Try the events endpoint which groups related markets
            url = f"{self.cfg.gamma_url}/events"
            params = {"active": "true", "closed": "false", "limit": 100}
            resp = self.session.get(
                url, params=params, timeout=self.cfg.request_timeout_seconds
            )
            resp.raise_for_status()
            events = resp.json()

            for event in events:
                for mkt in event.get("markets", []):
                    info = self._parse_market(mkt)
                    if info:
                        markets.append(info)
        except Exception as exc:
            logger.debug("Events endpoint failed (%s), trying /markets", exc)

        if not markets:
            try:
                url = f"{self.cfg.gamma_url}/markets"
                params = {"active": "true", "closed": "false", "limit": 100}
                resp = self.session.get(
                    url, params=params, timeout=self.cfg.request_timeout_seconds
                )
                resp.raise_for_status()
                raw_markets = resp.json()
                if isinstance(raw_markets, dict):
                    raw_markets = raw_markets.get("data", raw_markets.get("markets", []))
                for mkt in raw_markets:
                    info = self._parse_market(mkt)
                    if info:
                        markets.append(info)
            except Exception as exc:
                logger.warning("Markets endpoint failed: %s", exc)

        # Filter for BTC 15-min markets
        btc_15m = self._filter_btc_15m(markets)
        if btc_15m:
            markets = btc_15m
        elif self.filter_cfg.fallback_to_any_crypto:
            crypto = self._filter_crypto(markets)
            if crypto:
                markets = crypto

        # Sort by volume (highest first)
        markets.sort(key=lambda m: m.volume, reverse=True)

        self._market_cache = markets
        self._cache_time = now
        logger.info("Found %d active markets", len(markets))
        return markets

    def _parse_market(self, mkt: dict) -> Optional[MarketInfo]:
        """Parse a market dict from Gamma API into MarketInfo."""
        try:
            condition_id = mkt.get("conditionId") or mkt.get("condition_id") or mkt.get("id", "")
            question = mkt.get("question", "")
            end_date = mkt.get("endDate") or mkt.get("end_date_iso") or ""
            active = mkt.get("active", True)
            volume = float(mkt.get("volume", 0) or 0)

            # Get token IDs — different API versions use different field names
            tokens = mkt.get("clobTokenIds") or mkt.get("clob_token_ids") or []
            if not tokens:
                # Try nested tokens array
                token_list = mkt.get("tokens", [])
                if isinstance(token_list, list):
                    for t in token_list:
                        if isinstance(t, dict):
                            tid = t.get("token_id") or t.get("tokenId", "")
                            if tid:
                                tokens.append(tid)
                        elif isinstance(t, str):
                            tokens.append(t)

            if not condition_id or len(tokens) < 2:
                return None

            outcomes = mkt.get("outcomes") or ["Yes", "No"]
            if isinstance(outcomes, str):
                outcomes = outcomes.strip("[]").replace('"', "").split(",")
                outcomes = [o.strip() for o in outcomes]

            return MarketInfo(
                condition_id=str(condition_id),
                question=question,
                yes_token_id=str(tokens[0]),
                no_token_id=str(tokens[1]),
                end_date=end_date,
                active=bool(active),
                outcomes=outcomes,
                volume=volume,
            )
        except Exception as exc:
            logger.debug("Failed to parse market: %s", exc)
            return None

    def _filter_btc_15m(self, markets: List[MarketInfo]) -> List[MarketInfo]:
        """Filter markets for BTC 15-minute binary markets."""
        results = []
        for m in markets:
            q = m.question.lower()
            has_keyword = any(k.lower() in q for k in self.filter_cfg.keywords)
            has_duration = any(d.lower() in q for d in self.filter_cfg.duration_keywords)
            if has_keyword and has_duration:
                results.append(m)
        return results

    def _filter_crypto(self, markets: List[MarketInfo]) -> List[MarketInfo]:
        """Fallback: find any crypto-related market."""
        crypto_terms = ["btc", "bitcoin", "eth", "ethereum", "crypto", "xrp", "sol"]
        results = []
        for m in markets:
            q = m.question.lower()
            if any(term in q for term in crypto_terms):
                results.append(m)
        return results

    # ------------------------------------------------------------------
    # Order book (CLOB API)
    # ------------------------------------------------------------------

    def get_order_book(self, token_id: str) -> Optional[OrderBook]:
        """Fetch the live order book for a token from the CLOB API."""
        try:
            url = f"{self.cfg.clob_url}/book"
            resp = self.session.get(
                url,
                params={"token_id": token_id},
                timeout=self.cfg.request_timeout_seconds,
            )
            resp.raise_for_status()
            data = resp.json()
            return self._parse_order_book(token_id, data)
        except Exception as exc:
            logger.warning("Order book fetch failed for %s: %s", token_id, exc)
            return None

    def get_midpoint_price(self, token_id: str) -> Optional[float]:
        """Quick price check via /prices endpoint."""
        try:
            url = f"{self.cfg.clob_url}/price"
            resp = self.session.get(
                url,
                params={"token_id": token_id},
                timeout=self.cfg.request_timeout_seconds,
            )
            resp.raise_for_status()
            data = resp.json()
            return float(data.get("price") or data.get("mid", 0))
        except Exception:
            return None

    def _parse_order_book(self, token_id: str, data: dict) -> OrderBook:
        """Parse CLOB /book response into OrderBook model."""
        bids_raw = data.get("bids", [])
        asks_raw = data.get("asks", [])

        bids = []
        for b in bids_raw:
            price = float(b.get("price", 0))
            size = float(b.get("size", 0))
            if price > 0 and size > 0:
                bids.append(OrderLevel(price=price, size=size))

        asks = []
        for a in asks_raw:
            price = float(a.get("price", 0))
            size = float(a.get("size", 0))
            if price > 0 and size > 0:
                asks.append(OrderLevel(price=price, size=size))

        # Sort: bids descending, asks ascending
        bids.sort(key=lambda x: x.price, reverse=True)
        asks.sort(key=lambda x: x.price)

        return OrderBook(token_id=token_id, bids=bids, asks=asks)
