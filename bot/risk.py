"""
Risk management layer.

Enforces three independent limits:

* **Position limit** – absolute USD exposure per token.
* **Daily loss limit** – cumulative intra-day P&L floor.
* **Max drawdown** – percentage drawdown from the equity high-water mark.
"""
from decimal import Decimal


class RiskManager:
    """Stateful risk gate for the paper (and live) trading engine."""

    def __init__(
        self,
        max_position_usd: float = 20.0,
        daily_loss_limit: float = 8.0,
        max_drawdown: float = 15.0,
    ) -> None:
        self.max_position_usd = Decimal(str(max_position_usd))
        self.daily_loss_limit = Decimal(str(daily_loss_limit))
        self.max_drawdown_pct = Decimal(str(max_drawdown))
        self._daily_pnl: Decimal = Decimal("0")
        self._peak_equity: Decimal = Decimal("0")

    # ------------------------------------------------------------------
    # State updates
    # ------------------------------------------------------------------

    def update_equity(self, equity: Decimal) -> None:
        """Advance the high-water mark if *equity* is a new peak."""
        if equity > self._peak_equity:
            self._peak_equity = equity

    def record_pnl(self, pnl_delta: Decimal) -> None:
        """Accumulate *pnl_delta* into the daily P&L counter."""
        self._daily_pnl += pnl_delta

    def reset_daily(self) -> None:
        """Reset daily P&L (call at midnight / start of a new session)."""
        self._daily_pnl = Decimal("0")

    # ------------------------------------------------------------------
    # Checks
    # ------------------------------------------------------------------

    def position_ok(self, position_usd: float) -> bool:
        """Return *True* when ``|position_usd| ≤ max_position_usd``."""
        return abs(Decimal(str(position_usd))) <= self.max_position_usd

    def daily_loss_ok(self) -> bool:
        """Return *True* when cumulative daily P&L is above the loss floor."""
        return self._daily_pnl >= -self.daily_loss_limit

    def drawdown_ok(self, equity: Decimal) -> bool:
        """Return *True* when current drawdown is within the max-drawdown limit."""
        if self._peak_equity == 0:
            return True
        drawdown_pct = (self._peak_equity - equity) / self._peak_equity * 100
        return drawdown_pct <= self.max_drawdown_pct

    def can_trade(self, position_usd: float, equity: Decimal) -> bool:
        """Return *True* only when all three risk limits are satisfied."""
        return (
            self.position_ok(position_usd)
            and self.daily_loss_ok()
            and self.drawdown_ok(equity)
        )
