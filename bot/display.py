"""Terminal display — formatted output of bot status."""

from __future__ import annotations

import os
import time
from typing import List, Optional

from .models import MarketInfo, OrderBook, Side, Trade, VirtualOrder, Wallet


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def display_status(
    market: Optional[MarketInfo],
    book: Optional[OrderBook],
    wallet: Wallet,
    open_orders: dict,
    recent_trades: List[Trade],
    total_pnl: float,
    daily_pnl: float,
    starting_capital: float,
    risk_status: str,
    tick_count: int,
    is_seeded: bool,
) -> None:
    """Print a formatted status update to the terminal."""
    clear_screen()
    now = time.strftime("%Y-%m-%d %H:%M:%S")

    print("=" * 70)
    print("  POLYMARKET PAPER TRADING MARKET MAKER")
    print(f"  {now}  |  Tick #{tick_count}  |  PAPER MODE (no real money)")
    print("=" * 70)

    # Market info
    if market:
        q = market.question
        if len(q) > 55:
            q = q[:52] + "..."
        print(f"\n  Market: {q}")
        print(f"  Token:  {market.yes_token_id[:20]}...")
        print(f"  Ends:   {market.end_date}")
    else:
        print("\n  Market: Searching for active market...")

    # Order book
    if book and book.best_bid and book.best_ask:
        print(f"\n  ┌─── LIVE ORDER BOOK ────────────────────────────┐")
        print(f"  │  Best Bid: ${book.best_bid:.4f}   Mid: ${book.midpoint:.4f}   Best Ask: ${book.best_ask:.4f}")
        print(f"  │  Spread:   ${book.spread:.4f} ({book.spread * 100:.1f}¢)")
        # Show top 3 levels
        for i in range(min(3, max(len(book.bids), len(book.asks)))):
            bid_str = f"${book.bids[i].price:.2f} × {book.bids[i].size:.0f}" if i < len(book.bids) else " " * 14
            ask_str = f"${book.asks[i].price:.2f} × {book.asks[i].size:.0f}" if i < len(book.asks) else " " * 14
            print(f"  │  {bid_str:>16s}  |  {ask_str:<16s}")
        print(f"  └─────────────────────────────────────────────────┘")

    # Portfolio
    mid = book.midpoint if book else 0.5
    yes_value = wallet.yes_tokens * (mid or 0.5)
    port_value = wallet.usdc + yes_value
    pnl_pct = (total_pnl / starting_capital * 100) if starting_capital > 0 else 0

    print(f"\n  ┌─── PORTFOLIO ──────────────────────────────────┐")
    print(f"  │  USDC Balance:    ${wallet.usdc:>10.2f}")
    print(f"  │  YES Tokens:       {wallet.yes_tokens:>10.1f} (${yes_value:.2f})")
    print(f"  │  Avg Entry Price:  ${wallet.avg_yes_entry:>10.4f}")
    print(f"  │  ─────────────────────────────────────────────")
    print(f"  │  Portfolio Value:  ${port_value:>10.2f}")
    print(f"  │  Starting Capital: ${starting_capital:>10.2f}")

    pnl_color = "+" if total_pnl >= 0 else ""
    print(f"  │  Total P&L:       {pnl_color}${total_pnl:>9.2f} ({pnl_color}{pnl_pct:.1f}%)")

    daily_color = "+" if daily_pnl >= 0 else ""
    print(f"  │  Daily P&L:       {daily_color}${daily_pnl:>9.4f}")
    print(f"  │  Rebates Earned:  ${wallet.total_rebates_earned:>10.4f}")
    print(f"  └─────────────────────────────────────────────────┘")

    # Open orders
    buy_orders = [o for o in open_orders.values() if o.side == Side.BUY]
    sell_orders = [o for o in open_orders.values() if o.side == Side.SELL]
    buy_orders.sort(key=lambda o: o.price, reverse=True)
    sell_orders.sort(key=lambda o: o.price)

    print(f"\n  ┌─── VIRTUAL ORDERS ({len(open_orders)} open) ──────────────┐")
    if sell_orders:
        for o in reversed(sell_orders):
            print(f"  │  SELL  ${o.price:.2f}  ×  {o.size:>6.1f}  (L{o.level})")
    if book and book.midpoint:
        print(f"  │  ─── midpoint ${book.midpoint:.4f} ─────────────────")
    if buy_orders:
        for o in buy_orders:
            print(f"  │  BUY   ${o.price:.2f}  ×  {o.size:>6.1f}  (L{o.level})")
    if not open_orders:
        print(f"  │  (no open orders)")
    print(f"  └─────────────────────────────────────────────────┘")

    # Recent trades
    print(f"\n  ┌─── RECENT FILLS ({len(recent_trades)} total) ──────────────┐")
    for trade in recent_trades[-5:]:
        ts = time.strftime("%H:%M:%S", time.localtime(trade.timestamp))
        pnl_str = f" P&L ${trade.pnl:+.4f}" if trade.side == Side.SELL else ""
        print(f"  │  {ts}  {trade.side.value:4s}  ${trade.price:.2f} × {trade.size:.1f}{pnl_str}")
    if not recent_trades:
        print(f"  │  (no fills yet — waiting for market to cross our quotes)")
    print(f"  └─────────────────────────────────────────────────┘")

    # Status
    seeded = "✓ Inventory seeded" if is_seeded else "⏳ Waiting to seed..."
    print(f"\n  Status: {seeded}")
    print(f"  Risk:   {risk_status}")
    print(f"\n  Press Ctrl+C to stop the bot gracefully.")
    print("─" * 70)
