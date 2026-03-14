"""Paper trading engine — virtual wallet, order management, fill simulation."""

from __future__ import annotations

import logging
import time
from typing import Dict, List, Optional

from .models import OrderBook, OrderStatus, Side, Trade, VirtualOrder, Wallet

logger = logging.getLogger(__name__)


class PaperEngine:
    """Simulates order placement and fills against real Polymarket order books.

    How fills work:
      - Virtual BUY at price P fills when the real best ASK drops to P or below
        (meaning a real seller was willing to sell at our price).
      - Virtual SELL at price P fills when the real best BID rises to P or above
        (meaning a real buyer was willing to buy at our price).
    """

    def __init__(self, starting_capital: float = 100.0, seed_pct: float = 0.5):
        self.wallet = Wallet(usdc=starting_capital)
        self.starting_capital = starting_capital
        self.seed_pct = seed_pct
        self.open_orders: Dict[str, VirtualOrder] = {}
        self.trades: List[Trade] = []
        self.total_realized_pnl: float = 0.0
        self.daily_pnl: float = 0.0
        self.consecutive_losses: int = 0
        self.is_seeded: bool = False

    # ------------------------------------------------------------------
    # Seeding — acquire initial YES token inventory
    # ------------------------------------------------------------------

    def seed_inventory(self, midpoint: float) -> None:
        """Simulate buying initial YES tokens at current midpoint.

        This models the real-world step of splitting USDC into YES+NO tokens
        and selling the NO side, giving us YES inventory to sell.
        """
        if self.is_seeded or midpoint <= 0:
            return

        seed_usd = self.starting_capital * self.seed_pct
        tokens = seed_usd / midpoint
        self.wallet.usdc -= seed_usd
        self.wallet.yes_tokens = tokens
        self.wallet.avg_yes_entry = midpoint
        self.is_seeded = True
        logger.info(
            "Seeded inventory: bought %.1f YES tokens @ $%.4f (cost $%.2f)",
            tokens,
            midpoint,
            seed_usd,
        )

    # ------------------------------------------------------------------
    # Order management
    # ------------------------------------------------------------------

    def place_order(self, order: VirtualOrder) -> VirtualOrder:
        """Add a virtual order to the paper book."""
        # Check collateral
        if order.side == Side.BUY:
            cost = order.price * order.size
            available = self.wallet.usdc - self._locked_usdc()
            if cost > available + 0.001:
                logger.debug(
                    "Insufficient USDC for BUY: need $%.2f, have $%.2f",
                    cost,
                    available,
                )
                order.status = OrderStatus.CANCELLED
                return order
        elif order.side == Side.SELL:
            available_tokens = self.wallet.yes_tokens - self._locked_yes()
            if order.size > available_tokens + 0.001:
                logger.debug(
                    "Insufficient YES tokens for SELL: need %.1f, have %.1f",
                    order.size,
                    available_tokens,
                )
                order.status = OrderStatus.CANCELLED
                return order

        self.open_orders[order.id] = order
        return order

    def cancel_all_orders(self) -> int:
        """Cancel all open virtual orders."""
        count = 0
        for oid in list(self.open_orders):
            self.open_orders[oid].status = OrderStatus.CANCELLED
            count += 1
        self.open_orders.clear()
        return count

    def cancel_orders_by_side(self, side: Side) -> int:
        """Cancel all open orders on one side."""
        to_remove = [
            oid for oid, o in self.open_orders.items()
            if o.side == side and o.status == OrderStatus.OPEN
        ]
        for oid in to_remove:
            self.open_orders[oid].status = OrderStatus.CANCELLED
            del self.open_orders[oid]
        return len(to_remove)

    # ------------------------------------------------------------------
    # Fill simulation
    # ------------------------------------------------------------------

    def check_fills(self, book: OrderBook) -> List[Trade]:
        """Check if any virtual orders would have been filled given the real book."""
        if not book.best_bid or not book.best_ask:
            return []

        fills: List[Trade] = []
        to_remove: List[str] = []

        for oid, order in self.open_orders.items():
            if order.status != OrderStatus.OPEN:
                continue

            filled = False

            if order.side == Side.BUY and book.best_ask is not None:
                # Our BUY fills when real ask drops to our price or below
                if book.best_ask <= order.price:
                    filled = True
            elif order.side == Side.SELL and book.best_bid is not None:
                # Our SELL fills when real bid rises to our price or above
                if book.best_bid >= order.price:
                    filled = True

            if filled:
                trade = self._execute_fill(order, book)
                if trade:
                    fills.append(trade)
                    to_remove.append(oid)

        for oid in to_remove:
            del self.open_orders[oid]

        return fills

    def _execute_fill(self, order: VirtualOrder, book: OrderBook) -> Optional[Trade]:
        """Process a fill: update wallet and record trade."""
        order.status = OrderStatus.FILLED
        order.filled_at = time.time()
        mid = book.midpoint or order.price

        if order.side == Side.BUY:
            cost = order.price * order.size
            if cost > self.wallet.usdc + 0.01:
                return None
            # Update average entry price
            total_tokens = self.wallet.yes_tokens + order.size
            if total_tokens > 0:
                self.wallet.avg_yes_entry = (
                    self.wallet.yes_tokens * self.wallet.avg_yes_entry
                    + order.size * order.price
                ) / total_tokens
            self.wallet.usdc -= cost
            self.wallet.yes_tokens += order.size
            logger.info(
                "FILL BUY %.1f YES @ $%.4f (cost $%.2f)",
                order.size,
                order.price,
                cost,
            )

        elif order.side == Side.SELL:
            if order.size > self.wallet.yes_tokens + 0.01:
                return None
            revenue = order.price * order.size
            # Calculate realized P&L for this sale
            pnl = (order.price - self.wallet.avg_yes_entry) * order.size
            self.wallet.usdc += revenue
            self.wallet.yes_tokens -= order.size
            self.total_realized_pnl += pnl
            self.daily_pnl += pnl

            if pnl < 0:
                self.consecutive_losses += 1
            else:
                self.consecutive_losses = 0

            logger.info(
                "FILL SELL %.1f YES @ $%.4f (revenue $%.2f, P&L $%.4f)",
                order.size,
                order.price,
                revenue,
                pnl,
            )

        # Simulate maker rebate (25% of ~1% taker fee on the counter-party)
        taker_fee = order.price * order.size * 0.01 * 0.25
        self.wallet.total_rebates_earned += taker_fee

        trade = Trade(
            order_id=order.id,
            side=order.side,
            price=order.price,
            size=order.size,
            token_id=order.token_id,
            pnl=pnl if order.side == Side.SELL else 0.0,
        )
        self.trades.append(trade)
        return trade

    # ------------------------------------------------------------------
    # Collateral tracking
    # ------------------------------------------------------------------

    def _locked_usdc(self) -> float:
        """USDC locked in open BUY orders."""
        return sum(
            o.price * o.size
            for o in self.open_orders.values()
            if o.side == Side.BUY and o.status == OrderStatus.OPEN
        )

    def _locked_yes(self) -> float:
        """YES tokens locked in open SELL orders."""
        return sum(
            o.size
            for o in self.open_orders.values()
            if o.side == Side.SELL and o.status == OrderStatus.OPEN
        )

    # ------------------------------------------------------------------
    # Portfolio metrics
    # ------------------------------------------------------------------

    def portfolio_value(self, mid_price: float) -> float:
        """Current total portfolio value."""
        return self.wallet.portfolio_value(mid_price)

    def total_pnl(self, mid_price: float) -> float:
        """Total P&L (realized + unrealized)."""
        return self.portfolio_value(mid_price) - self.starting_capital

    def reset_daily(self) -> None:
        """Reset daily P&L counter (call at start of each day)."""
        self.daily_pnl = 0.0
        self.consecutive_losses = 0
