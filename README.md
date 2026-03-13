# Polymarket Paper Trading Market Maker Bot

A paper trading market maker for Polymarket prediction markets. Runs on your local machine — when you start the code, it starts market making with virtual money against real Polymarket order book data.

> **⚠️ This is a paper trading simulator. No real money is used.** Virtual $100 starting capital.  
> **⚠️ Not financial advice.** This is an educational tool for learning market microstructure.

## What It Does

The bot acts as an **automated liquidity provider** (market maker) on Polymarket's BTC 15-minute UP/DOWN binary markets:

1. **Fetches real order book data** from Polymarket's public CLOB API (no authentication needed)
2. **Places virtual limit orders** on both sides (BUY + SELL) using a bands strategy
3. **Simulates fills** when the real market price crosses your virtual order prices
4. **Tracks P&L, inventory, maker rebates** in real time
5. **Manages risk** with position limits, daily loss limits, and a circuit breaker

```
┌─────────────────────────────────────────────────────────────┐
│              MARKET MAKING LOOP (every 5 seconds)             │
│                                                               │
│  1. Fetch real order book → calculate midpoint                │
│  2. Generate BUY/SELL quotes at band levels                   │
│  3. Check if real market crossed our prices → simulate fills  │
│  4. Update inventory, P&L, rebates                            │
│  5. Apply risk checks → requote                               │
│  6. Display terminal dashboard                                │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.10+
- Internet connection (for live Polymarket data) — or use `--demo` for offline mode

### Install & Run

```bash
# Clone the repo
git clone https://github.com/epqqwppw/Poly-Trade.git
cd Poly-Trade

# Install dependency
pip install requests

# Run with real Polymarket data
python -m bot

# Or run in demo mode (no internet needed)
python -m bot --demo
```

### Options

```
python -m bot [OPTIONS]

Options:
  -c, --config PATH   Path to config.json (default: ./config.json)
  -v, --verbose        Enable debug logging
  --capital AMOUNT     Override starting capital (default: $100)
  --demo               Run with simulated market data (offline)
```

### Examples

```bash
# Paper trade with $100 on live Polymarket data
python -m bot

# Paper trade with $500 virtual capital
python -m bot --capital 500

# Test offline with simulated market data
python -m bot --demo

# Debug mode — see all API calls and strategy decisions
python -m bot --demo -v
```

## How Market Making Works

A market maker provides liquidity by posting both buy and sell orders. Profit comes from the **spread** (difference between buy and sell prices), not from predicting outcomes.

```
Example: BTC 15-minute UP/DOWN market

  Midpoint: $0.55 (YES token)

  You post:
    BUY  100 YES @ $0.53  (2¢ below mid)
    SELL 100 YES @ $0.57  (2¢ above mid)

  When both fill:
    Spent:    $53.00  (bought 100 @ $0.53)
    Received: $57.00  (sold 100 @ $0.57)
    Profit:   $4.00   (the spread × size)

  You don't care if BTC goes up or down!
```

### Bands Strategy

The bot uses a "bands" strategy — multiple order levels at increasing distances from the midpoint:

```
  $0.58 ── SELL level 3  ($8 size)
  $0.57 ── SELL level 2  ($8 size)
  $0.56 ── SELL level 1  ($8 size)
  $0.55 ← midpoint
  $0.54 ── BUY level 1   ($8 size)
  $0.53 ── BUY level 2   ($8 size)
  $0.52 ── BUY level 3   ($8 size)
```

### Inventory Skewing

When the bot accumulates too many YES tokens, it shifts quotes down to sell more and buy less. When inventory is low, it shifts up to buy more.

### Fill Simulation

Virtual orders fill when real market prices cross the order price:
- **BUY** fills when the real best ask drops to or below the buy price
- **SELL** fills when the real best bid rises to or above the sell price

## Risk Management

```
Level 1: Position Sizing
  └── Max $25 per position (25% of $100)

Level 2: Daily Loss Limit
  └── Stop trading at -$10/day

Level 3: Circuit Breaker
  └── 3 consecutive losses → pause 5 minutes

Level 4: Max Drawdown
  └── Stop at -$25 total (25% of capital)
