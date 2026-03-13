"""Market making bands strategy with inventory skewing."""

from __future__ import annotations

import logging
from typing import List

from .config import StrategyConfig
from .models import OrderBook, Side, VirtualOrder

logger = logging.getLogger(__name__)


class BandsStrategy:
    """Generates two-sided quotes using a bands approach.

    Places multiple limit orders at increasing distances from the midpoint.
    Skews quotes based on current inventory imbalance to reduce directional risk.
    """

    def __init__(self, config: StrategyConfig):
        self.spread_cents = config.spread_cents
        self.num_levels = config.num_levels
        self.size_per_level_usd = config.size_per_level_usd
        self.skew_factor = config.inventory_skew_factor

    def generate_quotes(
        self,
        book: OrderBook,
        yes_tokens: float,
        usdc_balance: float,
        starting_capital: float,
    ) -> List[VirtualOrder]:
        """Generate buy and sell limit orders based on current market state.

        Args:
            book: Current order book snapshot.
            yes_tokens: Current YES token inventory.
            usdc_balance: Available USDC (after locked collateral).
            starting_capital: Original capital for sizing reference.

        Returns:
            List of VirtualOrder objects to place.
        """
        mid = book.midpoint
        if mid is None or mid <= 0:
            logger.warning("Cannot generate quotes: no valid midpoint")
            return []

        spread = self.spread_cents / 100.0
        skew = self._calculate_skew(yes_tokens, mid, starting_capital)

        orders: List[VirtualOrder] = []

        for level in range(1, self.num_levels + 1):
            offset = spread * level

            # BUY side: below midpoint, adjusted by skew
            bid_price = round(mid - offset / 2 - skew, 2)
            bid_price = max(0.01, min(0.99, bid_price))
            bid_size = self.size_per_level_usd / bid_price if bid_price > 0 else 0

            # Check we have enough USDC
            bid_cost = bid_price * bid_size
            if bid_cost <= usdc_balance and bid_size >= 1:
                orders.append(
                    VirtualOrder(
                        side=Side.BUY,
                        price=bid_price,
                        size=round(bid_size, 1),
                        token_id=book.token_id,
                        level=level,
                    )
                )
                usdc_balance -= bid_cost

            # SELL side: above midpoint, adjusted by skew
            ask_price = round(mid + offset / 2 - skew, 2)
            ask_price = max(0.01, min(0.99, ask_price))
            sell_size = self.size_per_level_usd / ask_price if ask_price > 0 else 0

            # Check we have enough YES tokens
            if sell_size <= yes_tokens and sell_size >= 1:
                orders.append(
                    VirtualOrder(
                        side=Side.SELL,
                        price=ask_price,
                        size=round(sell_size, 1),
                        token_id=book.token_id,
                        level=level,
                    )
                )
                yes_tokens -= sell_size

        if orders:
            buys = [o for o in orders if o.side == Side.BUY]
            sells = [o for o in orders if o.side == Side.SELL]
            logger.debug(
                "Generated %d quotes: %d BUY (best $%.2f), %d SELL (best $%.2f), skew=%.4f",
                len(orders),
                len(buys),
                min(o.price for o in buys) if buys else 0,
                len(sells),
                max(o.price for o in sells) if sells else 0,
                skew,
            )

        return orders

    def _calculate_skew(
        self, yes_tokens: float, mid_price: float, starting_capital: float
    ) -> float:
        """Calculate quote skew based on inventory imbalance.

        When holding too many YES tokens, skew quotes DOWN to attract more
        sells (higher ask) and discourage buys (lower bid).
        When holding too few, skew UP to attract buys.

        Returns:
            Skew in price units (positive = shift quotes up).
        """
        if starting_capital <= 0 or mid_price <= 0:
            return 0.0

        # Target: hold ~50% of capital in YES tokens
        target_tokens = (starting_capital * 0.5) / mid_price
        if target_tokens <= 0:
            return 0.0

        imbalance = (yes_tokens - target_tokens) / target_tokens
        # Clamp imbalance to [-1, 1]
        imbalance = max(-1.0, min(1.0, imbalance))

        # Skew: when long (positive imbalance), shift quotes DOWN to sell more
        # Positive skew subtracts from both bid and ask prices (bid-skew, ask-skew),
        # so bids go further below mid (less buying) and asks drop closer to mid
        # (more aggressive selling).
        skew = imbalance * self.skew_factor * (self.spread_cents / 100.0)
        return round(skew, 4)
