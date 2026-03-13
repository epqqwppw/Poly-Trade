"""Demo mode — simulates a live Polymarket order book for offline testing."""

from __future__ import annotations

import math
import random
import time
from typing import List, Optional

from .models import MarketInfo, OrderBook, OrderLevel


class DemoMarketData:
    """Generates realistic, continuously-moving order book data for paper trading.

    Simulates a BTC 15-minute UP/DOWN binary market with:
    - Mid price oscillating around 0.50 (random walk)
    - Realistic spread (2-5 cents)
    - Multiple bid/ask levels with decreasing size
    - Occasional volatility spikes
    """

    def __init__(self) -> None:
        self._mid = 0.50 + random.uniform(-0.05, 0.05)
        self._volatility = 0.005  # Per-tick volatility
        self._tick = 0
        self._market_start = time.time()
        self._market_duration = 15 * 60  # 15 minutes

        # Create a fixed demo market
        self.demo_market = MarketInfo(
            condition_id="DEMO_CONDITION_001",
            question="Will BTC go up in the next 15 minutes? [DEMO]",
            yes_token_id="DEMO_YES_TOKEN",
            no_token_id="DEMO_NO_TOKEN",
            end_date=time.strftime(
                "%Y-%m-%dT%H:%M:%SZ",
                time.gmtime(self._market_start + self._market_duration),
            ),
            active=True,
            outcomes=["Up", "Down"],
            volume=15000.0,
        )

    def find_active_markets(self, force: bool = False) -> List[MarketInfo]:
        """Return the demo market."""
        # Refresh the market every 15 minutes
        elapsed = time.time() - self._market_start
        if elapsed > self._market_duration:
            self._market_start = time.time()
            self._mid = 0.50 + random.uniform(-0.05, 0.05)
            self.demo_market.end_date = time.strftime(
                "%Y-%m-%dT%H:%M:%SZ",
                time.gmtime(self._market_start + self._market_duration),
            )
        return [self.demo_market]

    def get_order_book(self, token_id: str) -> Optional[OrderBook]:
        """Generate a realistic order book snapshot with price movement."""
        self._tick += 1

        # Random walk for the midpoint
        drift = random.gauss(0, self._volatility)

        # Add occasional larger moves (simulating real BTC volatility)
        if random.random() < 0.05:
            drift *= 3  # 5% chance of a bigger move

        self._mid += drift
        self._mid = max(0.10, min(0.90, self._mid))  # Keep in reasonable range

        # Generate spread (wider when volatile)
        base_spread = random.uniform(0.02, 0.04)
        half_spread = base_spread / 2

        best_bid = round(self._mid - half_spread, 2)
        best_ask = round(self._mid + half_spread, 2)

        # Ensure valid prices
        best_bid = max(0.01, best_bid)
        best_ask = min(0.99, best_ask)
        if best_bid >= best_ask:
            best_ask = best_bid + 0.01

        # Generate depth: 5 levels on each side
        bids: List[OrderLevel] = []
        asks: List[OrderLevel] = []

        for i in range(5):
            bid_price = round(best_bid - i * 0.01, 2)
            ask_price = round(best_ask + i * 0.01, 2)
            # Size decreases with distance from mid
            base_size = random.uniform(50, 200) * (1 / (i + 1))

            if bid_price > 0:
                bids.append(OrderLevel(price=bid_price, size=round(base_size, 0)))
            if ask_price < 1.0:
                asks.append(OrderLevel(price=ask_price, size=round(base_size, 0)))

        return OrderBook(token_id=token_id, bids=bids, asks=asks)

    def get_midpoint_price(self, token_id: str) -> Optional[float]:
        return round(self._mid, 4)
