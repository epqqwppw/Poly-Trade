"""Data models for the paper trading market maker."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class Side(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderStatus(str, Enum):
    OPEN = "OPEN"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"


@dataclass
class OrderLevel:
    """Single price level in the order book."""

    price: float
    size: float


@dataclass
class OrderBook:
    """Snapshot of an order book for one token."""

    token_id: str
    bids: List[OrderLevel]
    asks: List[OrderLevel]
    timestamp: float = field(default_factory=time.time)

    @property
    def best_bid(self) -> Optional[float]:
        return self.bids[0].price if self.bids else None

    @property
    def best_ask(self) -> Optional[float]:
        return self.asks[0].price if self.asks else None

    @property
    def midpoint(self) -> Optional[float]:
        if self.best_bid is not None and self.best_ask is not None:
            return round((self.best_bid + self.best_ask) / 2, 4)
        return None

    @property
    def spread(self) -> Optional[float]:
        if self.best_bid is not None and self.best_ask is not None:
            return round(self.best_ask - self.best_bid, 4)
        return None


@dataclass
class MarketInfo:
    """Info about a Polymarket prediction market."""

    condition_id: str
    question: str
    yes_token_id: str
    no_token_id: str
    end_date: str
    active: bool
    outcomes: List[str] = field(default_factory=lambda: ["Yes", "No"])
    volume: float = 0.0


@dataclass
class VirtualOrder:
    """A paper trading order."""

    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    side: Side = Side.BUY
    price: float = 0.0
    size: float = 0.0
    token_id: str = ""
    status: OrderStatus = OrderStatus.OPEN
    created_at: float = field(default_factory=time.time)
    filled_at: Optional[float] = None
    level: int = 0  # Band level (1, 2, 3...)


@dataclass
class Trade:
    """Record of a completed fill."""

    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    order_id: str = ""
    side: Side = Side.BUY
    price: float = 0.0
    size: float = 0.0
    token_id: str = ""
    timestamp: float = field(default_factory=time.time)
    pnl: float = 0.0  # Realized P&L for this trade


@dataclass
class Wallet:
    """Virtual wallet tracking balances."""

    usdc: float = 100.0
    yes_tokens: float = 0.0
    avg_yes_entry: float = 0.0
    total_fees_paid: float = 0.0  # Always 0 for maker, but track anyway
    total_rebates_earned: float = 0.0

    @property
    def yes_cost_basis(self) -> float:
        return self.yes_tokens * self.avg_yes_entry

    def portfolio_value(self, yes_price: float) -> float:
        """Total portfolio value at current YES price."""
        return self.usdc + self.yes_tokens * yes_price

    def unrealized_pnl(self, yes_price: float) -> float:
        """Unrealized P&L on YES token holdings."""
        if self.yes_tokens <= 0:
            return 0.0
        return self.yes_tokens * (yes_price - self.avg_yes_entry)
