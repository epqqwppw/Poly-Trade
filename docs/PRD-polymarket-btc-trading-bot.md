# PRD: Polymarket BTC 15-Minute Trading Bot

## Automated Trading Bot for $1/Hour Profit on Polymarket BTC UP/DOWN Markets

> **Document version:** 1.0  
> **Last updated:** March 13, 2026  
> **Target:** $1/hour net profit with $100 capital  
> **Market:** Polymarket BTC 15-minute UP/DOWN binary contracts  
> **Status:** Draft

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement](#2-problem-statement)
3. [Market Analysis](#3-market-analysis)
4. [Strategy Design](#4-strategy-design)
5. [Profitability Math](#5-profitability-math)
6. [Technical Architecture](#6-technical-architecture)
7. [Data Sources & SDK Selection](#7-data-sources--sdk-selection)
8. [Risk Management](#8-risk-management)
9. [Implementation Phases](#9-implementation-phases)
10. [Bot Module Specification](#10-bot-module-specification)
11. [Configuration & Parameters](#11-configuration--parameters)
12. [Deployment & Infrastructure](#12-deployment--infrastructure)
13. [Monitoring & Alerting](#13-monitoring--alerting)
14. [Community Bot Audit — Lessons Learned](#14-community-bot-audit--lessons-learned)
15. [Risks & Mitigations](#15-risks--mitigations)
16. [Success Criteria](#16-success-criteria)
17. [Appendix A — Fee Calculator](#appendix-a--fee-calculator)
18. [Appendix B — Ecosystem Reference Map](#appendix-b--ecosystem-reference-map)
19. [Appendix C — Research Sources](#appendix-c--research-sources)

---

## 1. Executive Summary

This PRD defines a fully automated trading bot that targets **$1 net profit per hour** using **$100 starting capital** on Polymarket's BTC 15-minute UP/DOWN binary markets. The bot combines two complementary strategies — **latency arbitrage** (primary) and **same-platform arbitrage** (secondary) — to achieve consistent returns while maintaining strict risk controls.

### Why This Is Achievable

| Metric | Requirement | Market Reality |
|---|---|---|
| Target profit | $1/hour (1% of capital) | Latency arb yields 2-5% per winning trade |
| Trade frequency | 4 trades/hour (one per 15-min window) | New BTC market opens every 15 minutes, 24/7 |
| Win rate needed | >60% on 4 trades/hour | Latency arb historically achieves 65-78% win rate |
| Capital utilization | $20-25 per trade (max 25% exposure) | Sufficient for 15-min markets with $100-$500 depth |
| Fee impact | ~0.78% effective (maker orders = free) | Maker orders have zero fees + earn rebates |

### Recommended Strategy: Hybrid Latency + Same-Platform Arbitrage

```
┌─────────────────────────────────────────────────────────┐
│              HYBRID STRATEGY ENGINE                       │
│                                                           │
│  ┌─────────────────────┐  ┌───────────────────────────┐  │
│  │ PRIMARY: Latency Arb │  │ SECONDARY: Same-Platform  │  │
│  │ (70% of trades)      │  │ Arb (30% of trades)       │  │
│  │                       │  │                           │  │
│  │ Monitor Binance BTC   │  │ Monitor YES+NO ask sum    │  │
│  │ → detect momentum     │  │ → buy both when < 0.97    │  │
│  │ → buy mispriced side  │  │ → guaranteed profit at    │  │
│  │ → sell before expiry  │  │   expiry                  │  │
│  └─────────────────────┘  └───────────────────────────┘  │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐  │
│  │           SHARED: Risk Manager + Position Tracker     │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Problem Statement

### Goal

Build an automated trading bot that generates **$1/hour net profit** ($24/day, ~$720/month) trading Polymarket BTC 15-minute UP/DOWN markets, starting with $100 capital.

### Constraints

- **Capital:** $100 USDC starting balance (on Polygon)
- **Market:** BTC 15-minute binary (YES/NO) contracts only
- **Platform:** Polymarket CLOB (Central Limit Order Book)
- **Runtime:** 24/7 automated, zero human intervention after launch
- **Risk tolerance:** Maximum 10% daily drawdown ($10), maximum 25% total drawdown ($25)

### Key Questions This PRD Answers

1. What trading strategy achieves $1/hour with $100 capital?
2. Which SDKs and data sources power the bot?
3. What is the exact architecture, module breakdown, and deployment plan?
4. What risk controls prevent catastrophic loss?
5. What did we learn from auditing 6 community bots and 65 official repos?

---

## 3. Market Analysis

### 3.1 Polymarket BTC 15-Minute Market Mechanics

**How it works:**

1. Every 15 minutes, Polymarket opens a new binary market: _"Will BTC/USDT be higher than $X at [time]?"_
2. Traders buy YES (price goes up) or NO (price stays/goes down) shares at $0.01–$0.99
3. At expiry, Chainlink oracle reports the actual BTC price
4. Winning shares pay $1.00; losing shares pay $0.00
5. **96 markets per day** (24 hours × 4 per hour), running 24/7

**Resolution oracle:** Chainlink Data Streams on Polygon — aggregates spot prices from Binance, Coinbase, Kraken, and others.

### 3.2 Current Fee Structure (March 2026)

Polymarket introduced taker fees for crypto short-duration markets effective March 6, 2026:

```
fee = C × p × feeRate × (p × (1 - p))^exponent

Where:
  C         = number of shares
  p         = price per share ($0.01–$0.99)
  feeRate   = 0.25 (crypto markets)
  exponent  = 2   (crypto markets)
```

| Price (p) | Fee per 100 shares | Effective Rate |
|---|---|---|
| $0.10 | $0.020 | 0.20% |
| $0.20 | $0.128 | 0.64% |
| $0.30 | $0.331 | 1.10% |
| $0.40 | $0.576 | 1.44% |
| $0.50 | $0.781 | 1.56% |
| $0.60 | $0.576 | 0.96% |
| $0.70 | $0.331 | 0.47% |
| $0.80 | $0.128 | 0.16% |
| $0.90 | $0.020 | 0.02% |

**Critical insight: Maker orders pay ZERO fees and earn 20% of collected taker fees as daily USDC rebates.** Our bot should predominantly use **limit (maker) orders** to eliminate fee drag entirely.

### 3.3 Market Liquidity & Spreads

| Metric | Typical Value (2026) |
|---|---|
| Bid-ask spread (normal) | 1–3¢ |
| Bid-ask spread (volatile) | Up to 7¢+ |
| Depth to fill $10k | <0.3% slippage |
| Execution speed | <150ms (no taker delay since Feb 2026) |
| Maker rebate | 20% of taker fees (crypto) |
| Active market makers | Institutional (Susquehanna, Jump Trading) + bots |

### 3.4 The Latency Edge

Polymarket's BTC prices lag behind exchange prices (Binance, Coinbase) by **30–90 seconds** during volatile moves. This lag is the primary exploitable edge:

```
Timeline of a BTC price spike:

T+0s:    Binance price spikes +0.5%
T+2s:    Our bot detects momentum signal
T+5s:    Bot places maker order on Polymarket (YES at 0.52)
T+30s:   Polymarket odds start adjusting (YES moves to 0.60)
T+60s:   Market fully corrects (YES at 0.65)
T+90s:   Bot sells YES at 0.63 via maker order

Profit: $0.63 - $0.52 = $0.11 per share (21% return on capital deployed)
```

---

## 4. Strategy Design

### 4.1 Strategy 1: Latency Arbitrage (Primary — 70% of trades)

**Edge:** Polymarket odds lag behind real BTC price movements on Binance by 30-90 seconds.

**Signal pipeline:**
```
Binance aggTrade WebSocket (tick-level BTC/USDT)
    │
    ▼
Momentum Detector (rolling 60s window)
    │  Trigger: |price_change| > 0.3% in 60 seconds
    │
    ▼
Polymarket Price Comparator
    │  Compare: Binance-implied probability vs Polymarket order book
    │  Threshold: mispricing > 3¢ (after fees)
    │
    ▼
Order Executor (maker limit order on CLOB)
    │  Entry: Place limit order at current Polymarket ask - 1¢
    │  Exit: Place limit sell at entry + target (3-8¢ profit)
    │         OR hold to expiry if strongly in-the-money
    │
    ▼
Position Monitor (WebSocket exit watch)
    │  Stop-loss: -5¢ from entry
    │  Take-profit: +3¢ to +8¢ from entry
    │  Expiry exit: Sell 2 minutes before market close
```

**Entry conditions (ALL must be true):**

1. Binance BTC moves >0.3% in the last 60 seconds
2. Polymarket YES or NO price is >3¢ below the Binance-implied fair value
3. Time remaining in the 15-min window is between 3 and 12 minutes (avoid first 3 min of price discovery and last 3 min of expiry risk)
4. No existing position in this market
5. Daily loss limit not reached
6. Position size ≤ 25% of available capital

**Exit conditions (ANY triggers exit):**

1. **Take-profit:** Price moves +3¢ to +8¢ from entry → sell via maker limit order
2. **Stop-loss:** Price moves -5¢ from entry → sell via taker market order
3. **Time exit:** 2 minutes before market expiry → sell at market
4. **Momentum reversal:** Binance momentum reverses → close immediately

### 4.2 Strategy 2: Same-Platform Arbitrage (Secondary — 30% of trades)

**Edge:** Temporary mispricings where YES_ask + NO_ask < $0.97 — guaranteed profit at settlement.

**Logic:**
```python
# Continuously monitor all active BTC 15-min markets
for market in active_btc_15m_markets:
    yes_ask = get_best_ask(market, "YES")
    no_ask  = get_best_ask(market, "NO")
    total   = yes_ask + no_ask
    
    if total < 0.97:  # 3% guaranteed profit
        shares = min(
            available_capital * 0.25 / total,  # max 25% of capital
            get_available_liquidity(market)
        )
        buy(market, "YES", shares, yes_ask)
        buy(market, "NO",  shares, no_ask)
        # Hold to expiry → one side pays $1.00
        # Profit = $1.00 - total_cost per share
```

**This strategy is risk-free** (guaranteed profit at settlement), but opportunities are rare — typically 2-5 per day during volatile periods.

### 4.3 Strategy Priority & Capital Allocation

| Strategy | Capital Share | Expected Frequency | Expected Return/Trade | Risk Level |
|---|---|---|---|---|
| Latency Arb | 70% ($70) | 3-4 trades/hour | 2-8% per trade | Medium |
| Same-Platform Arb | 30% ($30) | 0-5 trades/day | 2-4% per trade | Zero (risk-free) |

---

## 5. Profitability Math

### 5.1 Latency Arbitrage P&L Model

**Conservative scenario (per hour):**

| Parameter | Value |
|---|---|
| Trades per hour | 3 (one per 15-min window, skip 1) |
| Capital per trade | $23 (70% of $100 ÷ 3 concurrent max) |
| Win rate | 65% |
| Avg win | $0.05/share × 46 shares = $2.30 |
| Avg loss | $0.03/share × 46 shares = $1.38 |
| Fee (maker orders) | $0.00 (maker = free) |
| Maker rebate | ~$0.02/day (small but positive) |

**Hourly P&L:**
```
Wins:   3 × 0.65 × $2.30 =  $4.49
Losses: 3 × 0.35 × $1.38 = -$1.45
─────────────────────────────────
Net:    $3.04/hour (before slippage)
Slippage (-20%):            -$0.61
─────────────────────────────────
Estimated net:  $2.43/hour
```

### 5.2 Same-Platform Arb P&L Model

**Conservative scenario (per day):**

| Parameter | Value |
|---|---|
| Opportunities per day | 3 |
| Capital per trade | $10 (30% of $100 ÷ 3) |
| Win rate | 100% (guaranteed at settlement) |
| Avg profit | 3% × $10 = $0.30 per trade |

**Daily P&L from arb:** 3 × $0.30 = **$0.90/day** ($0.04/hour)

### 5.3 Combined Hourly Projection

| Source | Hourly Estimate |
|---|---|
| Latency arbitrage | $2.43 |
| Same-platform arb | $0.04 |
| **Total** | **$2.47/hour** |
| **Target** | **$1.00/hour** |
| **Safety margin** | **2.47× target** |

The 2.47× safety margin accounts for:
- Periods of low volatility (no latency arb signals)
- Increased competition from other bots
- Occasional system downtime or API errors
- Taker fee erosion on stop-loss exits

### 5.4 Break-Even Analysis

| Scenario | Min Win Rate Needed | Trades/Hour Needed |
|---|---|---|
| Target $1/hour | 55% at 3 trades/hr | 2 at 65% win rate |
| Break-even | 42% at 3 trades/hr | 1 at 55% win rate |
| Worst case (fees + slippage) | 60% at 4 trades/hr | 3 at 60% win rate |

---

## 6. Technical Architecture

### 6.1 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        TRADING BOT                               │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐  │
│  │ Data Layer    │  │ Strategy     │  │ Execution Layer        │  │
│  │              │  │ Layer        │  │                        │  │
│  │ • Binance WS │  │              │  │ • Order Manager        │  │
│  │   (aggTrade) │──▶ • Latency   │──▶ • Fill Tracker         │  │
│  │ • Polymarket │  │   Arb Engine │  │ • Position Manager     │  │
│  │   CLOB WS   │  │ • Same-Plat  │  │ • CLOB Client          │  │
│  │ • Polymarket │  │   Arb Engine │  │   (py-clob-client)     │  │
│  │   REST API   │  │ • Signal     │  │                        │  │
│  │ • Chainlink  │  │   Combiner   │  │                        │  │
│  │   (optional) │  │              │  │                        │  │
│  └──────────────┘  └──────────────┘  └────────────────────────┘  │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐  │
│  │ Risk Layer   │  │ Persistence  │  │ Monitoring              │  │
│  │              │  │              │  │                        │  │
│  │ • Daily Loss │  │ • SQLite DB  │  │ • Discord Webhooks     │  │
│  │   Limit      │  │ • Trade Log  │  │ • Health Check         │  │
│  │ • Position   │  │ • P&L Track  │  │ • Performance Stats    │  │
│  │   Sizing     │  │ • Config     │  │ • Error Alerts         │  │
│  │ • Circuit    │  │   State      │  │                        │  │
│  │   Breaker    │  │              │  │                        │  │
│  └──────────────┘  └──────────────┘  └────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 6.2 Technology Stack

| Component | Choice | Rationale |
|---|---|---|
| **Language** | Python 3.11+ | Best SDK support (py-clob-client), fastest development, most community bot examples |
| **Polymarket SDK** | `py-clob-client` (v0.x) | Official Python SDK, 893 ⭐, actively maintained, covers orders + order book + auth |
| **Binance Feed** | `python-binance` or raw WebSocket | aggTrade stream for tick-level BTC/USDT prices |
| **WebSocket** | `websockets` + `asyncio` | Async event loop for concurrent Binance + Polymarket streams |
| **Database** | SQLite | Zero-config, file-based, sufficient for trade logging (used by `sed000` and `francescods04` bots) |
| **Deployment** | Docker + docker-compose | Cloud-ready (Railway, Render, AWS) — adopted from `svnmcqueen/polymarket-bot` |
| **Alerts** | Discord webhooks | Real-time trade and error notifications — proven in `svnmcqueen` bot |
| **Config** | `.env` + `config.json` | Environment secrets in `.env`, strategy parameters in `config.json` |

### 6.3 Why Python Over TypeScript or Rust

| Factor | Python | TypeScript | Rust |
|---|---|---|---|
| SDK maturity | ⭐ 893 (py-clob-client) | ⭐ 469 (clob-client) | ⭐ 604 (rs-clob-client) |
| Development speed | ✅ Fastest | ✅ Fast | ❌ Slow |
| Community bot examples | 4 of 6 bots | 1 of 6 bots | 1 of 6 bots |
| Latency requirement | ✅ Sufficient (<100ms) | ✅ Sufficient | ✅ Best (sub-ms) |
| Data science libraries | ✅ numpy, pandas | ❌ Limited | ❌ Limited |
| Deployment | ✅ Docker, pip | ✅ Docker, npm | ⚠️ Cargo build |

Python provides the best balance of development speed, SDK support, and community examples. For our $100 capital target, the sub-millisecond latency advantage of Rust is unnecessary — Python's <100ms execution is sufficient given the 30-90 second market lag we're exploiting.

---

## 7. Data Sources & SDK Selection

### 7.1 Required Data Feeds

| Feed | Source | Protocol | Purpose | Latency |
|---|---|---|---|---|
| **BTC spot price** | Binance aggTrade | WebSocket | Momentum signal detection | <10ms |
| **Polymarket order book** | Polymarket CLOB | WebSocket | Pricing, spread, entry/exit | <50ms |
| **Polymarket market discovery** | Gamma API | REST | Find active BTC 15-min markets | <200ms |
| **Polymarket order execution** | CLOB REST API | REST | Place/cancel/query orders | <150ms |
| **Chainlink BTC price** | Chainlink Data Streams | WebSocket (optional) | Resolution oracle price | <100ms |

### 7.2 Official Polymarket Repos We Use

| Repo | Role in Our Bot |
|---|---|
| [py-clob-client](https://github.com/Polymarket/py-clob-client) | Core SDK — order placement, book queries, authentication |
| [python-order-utils](https://github.com/Polymarket/python-order-utils) | EIP-712 order signing |
| [real-time-data-client](https://github.com/Polymarket/real-time-data-client) | WebSocket reference (we reimplement in Python) |
| [poly-market-maker](https://github.com/Polymarket/poly-market-maker) | Reference for maker order strategies |
| [examples](https://github.com/Polymarket/examples) | Official integration patterns |

### 7.3 API Endpoints

| Endpoint | Use |
|---|---|
| `https://clob.polymarket.com` | CLOB REST API (orders, book, fills) |
| `wss://ws-subscriptions-clob.polymarket.com/ws/` | CLOB WebSocket (live book, trades, user stream) |
| `https://gamma-api.polymarket.com/markets` | Market metadata discovery |
| `wss://stream.binance.com:9443/ws/btcusdt@aggTrade` | Binance BTC tick data |

### 7.4 Authentication

```python
from py_clob_client.client import ClobClient

# L1 Auth — one-time setup (generates API credentials)
client = ClobClient(
    host="https://clob.polymarket.com",
    key=os.environ["PRIVATE_KEY"],   # Polygon wallet private key
    chain_id=137                      # Polygon mainnet
)
api_creds = client.create_or_derive_api_creds()

# L2 Auth — for every session (uses API credentials)
client = ClobClient(
    host="https://clob.polymarket.com",
    key=os.environ["PRIVATE_KEY"],
    chain_id=137,
    creds=api_creds
)
```

---

## 8. Risk Management

### 8.1 Risk Control Hierarchy

```
Level 1: Position Sizing
    └── Max 25% of capital per trade ($25)
    └── Max 2 concurrent positions

Level 2: Per-Trade Stop Loss
    └── Latency arb: -5¢ per share hard stop
    └── Same-platform arb: no stop (guaranteed profit)

Level 3: Daily Loss Limit
    └── -$10 daily max loss (10% of capital) → halt trading for 24h

Level 4: Circuit Breaker
    └── 3 consecutive losses → pause 30 minutes
    └── 5 losses in 1 hour → pause 2 hours
    └── API error rate >20% → halt until manual review

Level 5: Total Drawdown Kill Switch
    └── -$25 total drawdown (25% of capital) → stop bot entirely
    └── Requires manual restart with config acknowledgment
```

### 8.2 Position Sizing Formula

```python
def calculate_position_size(capital, confidence, max_pct=0.25):
    """
    Kelly-inspired position sizing with conservative fraction.
    
    Uses 1/4 Kelly (kelly_fraction=0.25) rather than full Kelly because:
    - Full Kelly maximizes long-term growth but has very high variance
    - 1/2 Kelly is common in finance but still aggressive for prediction markets
    - 1/4 Kelly reduces variance by ~75% while sacrificing only ~44% of growth rate
    - With $100 capital and a 10% daily loss limit, 1/4 Kelly keeps individual
      trade losses small enough to survive 3-5 consecutive losses without
      triggering the circuit breaker or daily loss limit prematurely
    
    capital:    Current available USDC balance
    confidence: Signal strength (0.0 to 1.0)
    max_pct:    Maximum capital percentage per trade (hard cap)
    """
    kelly_fraction = 0.25  # Use 1/4 Kelly for safety
    base_size = capital * max_pct
    adjusted_size = base_size * confidence * kelly_fraction
    
    return max(1.0, min(adjusted_size, capital * max_pct))
```

### 8.3 Risk Parameters

| Parameter | Value | Rationale |
|---|---|---|
| `MAX_POSITION_PCT` | 25% | Never risk more than 1/4 of capital on any single trade |
| `MAX_CONCURRENT` | 2 | Limit exposure across overlapping 15-min windows |
| `STOP_LOSS_CENTS` | 5 | -5¢ per share max loss on latency arb trades |
| `DAILY_LOSS_LIMIT` | $10 | 10% daily max drawdown |
| `TOTAL_DRAWDOWN_LIMIT` | $25 | 25% total max drawdown → kill switch |
| `CIRCUIT_BREAKER_CONSEC` | 3 | 3 consecutive losses → 30-min pause |
| `CIRCUIT_BREAKER_HOURLY` | 5 | 5 losses in 1 hour → 2-hour pause |
| `MIN_TIME_REMAINING` | 180s | Don't enter trades with <3 min remaining |
| `MAX_TIME_REMAINING` | 720s | Don't enter trades with >12 min remaining |
| `MIN_EDGE_CENTS` | 3 | Minimum 3¢ mispricing to trigger latency arb entry |

---

## 9. Implementation Phases

### Phase 1: Foundation (Week 1-2)

**Goal:** Paper trading bot with full data pipeline

| Task | Description | Dependency |
|---|---|---|
| 1.1 | Set up Python project with `py-clob-client`, `python-binance`, `websockets` | — |
| 1.2 | Implement Binance WebSocket feed (aggTrade BTC/USDT) | — |
| 1.3 | Implement Polymarket market scanner (find active BTC 15-min markets) | 1.1 |
| 1.4 | Implement Polymarket WebSocket feed (order book for active markets) | 1.1 |
| 1.5 | Build momentum detector (rolling 60s window, >0.3% threshold) | 1.2 |
| 1.6 | Build Polymarket price comparator (Binance fair value vs CLOB price) | 1.4, 1.5 |
| 1.7 | Implement SQLite persistence (trades, P&L, config state) | — |
| 1.8 | Build paper trading engine (simulated fills, no real orders) | 1.6, 1.7 |
| 1.9 | Run paper trading for 48+ hours, collect performance data | 1.8 |

**Deliverable:** Paper trading bot running 24/7 with simulated P&L tracking.

### Phase 2: Risk & Execution (Week 3)

**Goal:** Production-grade execution with risk controls

| Task | Description | Dependency |
|---|---|---|
| 2.1 | Implement order manager (limit/market orders via py-clob-client) | Phase 1 |
| 2.2 | Implement fill tracker (WebSocket user stream for order updates) | 2.1 |
| 2.3 | Implement position manager (entry/exit tracking, P&L per position) | 2.2 |
| 2.4 | Build risk manager (daily loss, circuit breaker, position sizing) | 2.3 |
| 2.5 | Implement same-platform arb strategy | 2.1 |
| 2.6 | Add stop-loss logic (cancel limit order BEFORE market sell — learned from `sed000`) | 2.2 |
| 2.7 | Add retry logic on API errors (5 retries — learned from `sed000`) | 2.1 |
| 2.8 | Paper trade with real order book data for 48+ hours | 2.4 |

**Deliverable:** Full execution engine with risk controls in paper mode.

### Phase 3: Live Trading (Week 4)

**Goal:** Go live with minimum capital, validate real-world performance

| Task | Description | Dependency |
|---|---|---|
| 3.1 | Deploy to low-latency VPS (Amsterdam/London, <20ms to Polymarket) | Phase 2 |
| 3.2 | Fund trading wallet with $20 USDC (minimum viable balance) | — |
| 3.3 | Run live trading with $5 max position for 24 hours | 3.1, 3.2 |
| 3.4 | Analyze fills, slippage, actual vs expected P&L | 3.3 |
| 3.5 | Tune parameters based on live data | 3.4 |
| 3.6 | Scale to $50 capital, run for 48 hours | 3.5 |
| 3.7 | Scale to $100 capital, run for 72 hours | 3.6 |
| 3.8 | Add Discord webhook alerts (trades, errors, daily summary) | 3.3 |

**Deliverable:** Live bot running with $100 capital, targeting $1/hour.

### Phase 4: Optimization (Week 5+)

**Goal:** Improve win rate, add advanced features

| Task | Description | Dependency |
|---|---|---|
| 4.1 | Add Chainlink price feed as secondary signal (matches resolution oracle) | Phase 3 |
| 4.2 | Implement genetic parameter optimization (inspired by `sed000` bot) | Phase 3 |
| 4.3 | Add options pricing model (digital option fair value — inspired by `francescods04`) | Phase 3 |
| 4.4 | Implement legging strategy (one-leg-first for better arb entries — from `svnmcqueen`) | Phase 3 |
| 4.5 | Build backtesting framework against historical data | Phase 3 |
| 4.6 | Implement maker rebate tracking (earn 20% of taker fees) | Phase 3 |
| 4.7 | Capital compounding (reinvest profits to grow position sizes) | Phase 3 |

**Deliverable:** Optimized bot with higher win rates and advanced features.

---

## 10. Bot Module Specification

### 10.1 Project Structure

```
polymarket-btc-bot/
├── src/
│   ├── __init__.py
│   ├── main.py                 # Entry point, orchestration loop
│   ├── config.py               # Configuration loader + validation
│   │
│   ├── data/                   # Data feeds
│   │   ├── __init__.py
│   │   ├── binance_feed.py     # Binance aggTrade WebSocket
│   │   ├── polymarket_feed.py  # Polymarket CLOB WebSocket
│   │   ├── market_scanner.py   # Discover active BTC 15-min markets
│   │   └── chainlink_feed.py   # (Phase 4) Chainlink price stream
│   │
│   ├── strategy/               # Trading strategies
│   │   ├── __init__.py
│   │   ├── latency_arb.py      # Primary: latency arbitrage engine
│   │   ├── same_platform_arb.py# Secondary: YES+NO < $0.97 arb
│   │   ├── signal_combiner.py  # Combines strategy signals
│   │   └── momentum.py         # Momentum detection (rolling window)
│   │
│   ├── execution/              # Order execution
│   │   ├── __init__.py
│   │   ├── order_manager.py    # Place, cancel, query orders
│   │   ├── fill_tracker.py     # Track order fills via WebSocket
│   │   └── position_manager.py # Entry/exit tracking, P&L
│   │
│   ├── risk/                   # Risk management
│   │   ├── __init__.py
│   │   ├── risk_manager.py     # Daily loss, circuit breaker, sizing
│   │   ├── position_sizer.py   # Kelly-fraction position sizing
│   │   └── circuit_breaker.py  # Loss streak & error rate controls
│   │
│   ├── persistence/            # Database and state
│   │   ├── __init__.py
│   │   ├── database.py         # SQLite trade log, P&L, stats
│   │   └── state_manager.py    # Session state persistence
│   │
│   └── monitoring/             # Monitoring and alerts
│       ├── __init__.py
│       ├── discord_alerts.py   # Discord webhook notifications
│       ├── health_check.py     # Heartbeat + connectivity check
│       └── dashboard.py        # Terminal dashboard (optional)
│
├── config/
│   ├── config.json             # Strategy parameters
│   └── config.example.json     # Template for new users
│
├── scripts/
│   ├── paper_trade.py          # Paper trading entry point
│   ├── live_trade.py           # Live trading entry point
│   ├── backtest.py             # Backtesting (Phase 4)
│   └── check_balance.py        # Check wallet USDC balance
│
├── tests/
│   ├── test_momentum.py        # Momentum detector unit tests
│   ├── test_risk_manager.py    # Risk management unit tests
│   ├── test_position_sizer.py  # Position sizing unit tests
│   └── test_fee_calculator.py  # Fee calculation unit tests
│
├── .env.example                # Environment variable template
├── Dockerfile                  # Container build
├── docker-compose.yml          # Container orchestration
├── requirements.txt            # Python dependencies
└── README.md                   # Setup and usage guide
```

### 10.2 Module Specifications

#### `data/binance_feed.py`
- Connects to `wss://stream.binance.com:9443/ws/btcusdt@aggTrade`
- Emits price updates via async callback
- Maintains rolling 60-second price buffer for momentum calculation
- Auto-reconnects on disconnect with exponential backoff

#### `data/polymarket_feed.py`
- Connects to `wss://ws-subscriptions-clob.polymarket.com/ws/`
- Subscribes to order book updates for active BTC 15-min market token IDs
- Maintains local order book snapshot (bids + asks)
- Emits best bid/ask updates via async callback

#### `data/market_scanner.py`
- Polls `https://gamma-api.polymarket.com/markets?tag_slug=bitcoin&active=true` every 60 seconds
- Filters for 15-minute BTC UP/DOWN markets
- Returns token IDs for YES and NO outcomes
- Tracks market open/close times for time-remaining calculations

#### `strategy/latency_arb.py`
- Receives Binance price updates + Polymarket book updates
- Calculates Binance-implied fair probability using the digital options pricing formula:
  ```
  p = Φ((ln(St/S0) + μτ) / (σ√τ))
  
  Where:
    Φ  = Standard normal CDF (scipy.stats.norm.cdf)
    St = Current BTC price from Binance aggTrade feed
    S0 = BTC price at the start of the 15-min window (the strike price)
    μ  = Estimated drift (annualized, from recent price history; typically ~0 for 15-min)
    τ  = Time remaining to expiry, in years (e.g., 10 min = 10/(365.25×24×60))
    σ  = Estimated annualized volatility (EWMA of recent log returns)
  ```
- Compares the Binance-implied fair probability against Polymarket's best ask price
- Emits BUY signal when mispricing > `MIN_EDGE_CENTS` (3¢)
- Emits SELL signal on take-profit, stop-loss, or momentum reversal

#### `strategy/same_platform_arb.py`
- Monitors YES_ask + NO_ask for all active markets
- Emits BUY_BOTH signal when sum < `ARB_THRESHOLD` (0.97)
- Calculates exact profit: `$1.00 - (YES_ask + NO_ask)`
- Includes liquidity check before signaling

#### `execution/order_manager.py`
- Wraps `py-clob-client` for order placement
- Supports GTC (Good-Till-Cancelled) limit orders (maker, zero fees)
- Supports FOK (Fill-or-Kill) market orders (taker, for stop-loss only)
- Implements 5-retry logic on API errors (learned from `sed000/polymarket-btc-1h`)
- Cancels existing limit orders before placing opposite-side orders (learned from `sed000`)

#### `risk/risk_manager.py`
- Tracks daily P&L, consecutive losses, hourly loss count
- Implements all 5 levels of risk control hierarchy
- Returns `ALLOW_TRADE`, `PAUSE`, or `HALT` status
- Logs every risk decision to SQLite for audit

---

## 11. Configuration & Parameters

### 11.1 Environment Variables (`.env`)

```bash
# === Wallet Credentials ===
PRIVATE_KEY=0xYOUR_POLYGON_PRIVATE_KEY
# Optional (auto-derived from PRIVATE_KEY if not set)
POLY_API_KEY=
POLY_API_SECRET=
POLY_API_PASSPHRASE=
# For proxy wallets (signature type 1)
FUNDER_ADDRESS=

# === Trading Mode ===
PAPER_TRADING=true         # true=paper, false=live
INITIAL_CAPITAL=100        # Starting USDC balance

# === Discord Alerts (optional) ===
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_URL
```

### 11.2 Strategy Parameters (`config.json`)

```json
{
  "strategy": {
    "primary": "latency_arb",
    "secondary": "same_platform_arb",
    "capital_split": {
      "latency_arb": 0.70,
      "same_platform_arb": 0.30
    }
  },

  "latency_arb": {
    "momentum_window_seconds": 60,
    "momentum_threshold_pct": 0.3,
    "min_edge_cents": 3,
    "take_profit_cents": 5,
    "stop_loss_cents": 5,
    "min_time_remaining_seconds": 180,
    "max_time_remaining_seconds": 720,
    "use_maker_orders": true
  },

  "same_platform_arb": {
    "arb_threshold": 0.97,
    "min_profit_pct": 2.0,
    "hold_to_expiry": true
  },

  "risk": {
    "max_position_pct": 0.25,
    "max_concurrent_positions": 2,
    "daily_loss_limit_usd": 10.0,
    "total_drawdown_limit_usd": 25.0,
    "circuit_breaker_consecutive_losses": 3,
    "circuit_breaker_pause_minutes": 30,
    "circuit_breaker_hourly_losses": 5,
    "circuit_breaker_hourly_pause_minutes": 120
  },

  "execution": {
    "order_retry_count": 5,
    "order_retry_delay_ms": 500,
    "cancel_before_opposite_order": true,
    "expiry_exit_seconds_before": 120
  },

  "monitoring": {
    "discord_enabled": true,
    "health_check_interval_seconds": 60,
    "daily_summary_hour_utc": 0
  }
}
```

---

## 12. Deployment & Infrastructure

### 12.1 Recommended Setup

| Component | Recommendation | Cost |
|---|---|---|
| **VPS** | Hetzner CPX11 (Amsterdam) or DigitalOcean Basic (AMS3) | $4-6/month |
| **Latency** | <20ms to Polymarket CLOB, <50ms to Binance | Critical for latency arb |
| **OS** | Ubuntu 22.04 LTS | Free |
| **Python** | 3.11+ (via pyenv or Docker) | Free |
| **Database** | SQLite (local file) | Free |
| **Monitoring** | Discord webhooks | Free |

**Total infrastructure cost: ~$5/month** (paid for by <5 hours of bot profit)

### 12.2 Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Health check
HEALTHCHECK --interval=60s --timeout=10s --retries=3 \
    CMD python scripts/check_balance.py || exit 1

CMD ["python", "scripts/live_trade.py"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  bot:
    build: .
    env_file: .env
    volumes:
      - ./data:/app/data          # SQLite persistence
      - ./config:/app/config      # Config files
    restart: unless-stopped
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
```

### 12.3 Deployment Commands

```bash
# Clone and configure
git clone <repo-url>
cd polymarket-btc-bot
cp .env.example .env
# Edit .env with your private key and Discord webhook

# Paper trading (recommended first)
docker-compose up -d
docker-compose logs -f

# Switch to live trading
# Edit .env: PAPER_TRADING=false
docker-compose down && docker-compose up -d

# Check status
docker-compose exec bot python scripts/check_balance.py
```

---

## 13. Monitoring & Alerting

### 13.1 Discord Alert Types

| Alert | Trigger | Example |
|---|---|---|
| 🟢 **Trade Entry** | Order filled | `🟢 ENTRY: BTC-15m YES @ $0.48, 50 shares ($24.00)` |
| 💰 **Take Profit** | Exit at profit | `💰 PROFIT: BTC-15m YES sold @ $0.53, +$2.50 (+10.4%)` |
| 🔴 **Stop Loss** | Exit at loss | `🔴 STOP LOSS: BTC-15m YES sold @ $0.43, -$2.50 (-10.4%)` |
| 🏦 **Arb Entry** | Both sides bought | `🏦 ARB: BTC-15m YES+NO @ $0.96, 10 shares (4.2% profit locked)` |
| ⚠️ **Circuit Breaker** | Pause triggered | `⚠️ CIRCUIT BREAKER: 3 consecutive losses, pausing 30 min` |
| 🛑 **Kill Switch** | Bot halted | `🛑 KILL SWITCH: Daily loss limit reached (-$10.00), halting` |
| 📊 **Daily Summary** | Daily at 00:00 UTC | `📊 DAILY: +$18.50 (74 trades, 68% win rate, $100.00 → $118.50)` |
| ❤️ **Heartbeat** | Every 5 minutes | `❤️ BOT ALIVE: Capital $108.50, 2 open positions, latency 12ms` |

### 13.2 Performance Metrics (SQLite Dashboard)

| Metric | Query Interval |
|---|---|
| Hourly P&L | Every hour |
| Win rate (rolling 24h) | Every hour |
| Avg profit per trade | Every hour |
| Max drawdown | Continuous |
| Latency (Binance → order) | Per trade |
| Fill rate (orders filled / orders placed) | Per trade |
| Arb opportunities detected vs executed | Per market |

---

## 14. Community Bot Audit — Lessons Learned

We audited all 6 community bots and 65 official Polymarket repos. Here are the critical lessons incorporated into our design:

### From `taetaehoho/poly-kalshi-arb` (Rust, 421⭐)

| Lesson | How We Apply It |
|---|---|
| ✅ Circuit breaker with daily loss limit | Adopted: 5-level risk hierarchy |
| ✅ Dry-run mode before live trading | Adopted: `PAPER_TRADING=true` default |
| ✅ Position tracking per market | Adopted: `position_manager.py` |
| ❌ Requires Kalshi (US-only, geo-restricted) | Avoided: Our bot is Polymarket-only |

### From `sed000/polymarket-btc-1h` (TypeScript, most active)

| Lesson | How We Apply It |
|---|---|
| ✅ Cancel limit order BEFORE market sell on stop-loss | Adopted: Critical fix in `order_manager.py` |
| ✅ 5-retry logic on API errors | Adopted: Prevents premature order failures |
| ✅ WebSocket monitoring instead of limit orders for exits | Adopted: More reliable exit execution |
| ✅ Genetic optimization for parameters | Phase 4: Parameter tuning |
| ✅ SQLite trade persistence | Adopted: `database.py` |
| ⚠️ 1-hour markets only | Adapted: We target 15-min markets (higher frequency = more trades/hour) |

### From `svnmcqueen/polymarket-bot` (Python, arb)

| Lesson | How We Apply It |
|---|---|
| ✅ Same-platform arb (YES+NO < 0.97) — Polymarket only | Adopted as secondary strategy |
| ✅ Legging strategy (one leg first for better entry) | Phase 4: Advanced arb entry |
| ✅ Docker deployment (Dockerfile + docker-compose) | Adopted: Identical pattern |
| ✅ Discord webhook alerts | Adopted: Real-time notifications |
| ✅ Daily loss limit ($5) | Adopted: Scaled to $10 for $100 capital |
| ✅ Graceful shutdown (cancel all orders on Ctrl+C) | Adopted: Signal handler in `main.py` |

### From `francescods04/poly` (Python, options model)

| Lesson | How We Apply It |
|---|---|
| ✅ Chainlink as resolution oracle source (not Binance) | Phase 4: Secondary confirmation signal |
| ✅ Digital options pricing formula: `p = Φ((ln(St/S0) + μτ) / (σ√τ))` | Adopted in `latency_arb.py` for fair value calculation (see Module Spec §10.2 for full variable definitions) |
| ✅ Kelly criterion position sizing | Adopted: 1/4 Kelly in `position_sizer.py` |
| ✅ ML calibration (Platt scaling) | Phase 4: Probability calibration |
| ❌ Live trading NOT implemented | We implement full live execution |

### From `bking5496/guerilla-trading` (Python, multi-signal)

| Lesson | How We Apply It |
|---|---|
| ✅ Multi-signal weighted combination concept | Considered for Phase 4 (sentiment signals) |
| ⚠️ Very early stage (1 commit) | Not relied on for production patterns |

### From `evgenss79/PolM` (Python, semi-manual)

| Lesson | How We Apply It |
|---|---|
| ✅ Session state persistence (`state.json`) | Adopted: `state_manager.py` for restart recovery |
| ✅ Watch mode (monitor without executing) | Adopted: `PAPER_TRADING=true` mode |

---

## 15. Risks & Mitigations

### 15.1 Market Risks

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| **Latency edge erodes** (more bots compete) | High | Reduces win rate to ~55% | Safety margin: we need only 55% to hit $1/hour; same-platform arb as fallback |
| **Low volatility period** (no momentum signals) | Medium | No latency arb trades for hours | Same-platform arb continues; daily P&L target relaxes automatically |
| **Flash crash/spike** (extreme BTC move) | Low | Stop-loss triggered, -$25 max | 5-level risk hierarchy; circuit breaker pauses after 3 losses |
| **Market resolution dispute** (UMA oracle) | Very Low | Funds locked in disputed market | Only trade markets >3 min from expiry; monitor UMA disputes |

### 15.2 Technical Risks

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| **API downtime** (Polymarket or Binance) | Medium | Cannot trade | Health check; auto-pause on disconnect; retry with backoff |
| **WebSocket disconnect** | Medium | Missed signals | Auto-reconnect with exponential backoff; heartbeat monitoring |
| **Order fill failure** | Medium | Stuck in position | 5-retry logic; timeout → market sell; cancel-before-sell pattern |
| **Stale order book** | Low | Bad entry price | Validate book freshness (<2s old); reject stale data |
| **Private key compromise** | Very Low | Total loss of funds | Dedicated trading wallet; minimum balance; env-only storage |

### 15.3 Financial Risks

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| **Fee changes** (Polymarket increases taker fees) | Low | Reduces profitability | Use maker orders exclusively (zero fees); monitor fee API |
| **USDC depeg** | Very Low | Capital value loss | Out of scope; accept platform risk |
| **Polygon network congestion** | Low | Slow settlement | CLOB operates off-chain; on-chain only for deposit/withdraw |

---

## 16. Success Criteria

### 16.1 Phase 1 (Paper Trading) — Week 2

| Metric | Target |
|---|---|
| Paper P&L | >$1/hour averaged over 48 hours |
| Win rate | >60% |
| Uptime | >95% |
| Latency (signal → order) | <200ms |

### 16.2 Phase 3 (Live Trading) — Week 4

| Metric | Target |
|---|---|
| Net P&L | >$1/hour averaged over 72 hours |
| Win rate | >55% |
| Max daily drawdown | <$10 |
| Max total drawdown | <$25 |
| Fill rate | >80% |
| Uptime | >98% |

### 16.3 Phase 4 (Optimization) — Week 5+

| Metric | Target |
|---|---|
| Net P&L | >$1.50/hour (50% above target) |
| Win rate | >65% |
| Capital growth | $100 → $200+ in first month |
| Maker rebate income | >$0.50/day |

---

## Appendix A — Fee Calculator

### Python Fee Calculator

```python
def calculate_polymarket_fee(shares: int, price: float, 
                              fee_rate: float = 0.25, 
                              exponent: int = 2) -> float:
    """
    Calculate Polymarket taker fee for crypto markets.
    
    Args:
        shares:   Number of shares traded
        price:    Price per share (0.01 to 0.99)
        fee_rate: 0.25 for crypto, varies for sports
        exponent: 2 for crypto, 1 for sports
    
    Returns:
        Fee in USDC (only applies to taker orders; maker = $0)
    """
    fee = shares * price * fee_rate * (price * (1 - price)) ** exponent
    return round(fee, 4)

# Examples:
# 100 shares at $0.50: fee = $0.78 (1.56%)
# 100 shares at $0.30: fee = $0.33 (1.10%)
# 100 shares at $0.80: fee = $0.13 (0.16%)
# Maker order at any price: fee = $0.00 (FREE)
```

### Fee Impact on Strategy

| Order Type | When Used | Fee |
|---|---|---|
| **Maker limit order** (entry) | Latency arb + arb entry | $0.00 |
| **Maker limit order** (take-profit exit) | Normal exit | $0.00 |
| **Taker market order** (stop-loss) | Emergency exit only | ~$0.30-$0.78 per $25 position |
| **Average blended fee** | ~20% taker exits | ~$0.06-$0.16 per trade |

---

## Appendix B — Ecosystem Reference Map

### Complete Stack Used by This Bot

```
┌─────────────────────────────────────────────────────────────┐
│                     OUR TRADING BOT                          │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                   Data Layer                              │  │
│  │                                                           │  │
│  │  Binance aggTrade WS ─────────── BTC/USDT tick prices    │  │
│  │  Polymarket CLOB WS  ─────────── Order book updates      │  │
│  │  Gamma API REST  ─────────────── Market discovery         │  │
│  │  Chainlink (Phase 4) ─────────── Resolution oracle price │  │
│  └─────────────────────────────────────────────────────────┘  │
│                            │                                   │
│  ┌─────────────────────────▼───────────────────────────────┐  │
│  │                Strategy Layer                              │  │
│  │                                                           │  │
│  │  Latency Arb Engine ─── Momentum + Fair Value Pricing    │  │
│  │  Same-Platform Arb ──── YES+NO Sum Monitor               │  │
│  │  Signal Combiner ────── Priority-weighted decision        │  │
│  └─────────────────────────────────────────────────────────┘  │
│                            │                                   │
│  ┌─────────────────────────▼───────────────────────────────┐  │
│  │              Execution Layer                               │  │
│  │                                                           │  │
│  │  py-clob-client ──────── Order placement (maker/taker)    │  │
│  │  python-order-utils ──── EIP-712 signing                  │  │
│  │  CLOB REST API ────────── Order management                │  │
│  └─────────────────────────────────────────────────────────┘  │
│                            │                                   │
│  ┌─────────────────────────▼───────────────────────────────┐  │
│  │             Infrastructure Layer                           │  │
│  │                                                           │  │
│  │  ctf-exchange ────────── On-chain settlement (Polygon)    │  │
│  │  uma-ctf-adapter ─────── Market resolution (UMA OOv3)    │  │
│  │  Goldsky subgraph ────── Historical data (Phase 4)        │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Official Repos by Priority

| Priority | Repo | Why |
|---|---|---|
| 🔴 **Must have** | `Polymarket/py-clob-client` | Core SDK for all order operations |
| 🔴 **Must have** | `Polymarket/python-order-utils` | Order signing (used internally by py-clob-client) |
| 🟠 **Important** | `Polymarket/real-time-data-client` | WebSocket reference (we reimplement in Python) |
| 🟠 **Important** | `Polymarket/poly-market-maker` | Maker order strategy reference |
| 🟡 **Useful** | `Polymarket/examples` | Official integration examples |
| 🟡 **Useful** | `Polymarket/ctf-exchange` | On-chain ABI for direct contract calls |
| 🟡 **Phase 4** | `Polymarket/agents` | AI agent reference architecture |
| 🟡 **Phase 4** | `Polymarket/polymarket-subgraph` | Historical data for backtesting |

---

## Appendix C — Research Sources

### Official Polymarket Documentation

- [Polymarket Fee Documentation](https://docs.polymarket.com/trading/fees) — Fee formula, crypto feeRate=0.25, exponent=2
- [Maker Rebates Program](https://docs.polymarket.com/market-makers/maker-rebates) — 20% rebate for crypto market makers
- [Polymarket CLOB API](https://docs.polymarket.com/) — REST + WebSocket API documentation

### Community Bot Repositories Analyzed

| Repo | Key Takeaway |
|---|---|
| [taetaehoho/poly-kalshi-arb](https://github.com/taetaehoho/poly-kalshi-arb) | Circuit breaker, position tracking, Rust performance |
| [sed000/polymarket-btc-1h](https://github.com/sed000/polymarket-btc-1h) | Stop-loss fix (cancel before sell), WebSocket exits, genetic optimization |
| [svnmcqueen/polymarket-bot](https://github.com/svnmcqueen/polymarket-bot) | Same-platform arb, Docker deployment, Discord alerts |
| [francescods04/poly](https://github.com/francescods04/poly) | Options pricing, Kelly sizing, Chainlink oracle, ML calibration |
| [bking5496/guerilla-trading](https://github.com/bking5496/guerilla-trading) | Multi-signal concept (price + sentiment + whale) |
| [evgenss79/PolM](https://github.com/evgenss79/PolM) | Session persistence, watch mode |

### Official SDK Repositories Used

| Repo | Stars | Role |
|---|---|---|
| [Polymarket/py-clob-client](https://github.com/Polymarket/py-clob-client) | 893 | Primary Python SDK |
| [Polymarket/python-order-utils](https://github.com/Polymarket/python-order-utils) | 60 | Order signing |
| [Polymarket/real-time-data-client](https://github.com/Polymarket/real-time-data-client) | 183 | WebSocket reference |
| [Polymarket/poly-market-maker](https://github.com/Polymarket/poly-market-maker) | 269 | Maker strategy reference |
| [Polymarket/ctf-exchange](https://github.com/Polymarket/ctf-exchange) | 327 | On-chain contracts |
| [Polymarket/examples](https://github.com/Polymarket/examples) | 72 | Integration examples |

### External Research

- [Polymarket Liquidity & Execution Quality](https://ats.io/prediction-markets/polymarket/liquidity/) — Spread, depth, slippage data
- [Binance to Polymarket Arbitrage Strategies](https://www.quantvps.com/blog/binance-to-polymarket-arbitrage-strategies) — Latency arb architecture
- [Building a Real-Time Momentum Signal Pipeline](https://chudi.dev/blog/binance-polymarket-momentum-signal-pipeline) — Signal detection methodology
- [Latency Arbitrage on Polymarket](https://grokipedia.com/page/Latency_Arbitrage_on_Polymarket) — Edge quantification

---

## Document History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | March 13, 2026 | Poly-Trade Research | Initial PRD — full strategy, architecture, risk management |

---

> ⚠️ **Disclaimer:** Trading prediction markets involves real financial risk. Past performance does not guarantee future results. The profitability projections in this document are estimates based on current market conditions and may not hold as markets evolve. Always start with paper trading and minimum capital. Never risk money you cannot afford to lose.
