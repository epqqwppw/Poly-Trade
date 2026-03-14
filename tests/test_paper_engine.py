"""
Unit tests for the Poly-Trade bot.

Run with:
    python -m unittest tests.test_paper_engine -v

Coverage areas (56 tests total):
    TestOrderBook       — snapshot, delta, best bid/ask, mid, spread
    TestWsFeed          — message dispatch, book/trade callbacks
    TestBandsStrategy   — quote computation, inventory skew direction
    TestRiskManager     — position, daily-loss, drawdown limits
    TestWallet          — deposit, withdraw
    TestPaperEngine     — order lifecycle, fills, position tracking
    TestMarketData      — duration keyword match, expiry check
"""
import time
import unittest
from decimal import Decimal
from unittest.mock import MagicMock, patch

from bot.market_data import is_market_active, is_short_duration_market
from bot.order_book import OrderBook
from bot.paper_engine import PaperEngine, Wallet
from bot.risk import RiskManager
from bot.strategy import BandsStrategy
from bot.ws_feed import WsFeed


# ── helpers ─────────────────────────────────────────────────────────────────

def _book(bid: str, ask: str, asset_id: str = "TKN") -> OrderBook:
    """Return a simple two-level OrderBook for testing."""
    ob = OrderBook(asset_id)
    ob.apply_snapshot(
        bids=[{"price": bid, "size": "100"}],
        asks=[{"price": ask, "size": "100"}],
    )
    return ob


def _engine(
    spread_cents: int = 4,
    size: float = 5.0,
    skew_factor: float = 1.0,
    max_pos: float = 20.0,
    balance: float = 100.0,
) -> PaperEngine:
    strat = BandsStrategy(spread_cents, size, skew_factor, max_pos)
    risk = RiskManager(max_pos, daily_loss_limit=8.0, max_drawdown=15.0)
    return PaperEngine(strat, risk, initial_balance=balance)


# ── OrderBook ────────────────────────────────────────────────────────────────

class TestOrderBook(unittest.TestCase):

    def test_empty_book_returns_none(self):
        ob = OrderBook("X")
        self.assertIsNone(ob.best_bid())
        self.assertIsNone(ob.best_ask())
        self.assertIsNone(ob.mid_price())
        self.assertIsNone(ob.spread())

    def test_snapshot_populates_book(self):
        ob = _book("0.48", "0.52")
        self.assertEqual(ob.best_bid(), Decimal("0.48"))
        self.assertEqual(ob.best_ask(), Decimal("0.52"))

    def test_snapshot_replaces_previous_data(self):
        ob = _book("0.45", "0.55")
        ob.apply_snapshot(
            bids=[{"price": "0.48", "size": "50"}],
            asks=[{"price": "0.52", "size": "50"}],
        )
        self.assertEqual(ob.best_bid(), Decimal("0.48"))
        self.assertEqual(ob.best_ask(), Decimal("0.52"))

    def test_delta_updates_level(self):
        ob = _book("0.48", "0.52")
        ob.apply_delta([{"price": "0.48", "side": "BUY", "size": "200"}])
        self.assertEqual(ob._bids[Decimal("0.48")], Decimal("200"))

    def test_delta_removes_zero_size_level(self):
        ob = _book("0.48", "0.52")
        ob.apply_delta([{"price": "0.48", "side": "BUY", "size": "0"}])
        self.assertNotIn(Decimal("0.48"), ob._bids)

    def test_mid_price_is_arithmetic_mean(self):
        ob = _book("0.48", "0.52")
        self.assertEqual(ob.mid_price(), Decimal("0.50"))

    def test_spread_is_ask_minus_bid(self):
        ob = _book("0.48", "0.52")
        self.assertEqual(ob.spread(), Decimal("0.04"))

    def test_bids_sorted_descending(self):
        ob = OrderBook("X")
        ob.apply_snapshot(
            bids=[
                {"price": "0.45", "size": "10"},
                {"price": "0.48", "size": "10"},
                {"price": "0.46", "size": "10"},
            ],
            asks=[{"price": "0.52", "size": "10"}],
        )
        prices = [p for p, _ in ob.bids()]
        self.assertEqual(prices, sorted(prices, reverse=True))

    def test_asks_sorted_ascending(self):
        ob = OrderBook("X")
        ob.apply_snapshot(
            bids=[{"price": "0.48", "size": "10"}],
            asks=[
                {"price": "0.55", "size": "10"},
                {"price": "0.52", "size": "10"},
                {"price": "0.53", "size": "10"},
            ],
        )
        prices = [p for p, _ in ob.asks()]
        self.assertEqual(prices, sorted(prices))

    def test_is_valid_normal_book(self):
        self.assertTrue(_book("0.48", "0.52").is_valid())

    def test_is_valid_empty_book(self):
        self.assertFalse(OrderBook("X").is_valid())


