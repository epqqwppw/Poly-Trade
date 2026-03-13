"""Unit tests for the paper trading engine and strategy."""

import time
import unittest

from bot.config import Config, StrategyConfig
from bot.models import (
    OrderBook,
    OrderLevel,
    OrderStatus,
    Side,
    VirtualOrder,
    Wallet,
)
from bot.paper_engine import PaperEngine
from bot.risk import RiskManager
from bot.strategy import BandsStrategy


def _make_book(
    bid_price: float = 0.53,
    ask_price: float = 0.57,
    bid_size: float = 100,
    ask_size: float = 100,
    token_id: str = "TEST_TOKEN",
) -> OrderBook:
    """Helper to build a simple order book."""
    return OrderBook(
        token_id=token_id,
        bids=[OrderLevel(price=bid_price, size=bid_size)],
        asks=[OrderLevel(price=ask_price, size=ask_size)],
    )


class TestWallet(unittest.TestCase):
    def test_initial_state(self):
        w = Wallet(usdc=100.0)
        self.assertEqual(w.usdc, 100.0)
        self.assertEqual(w.yes_tokens, 0.0)

    def test_portfolio_value(self):
        w = Wallet(usdc=50.0, yes_tokens=100, avg_yes_entry=0.55)
        # 50 + 100*0.55 = 105
        self.assertAlmostEqual(w.portfolio_value(0.55), 105.0)

    def test_unrealized_pnl(self):
        w = Wallet(usdc=50.0, yes_tokens=100, avg_yes_entry=0.50)
        # 100 * (0.55 - 0.50) = 5.0
        self.assertAlmostEqual(w.unrealized_pnl(0.55), 5.0)


class TestOrderBook(unittest.TestCase):
    def test_midpoint_and_spread(self):
        book = _make_book(bid_price=0.53, ask_price=0.57)
        self.assertAlmostEqual(book.midpoint, 0.55)
        self.assertAlmostEqual(book.spread, 0.04)

    def test_empty_book(self):
        book = OrderBook(token_id="X", bids=[], asks=[])
        self.assertIsNone(book.midpoint)
        self.assertIsNone(book.spread)


class TestPaperEngine(unittest.TestCase):
    def test_seed_inventory(self):
        eng = PaperEngine(starting_capital=100.0, seed_pct=0.5)
        eng.seed_inventory(midpoint=0.50)
        self.assertTrue(eng.is_seeded)
        self.assertAlmostEqual(eng.wallet.usdc, 50.0)
        self.assertAlmostEqual(eng.wallet.yes_tokens, 100.0)
        self.assertAlmostEqual(eng.wallet.avg_yes_entry, 0.50)

    def test_place_buy_order(self):
        eng = PaperEngine(starting_capital=100.0)
        order = VirtualOrder(
            side=Side.BUY, price=0.50, size=10, token_id="T"
        )
        result = eng.place_order(order)
        self.assertEqual(result.status, OrderStatus.OPEN)
        self.assertIn(result.id, eng.open_orders)

    def test_place_buy_insufficient_usdc(self):
        eng = PaperEngine(starting_capital=10.0)
        order = VirtualOrder(
            side=Side.BUY, price=0.50, size=100, token_id="T"
        )
        result = eng.place_order(order)
        self.assertEqual(result.status, OrderStatus.CANCELLED)

    def test_place_sell_insufficient_tokens(self):
        eng = PaperEngine(starting_capital=100.0)
        # No YES tokens at all
        order = VirtualOrder(
            side=Side.SELL, price=0.55, size=10, token_id="T"
        )
        result = eng.place_order(order)
        self.assertEqual(result.status, OrderStatus.CANCELLED)

    def test_buy_fill_simulation(self):
        eng = PaperEngine(starting_capital=100.0)
        order = VirtualOrder(
            side=Side.BUY, price=0.54, size=10, token_id="T"
        )
        eng.place_order(order)

        # Book ask drops to our buy price → fill
        book = _make_book(bid_price=0.50, ask_price=0.54, token_id="T")
        fills = eng.check_fills(book)
        self.assertEqual(len(fills), 1)
        self.assertEqual(fills[0].side, Side.BUY)
        self.assertAlmostEqual(eng.wallet.yes_tokens, 10.0)
        self.assertAlmostEqual(eng.wallet.usdc, 100.0 - 0.54 * 10)

    def test_sell_fill_simulation(self):
        eng = PaperEngine(starting_capital=100.0)
        eng.seed_inventory(midpoint=0.50)  # Get 100 YES tokens at $0.50

        order = VirtualOrder(
            side=Side.SELL, price=0.56, size=10, token_id="T"
        )
        eng.place_order(order)

        # Book bid rises to our sell price → fill
        book = _make_book(bid_price=0.56, ask_price=0.60, token_id="T")
        fills = eng.check_fills(book)
        self.assertEqual(len(fills), 1)
        self.assertEqual(fills[0].side, Side.SELL)
        # Sold 10 @ 0.56, bought at 0.50 → pnl = 10 * 0.06 = 0.60
        self.assertAlmostEqual(fills[0].pnl, 0.60, places=2)

    def test_no_fill_when_price_doesnt_cross(self):
        eng = PaperEngine(starting_capital=100.0)
        order = VirtualOrder(
            side=Side.BUY, price=0.50, size=10, token_id="T"
        )
        eng.place_order(order)

        # Ask is above our buy → no fill
        book = _make_book(bid_price=0.48, ask_price=0.55, token_id="T")
        fills = eng.check_fills(book)
        self.assertEqual(len(fills), 0)

    def test_cancel_all_orders(self):
        eng = PaperEngine(starting_capital=100.0)
        eng.place_order(VirtualOrder(side=Side.BUY, price=0.50, size=5, token_id="T"))
        eng.place_order(VirtualOrder(side=Side.BUY, price=0.49, size=5, token_id="T"))
        self.assertEqual(len(eng.open_orders), 2)

        cancelled = eng.cancel_all_orders()
        self.assertEqual(cancelled, 2)
        self.assertEqual(len(eng.open_orders), 0)

    def test_portfolio_value(self):
        eng = PaperEngine(starting_capital=100.0)
        eng.seed_inventory(midpoint=0.50)
        # USDC=50, YES=100 tokens, at mid 0.55 → 50 + 100*0.55 = 105
        self.assertAlmostEqual(eng.portfolio_value(0.55), 105.0)


