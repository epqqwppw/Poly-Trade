"""
Bands market-making strategy with inventory skew.

The strategy places a bid at ``mid − half_spread`` and an ask at
``mid + half_spread``, then shifts both quotes by an inventory-skew term
so the bot naturally leans against a growing position.

Skew formula
------------
::

    skew = imbalance × skew_factor × (spread_cents / 100)

where ``imbalance = position_usd / max_position_usd`` ∈ [−1, 1].

* Positive imbalance (long) → positive skew → both quotes shift **down**
  (cheaper ask attracts sells, which reduce the long).
* Negative imbalance (short) → negative skew → both quotes shift **up**
  (higher bid attracts buys, which reduce the short).
"""
from decimal import Decimal
from typing import Tuple


def _d(x: object) -> Decimal:
    return Decimal(str(x))


class BandsStrategy:
    """Simple symmetric-bands market-making strategy."""

    def __init__(
        self,
        spread_cents: int = 4,
        size_per_level_usd: float = 5.0,
        skew_factor: float = 1.0,
        max_position_usd: float = 20.0,
    ) -> None:
        self.spread_cents = _d(spread_cents)
        self.size = _d(size_per_level_usd)
        self.skew_factor = _d(skew_factor)
        self.max_position_usd = _d(max_position_usd)

    def compute_quotes(
        self,
        mid: Decimal,
        position_usd: float = 0.0,
    ) -> Tuple[Decimal, Decimal, Decimal]:
        """Return *(bid_price, ask_price, size_usd)*.

        Both prices are clipped to the valid Polymarket range [0.01, 0.99].

        Parameters
        ----------
        mid:
            Current mid price (0–1).
        position_usd:
            Current signed position in USD (positive = long, negative = short).
        """
        half = self.spread_cents / _d(200)  # spread_cents / 2 / 100
        imbalance = _d(position_usd) / self.max_position_usd
        skew = imbalance * self.skew_factor * (self.spread_cents / _d(100))

        bid = mid - half - skew
        ask = mid + half - skew

        bid = max(bid, _d("0.01"))
        ask = min(ask, _d("0.99"))

        return bid, ask, self.size