# ── WsFeed ───────────────────────────────────────────────────────────────────

class TestWsFeed(unittest.TestCase):

    def _feed(self, on_book=None, on_trade=None):
        return WsFeed(["TKN"], on_book=on_book, on_trade=on_trade)

    def test_handle_book_event_populates_order_book(self):
        feed = self._feed()
        feed._handle_message({
            "event_type": "book",
            "asset_id": "TKN",
            "bids": [{"price": "0.48", "size": "100"}],
            "asks": [{"price": "0.52", "size": "100"}],
            "timestamp": "1234567890",
        })
        book = feed.get_book("TKN")
        self.assertEqual(book.best_bid(), Decimal("0.48"))
        self.assertEqual(book.best_ask(), Decimal("0.52"))

    def test_handle_price_change_updates_level(self):
        feed = self._feed()
        # Seed a snapshot first
        feed._handle_message({
            "event_type": "book",
            "asset_id": "TKN",
            "bids": [{"price": "0.48", "size": "100"}],
            "asks": [{"price": "0.52", "size": "100"}],
        })
        # Apply a delta
        feed._handle_message({
            "event_type": "price_change",
            "asset_id": "TKN",
            "changes": [{"price": "0.49", "side": "BUY", "size": "50"}],
        })
        book = feed.get_book("TKN")
        self.assertEqual(book.best_bid(), Decimal("0.49"))

    def test_handle_last_trade_price(self):
        feed = self._feed()
        feed._handle_message({
            "event_type": "book",
            "asset_id": "TKN",
            "bids": [{"price": "0.48", "size": "10"}],
            "asks": [{"price": "0.52", "size": "10"}],
        })
        feed._handle_message({
            "event_type": "last_trade_price",
            "asset_id": "TKN",
            "price": "0.50",
        })
        self.assertEqual(feed.get_book("TKN").last_trade_price, Decimal("0.50"))

    def test_on_book_callback_fires(self):
        callback = MagicMock()
        feed = self._feed(on_book=callback)
        feed._handle_message({
            "event_type": "book",
            "asset_id": "TKN",
            "bids": [{"price": "0.48", "size": "10"}],
            "asks": [{"price": "0.52", "size": "10"}],
        })
        callback.assert_called_once()
        asset_id, book = callback.call_args[0]
        self.assertEqual(asset_id, "TKN")

    def test_on_trade_callback_fires(self):
        trade_cb = MagicMock()
        feed = self._feed(on_trade=trade_cb)
        feed._handle_message({
            "event_type": "book",
            "asset_id": "TKN",
            "bids": [{"price": "0.48", "size": "10"}],
            "asks": [{"price": "0.52", "size": "10"}],
        })
        feed._handle_message({
            "event_type": "last_trade_price",
            "asset_id": "TKN",
            "price": "0.50",
        })
        trade_cb.assert_called_once()

    def test_unknown_asset_id_auto_registered(self):
        feed = self._feed()
        feed._handle_message({
            "event_type": "book",
            "asset_id": "NEW_TOKEN",
            "bids": [{"price": "0.45", "size": "10"}],
            "asks": [{"price": "0.55", "size": "10"}],
        })
        self.assertIn("NEW_TOKEN", feed.books)

    def test_dispatch_list_of_messages(self):
        feed = self._feed()
        feed._dispatch('[{"event_type":"book","asset_id":"TKN",'
                       '"bids":[{"price":"0.48","size":"10"}],'
                       '"asks":[{"price":"0.52","size":"10"}]},'
                       '{"event_type":"last_trade_price",'
                       '"asset_id":"TKN","price":"0.50"}]')
        self.assertEqual(feed.get_book("TKN").last_trade_price, Decimal("0.50"))

    def test_get_book_unknown_returns_none(self):
        feed = self._feed()
        self.assertIsNone(feed.get_book("UNKNOWN"))


# ── BandsStrategy ────────────────────────────────────────────────────────────

