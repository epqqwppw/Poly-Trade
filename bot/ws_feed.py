"""
WebSocket feed for Polymarket CLOB market data.

Connects to ``wss://ws-subscriptions-clob.polymarket.com/ws/market``,
subscribes to the requested token IDs, and maintains one
:class:`~bot.order_book.OrderBook` per token.  Optional callbacks fire on
every book update or last-trade-price event.

No authentication is required for read-only market data.
"""
import asyncio
import json
import logging
import threading
from typing import Callable, Dict, List, Optional

from .order_book import OrderBook

logger = logging.getLogger(__name__)

WS_URL = "wss://ws-subscriptions-clob.polymarket.com/ws/market"


class WsFeed:
    """
    Push-based Polymarket CLOB market data feed.

    Parameters
    ----------
    asset_ids:
        List of Polymarket token IDs to subscribe to.
    on_book:
        Called as ``on_book(asset_id, book)`` after every snapshot or delta
        that updates the local :class:`~bot.order_book.OrderBook`.
    on_trade:
        Called as ``on_trade(asset_id, msg)`` on every
        ``last_trade_price`` event.
    reconnect_delay:
        Seconds to wait before reconnecting after a disconnection.
    ws_url:
        WebSocket endpoint (override for testing).
    """

    def __init__(
        self,
        asset_ids: List[str],
        on_book: Optional[Callable[[str, OrderBook], None]] = None,
        on_trade: Optional[Callable[[str, dict], None]] = None,
        reconnect_delay: float = 5.0,
        ws_url: str = WS_URL,
    ) -> None:
        self.asset_ids = list(asset_ids)
        self.on_book = on_book
        self.on_trade = on_trade
        self.reconnect_delay = reconnect_delay
        self.ws_url = ws_url
        self.books: Dict[str, OrderBook] = {
            aid: OrderBook(aid) for aid in self.asset_ids
        }
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Launch the feed in a background daemon thread."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(
            target=self._run, daemon=True, name="ws-feed"
        )
        self._thread.start()

    def stop(self) -> None:
        """Signal the feed to stop and wait for the thread to exit."""
        self._running = False
        if self._loop is not None:
            self._loop.call_soon_threadsafe(self._loop.stop)
        if self._thread is not None:
            self._thread.join(timeout=10)

    def get_book(self, asset_id: str) -> Optional[OrderBook]:
        """Return the live :class:`~bot.order_book.OrderBook` for *asset_id*."""
        return self.books.get(asset_id)

    def get_mid(self, asset_id: str) -> Optional[object]:
        """Return the current mid price for *asset_id*, or *None*."""
        book = self.books.get(asset_id)
        return book.mid_price() if book else None

    # ------------------------------------------------------------------
    # Internal — threading / asyncio
    # ------------------------------------------------------------------

    def _run(self) -> None:
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_until_complete(self._connect_loop())
        finally:
            self._loop.close()

    async def _connect_loop(self) -> None:
        while self._running:
            try:
                await self._connect()
            except Exception as exc:
                logger.warning(
                    "WS error: %s — retrying in %.1fs", exc, self.reconnect_delay
                )
                if self._running:
                    await asyncio.sleep(self.reconnect_delay)

    async def _connect(self) -> None:
        import websockets  # imported lazily; not needed in tests

        async with websockets.connect(self.ws_url) as ws:
            logger.info("WS connected → %s", self.ws_url)
            await ws.send(json.dumps({"assets_ids": self.asset_ids}))
            logger.info("Subscribed to %d token(s)", len(self.asset_ids))
            async for raw in ws:
                if not self._running:
                    break
                self._dispatch(raw)

    # ------------------------------------------------------------------
    # Message handling (public for unit-testing without a live connection)
    # ------------------------------------------------------------------

    def _dispatch(self, raw: str) -> None:
        """Parse one raw WebSocket frame and route each message."""
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            logger.warning("Bad JSON from WS: %s", exc)
            return
        messages = payload if isinstance(payload, list) else [payload]
        for msg in messages:
            try:
                self._handle_message(msg)
            except Exception as exc:
                logger.warning("Error handling WS message: %s", exc)

    def _handle_message(self, msg: dict) -> None:
        """Process a single parsed market-data message."""
        event_type = msg.get("event_type")
        asset_id = msg.get("asset_id")

        # Auto-register previously unseen tokens
        if asset_id and asset_id not in self.books:
            self.books[asset_id] = OrderBook(asset_id)

        book = self.books.get(asset_id) if asset_id else None

        if event_type == "book":
            if book is not None:
                book.apply_snapshot(
                    msg.get("bids", []),
                    msg.get("asks", []),
                    msg.get("timestamp"),
                )
                logger.debug(
                    "Snapshot %s bid=%s ask=%s",
                    asset_id,
                    book.best_bid(),
                    book.best_ask(),
                )
            if self.on_book and book is not None:
                self.on_book(asset_id, book)

        elif event_type == "price_change":
            if book is not None:
                book.apply_delta(msg.get("changes", []))
                logger.debug(
                    "Delta %s bid=%s ask=%s",
                    asset_id,
                    book.best_bid(),
                    book.best_ask(),
                )
            if self.on_book and book is not None:
                self.on_book(asset_id, book)

        elif event_type == "last_trade_price":
            price_str = msg.get("price")
            if book is not None and price_str is not None:
                from decimal import Decimal

                book.last_trade_price = Decimal(str(price_str))
            if self.on_trade:
                self.on_trade(asset_id, msg)

        else:
            logger.debug("Unhandled WS event_type: %s", event_type)