```

## Configuration

Edit `config.json` to customize:

```jsonc
{
  "starting_capital_usd": 100.0,    // Virtual starting balance
  "seed_pct": 0.5,                  // % of capital to seed as YES tokens
  "strategy": {
    "spread_cents": 3,              // Distance from mid per level (in cents)
    "num_levels": 3,                // Number of bands on each side
    "size_per_level_usd": 8.0,     // USD per order level
    "requote_interval_seconds": 30, // How often to refresh quotes
    "inventory_skew_factor": 0.5   // How aggressively to skew (0-1)
  },
  "risk": {
    "max_position_usd": 25.0,      // Max $ in any single position
    "daily_loss_limit_usd": 10.0,  // Stop trading after this daily loss
    "max_drawdown_usd": 25.0,      // Kill switch threshold
    "circuit_breaker_losses": 3,   // Consecutive losses before pause
    "circuit_breaker_pause_seconds": 300
  },
  "api": {
    "poll_interval_seconds": 5,     // How often to fetch order book
    "market_scan_interval_seconds": 60
  }
}
```

## Project Structure

```
Poly-Trade/
├── bot/
│   ├── __init__.py
│   ├── __main__.py        # python -m bot entry point
│   ├── main.py            # Main loop and CLI
│   ├── config.py          # Configuration loading
│   ├── models.py          # Data models (Order, Trade, Wallet, OrderBook)
│   ├── market_data.py     # Polymarket API client (public, no auth needed)
│   ├── paper_engine.py    # Paper trading engine (virtual fills, wallet)
│   ├── strategy.py        # Bands market making strategy
│   ├── risk.py            # Risk management (limits, circuit breaker)
│   ├── display.py         # Terminal dashboard
│   └── demo.py            # Offline demo mode with simulated data
├── tests/
│   └── test_paper_engine.py  # Unit tests (24 tests)
├── docs/                     # Research documentation
├── config.json               # Default configuration
├── requirements.txt          # Python dependencies (just 'requests')
└── README.md
```

## Running Tests

```bash
python -m unittest tests.test_paper_engine -v
```

## Key Polymarket Concepts

| Concept | Explanation |
|---|---|
| **CLOB** | Central Limit Order Book — like a stock exchange, not an AMM |
| **Maker** | Posts limit orders (resting on book) — **0% fees + rebates** |
| **Taker** | Crosses the spread (market orders) — pays up to 1.56% fee |
| **YES/NO tokens** | Binary outcome tokens: one resolves to $1, the other to $0 |
| **Token split** | Convert 1 USDC → 1 YES + 1 NO token |
| **Midpoint** | Average of best bid and best ask |
| **Spread** | Difference between best ask and best bid |

## Revenue Sources for Market Makers

| Source | Mechanism |
|---|---|
| **Spread capture** | Buy low (bid), sell high (ask) on round trips |
| **Maker rebates** | 25% of taker fees earned daily in USDC (at 00:00 UTC) |
| **Liquidity rewards** | Direct USDC rewards for maintaining tight quotes |

## From Paper to Real Trading

This paper trading bot is Phase 1. After validating the strategy:

1. **Paper trade for 1-2 weeks** — verify positive P&L, understand market behavior
2. **Scale to $5-10 real USDC** — test with real execution (see PRD for auth setup)
3. **Scale to $100** — full deployment with validated strategy

See [docs/PRD-polymarket-btc-trading-bot.md](docs/PRD-polymarket-btc-trading-bot.md) for the full production roadmap.

## Related Documentation

- [PRD: Polymarket BTC 15-Min Trading Bot](docs/PRD-polymarket-btc-trading-bot.md) — Full product requirements
- [Market Making & Custom Skills Research](docs/market-making-and-custom-skills-research.md) — Deep dive on market making viability
- [OpenClaw Deep Research](docs/openclaw-deep-research.md) — OpenClaw/PolyClaw analysis

---

> ⚠️ **Disclaimer:** This is an educational paper trading tool, not financial advice. Real trading on Polymarket involves real financial risk. Never risk money you can't afford to lose. Always use dedicated hot wallets and test thoroughly before live trading.
