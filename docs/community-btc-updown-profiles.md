# Community Polymarket BTC UP/DOWN Trading Bot Profiles

> **Last updated:** March 13, 2026  
> **Scope:** Community-built GitHub profiles focused on Polymarket Bitcoin UP/DOWN trading.  
> **Related doc:** [`ecosystem-github-profiles.md`](./ecosystem-github-profiles.md) for official org profiles.

---

## Overview

These six repositories represent the most active and battle-tested community implementations for trading Polymarket's Bitcoin binary markets. Each profile was researched using the GitHub API — READMEs, file trees, commit histories, and fork networks were all examined.

| Rank | Repo | Language | ⭐ Stars | 🍴 Forks | Strategy | Last Active |
|---|---|---|---|---|---|---|
| 🥇 | [taetaehoho/poly-kalshi-arb](#1-taetaehoho-poly-kalshi-arb) | Rust | 421 | 131 | Cross-platform arb (Poly + Kalshi) | Dec 2025 |
| 🥈 | [sed000/polymarket-btc-1h](#2-sed000-polymarket-btc-1h) | TypeScript | 0 | 1 | Directional 1h BTC | Feb 2026 🟢 |
| 🥉 | [svnmcqueen/polymarket-bot](#3-svnmcqueen-polymarket-bot) | Python | 2 | 1 | Same-platform arb (buy both sides) | Dec 2025 |
| 4 | [francescods04/poly](#4-francescods04-poly) | Python | 1 | 0 | Options pricing model | Jan 2026 |
| 5 | [bking5496/guerilla-trading](#5-bking5496-guerilla-trading) | Python | 0 | 0 | Multi-signal (price+sentiment+whale) | Jan 2026 |
| 6 | [evgenss79/PolM](#6-evgenss79-polm) | Python | 0 | 0 | Semi-manual browser-based | Jan 2026 |

---

## 1. taetaehoho/poly-kalshi-arb

**GitHub:** https://github.com/taetaehoho/poly-kalshi-arb  
**Language:** Rust 🦀  
**Stars:** ⭐ 421 | **Forks:** 131  
**Created:** Dec 16, 2025 | **Last Push:** Dec 21, 2025  
**License:** Not specified  

### Profile Summary

The most-starred community arbitrage bot in the Polymarket ecosystem. Built in Rust for ultra-low latency, this bot exploits price discrepancies between **Polymarket and Kalshi** on identical BTC/ETH/SOL/XRP 15-minute UP/DOWN binary markets. With 131 forks, it has become the de facto reference implementation for cross-exchange prediction market arbitrage.

### Why It Stands Out

- **Rust performance:** Lock-free order book cache, SIMD arb detection — sub-millisecond opportunity detection
- **Battle-tested:** 421 stars acquired within weeks of publish — organic traction from the trading community
- **Circuit breaker:** Built-in risk controls halt the bot automatically on excessive losses or errors
- **Dry-run mode:** Full paper trading with `DRY_RUN=1` before touching real funds
- **Both exchanges:** Covers Polymarket + Kalshi simultaneously

### Strategy

**Core arbitrage logic:**
```
YES + NO = $1.00 guaranteed at settlement

Opportunity: Kalshi_YES_ask + Poly_NO_ask < $1.00
Example:
  Kalshi YES ask:  42¢
  Poly   NO  ask:  56¢
  Total cost:      98¢  ← pay this
  Guaranteed:     100¢  ← collect this
  Profit:           2¢  per contract (after fees)
```

**Four arbitrage types detected:**

| Type | Buy Side | Sell Side |
|---|---|---|
| `poly_yes_kalshi_no` | Polymarket YES | Kalshi NO |
| `kalshi_yes_poly_no` | Kalshi YES | Polymarket NO |
| `poly_same_market` | Polymarket YES + NO | (same platform rare arb) |
| `kalshi_same_market` | Kalshi YES + NO | (same platform rare arb) |

**Fee handling:** Kalshi fees (`ceil(0.07 × contracts × price × (1-price))`) are baked into arb detection; Polymarket has zero trading fees.

### File Structure

```
e_poly_kalshi_arb/src/
├── main.rs              ← Entry point, WebSocket orchestration
├── types.rs             ← MarketArbState type definitions
├── execution.rs         ← Concurrent leg execution, in-flight deduplication
├── position_tracker.rs  ← Channel-based fill recording, P&L tracking
├── circuit_breaker.rs   ← Risk limits, error tracking, auto-halt
├── discovery.rs         ← Kalshi↔Polymarket market matching & caching
├── cache.rs             ← Team code mappings (EPL, NBA, etc.)
├── kalshi.rs            ← Kalshi REST/WebSocket client
├── polymarket.rs        ← Polymarket WebSocket client
├── polymarket_clob.rs   ← Polymarket CLOB order execution
└── config.rs            ← League configs, arb thresholds
```

### Key Configuration (`.env`)

```bash
# Kalshi credentials
KALSHI_API_KEY_ID=your_kalshi_api_key_id
KALSHI_PRIVATE_KEY_PATH=/path/to/kalshi_private_key.pem

# Polymarket credentials
POLY_PRIVATE_KEY=0xYOUR_WALLET_PRIVATE_KEY
POLY_FUNDER=0xYOUR_WALLET_ADDRESS

# Bot config
DRY_RUN=1                    # 1=paper, 0=live
CB_MAX_DAILY_LOSS=5000        # Max daily loss in cents
CB_MAX_POSITION_PER_MARKET=100
CB_MAX_TOTAL_POSITION=500
```

### Quick Start

```bash
# Install Rust 1.75+, then:
cd e_poly_kalshi_arb
cargo build --release

# Paper trading
DRY_RUN=1 dotenvx run -- cargo run --release

# Test synthetic arb
TEST_ARB=1 DRY_RUN=0 dotenvx run -- cargo run --release

# Live trading
DRY_RUN=0 CB_MAX_DAILY_LOSS=10000 dotenvx run -- cargo run --release
```

### Commit History (Full)

| # | SHA | Message | Date |
|---|---|---|---|
| 1 | `15aeb77` | `.` | 2025-12-21 |
| 2 | `03a37b6` | `remove dumb stuff` | 2025-12-21 |
| 3 | `e621d3d` | `.` | 2025-12-17 |
| 4 | `e0f3a47` | `.` | 2025-12-16 |
| 5 | `70f9f53` | `Initial commit` | 2025-12-16 |

> **Note:** Minimal commit messages — the author iterated rapidly over 5 days. The 421 stars indicate the code was shared in trading communities and spread organically.

### Status & Limitations

- ✅ Production-ready architecture (circuit breaker, position tracking, fee calc)
- ✅ Dry-run / paper trading mode
- ⚠️ **Requires both a Kalshi account and a Polymarket account** — not Polymarket-only
- ⚠️ Kalshi is US-only (geo-restricted); non-US users cannot use the Kalshi leg
- ❌ No UI configuration — risk limits set only via env vars
- ❌ No multi-account support (listed as TODO)

---

## 2. sed000/polymarket-btc-1h

**GitHub:** https://github.com/sed000/polymarket-btc-1h  
**Language:** TypeScript (Bun runtime)  
**Stars:** 0 | **Forks:** 1  
**Created:** Jan 21, 2026 | **Last Push:** Feb 4, 2026 🟢  
**License:** Not specified  

### Profile Summary

The **most actively maintained** community bot as of early 2026. A directional trading bot for **Polymarket Bitcoin 1-hour markets** built with TypeScript and Bun. Unlike the arb bots, this one takes a directional position (betting that BTC will go UP or DOWN) based on configurable thresholds and entry criteria. Features a rich terminal UI, SQLite trade tracking, backtesting, and a genetic optimization system for parameter tuning.

### Why It Stands Out

- **Active development:** Resolved real production bugs — stop-loss race conditions, WebSocket exit monitoring, order fill retries
- **Backtesting + optimization:** Includes genetic algorithm optimizer for parameter tuning (`bun run backtest:genetic`)
- **SQLite persistence:** Every trade, stat, and log stored in a local database with queryable CLI commands
- **Bun runtime:** Faster startup and execution than Node.js
- **Co-authored with Claude:** Commit messages show AI-assisted development using Claude Opus — modern workflow

### Strategy

**Directional trading on 1-hour BTC markets:**
1. Scanner (`scanner.ts`) finds eligible BTC 1-hour markets on Polymarket
2. Bot evaluates entry criteria from `trading.config.json`
3. Enters a position (YES or NO) when thresholds are met
4. Monitors exit via WebSocket price feed (replacing broken limit-order approach)
5. Exits on profit target or stop-loss

**Key design decisions revealed in commits:**
- Replaced limit orders with WebSocket monitoring to fix stop-loss race conditions
- Added 5-retry logic on API errors to prevent premature order cancellation
- Stop-loss now cancels any open limit order BEFORE executing market sell

### File Structure

```
src/
├── index.ts         ← Entry point
├── bot.ts           ← Main trading loop (61KB — the core logic)
├── scanner.ts       ← Market discovery and eligibility filters
├── trader.ts        ← Order placement and trade execution (24KB)
├── websocket.ts     ← WebSocket price feed, user stream (25KB)
├── db.ts            ← SQLite trade/stats/log persistence (22KB)
├── config.ts        ← Config loader and validation (15KB)
├── ui.tsx           ← Terminal dashboard (Ink/React, 14KB)
├── logger.ts        ← Log levels and activity log
├── rate-limiter.ts  ← API rate limiter
└── backtest/        ← Backtesting engine + genetic optimizer
```

### Key Configuration (`trading.config.json`)

```json
{
  "trading": {
    "paperTrading": true,
    "paperBalance": 100,
    "maxPositions": 3
  },
  "activeMode": "normal",
  "modes": {
    "normal": {
      "entryThreshold": 0.35,
      "exitProfit": 0.15,
      "stopLoss": -0.10
    }
  },
  "backtest": {
    "mode": "normal"
  }
}
```

### Environment Variables

```bash
# Required for live trading
PRIVATE_KEY=0xYOUR_PRIVATE_KEY

# Optional (auto-derived from PRIVATE_KEY if not set)
POLY_API_KEY=
POLY_API_SECRET=
POLY_API_PASSPHRASE=

# For proxy wallets (signature type 1)
FUNDER_ADDRESS=
```

### Quick Start

```bash
npm install -g bun  # or: curl -fsSL https://bun.sh/install | bash

git clone https://github.com/sed000/polymarket-btc-1h
cd polymarket-btc-1h
bun install

# Paper trading (default)
bun dev

# Check paper trade history
bun run db:paper
bun run db:stats:paper

# Backtest
bun run backtest:run

# Genetic optimization
bun run backtest:genetic
```

### CLI Commands

| Command | Description |
|---|---|
| `bun start` | Run the bot |
| `bun dev` | Run with auto-reload |
| `bun run backtest:run` | Run a backtest |
| `bun run backtest:optimize` | Optimize parameters |
| `bun run backtest:genetic` | Genetic optimization (recommended) |
| `bun run db:paper` | Recent paper trades |
| `bun run db:real` | Recent real trades |
| `bun run db:stats:paper` | Paper trading stats |
| `bun run db:stats:real` | Real trading stats |

### Recent Commit History (Most Recent 10)

| Date | Message |
|---|---|
| 2026-02-04 | `README.md` |
| 2026-02-01 | `Fix stop-loss false sold on unfilled exits` |
| 2026-02-01 | `Improve exit handling and sell diagnostics` |
| 2026-02-01 | `Remove spammy activity logs` |
| 2026-02-01 | `Remove limit orders - use WebSocket monitoring instead` ← Key fix |
| 2026-01-31 | `Fix premature order cancellation on API errors` |
| 2026-01-31 | `Add detailed stop-loss error logging to activity log` |
| 2026-01-31 | `Fix stop-loss: cancel limit order BEFORE market sell` ← Key fix |
| 2026-01-31 | `Fix stop-loss not triggering and add persistent activity logging` |
| 2026-01-31 | `Fix stop-loss recording wrong exit price` |

> **Pattern:** 7 of the top 10 commits are stop-loss related — shows the author battle-tested the exit logic with real money on Jan 31, 2026.

### Status & Limitations

- ✅ Most recently updated bot (Feb 2026)
- ✅ Paper trading + real trading modes
- ✅ Full backtesting + genetic optimization
- ✅ SQLite persistence + queryable stats
- ✅ WebSocket-based exit monitoring (fixed broken limit-order exits)
- ⚠️ **Directional strategy** — not risk-free like arb; requires correct market direction
- ⚠️ 1-hour markets only (not 15-minute)
- ⚠️ No Docker deployment (Bun-only)

---

## 3. svnmcqueen/polymarket-bot

**GitHub:** https://github.com/svnmcqueen/polymarket-bot  
**Language:** Python  
**Stars:** ⭐ 2 | **Forks:** 1  
**Created:** Dec 29, 2025 | **Last Push:** Dec 31, 2025  
**License:** Not specified  

### Profile Summary

A production-grade Python arbitrage bot targeting **BTC 15-minute UP/DOWN markets on Polymarket only** (no Kalshi dependency). Core strategy: when `UP_ask + DOWN_ask < 0.97`, buy both sides simultaneously for a guaranteed profit at expiry. Features the most complete modular architecture of any Python bot in this list, with Docker support and Discord alerts.

### Why It Stands Out

- **Polymarket-only** — no Kalshi account needed
- **Cleanest Python architecture:** Separate modules for scanning, execution, hedging, monitoring
- **Docker deployment:** Full `Dockerfile` + `docker-compose.yml` for cloud deployment
- **Legging strategy:** Optional asymmetric entry — buy one side first, then leg into the second at a better price
- **Daily loss limit:** Hard stop after losing > $5 in 24 hours
- **Discord webhooks:** Real-time trade and error notifications

### Strategy

**Same-platform arbitrage (both sides on Polymarket):**
```
Signal: UP_ask + DOWN_ask < 0.97

Example:
  UP ask:   0.48
  DOWN ask: 0.48
  Total:    0.96  ← pay this
  Payout:   1.00  ← collect this at expiry
  Profit:   0.04 per $1 invested (4%)
```

**Optional legging entry** — instead of buying both legs simultaneously, buy one leg first:
- Target combined total: `LEGGING_TARGET_TOTAL_MIN=0.84` to `LEGGING_TARGET_TOTAL_MAX=0.96`
- Max unhedged time: `LEGGING_MAX_UNHEDGED_SECONDS=60` before force-hedging

### File Structure

```
polymarket-bot/
├── btc_arb_bot.py          ← Main bot logic (single-file, 43KB)
├── cancel_all.py           ← Emergency: cancel all open orders
├── check_balance.py        ← Check wallet USDC balance
├── config.py               ← Config loader with validation (10KB)
├── logger.py               ← Structured logging with decorators (10KB)
├── test_ob.py              ← Order book tests
├── requirements.txt        ← Python dependencies
├── Dockerfile              ← Container build
├── docker-compose.yml      ← Container orchestration
├── entrypoint.sh           ← Docker startup with health check
├── .env.example            ← Config template
├── core/                   ← Core trading engine
├── strategy/               ← Strategy logic (ArbitrageEngine, RiskManager)
├── execution/              ← Order execution (LeggingManager, OrderManager)
├── monitoring/             ← Dashboard + Discord notifications
└── utils/                  ← Shared utilities
```

### Key Configuration (`.env`)

```bash
# Required
PRIVATE_KEY=0xYOUR_PRIVATE_KEY_HERE
WALLET_ADDRESS=0xYOUR_WALLET_ADDRESS
INITIAL_BUDGET=25            # Total bankroll in USDC

# Arb thresholds
ARB_THRESHOLD=0.97           # Execute when UP+DOWN < this value
MIN_NET_ROI=0.02             # Minimum 2% ROI after fees

# Safety
DAILY_LOSS_LIMIT=5.00        # Stop if daily loss exceeds $5
MAX_POSITION_SIZE=1.00       # Never risk more than $1 per position
STOP_LOSS_PCT=0.50           # Exit at -50% loss

# Legging (optional — enabled by default)
LEGGING_ENABLED=true
LEGGING_TARGET_TOTAL_MIN=0.84
LEGGING_TARGET_TOTAL_MAX=0.96
LEGGING_MAX_UNHEDGED_SECONDS=60

# Discord alerts (optional)
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_URL
```

### Safety Features

| Feature | Description |
|---|---|
| Startup confirmation | Prompts `Y` before trading |
| Daily loss limit | Stops if down > $5 in 24h |
| Position size limit | Never exceeds $1 per position |
| Stop loss | Auto-exits at -50% |
| Market cooldown | Won't re-enter same market for 24h |
| Graceful shutdown | `Ctrl+C` cancels all pending orders |

### Quick Start

```bash
git clone https://github.com/svnmcqueen/polymarket-bot
cd polymarket-bot
python3.11 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Edit with your credentials

# Dry run
python btc_arb_bot.py --dry-run

# Live trading
python btc_arb_bot.py

# Docker
docker-compose up -d
```

### Cloud Deployment

Supports: Railway, Render, AWS EC2, DigitalOcean Droplet (via Docker)

### Status & Limitations

- ✅ Polymarket-only (no Kalshi needed)
- ✅ Docker deployment ready
- ✅ Discord notifications
- ✅ Legging strategy for better entries
- ✅ Safety limits (daily loss, position size, stop-loss)
- ⚠️ Only 2 commits total (very fresh codebase — created Dec 29, pushed Dec 31, 2025)
- ⚠️ 15-minute markets only
- ⚠️ Low community adoption vs `taetaehoho` (only 2 stars vs 421)

---

## 4. francescods04/poly

**GitHub:** https://github.com/francescods04/poly  
**Language:** Python  
**Stars:** ⭐ 1 | **Forks:** 0  
**Created:** Jan 4, 2026 | **Last Push:** Jan 6, 2026  
**License:** MIT  

### Profile Summary

The most **academically complete** bot in this list. Rather than pure arbitrage, it builds a **digital options pricing model** using Chainlink price feeds as the resolution oracle source — matching Polymarket's actual resolution mechanism. Includes ML-calibrated probabilities, Kelly criterion position sizing, and a comprehensive backtesting framework.

### Why It Stands Out

- **Correct pricing source:** Uses Chainlink WebSocket for prices, matching Polymarket's resolution oracle — avoids Binance/Coinbase discrepancies
- **Options pricing formula:** `p = Φ((ln(St/S0) + μτ) / (σ√τ))` — professional digital option pricing
- **ML calibration:** Platt scaling + isotonic regression to calibrate model probabilities
- **EWMA volatility:** Dynamic volatility forecasting with regime detection
- **Kelly criterion:** Optimal position sizing based on edge
- **Avellaneda-Stoikov quoting:** Market-maker style spread generation

### Strategy

**Three combined signal types:**

| Signal Type | Weight | Indicators |
|---|---|---|
| Momentum | 40% | RSI, MACD, SMA(20) |
| Mean Reversion | 30% | Z-score ±1.5, Bollinger Bands |
| Volatility filter | 30% | ATR — reduces size in high vol |

**15-minute digital options pricing:**
```python
# Core formula (Black-Scholes digital option)
p = Φ((ln(St/S0) + μτ) / (σ√τ))
# Where:
#   S0 = Chainlink price at window start
#   St = Current Chainlink price  
#   σ  = EWMA volatility forecast
#   τ  = Time remaining to expiration
#   Φ  = Normal CDF
```

### File Structure

```
poly/
├── src/
│   ├── data/
│   │   ├── chainlink.py        ← Chainlink WebSocket feed (the resolution source)
│   │   ├── polymarket.py       ← Polymarket CLOB client
│   │   ├── timeseries.py       ← Timeseries data handling
│   │   └── storage/
│   │       ├── database.py     ← SQLite manager
│   │       └── parquet_storage.py
│   ├── strategy/
│   │   ├── momentum.py         ← RSI, MACD, SMA signals
│   │   ├── reversion.py        ← Z-score, Bollinger Band signals
│   │   ├── volatility.py       ← ATR volatility filter
│   │   ├── hybrid.py           ← Combines all signals
│   │   └── enhanced.py         ← Enhanced strategy + Kelly sizing
│   ├── backtest/
│   │   ├── engine.py           ← Simple backtest engine
│   │   └── enhanced_engine.py  ← Full engine with Kelly criterion
│   └── execution/
│       ├── paper_bot.py        ← Paper trading simulation
│       └── live_bot.py         ← Live trading (TODO — not yet implemented)
│
├── strategies/
│   └── digital_options_15m/    ← NEW professional strategy
│       ├── core/               ← Digital option pricing + EWMA vol
│       ├── models/             ← ML calibration (Platt, isotonic)
│       ├── execution/          ← CLOB client + GTD orders
│       ├── risk/               ← Position limits + kill-switch
│       └── backtest/           ← Realistic backtesting
│
├── data/databases/
│   └── polymarket.db           ← SQLite (14,600+ markets)
│
└── scripts/
    ├── run_paper.py            ← Paper trading entry point
    ├── backtest_enhanced.py    ← Enhanced backtest (recommended)
    ├── train_calibration_model.py ← Train ML probability model
    └── run_backtest.py         ← Run full backtest pipeline
```

### Supported Assets

BTC, ETH, SOL, ADA, DOGE, MATIC, AVAX, DOT, XRP, LINK — all Polymarket 15-minute UP/DOWN markets.

### Quick Start

```bash
git clone https://github.com/francescods04/poly
cd poly
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Paper trading
python scripts/run_paper.py

# Enhanced backtesting with Kelly criterion
python scripts/backtest_enhanced.py

# Full ML pipeline (collect → scrape → generate → train → backtest)
python scripts/collect_historical_prices.py --symbol BTC --days 30
python scripts/scrape_historical_15m_markets.py --symbols BTC --days 30
python scripts/generate_calibration_examples.py --symbols BTC --days 30
python scripts/train_calibration_model.py --cross-validate
python scripts/run_backtest.py --symbols BTC --start-date 2024-12-01 --end-date 2024-12-31
```

### Status & Limitations

- ✅ Correct Chainlink price source (matches Polymarket resolution)
- ✅ Professional options pricing model
- ✅ ML probability calibration
- ✅ Kelly criterion position sizing
- ✅ Multi-asset support (10 cryptos)
- ✅ Comprehensive backtesting
- ⚠️ **Live trading NOT implemented** — paper trading only
- ⚠️ Very fresh codebase (3 days of commits: Jan 4–6, 2026)
- ❌ No deployment tooling (no Docker)

---

## 5. bking5496/guerilla-trading

**GitHub:** https://github.com/bking5496/guerilla-trading  
**Language:** Python  
**Stars:** 0 | **Forks:** 0  
**Created:** Jan 26, 2026 | **Last Push:** Jan 26, 2026  
**License:** Not specified  

### Profile Summary

A multi-signal trading framework built by an AI agent ("Guerilla") learning to trade crypto and prediction markets. Currently in **Phase 0.5 — Foundation building**. Unique because it combines **market odds + X/Twitter sentiment + whale activity** into a weighted signal, rather than pure price/arb logic. The `bots/polymarket/` sub-directory contains the Polymarket-specific trading logic.

### Why It Stands Out

- **Multi-signal approach:** 3 independent signal sources combined with configurable weights
- **Sentiment integration:** X/Twitter sentiment analysis as a trading signal
- **Whale tracking:** On-chain large trade activity as a signal
- **AI-authored:** Self-described as an AI agent learning to trade — interesting meta-layer
- **Extensible framework:** Easy to add new signal sources

### Strategy

**Three-signal weighted combination:**

| Signal | Default Weight | Source |
|---|---|---|
| Market odds | 40% | Polymarket order book (current prices) |
| X/Twitter sentiment | 35% | Twitter/X API sentiment analysis |
| Whale activity | 25% | On-chain large transaction monitoring |

**Entry logic:** Combined weighted signal must exceed threshold to trigger trade on BTC 15-minute markets.

### Repository Structure

```
guerilla-trading/
├── README.md
├── bots/
│   └── polymarket/     ← Polymarket-specific bot logic
├── tools/              ← Trading utilities and scripts
├── analysis/           ← Market analysis notebooks
└── docs/               ← Learning notes and documentation
```

### Status

> **Phase 0.5** — Foundation building, paper trading, learning

- ✅ Unique multi-signal framework (sentiment + whale + price)
- ✅ Extensible architecture
- ⚠️ Very early stage — one commit, created and last pushed same day (Jan 26, 2026)
- ⚠️ Requires X/Twitter API access for sentiment signals
- ❌ No README detail on specific implementation
- ❌ No quick start guide or config documentation

---

## 6. evgenss79/PolM

**GitHub:** https://github.com/evgenss79/PolM  
**Language:** Python  
**Stars:** 0 | **Forks:** 0  
**Created:** Jan 20, 2026 | **Last Push:** Jan 21, 2026  
**License:** Not specified  

### Profile Summary

A **semi-manual / assisted trading bot** for Polymarket BTC 15-minute markets. Rather than fully autonomous execution, it uses a **watch mode** where the bot finds markets, generates signals, and presents them to the trader, who confirms each trade. Built around a `config.json` driven state machine with session persistence.

> **Note:** The main `README.md` describes a Flutter mobile app (FamilyApp — an unrelated project in Russian). The actual trading bot documentation is in `README_BOT.md` and `QUICKSTART.md`. The GitHub repo name "PolM" and `.env`/config files confirm it is a Polymarket monitor bot.

### Why It Stands Out

- **Semi-manual safety:** Human confirmation on each trade — prevents runaway losses from bugs
- **Watch mode:** Monitor-only mode with no execution — good for research
- **Session persistence:** `state.json` tracks open positions across restarts
- **Configurable signals:** `config.json.example` shows pluggable signal architecture
- **Most documentation:** Has `BUILD_SUMMARY.txt`, `CHANGELOG.md`, `MEMORY_RULES.md`, `PROJECT_STATE.md`, `QUICKSTART.md`, `README_BOT.md`, `TODO.md` — unusually thorough for a small repo

### File Structure

```
PolM/
├── README.md               ← (Unrelated Flutter app docs — ignore)
├── README_BOT.md           ← Actual trading bot documentation (26KB)
├── QUICKSTART.md           ← Quick start guide
├── BUILD_SUMMARY.txt       ← Build and deployment summary
├── CHANGELOG.md            ← Change history (16KB)
├── MEMORY_RULES.md         ← Bot operating rules
├── PROJECT_STATE.md        ← Current project state
├── TODO.md                 ← Pending features
├── config.json.example     ← Configuration template
├── state.json.example      ← State persistence template
├── requirements.txt        ← Python dependencies
├── scripts/                ← Utility scripts
└── src/                    ← Bot source code
```

### Status & Limitations

- ✅ Semi-manual mode for safe learning
- ✅ Watch-only mode (no execution)
- ✅ Session persistence
- ✅ Most documentation of any bot here
- ⚠️ Only 1 meaningful commit after initial push (very fresh — Jan 20–21, 2026)
- ⚠️ Main README is misleading (Flutter app docs in Russian)
- ❌ Not fully autonomous
- ❌ No Docker or cloud deployment docs

---

## Comparison Table

| Feature | taetaehoho | sed000 | svnmcqueen | francescods04 | bking5496 | evgenss79 |
|---|---|---|---|---|---|---|
| **Language** | Rust | TypeScript | Python | Python | Python | Python |
| **Strategy** | Cross-platform arb | Directional 1h | Same-platform arb | Options pricing | Multi-signal | Semi-manual |
| **Market** | BTC/ETH/SOL/XRP 15m | BTC 1h | BTC 15m | BTC/ETH/SOL 15m | BTC 15m | BTC 15m |
| **Stars** | ⭐ 421 | 0 | ⭐ 2 | ⭐ 1 | 0 | 0 |
| **Forks** | 131 | 1 | 1 | 0 | 0 | 0 |
| **Paper mode** | ✅ (`DRY_RUN=1`) | ✅ (default) | ✅ (`--dry-run`) | ✅ (paper only) | ❌ | ✅ (watch mode) |
| **Docker** | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| **Backtesting** | ❌ | ✅ + genetic opt | ❌ | ✅ + Kelly | ❌ | ❌ |
| **Discord alerts** | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| **Kalshi required** | ✅ Yes | ❌ No | ❌ No | ❌ No | ❌ No | ❌ No |
| **Live trading** | ✅ | ✅ | ✅ | ❌ Not yet | ❌ Not yet | ✅ (manual) |
| **Risk-free arb** | ✅ Yes | ❌ No | ✅ Yes | ❌ No | ❌ No | ❌ No |
| **Last active** | Dec 2025 | 🟢 Feb 2026 | Dec 2025 | Jan 2026 | Jan 2026 | Jan 2026 |

---

## Strategy Selector Guide

| Your goal | Best choice | Reason |
|---|---|---|
| **Guaranteed profit (risk-free), Polymarket-only** | `svnmcqueen/polymarket-bot` | Buy both UP+DOWN when sum < $0.97, no Kalshi needed |
| **Guaranteed profit, cross-exchange (highest potential)** | `taetaehoho/poly-kalshi-arb` | Poly + Kalshi arb, Rust performance, most proven (421⭐) |
| **Directional bet (take a market view on BTC)** | `sed000/polymarket-btc-1h` | Most actively maintained, battle-tested stop-loss, 1h markets |
| **Learn and backtest before risking money** | `francescods04/poly` | Paper trading only, full backtesting, correct Chainlink pricing |
| **Multi-signal + sentiment trading** | `bking5496/guerilla-trading` | Price + Twitter sentiment + whale signals combined |
| **Semi-manual / want to approve each trade** | `evgenss79/PolM` | Watch mode + manual confirm — safe for beginners |
| **Ultra-low latency (HFT style)** | `taetaehoho/poly-kalshi-arb` | Rust + SIMD + lock-free orderbook — fastest possible |

---

## How These Bots Use the Official Polymarket Stack

| Bot | Official SDK Used | WebSocket | Subgraph |
|---|---|---|---|
| `taetaehoho/poly-kalshi-arb` | Custom Rust CLOB client (Polymarket REST) | ✅ (`polymarket.rs`) | ❌ |
| `sed000/polymarket-btc-1h` | `@polymarket/clob-client` (TypeScript) | ✅ (`websocket.ts`) | ❌ |
| `svnmcqueen/polymarket-bot` | `py-clob-client` (Python) | ✅ (order book polling) | ❌ |
| `francescods04/poly` | `py-clob-client` (Python) | ✅ (Chainlink WS for prices) | ❌ |
| `bking5496/guerilla-trading` | `py-clob-client` (Python) | Likely | ❌ |
| `evgenss79/PolM` | `py-clob-client` (Python) | Likely | ❌ |

> **Observation:** None of these community bots use the Goldsky/subgraph layer — they all query live order books directly. The subgraph is more useful for historical data analysis than live trading.

---

## Security Notes

> ⚠️ **Always audit source code before providing any private keys or deploying with real funds.**

- All bots require your Ethereum **private key** for signing Polymarket transactions
- Store private keys in `.env` files — never hardcode them
- Use a **dedicated trading wallet** — never your primary Ethereum wallet
- Start with the minimum viable balance
- Test thoroughly in paper/dry-run mode first
- The `taetaehoho` bot additionally requires Kalshi RSA private key credentials

---

## Related Documentation

- [`ecosystem-github-profiles.md`](./ecosystem-github-profiles.md) — Official Polymarket, UMAprotocol, Goldsky org profiles
- [`bot-dev-quick-reference.md`](./bot-dev-quick-reference.md) — API endpoints and code snippets for bot developers
