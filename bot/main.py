"""Main entry point — runs the paper trading market maker loop."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import logging
import signal
import sys
import time

from .config import Config
from .demo import DemoMarketData
from .display import display_status
from .market_data import MarketDataClient
from .models import MarketInfo, OrderBook
from .paper_engine import PaperEngine
from .risk import RiskManager
from .strategy import BandsStrategy

logger = logging.getLogger(__name__)

# Graceful shutdown flag
_shutdown = False


def _handle_signal(signum: int, frame: object) -> None:
    global _shutdown
    _shutdown = True


def _is_near_expiry(market: MarketInfo, min_seconds: float) -> bool:
    """Return True if the market is within *min_seconds* of its end time."""
    if not market.end_date:
        return False
    try:
        end_str = market.end_date.replace("Z", "+00:00")
        end_dt = datetime.fromisoformat(end_str)
        remaining = (end_dt - datetime.now(timezone.utc)).total_seconds()
        return remaining <= min_seconds
    except (ValueError, TypeError):
        return False


def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    # Quiet noisy libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)


def run(config: Config, demo: bool = False) -> None:
    """Main market making loop."""
    global _shutdown

    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    # Initialize components
    data_client: MarketDataClient | DemoMarketData
    if demo:
        data_client = DemoMarketData()
        logger.info("Running in DEMO mode with simulated market data")
    else:
        data_client = MarketDataClient(config)
    engine = PaperEngine(
        starting_capital=config.starting_capital_usd,
        seed_pct=config.seed_pct,
    )
    strategy = BandsStrategy(config.strategy)
    risk = RiskManager(config.risk)

    tick_count = 0
    current_market: MarketInfo | None = None
    last_requote_time: float = 0

    logger.info(
        "Starting paper trading market maker with $%.2f virtual capital",
        config.starting_capital_usd,
    )

    while not _shutdown:
        tick_count += 1
        try:
            # 1. Find or refresh active market
            if current_market is None or tick_count % 12 == 0:
                markets = data_client.find_active_markets()
                if markets:
                    if current_market is None or current_market.condition_id != markets[0].condition_id:
                        current_market = markets[0]
                        logger.info("Selected market: %s", current_market.question)
                        engine.cancel_all_orders()
                        last_requote_time = 0

            if current_market is None:
                display_status(
                    market=None, book=None, wallet=engine.wallet,
                    open_orders=engine.open_orders, recent_trades=engine.trades,
                    total_pnl=0, daily_pnl=engine.daily_pnl,
                    starting_capital=engine.starting_capital,
                    risk_status="Searching for market...",
                    tick_count=tick_count, is_seeded=engine.is_seeded,
                )
                time.sleep(config.api.poll_interval_seconds)
                continue

            # 2. Fetch live order book
            book = data_client.get_order_book(current_market.yes_token_id)
            if book is None or book.midpoint is None:
                logger.warning("No order book data, retrying...")
                time.sleep(config.api.poll_interval_seconds)
                continue

            # 3. Seed initial inventory (first time only)
            if not engine.is_seeded:
                engine.seed_inventory(book.midpoint)

            # 4. Check for fills on existing virtual orders
            fills = engine.check_fills(book)
            if fills:
                logger.info("Got %d fill(s) this tick", len(fills))
                last_requote_time = 0  # Force requote after fills

            # 5. Risk check
            total_pnl = engine.total_pnl(book.midpoint)
            can_trade, risk_reason = risk.check_can_trade(
                daily_pnl=engine.daily_pnl,
                total_pnl=total_pnl,
                consecutive_losses=engine.consecutive_losses,
            )

            # 5b. Expiry check — stop placing new orders near market close
            near_expiry = _is_near_expiry(
                current_market, config.risk.min_time_before_expiry_seconds
            )
            if near_expiry and can_trade:
                can_trade = False
                risk_reason = "Market near expiry — no new orders"
                if engine.open_orders:
                    engine.cancel_all_orders()
                    logger.info("Cancelled orders: market within %ds of expiry",
                                int(config.risk.min_time_before_expiry_seconds))

            # 6. Generate new quotes (periodically or after fills)
            now = time.time()
            time_since_requote = now - last_requote_time
            should_requote = (
                can_trade
                and (
                    time_since_requote >= config.strategy.requote_interval_seconds
                    or fills  # Always requote after a fill
                    or not engine.open_orders  # No orders outstanding
                )
            )

            if should_requote:
                engine.cancel_all_orders()
                available_usdc = engine.wallet.usdc - engine._locked_usdc()
                quotes = strategy.generate_quotes(
                    book=book,
                    yes_tokens=engine.wallet.yes_tokens - engine._locked_yes(),
                    usdc_balance=available_usdc,
                    starting_capital=engine.starting_capital,
                )
                inventory_value = engine.wallet.yes_tokens * (book.midpoint or 0)
                quotes = risk.filter_orders(
                    quotes,
                    engine.portfolio_value(book.midpoint),
                    inventory_value=inventory_value,
                )
                for order in quotes:
                    engine.place_order(order)
                last_requote_time = now

            # 7. Display status
            risk_status = risk_reason if not can_trade else "✓ All systems go"
            display_status(
                market=current_market,
                book=book,
                wallet=engine.wallet,
                open_orders=engine.open_orders,
                recent_trades=engine.trades,
                total_pnl=total_pnl,
                daily_pnl=engine.daily_pnl,
                starting_capital=engine.starting_capital,
                risk_status=risk_status,
                tick_count=tick_count,
                is_seeded=engine.is_seeded,
            )

        except KeyboardInterrupt:
            break
        except Exception as exc:
            logger.error("Error in main loop: %s", exc, exc_info=True)

        # 8. Sleep until next tick
        time.sleep(config.api.poll_interval_seconds)

    # Shutdown
    cancelled = engine.cancel_all_orders()
    mid = 0.5
    final_pnl = engine.total_pnl(mid)
    print(f"\n{'=' * 70}")
    print("  BOT STOPPED GRACEFULLY")
    print(f"  Cancelled {cancelled} open orders")
    print(f"  Total trades: {len(engine.trades)}")
    print(f"  Final P&L:    ${final_pnl:+.2f}")
    print(f"  Rebates earned: ${engine.wallet.total_rebates_earned:.4f}")
    print(f"{'=' * 70}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Polymarket Paper Trading Market Maker Bot"
    )
    parser.add_argument(
        "-c", "--config",
        default=None,
        help="Path to config.json (default: ./config.json)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable debug logging",
    )
    parser.add_argument(
        "--capital",
        type=float,
        default=None,
        help="Override starting capital (default: $100)",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run with simulated market data (no internet needed)",
    )
    args = parser.parse_args()

    setup_logging(verbose=args.verbose)
    config = Config.load(args.config)
    if args.capital is not None:
        config.starting_capital_usd = args.capital

    mode = "DEMO (simulated data)" if args.demo else "LIVE (Polymarket API)"
    print(f"\n  Polymarket Paper Trading Market Maker v0.1.0")
    print(f"  Mode: {mode}")
    print(f"  Starting capital: ${config.starting_capital_usd:.2f} (VIRTUAL)")
    print(f"  Strategy: Bands ({config.strategy.num_levels} levels, {config.strategy.spread_cents}¢ spread)")
    print(f"  Polling: every {config.api.poll_interval_seconds}s")
    print(f"  Risk: max position ${config.risk.max_position_usd}, daily limit -${config.risk.daily_loss_limit_usd}")
    print(f"\n  {'Generating simulated market...' if args.demo else 'Connecting to Polymarket...'}\n")

    run(config, demo=args.demo)


if __name__ == "__main__":
    main()