class TestBandsStrategy(unittest.TestCase):

    def _strat(self, **kw) -> BandsStrategy:
        defaults = dict(
            spread_cents=4, size_per_level_usd=5.0, skew_factor=1.0, max_position_usd=20.0
        )
        defaults.update(kw)
        return BandsStrategy(**defaults)

    def test_quotes_symmetric_at_zero_inventory(self):
        strat = self._strat()
        bid, ask, _ = strat.compute_quotes(Decimal("0.50"), 0.0)
        self.assertEqual(bid, Decimal("0.48"))
        self.assertEqual(ask, Decimal("0.52"))

    def test_spread_applied_correctly(self):
        strat = self._strat(spread_cents=6)
        bid, ask, _ = strat.compute_quotes(Decimal("0.50"), 0.0)
        self.assertEqual(ask - bid, Decimal("0.06"))

    def test_size_returned(self):
        strat = self._strat(size_per_level_usd=7.5)
        _, _, size = strat.compute_quotes(Decimal("0.50"))
        self.assertEqual(size, Decimal("7.5"))

    def test_long_inventory_skew_shifts_quotes_down(self):
        strat = self._strat()
        bid0, ask0, _ = strat.compute_quotes(Decimal("0.50"), 0.0)
        bid_long, ask_long, _ = strat.compute_quotes(Decimal("0.50"), 10.0)
        self.assertLess(bid_long, bid0)
        self.assertLess(ask_long, ask0)

    def test_short_inventory_skew_shifts_quotes_up(self):
        strat = self._strat()
        bid0, ask0, _ = strat.compute_quotes(Decimal("0.50"), 0.0)
        bid_short, ask_short, _ = strat.compute_quotes(Decimal("0.50"), -10.0)
        self.assertGreater(bid_short, bid0)
        self.assertGreater(ask_short, ask0)

    def test_bid_clipped_at_minimum(self):
        strat = self._strat(spread_cents=4)
        # Very low mid price — bid should not go below 0.01
        bid, _, _ = strat.compute_quotes(Decimal("0.02"), 20.0)
        self.assertGreaterEqual(bid, Decimal("0.01"))

    def test_ask_clipped_at_maximum(self):
        strat = self._strat(spread_cents=4)
        # Very high mid price — ask should not exceed 0.99
        _, ask, _ = strat.compute_quotes(Decimal("0.98"), -20.0)
        self.assertLessEqual(ask, Decimal("0.99"))


# ── RiskManager ──────────────────────────────────────────────────────────────

class TestRiskManager(unittest.TestCase):

    def _rm(self) -> RiskManager:
        return RiskManager(max_position_usd=20.0, daily_loss_limit=8.0, max_drawdown=15.0)

    def test_position_within_limit(self):
        rm = self._rm()
        self.assertTrue(rm.position_ok(15.0))

    def test_position_exceeds_limit(self):
        rm = self._rm()
        self.assertFalse(rm.position_ok(25.0))

    def test_negative_position_uses_absolute_value(self):
        rm = self._rm()
        self.assertFalse(rm.position_ok(-25.0))

    def test_daily_loss_ok_initially(self):
        rm = self._rm()
        self.assertTrue(rm.daily_loss_ok())

    def test_daily_loss_exceeded(self):
        rm = self._rm()
        rm.record_pnl(Decimal("-9"))
        self.assertFalse(rm.daily_loss_ok())

    def test_drawdown_ok_without_peak(self):
        rm = self._rm()
        self.assertTrue(rm.drawdown_ok(Decimal("90")))

    def test_drawdown_ok_within_limit(self):
        rm = self._rm()
        rm.update_equity(Decimal("100"))
        self.assertTrue(rm.drawdown_ok(Decimal("90")))  # 10% < 15% limit

    def test_drawdown_exceeded(self):
        rm = self._rm()
        rm.update_equity(Decimal("100"))
        self.assertFalse(rm.drawdown_ok(Decimal("80")))  # 20% > 15% limit

    def test_can_trade_all_ok(self):
        rm = self._rm()
        rm.update_equity(Decimal("100"))
        self.assertTrue(rm.can_trade(5.0, Decimal("100")))

    def test_can_trade_blocked_by_position(self):
        rm = self._rm()
        self.assertFalse(rm.can_trade(21.0, Decimal("100")))

    def test_reset_daily(self):
        rm = self._rm()
        rm.record_pnl(Decimal("-9"))
        self.assertFalse(rm.daily_loss_ok())
        rm.reset_daily()
        self.assertTrue(rm.daily_loss_ok())

    def test_inventory_aware_risk_blocks_at_limit(self):
        """Position exactly at the limit is still allowed; one cent over is not."""
        rm = self._rm()
        self.assertTrue(rm.position_ok(20.0))
        self.assertFalse(rm.position_ok(20.01))


# ── Wallet ───────────────────────────────────────────────────────────────────

class TestWallet(unittest.TestCase):

    def test_initial_balance(self):
        w = Wallet(100.0)
        self.assertEqual(w.balance, Decimal("100"))

    def test_deposit(self):
        w = Wallet(100.0)
        w.deposit(Decimal("50"))
        self.assertEqual(w.balance, Decimal("150"))

    def test_withdraw(self):
        w = Wallet(100.0)
        w.withdraw(Decimal("30"))
        self.assertEqual(w.balance, Decimal("70"))

    def test_withdraw_insufficient_funds(self):
        w = Wallet(10.0)
        with self.assertRaises(ValueError):
            w.withdraw(Decimal("50"))


# ── PaperEngine ──────────────────────────────────────────────────────────────