class TestBandsStrategy(unittest.TestCase):
    def test_generates_both_sides(self):
        cfg = StrategyConfig(
            spread_cents=4.0, num_levels=2, size_per_level_usd=8.0
        )
        strat = BandsStrategy(cfg)
        book = _make_book(bid_price=0.53, ask_price=0.57)
        orders = strat.generate_quotes(
            book=book, yes_tokens=50, usdc_balance=50, starting_capital=100
        )
        buys = [o for o in orders if o.side == Side.BUY]
        sells = [o for o in orders if o.side == Side.SELL]
        self.assertGreater(len(buys), 0, "Should generate buy orders")
        self.assertGreater(len(sells), 0, "Should generate sell orders")

    def test_buy_prices_below_mid(self):
        cfg = StrategyConfig(
            spread_cents=4.0, num_levels=2, size_per_level_usd=8.0,
            inventory_skew_factor=0.0,  # Zero skew to test pure band placement
        )
        strat = BandsStrategy(cfg)
        book = _make_book(bid_price=0.53, ask_price=0.57)
        orders = strat.generate_quotes(
            book=book, yes_tokens=50, usdc_balance=50, starting_capital=100
        )
        mid = book.midpoint
        for o in orders:
            if o.side == Side.BUY:
                self.assertLess(o.price, mid, f"Buy at {o.price} should be < mid {mid}")

    def test_sell_prices_above_mid(self):
        cfg = StrategyConfig(
            spread_cents=4.0, num_levels=2, size_per_level_usd=8.0,
            inventory_skew_factor=0.0,  # Zero skew to test pure band placement
        )
        strat = BandsStrategy(cfg)
        book = _make_book(bid_price=0.53, ask_price=0.57)
        orders = strat.generate_quotes(
            book=book, yes_tokens=50, usdc_balance=50, starting_capital=100
        )
        mid = book.midpoint
        for o in orders:
            if o.side == Side.SELL:
                self.assertGreater(o.price, mid, f"Sell at {o.price} should be > mid {mid}")

    def test_no_quotes_without_midpoint(self):
        cfg = StrategyConfig()
        strat = BandsStrategy(cfg)
        book = OrderBook(token_id="T", bids=[], asks=[])
        orders = strat.generate_quotes(
            book=book, yes_tokens=50, usdc_balance=50, starting_capital=100
        )
        self.assertEqual(len(orders), 0)

    def test_respects_usdc_limit(self):
        cfg = StrategyConfig(
            spread_cents=4.0, num_levels=3, size_per_level_usd=40.0  # Large size
        )
        strat = BandsStrategy(cfg)
        book = _make_book(bid_price=0.53, ask_price=0.57)
        orders = strat.generate_quotes(
            book=book, yes_tokens=200, usdc_balance=10, starting_capital=100
        )
        buy_cost = sum(o.price * o.size for o in orders if o.side == Side.BUY)
        self.assertLessEqual(buy_cost, 10.01, "Buy cost should not exceed USDC balance")


