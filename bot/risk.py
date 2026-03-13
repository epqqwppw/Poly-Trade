"""Risk management — position limits, circuit breaker, loss limits."""

from __future__ import annotations

import logging
import time
from typing import List

from .config import RiskConfig
from .models import Side, VirtualOrder

logger = logging.getLogger(__name__)


class RiskManager:
    """Enforces risk limits on the paper trading bot."""

    def __init__(self, config: RiskConfig):
        self.cfg = config
        self.paused_until: float = 0.0

    def check_can_trade(
        self,
        daily_pnl: float,
        total_pnl: float,
        consecutive_losses: int,
    ) -> tuple[bool, str]:
        """Check if trading is allowed given current state.

        Returns:
            (allowed, reason) — if not allowed, reason explains why.
        """
        now = time.time()

        # Check pause timer (circuit breaker cooldown)
        if now < self.paused_until:
            remaining = int(self.paused_until - now)
            return False, f"Circuit breaker active ({remaining}s remaining)"

        # Daily loss limit
        if daily_pnl <= -self.cfg.daily_loss_limit_usd:
            return False, f"Daily loss limit hit (${daily_pnl:.2f} / -${self.cfg.daily_loss_limit_usd:.2f})"

        # Total drawdown limit
        if total_pnl <= -self.cfg.max_drawdown_usd:
            return False, f"Max drawdown hit (${total_pnl:.2f} / -${self.cfg.max_drawdown_usd:.2f})"

        # Circuit breaker on consecutive losses
        if consecutive_losses >= self.cfg.circuit_breaker_losses:
            self.paused_until = now + self.cfg.circuit_breaker_pause_seconds
            logger.warning(
                "Circuit breaker triggered: %d consecutive losses. Pausing %.0fs.",
                consecutive_losses,
                self.cfg.circuit_breaker_pause_seconds,
            )
            return False, f"{consecutive_losses} consecutive losses — pausing"

        return True, "OK"

    def filter_orders(
        self,
        orders: List[VirtualOrder],
        portfolio_value: float,
        inventory_value: float = 0.0,
    ) -> List[VirtualOrder]:
        """Remove orders that would exceed position limits.

        Args:
            orders: Proposed orders from strategy.
            portfolio_value: Current total portfolio value.
            inventory_value: Current YES token inventory value (tokens × mid).

        Returns:
            Filtered list of orders that pass risk checks.
        """
        max_pos = self.cfg.max_position_usd
        approved: List[VirtualOrder] = []
        buy_exposure = 0.0
        sell_exposure = 0.0

        for order in orders:
            order_value = order.price * order.size

            if order.side == Side.BUY:
                # Cap buy exposure accounting for existing inventory
                if buy_exposure + inventory_value + order_value > max_pos:
                    logger.debug(
                        "BUY order rejected: $%.2f + $%.2f inventory + $%.2f new > $%.2f limit",
                        buy_exposure,
                        inventory_value,
                        order_value,
                        max_pos,
                    )
                    continue
                buy_exposure += order_value
            else:
                # Sell orders reduce inventory risk — cap more loosely
                if sell_exposure + order_value > max_pos:
                    logger.debug(
                        "SELL order rejected: $%.2f would exceed $%.2f limit",
                        sell_exposure + order_value,
                        max_pos,
                    )
                    continue
                sell_exposure += order_value

            approved.append(order)

        if len(approved) < len(orders):
            logger.info(
                "Risk filter: %d/%d orders approved (buy $%.2f, sell $%.2f, inventory $%.2f / max $%.2f)",
                len(approved),
                len(orders),
                buy_exposure,
                sell_exposure,
                inventory_value,
                max_pos,
            )
        return approved
