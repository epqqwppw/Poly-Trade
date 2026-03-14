"""
Paper trading engine.

Simulates a market-maker on Polymarket binary options without placing real
orders.  The engine is driven by :class:`~bot.order_book.OrderBook` updates
delivered by the WebSocket feed (or injected directly in tests).

Fill model
----------
A resting bid at price *P* fills when the market mid price falls to *P* or
below.  A resting ask at price *P* fills when the market mid price rises to
*P* or above.  This approximates maker fills without modelling the full CLOB
queue.
"""
from decimal import Decimal
from typing import Dict, List, Optional

from .order_book import OrderBook
from .risk import RiskManager
from .strategy import BandsStrategy


class Wallet:
    """Simulated USDC wallet used by the paper engine."""

    def __init__(self, balance: float = 100.0) -> None:
        self.balance: Decimal = Decimal(str(balance))

    def deposit(self, amount: Decimal) -> None:
        self.balance += amount

    def withdraw(self, amount: Decimal) -> None:
        if amount > self.balance:
            raise ValueError(
                f"Insufficient funds: tried to withdraw {amount}, "
                f"have {self.balance}"
            )
        self.balance -= amount

    def __repr__(self) -> str:
        return f"Wallet(balance={self.balance})"


class PaperEngine:
    """
    Drives the market-making loop in paper (simulation) mode.

    Parameters
    ----------
    strategy:
        A :class:`~bot.strategy.BandsStrategy` instance.
    risk:
        A :class:`~bot.risk.RiskManager` instance.
    initial_balance:
        Starting USDC wallet balance.
    """

    def __init__(
        self,
        strategy: BandsStrategy,
        risk: RiskManager,
        initial_balance: float = 100.0,
    ) -> None:
        self.strategy = strategy
        self.risk = risk
        self.wallet = Wallet(initial_balance)
        self.positions: Dict[str, float] = {}  # asset_id → net token position
        self.open_orders: Dict[str, dict] = {}  # order_id → order
        self.realized_pnl: Decimal = Decimal("0")
        self._next_order_id: int = 1
        self._avg_cost: Dict[str, Decimal] = {}  # asset_id → average cost per token

    # ------------------------------------------------------------------
    # Callback — called on every book update
    # ------------------------------------------------------------------

    def on_book_update(self, asset_id: str, book: OrderBook) -> None:
        """Check for fills on resting orders, then refresh quotes."""
        mid = book.mid_price()
        if mid is None:
            return

        self.risk.update_equity(self.wallet.balance)

        # Fill existing orders first, before cancelling/replacing them.
        self._check_fills(asset_id, book)

        position = self.positions.get(asset_id, 0.0)
        if not self.risk.can_trade(position, self.wallet.balance):
            return

        bid, ask, size = self.strategy.compute_quotes(mid, position)
        self._replace_orders(asset_id, bid, ask, size)

    # ------------------------------------------------------------------
    # Order management
    # ------------------------------------------------------------------

    def _replace_orders(
        self,
        asset_id: str,
        bid: Decimal,
        ask: Decimal,
        size: Decimal,
    ) -> None:
        """Cancel all existing orders for *asset_id* and post fresh quotes."""
        self.open_orders = {
            oid: o
            for oid, o in self.open_orders.items()
            if o["asset_id"] != asset_id
        }
        self._place_order(asset_id, "buy", bid, size)
        self._place_order(asset_id, "sell", ask, size)

    def _place_order(
        self,
        asset_id: str,
        side: str,
        price: Decimal,
        size: Decimal,
    ) -> str:
        order_id = str(self._next_order_id)
        self._next_order_id += 1
        self.open_orders[order_id] = {
            "order_id": order_id,
            "asset_id": asset_id,
            "side": side,
            "price": price,
            "size": size,
        }
        return order_id

    def _check_fills(self, asset_id: str, book: OrderBook) -> None:
        """Fill any resting orders whose price has been touched by the mid."""
        mid = book.mid_price()
        if mid is None:
            return

        filled: List[str] = []
        for order_id, order in self.open_orders.items():
            if order["asset_id"] != asset_id:
                continue
            if order["side"] == "buy" and mid <= order["price"]:
                self._fill_order(order, order["price"])
                filled.append(order_id)
            elif order["side"] == "sell" and mid >= order["price"]:
                self._fill_order(order, order["price"])
                filled.append(order_id)

        for oid in filled:
            del self.open_orders[oid]

    def _fill_order(self, order: dict, fill_price: Decimal) -> None:
        """Update wallet, position, and realized P&L after a simulated fill."""
        cost = fill_price * order["size"]
        asset_id = order["asset_id"]
        prev_pos = Decimal(str(self.positions.get(asset_id, 0.0)))
        prev_avg = self._avg_cost.get(asset_id, Decimal("0"))

        if order["side"] == "buy":
            self.wallet.withdraw(cost)
            new_pos = prev_pos + order["size"]
            self.positions[asset_id] = float(new_pos)
            # Update weighted-average cost basis
            if new_pos > 0:
                self._avg_cost[asset_id] = (
                    prev_avg * prev_pos + cost
                ) / new_pos
        else:
            self.wallet.deposit(cost)
            new_pos = prev_pos - order["size"]
            self.positions[asset_id] = float(new_pos)
            # Realized P&L = (sell price − average cost) × tokens sold
            pnl = (fill_price - prev_avg) * order["size"]
            self.realized_pnl += pnl
            self.risk.record_pnl(pnl)
            if new_pos <= 0:
                self._avg_cost[asset_id] = Decimal("0")

    # ------------------------------------------------------------------
    # Demo / offline mode
    # ------------------------------------------------------------------

    def run_demo(self, steps: int = 5) -> None:
        """Run a simple synthetic demo that does not need a live feed."""
        from decimal import Decimal as D

        print("=== Paper trading demo ===")
        prices = [D("0.50"), D("0.49"), D("0.48"), D("0.51"), D("0.52")]
        for i, price in enumerate(prices[:steps]):
            book = OrderBook("DEMO")
            # Build a thin synthetic book around the demo price
            book.apply_snapshot(
                bids=[{"price": str(price - D("0.02")), "size": "100"}],
                asks=[{"price": str(price + D("0.02")), "size": "100"}],
            )
            book.last_trade_price = price
            self.on_book_update("DEMO", book)
            print(
                f"  step {i+1}: mid={price} wallet={self.wallet.balance:.4f} "
                f"pos={self.positions.get('DEMO', 0.0):.4f}"
            )
        print("=== Demo complete ===")