class TestRiskManager(unittest.TestCase):
    def test_allows_trading_normal(self):
        cfg = Config.load()
        risk = RiskManager(cfg.risk)
        allowed, reason = risk.check_can_trade(
            daily_pnl=0, total_pnl=0, consecutive_losses=0
        )
        self.assertTrue(allowed)

    def test_blocks_on_daily_loss(self):
        cfg = Config.load()
        risk = RiskManager(cfg.risk)
        allowed, reason = risk.check_can_trade(
            daily_pnl=-15, total_pnl=-15, consecutive_losses=0
        )
        self.assertFalse(allowed)
        self.assertIn("Daily loss", reason)

    def test_blocks_on_drawdown(self):
        cfg = Config.load()
        risk = RiskManager(cfg.risk)
        allowed, reason = risk.check_can_trade(
            daily_pnl=-5, total_pnl=-30, consecutive_losses=0
        )
        self.assertFalse(allowed)
        self.assertIn("drawdown", reason)

    def test_circuit_breaker_on_consecutive_losses(self):
        cfg = Config.load()
        risk = RiskManager(cfg.risk)
        allowed, reason = risk.check_can_trade(
            daily_pnl=-2, total_pnl=-2, consecutive_losses=3
        )
        self.assertFalse(allowed)

    def test_filters_excessive_orders(self):
        cfg = Config.load()
        risk = RiskManager(cfg.risk)
        orders = [
            VirtualOrder(side=Side.BUY, price=0.50, size=100),  # $50
            VirtualOrder(side=Side.BUY, price=0.50, size=100),  # $50 → total $100
        ]
        filtered = risk.filter_orders(orders, portfolio_value=100)
        # Max position is $20, so should only allow partial
        total = sum(o.price * o.size for o in filtered)
        self.assertLessEqual(total, cfg.risk.max_position_usd + 0.01)

    def test_filter_accounts_for_inventory(self):
        """Risk filter should block buy orders when existing inventory is high."""
        cfg = Config.load()
        risk = RiskManager(cfg.risk)
        orders = [
            VirtualOrder(side=Side.BUY, price=0.50, size=20),  # $10
            VirtualOrder(side=Side.BUY, price=0.49, size=20),  # $9.80
        ]
        # Existing inventory already at $18 → only $2 room before $20 limit
        filtered = risk.filter_orders(orders, portfolio_value=100, inventory_value=18.0)
        buy_total = sum(o.price * o.size for o in filtered if o.side == Side.BUY)
        self.assertLessEqual(buy_total + 18.0, cfg.risk.max_position_usd + 0.01)

    def test_filter_allows_sells_with_high_inventory(self):
        """Sell orders should still be allowed even when inventory is high."""
        cfg = Config.load()
        risk = RiskManager(cfg.risk)
        orders = [
            VirtualOrder(side=Side.SELL, price=0.55, size=10),  # $5.50
            VirtualOrder(side=Side.SELL, price=0.56, size=10),  # $5.60
        ]
        # High inventory should NOT block sells (selling reduces risk)
        filtered = risk.filter_orders(orders, portfolio_value=100, inventory_value=50.0)
        self.assertEqual(len(filtered), 2)


