"""
Entry point for the Poly-Trade market-making bot.

Usage
-----
::

    python -m bot            # live mode (requires token_ids in config.json)
    python -m bot --demo     # offline paper-trading demo

The ``--demo`` flag runs a short synthetic simulation without any network
connections.  In live mode the bot connects to Polymarket's WebSocket feed
and drives the paper engine on every order-book update.
"""
import argparse
import logging
import signal
import sys
import time

from .config import load_config
from .paper_engine import PaperEngine
from .risk import RiskManager
from .strategy import BandsStrategy
from .ws_feed import WsFeed

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
logger = logging.getLogger("bot")


def _build_engine(cfg) -> PaperEngine:
    strategy = BandsStrategy(
        spread_cents=cfg.spread_cents,
        size_per_level_usd=cfg.size_per_level_usd,
        skew_factor=cfg.skew_factor,
        max_position_usd=cfg.max_position_usd,
    )
    risk = RiskManager(
        max_position_usd=cfg.max_position_usd,
        daily_loss_limit=cfg.daily_loss_limit,
        max_drawdown=cfg.max_drawdown,
    )
    return PaperEngine(strategy=strategy, risk=risk)


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(
        description="Poly-Trade Polymarket market-making bot"
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run offline paper-trading demo (no network required)",
    )
    parser.add_argument(
        "--config",
        default="config.json",
        metavar="PATH",
        help="Path to config.json (default: config.json)",
    )
    args = parser.parse_args(argv)

    cfg = load_config(args.config)
    engine = _build_engine(cfg)

    if args.demo or not cfg.token_ids:
        if not args.demo:
            logger.info("No token_ids in config — running demo mode")
        engine.run_demo()
        return

    # --- Live mode ---
    feed = WsFeed(
        asset_ids=cfg.token_ids,
        on_book=engine.on_book_update,
        ws_url=cfg.ws_url,
    )
    feed.start()
    logger.info("Feed started for %d token(s). Press Ctrl-C to stop.", len(cfg.token_ids))

    stop_event = [False]

    def _handle_sig(signum, frame):
        stop_event[0] = True

    signal.signal(signal.SIGINT, _handle_sig)
    signal.signal(signal.SIGTERM, _handle_sig)

    try:
        while not stop_event[0]:
            time.sleep(1)
    finally:
        feed.stop()
        logger.info(
            "Stopped. Wallet=%.4f  Realized PnL=%.4f",
            float(engine.wallet.balance),
            float(engine.realized_pnl),
        )


if __name__ == "__main__":
    main()
