"""In-memory order book for a single Polymarket CLOB token."""
from decimal import Decimal
from typing import Dict, List, Optional, Tuple


class OrderBook:
    """
    Maintains a sorted bid/ask book built from WebSocket snapshots and
    incremental delta messages.

    Prices and sizes are stored as :class:`decimal.Decimal` for precision.
    """

    def __init__(self, asset_id: str) -> None:
        self.asset_id = asset_id
        self._bids: Dict[Decimal, Decimal] = {}  # price → size
        self._asks: Dict[Decimal, Decimal] = {}  # price → size
        self.last_trade_price: Optional[Decimal] = None
        self.timestamp: Optional[str] = None

    # ------------------------------------------------------------------
    # Book updates
    # ------------------------------------------------------------------

    def apply_snapshot(
        self, bids: list, asks: list, timestamp: Optional[str] = None
    ) -> None:
        """Replace the entire book with a fresh snapshot."""
        self._bids = {}
        self._asks = {}
        for lvl in bids:
            p = Decimal(str(lvl["price"]))
            s = Decimal(str(lvl["size"]))
            if s > 0:
                self._bids[p] = s
        for lvl in asks:
            p = Decimal(str(lvl["price"]))
            s = Decimal(str(lvl["size"]))
            if s > 0:
                self._asks[p] = s
        self.timestamp = timestamp

    def apply_delta(self, changes: list) -> None:
        """Apply incremental price-level changes.

        Each change dict must have ``price``, ``size``, and ``side``
        (``"BUY"`` / ``"BID"`` for bids; ``"SELL"`` / ``"ASK"`` for asks).
        A size of ``0`` removes the level.
        """
        for ch in changes:
            price = Decimal(str(ch["price"]))
            size = Decimal(str(ch["size"]))
            side = ch.get("side", "").upper()
            book = self._bids if side in ("BUY", "BID") else self._asks
            if size == 0:
                book.pop(price, None)
            else:
                book[price] = size

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    def best_bid(self) -> Optional[Decimal]:
        """Highest bid price, or *None* if no bids."""
        return max(self._bids) if self._bids else None

    def best_ask(self) -> Optional[Decimal]:
        """Lowest ask price, or *None* if no asks."""
        return min(self._asks) if self._asks else None

    def mid_price(self) -> Optional[Decimal]:
        """Arithmetic mid between best bid and best ask."""
        bid, ask = self.best_bid(), self.best_ask()
        if bid is not None and ask is not None:
            return (bid + ask) / 2
        return None

    def spread(self) -> Optional[Decimal]:
        """Best ask minus best bid, or *None* if either side is empty."""
        bid, ask = self.best_bid(), self.best_ask()
        if bid is not None and ask is not None:
            return ask - bid
        return None

    def bids(self) -> List[Tuple[Decimal, Decimal]]:
        """All bid levels sorted descending (best first)."""
        return sorted(self._bids.items(), reverse=True)

    def asks(self) -> List[Tuple[Decimal, Decimal]]:
        """All ask levels sorted ascending (best first)."""
        return sorted(self._asks.items())

    def is_valid(self) -> bool:
        """True when the book has at least one bid below the best ask."""
        bid, ask = self.best_bid(), self.best_ask()
        return bid is not None and ask is not None and bid < ask