class TestSkewDirection(unittest.TestCase):
    """Tests to verify inventory skew pushes quotes in the correct direction."""

    def test_long_inventory_lowers_asks(self):
        """When holding excess tokens, asks should drop to sell more aggressively."""
        cfg = StrategyConfig(
            spread_cents=4.0, num_levels=2, size_per_level_usd=5.0,
            inventory_skew_factor=1.0,
        )
        strat = BandsStrategy(cfg)
        book = _make_book(bid_price=0.53, ask_price=0.57)
        mid = book.midpoint  # 0.55

        # Balanced inventory
        # Balanced inventory: target = starting_capital * 0.5 / mid
        # = 100 * 0.5 / 0.55 ≈ 91 tokens
        balanced = strat.generate_quotes(
            book=book, yes_tokens=91, usdc_balance=50, starting_capital=100,
        )
        balanced_asks = [o.price for o in balanced if o.side == Side.SELL]

        # Heavy long inventory (200 tokens, way above target ~91)
        long_orders = strat.generate_quotes(
            book=book, yes_tokens=200, usdc_balance=50, starting_capital=100,
        )
        long_asks = [o.price for o in long_orders if o.side == Side.SELL]

        if balanced_asks and long_asks:
            # Long inventory → asks should be LOWER (more aggressive selling)
            self.assertLess(
                min(long_asks), min(balanced_asks),
                "Long inventory should lower asks to sell more aggressively",
            )

    def test_long_inventory_lowers_bids(self):
        """When holding excess tokens, bids should drop to buy less aggressively."""
        cfg = StrategyConfig(
            spread_cents=4.0, num_levels=2, size_per_level_usd=5.0,
            inventory_skew_factor=1.0,
        )
        strat = BandsStrategy(cfg)
        book = _make_book(bid_price=0.53, ask_price=0.57)

        # Balanced: ~91 tokens (see calculation above)
        balanced = strat.generate_quotes(
            book=book, yes_tokens=91, usdc_balance=50, starting_capital=100,
        )
        balanced_bids = [o.price for o in balanced if o.side == Side.BUY]

        long_orders = strat.generate_quotes(
            book=book, yes_tokens=200, usdc_balance=50, starting_capital=100,
        )
        long_bids = [o.price for o in long_orders if o.side == Side.BUY]

        if balanced_bids and long_bids:
            self.assertLess(
                max(long_bids), max(balanced_bids),
                "Long inventory should lower bids to buy less aggressively",
            )

    def test_short_inventory_raises_bids(self):
        """When holding too few tokens, bids should rise to buy more aggressively."""
        cfg = StrategyConfig(
            spread_cents=4.0, num_levels=2, size_per_level_usd=5.0,
            inventory_skew_factor=1.0,
        )
        strat = BandsStrategy(cfg)
        book = _make_book(bid_price=0.53, ask_price=0.57)

        # Balanced: ~91 tokens (see calculation above)
        balanced = strat.generate_quotes(
            book=book, yes_tokens=91, usdc_balance=50, starting_capital=100,
        )
        balanced_bids = [o.price for o in balanced if o.side == Side.BUY]

        # Very few tokens — want to buy more
        short_orders = strat.generate_quotes(
            book=book, yes_tokens=10, usdc_balance=50, starting_capital=100,
        )
        short_bids = [o.price for o in short_orders if o.side == Side.BUY]

        if balanced_bids and short_bids:
            self.assertGreater(
                max(short_bids), max(balanced_bids),
                "Short inventory should raise bids to buy more aggressively",
            )


class TestExpiryCheck(unittest.TestCase):
    """Tests for the market expiry proximity check."""

    def test_not_near_expiry(self):
        from bot.main import _is_near_expiry
        from bot.models import MarketInfo

        # Market ending far in the future
        market = MarketInfo(
            condition_id="test",
            question="Test",
            yes_token_id="YES",
            no_token_id="NO",
            end_date="2099-12-31T23:59:59Z",
            active=True,
        )
        self.assertFalse(_is_near_expiry(market, 120))

    def test_near_expiry(self):
        from bot.main import _is_near_expiry
        from bot.models import MarketInfo
        from datetime import datetime, timezone, timedelta

        # Market ending 60 seconds from now
        soon = (datetime.now(timezone.utc) + timedelta(seconds=60)).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        market = MarketInfo(
            condition_id="test",
            question="Test",
            yes_token_id="YES",
            no_token_id="NO",
            end_date=soon,
            active=True,
        )
        # 120s threshold → 60s remaining → near expiry
        self.assertTrue(_is_near_expiry(market, 120))

    def test_empty_end_date(self):
        from bot.main import _is_near_expiry
        from bot.models import MarketInfo

        market = MarketInfo(
            condition_id="test",
            question="Test",
            yes_token_id="YES",
            no_token_id="NO",
            end_date="",
            active=True,
        )
        self.assertFalse(_is_near_expiry(market, 120))


if __name__ == "__main__":
    unittest.main()