class TestPaperEngine(unittest.TestCase):

    def test_initial_wallet_balance(self):
        eng = _engine(balance=100.0)
        self.assertEqual(eng.wallet.balance, Decimal("100"))

    def test_on_book_update_places_orders(self):
        eng = _engine()
        book = _book("0.48", "0.52")
        eng.on_book_update("TKN", book)
        # Should have two open orders (buy + sell) for TKN
        tkn_orders = [o for o in eng.open_orders.values() if o["asset_id"] == "TKN"]
        self.assertEqual(len(tkn_orders), 2)
        sides = {o["side"] for o in tkn_orders}
        self.assertIn("buy", sides)
        self.assertIn("sell", sides)

    def test_bid_fills_when_mid_falls_to_bid(self):
        eng = _engine(spread_cents=4, size=5.0)
        # First update: place quotes around 0.50
        eng.on_book_update("TKN", _book("0.48", "0.52"))
        # Find the placed bid price
        buy_order = next(o for o in eng.open_orders.values() if o["side"] == "buy")
        bid_price = buy_order["price"]

        # Second update: market mid drops to or below bid → fill
        fill_book = _book(str(bid_price - Decimal("0.01")), str(bid_price + Decimal("0.01")))
        initial_balance = eng.wallet.balance
        eng.on_book_update("TKN", fill_book)

        # After a buy fill the wallet balance decreases
        self.assertLess(eng.wallet.balance, initial_balance)

    def test_ask_fills_when_mid_rises_to_ask(self):
        eng = _engine(spread_cents=4, size=5.0)
        eng.on_book_update("TKN", _book("0.48", "0.52"))
        sell_order = next(o for o in eng.open_orders.values() if o["side"] == "sell")
        ask_price = sell_order["price"]

        fill_book = _book(str(ask_price - Decimal("0.01")), str(ask_price + Decimal("0.01")))
        initial_balance = eng.wallet.balance
        eng.on_book_update("TKN", fill_book)

        # After a sell fill the wallet balance increases
        self.assertGreater(eng.wallet.balance, initial_balance)

    def test_position_increases_after_buy_fill(self):
        eng = _engine(spread_cents=4, size=5.0)
        eng.on_book_update("TKN", _book("0.48", "0.52"))
        buy_order = next(o for o in eng.open_orders.values() if o["side"] == "buy")
        bid_price = buy_order["price"]
        fill_book = _book(str(bid_price - Decimal("0.01")), str(bid_price + Decimal("0.01")))
        eng.on_book_update("TKN", fill_book)
        self.assertGreater(eng.positions.get("TKN", 0.0), 0.0)

    def test_no_orders_when_risk_blocks_position(self):
        eng = _engine(max_pos=5.0, size=5.0)
        # Manually inject a position that exceeds the limit
        eng.positions["TKN"] = 6.0
        eng.on_book_update("TKN", _book("0.48", "0.52"))
        tkn_orders = [o for o in eng.open_orders.values() if o["asset_id"] == "TKN"]
        self.assertEqual(len(tkn_orders), 0)

    def test_run_demo_completes_without_error(self):
        eng = _engine()
        eng.run_demo(steps=3)  # should not raise

    def test_replace_orders_cancels_stale_quotes(self):
        eng = _engine()
        eng.on_book_update("TKN", _book("0.48", "0.52"))
        count_after_first = len([o for o in eng.open_orders.values() if o["asset_id"] == "TKN"])
        eng.on_book_update("TKN", _book("0.47", "0.53"))
        count_after_second = len([o for o in eng.open_orders.values() if o["asset_id"] == "TKN"])
        # Each refresh should leave exactly 2 open orders for TKN
        self.assertEqual(count_after_first, 2)
        self.assertEqual(count_after_second, 2)


# ── MarketData helpers ───────────────────────────────────────────────────────

class TestMarketData(unittest.TestCase):

    def test_duration_keyword_match(self):
        self.assertTrue(
            is_short_duration_market("Will BTC be UP 1-hour?", ["1-hour", "hourly"])
        )

    def test_duration_keyword_case_insensitive(self):
        self.assertTrue(
            is_short_duration_market("BTC HOURLY UP/DOWN", ["1-hour", "hourly"])
        )

    def test_duration_keyword_no_match(self):
        self.assertFalse(
            is_short_duration_market("BTC daily market", ["1-hour", "hourly"])
        )

    def test_market_active_before_close(self):
        future = time.time() + 3600  # 1 hour from now
        self.assertTrue(is_market_active(future))

    def test_market_expired_after_close(self):
        past = time.time() - 1
        self.assertFalse(is_market_active(past))

    def test_market_active_when_close_time_is_none(self):
        self.assertTrue(is_market_active(None))


if __name__ == "__main__":
    unittest.main()
