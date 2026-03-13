# Market Making on Polymarket & Custom OpenClaw Skills — Deep Research

> **Last updated:** March 13, 2026  
> **Scope:** Can we market-make on Polymarket with $100? What exactly is market making? Can we add custom strategies to OpenClaw/PolyClaw?  
> **Related docs:** [`openclaw-deep-research.md`](./openclaw-deep-research.md) · [`PRD-polymarket-btc-trading-bot.md`](./PRD-polymarket-btc-trading-bot.md)

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [What Exactly Is Market Making?](#2-what-exactly-is-market-making)
3. [How Market Making Works on Polymarket (CLOB)](#3-how-market-making-works-on-polymarket-clob)
4. [Polymarket Fee Structure — Why Makers Have the Advantage](#4-polymarket-fee-structure--why-makers-have-the-advantage)
5. [Market Making with $100 — Honest Analysis](#5-market-making-with-100--honest-analysis)
6. [Polymarket Liquidity Rewards Program](#6-polymarket-liquidity-rewards-program)
7. [Official Polymarket Market Maker Bot (poly-market-maker)](#7-official-polymarket-market-maker-bot-poly-market-maker)
8. [OpenClaw Custom Skills — Yes, You Can Build Your Own](#8-openclaw-custom-skills--yes-you-can-build-your-own)
9. [Extending PolyClaw with Custom Trading Strategies](#9-extending-polyclaw-with-custom-trading-strategies)
10. [Combined Strategy: Market Making + Our Custom Bot](#10-combined-strategy-market-making--our-custom-bot)
11. [Step-by-Step Action Plan](#11-step-by-step-action-plan)
12. [Research Sources](#12-research-sources)

---

## 1. Executive Summary

### The Quick Answers

| Question | Answer |
|---|---|
| **Is the OpenClaw bot a market maker?** | ✅ Yes — the $115K/week bot used automated market making (dual-sided quoting + spread capture) |
| **Can we market-make with $100?** | ⚠️ Technically yes, but profits will be very small ($0.10–$1.00/day). Practical minimum is $500–$1,000. |
| **Are there specific requirements?** | ✅ Zero maker fees, need API access, Python bot, Polygon wallet with USDC, and a VPS for 24/7 uptime |
| **Can we add custom skills to OpenClaw?** | ✅ Absolutely — OpenClaw has a straightforward SKILL.md specification for building custom skills |
| **Can we extend PolyClaw with custom strategies?** | ✅ Yes — it's open-source Python. Clone, modify, add strategy modules, and register as a skill |
| **Is there an official Polymarket market maker bot?** | ✅ Yes — `Polymarket/poly-market-maker` on GitHub, with Bands and AMM strategies |

### The Bottom Line

Market making is **the strategy that makes the big OpenClaw bots profitable**, not simple directional betting. It works by posting both buy and sell orders and earning the spread on every round trip. With $100, it's **educational but not yet profitable** at scale — you need $500-$1,000 to start seeing meaningful returns. The good news: you can absolutely build custom OpenClaw skills and extend PolyClaw with your own market-making logic, and Polymarket even has an official open-source market maker bot to study.

---

## 2. What Exactly Is Market Making?

### Simple Explanation

A market maker is someone who **provides liquidity** to a market by always being willing to both buy and sell. They profit from the **spread** — the difference between their buy price and sell price — not from predicting which direction the market will move.

### How It Works in Plain English

```
Example: "Will BTC be above $85K at 3:00 PM?" market

Current consensus: YES is worth ~$0.55

The market maker:
  Posts a BUY order at $0.53  ("I'll buy YES shares at 53¢")
  Posts a SELL order at $0.57 ("I'll sell YES shares at 57¢")

When both orders fill:
  Bought 100 shares at $0.53 = spent $53
  Sold 100 shares at $0.57   = received $57
  Profit: $4 per round trip (the "spread")
  
The market maker doesn't care if BTC goes up or down.
They profit from the 4¢ spread between buy and sell.
```

### Why Market Makers Exist

| Reason | Explanation |
|---|---|
| **Liquidity** | Without market makers, you'd have to wait for someone who wants the opposite trade |
| **Tighter spreads** | They compete with each other, pushing buy/sell prices closer together |
| **Price discovery** | Their presence helps the market find the "true" price faster |
| **24/7 markets** | Automated bots provide liquidity even at 3 AM |

### Key Difference: Market Maker vs Directional Trader

| Aspect | Market Maker | Directional Trader |
|---|---|---|
| **Goal** | Earn the spread | Predict the outcome correctly |
| **Position** | Both sides simultaneously | One side (YES or NO) |
| **Profit source** | Spread × volume | Price movement |
| **Requires** | High trade volume, low risk | Correct prediction |
| **Win rate needed** | Volume-dependent, not outcome-dependent | >50% for profit |
| **Capital needed** | More (tied up on both sides) | Less (only one side) |
| **Risk** | Inventory risk (holding too much of one side) | Prediction risk (being wrong) |

---

## 3. How Market Making Works on Polymarket (CLOB)

### Polymarket Uses a Central Limit Order Book (CLOB)

Unlike Uniswap-style AMMs (automated market makers that use liquidity pools), Polymarket uses a **traditional order book** — like a stock exchange. This means:

1. **You post limit orders** — specific price + size, waiting for a counterparty
2. **Others can hit your orders** — executing against your posted liquidity
3. **You control your prices** — decide exactly where to quote
4. **No impermanent loss** — unlike DeFi AMMs, you control your inventory

### The Market Making Loop

```
┌─────────────────────────────────────────────────────────────┐
│                   MARKET MAKING LOOP                          │
│                                                               │
│  1. Fetch current midpoint price                              │
│     └─ e.g., YES = $0.55                                     │
│                                                               │
│  2. Calculate your spread                                     │
│     └─ BID at $0.53 (2¢ below mid)                           │
│     └─ ASK at $0.57 (2¢ above mid)                           │
│                                                               │
│  3. Post both orders on CLOB                                  │
│     └─ BUY 50 YES @ $0.53                                    │
│     └─ SELL 50 YES @ $0.57                                   │
│                                                               │
│  4. Wait for fills                                            │
│     └─ If BUY fills → you now hold YES inventory              │
│     └─ If SELL fills → you sold YES inventory                 │
│                                                               │
│  5. Rebalance inventory                                       │
│     └─ If holding too much YES → widen buy, tighten sell      │
│     └─ If holding too much NO → widen sell, tighten buy       │
│     └─ If balanced → keep symmetric                           │
│                                                               │
│  6. Repeat every 10-30 seconds                                │
│                                                               │
│  PROFIT = (Ask - Bid) × number of round trips completed       │
└─────────────────────────────────────────────────────────────┘
```

### Inventory Management — The Critical Risk

The biggest risk in market making is **adverse selection** — trading against someone who knows more than you:

| Risk | What Happens | Mitigation |
|---|---|---|
| **Inventory drift** | You get filled mostly on one side and hold unbalanced inventory | Skew quotes: lower price on the side you're overweight |
| **Adverse selection** | Informed traders buy from you right before a big move | Widen spreads before major events; use "toxic flow" detection |
| **Event resolution** | Market settles to $0 or $1 while you hold losing inventory | Pull all orders before resolution; never market-make near expiry |
| **Low volume** | You post orders but nobody trades, tying up capital | Choose high-volume markets only; set time-based cancellation |

### Polymarket-Specific: Token Split/Merge

On Polymarket, inventory management uses a unique mechanism:

```
USDC ──split──→ YES + NO tokens (1 USDC = 1 YES + 1 NO)
YES + NO ──merge──→ USDC (1 YES + 1 NO = 1 USDC)

This means:
- To start market making, split USDC into equal YES + NO inventory
- To unwind, merge YES + NO back into USDC
- You always maintain inventory on both sides
```

---

## 4. Polymarket Fee Structure — Why Makers Have the Advantage

### Current Fee Structure (2026)

| Order Type | Fee | Rebate |
|---|---|---|
| **Maker** (limit order, resting on book) | **0% — Zero fees** | **25% of taker fees on your fills** |
| **Taker** (market order, crossing the book) | **Up to ~1.56%** (dynamic, based on probability) | None |

### How Maker Rebates Work

```
Example:
  Your resting SELL at $0.57 gets filled by a taker buying at market

  Taker pays: 1.56% fee on $0.57 = $0.0089/share
  Maker rebate: 25% × $0.0089 = $0.0022/share back to you
  
  So you EARN money just for providing liquidity — on top of your spread profit!
```

### Fee Math for Market Making with $100

| Metric | Maker (You) | Taker (Opponent) |
|---|---|---|
| Fee on $100 trade | $0.00 | $1.56 |
| Rebate earned | ~$0.39 (from their fee) | $0.00 |
| Net cost | **-$0.39** (you EARN) | $1.56 |

**This is why market making is the smart approach on Polymarket** — you literally get paid by the platform to provide liquidity, while takers pay the fees.

### Daily Rebate Distribution

- Rebates are calculated and distributed **daily at 00:00 UTC** in USDC
- 100% of taker fees are redistributed to makers (Polymarket takes nothing)
- Your share depends on what percentage of total maker volume you provided

---

## 5. Market Making with $100 — Honest Analysis

### Can You Do It?

**Yes, technically.** Polymarket has no minimum capital requirement for posting limit orders. You can start market-making with any amount.

### But Should You?

Here's the brutally honest math:

### Scenario: $100 Capital, Market Making on BTC 15-Min Markets

```
Setup:
  Capital: $100 USDC
  Split into: 50 YES + 50 NO tokens (via $50 USDC split)
  Remaining: $50 USDC as reserve
  
  Spread: 4¢ ($0.53 bid / $0.57 ask)
  Order size: $5 per side (conservative 5% of capital)
  
Per Round Trip:
  Spread profit: $5 × 0.04 = $0.20
  Maker rebate:  ~$0.01
  Total: $0.21 per complete round trip
  
Daily Estimate (optimistic):
  Round trips per day: 5-15 (depends on market activity)
  Daily profit: $1.05 - $3.15
  
Daily Estimate (realistic):
  Round trips per day: 2-5
  Inventory losses (adverse fills): -$0.50 to -$2.00
  Net daily profit: $0.10 - $1.50
  
Monthly Estimate:
  Optimistic: $30 - $90 (30-90% monthly return)
  Realistic: $3 - $45 (3-45% monthly return)
  Conservative: $0 - $20 (0-20% monthly return, accounting for bad days)
```

### Capital Tiers — What's Realistic

| Capital | Strategy | Expected Daily P&L | Verdict |
|---|---|---|---|
| **$100** | Single-market MM + rebates | $0.10–$1.50 | 📚 Great for learning, too small for income |
| **$500** | 2-3 markets, tighter spreads | $1–$5 | 🟡 Starting to be meaningful |
| **$1,000** | 3-5 markets, automated bot | $3–$15 | 🟢 Practical minimum for serious MM |
| **$5,000** | 5-10 markets, professional bot | $15–$60 | 🟢 Solid income potential |
| **$10,000** | 10+ markets, full automation | $30–$80+ | 🟢 Professional-level (matches liquidity reward data) |
| **$50K-$500K** | 30+ markets, HFT-speed | $500–$5,000+ | 💰 The "$115K/week" league |

### Requirements Checklist for Market Making on Polymarket

| Requirement | Details | Cost |
|---|---|---|
| **USDC on Polygon** | Your trading capital | $100+ |
| **Polygon wallet** | MetaMask or dedicated hot wallet | Free |
| **Polymarket API key** | For programmatic order management | Free |
| **Python 3.10+** | Bot runtime | Free |
| **py-clob-client SDK** | Official Polymarket Python SDK | Free |
| **VPS (recommended)** | 24/7 uptime for bot (QuantVPS, DigitalOcean) | $5-20/mo |
| **Polygon RPC node** | Chainstack free tier or Alchemy | Free tier available |
| **Gas fees (POL)** | For on-chain transactions | ~$0.01-$0.05/tx |

### The $100 Market Making Verdict

| Aspect | Assessment |
|---|---|
| **Is it possible?** | ✅ Yes — no minimum capital requirement |
| **Will I make thousands daily?** | ❌ Absolutely not. Need $50K+ for that |
| **Is it worth doing at $100?** | ✅ As a learning exercise — you'll learn market microstructure hands-on |
| **What's the realistic return?** | $0.10–$1.50/day ($3–$45/month) |
| **Main risk?** | Holding inventory when market moves sharply against you |
| **Best approach at $100?** | Combine MM with directional trading (our latency arb from PRD) |

---

## 6. Polymarket Liquidity Rewards Program

Beyond spread capture, Polymarket pays **direct USDC rewards** to liquidity providers — even if your orders don't fill.

### How Liquidity Rewards Work

```
You place a resting limit order close to the midpoint
  ↓
Polymarket calculates your "Q-score":
  - Order size (bigger = more points)
  - Distance from midpoint (closer = WAY more points)
  - Duration on book (longer = more points)
  ↓
Daily pool ($10,000-$16,000 total across all markets) is split by Q-score
  ↓
Your share paid out in USDC at 00:00 UTC
```

### Q-Score Formula

Your Q-score determines your share of the daily reward pool:

```
Q-score ≈ Order_Size × (1 / Distance_from_Midpoint²)

The exponential distance penalty means:
  Order 1¢ from mid → 100× more rewards than order 10¢ from mid
  Order at mid → Maximum possible rewards
```

### Liquidity Rewards at Different Capital Levels

| Capital | Expected Daily Rewards | Monthly | Notes |
|---|---|---|---|
| $100 | $0.01–$0.10 | $0.30–$3.00 | Tiny share of pool (you're competing with big players) |
| $500 | $0.05–$0.50 | $1.50–$15.00 | Still small |
| $1,000 | $0.10–$1.00 | $3.00–$30.00 | Starting to matter |
| $5,000 | $0.50–$5.00 | $15.00–$150.00 | Meaningful supplement |
| $10,000 | $3.00–$8.00 | $90–$240 | Serious passive income |

### Bonus: 4% Annualized Position Rewards

For select long-term markets, Polymarket offers **4% annualized daily rewards** just for holding positions:

```
$100 invested in eligible long-term market
4% annual = $4/year = ~$0.011/day

Not game-changing at $100, but it compounds when combined with
spread capture and liquidity rewards.
```

### Combined Revenue Streams for $100 Market Maker

| Revenue Source | Daily Estimate | Monthly |
|---|---|---|
| Spread capture (round trips) | $0.10–$1.50 | $3–$45 |
| Maker rebates (25% of taker fees) | $0.01–$0.05 | $0.30–$1.50 |
| Liquidity rewards (Q-score) | $0.01–$0.10 | $0.30–$3.00 |
| Position rewards (4% annual) | $0.01 | $0.30 |
| **Total** | **$0.13–$1.66** | **$3.90–$49.80** |

---

## 7. Official Polymarket Market Maker Bot (poly-market-maker)

### Overview

Polymarket has released an **official, open-source market maker bot** — this is the single most important tool for anyone wanting to do market making on the platform.

| Attribute | Value |
|---|---|
| **Repo** | [github.com/Polymarket/poly-market-maker](https://github.com/Polymarket/poly-market-maker) |
| **Maintainer** | Polymarket team (official) |
| **Language** | Python 3.10+ |
| **License** | Open source |
| **Strategies** | Bands, AMM |
| **Status** | Experimental / active development |

### Two Built-In Strategies

#### Strategy 1: Bands

Places orders at multiple price levels ("bands") around the current midpoint.

```json
// config/bands.json (simplified)
{
  "spread": 0.02,     // 2¢ away from midpoint on each side
  "depth": 0.10,      // How deep into the book to quote
  "levels": 3,        // Number of order bands
  "size": 10,         // Size per band in USDC
  "rebalance": true   // Auto-rebalance inventory
}
```

```
Visualization:
  
  Price     Orders
  $0.60     ── SELL band 3 (10 shares)
  $0.58     ── SELL band 2 (10 shares)
  $0.57     ── SELL band 1 (10 shares)
  $0.55     ← midpoint
  $0.53     ── BUY band 1 (10 shares)
  $0.52     ── BUY band 2 (10 shares)
  $0.50     ── BUY band 3 (10 shares)
```

#### Strategy 2: AMM (Automated Market Maker Style)

Emulates Uniswap V3-style concentrated liquidity on the order book.

```json
// config/amm.json (simplified)
{
  "p_min": 0.30,          // Minimum price to provide liquidity
  "p_max": 0.70,          // Maximum price range
  "spread": 0.01,         // Minimum 1¢ spread
  "delta": 0.02,          // Price increment between orders
  "depth": 0.05,          // Order depth
  "max_collateral": 100   // Maximum USDC to deploy
}
```

### Configuration

```bash
# .env file
CLOB_API_KEY="your-api-key"
CLOB_SECRET="your-api-secret"
CLOB_PASS_PHRASE="your-passphrase"
PRIVATE_KEY="0xYOUR_WALLET_PRIVATE_KEY"
CHAIN_ID=137                    # Polygon mainnet

# config.env
CONDITION_ID="0x..."            # Market condition ID
STRATEGY="Bands"                # or "AMM"
CONFIG="./config/bands.json"
```

### Running the Bot

```bash
# Install
git clone https://github.com/Polymarket/poly-market-maker
cd poly-market-maker
./install.sh

# Configure
cp .env.example .env
# Edit .env with your credentials

# Run
./run-local.sh
# or with Docker:
docker-compose up
```

### Bot Behavior

- Syncs every 30 seconds (configurable)
- Cancels stale orders and posts fresh ones based on current midpoint
- Graceful shutdown cancels all open orders
- Logs all activity for P&L tracking

### Why This Matters for Us

The official bot is **the gold standard** for Polymarket market making. It's:
1. **Maintained by Polymarket** — guaranteed API compatibility
2. **Production-tested** — used by professional market makers
3. **Simple to configure** — JSON config + env vars
4. **Extensible** — Python codebase you can modify

**This is more relevant to our project than PolyClaw for market-making specifically.**

---

## 8. OpenClaw Custom Skills — Yes, You Can Build Your Own

### The Big Answer: Yes, OpenClaw Is Fully Extensible

If PolyClaw's built-in strategies aren't enough, you have **three options**:

1. **Build a completely new OpenClaw skill** (custom SKILL.md)
2. **Fork and extend PolyClaw** (add strategy modules)
3. **Use the official poly-market-maker bot standalone** (no OpenClaw needed)

### Option 1: Build a Custom OpenClaw Skill

Every OpenClaw skill is a folder with a `SKILL.md` file. That's it.

#### Directory Structure

```
~/.openclaw/workspace/skills/polymarket-mm/
├── SKILL.md              # Required: Instructions + metadata
├── scripts/
│   ├── market_maker.py   # Your custom market making bot
│   ├── config.json       # Strategy configuration
│   └── utils.py          # Helper functions
└── references/
    └── strategy-notes.md # Optional documentation
```

#### SKILL.md Specification

```markdown
---
name: polymarket_mm
description: Custom market making bot for Polymarket BTC 15-minute markets with spread capture, inventory management, and latency arbitrage.
metadata:
  openclaw:
    requires:
      bins: [python3, uv]
      env: [POLYMARKET_API_KEY, POLYMARKET_SECRET, PRIVATE_KEY, CHAINSTACK_NODE]
    emoji: "📈"
---

# Polymarket Market Maker

Custom market making skill for Polymarket BTC 15-minute UP/DOWN markets.

## Capabilities

- Two-sided quoting with configurable spread
- Inventory skewing based on position imbalance
- Binance price feed for fair value calculation
- Automatic order management (post/cancel/replace)
- Risk controls: max position, max loss, circuit breaker

## Commands

### Start Market Making
```
start mm on [market_id] with $[amount] spread [cents]
```

### Check Status
```
mm status
mm positions
mm pnl today
```

### Stop
```
stop mm
```

## Usage Examples

- "Start market making on BTC 15-min UP with $50 and 3 cent spread"
- "What's my market making P&L today?"
- "Stop all market making and cancel open orders"

## Safety

- Always uses a dedicated hot wallet (never main wallet)
- Maximum position size capped at 25% of capital
- Circuit breaker triggers on 5% daily loss
- Pulls all quotes 60 seconds before market resolution
```

#### SKILL.md Metadata Fields

| Field | Required | Description |
|---|---|---|
| `name` | ✅ | Unique skill identifier (snake_case) |
| `description` | ✅ | One-line description of what the skill does |
| `metadata.openclaw.requires.bins` | ❌ | Required system binaries (e.g., python3, node) |
| `metadata.openclaw.requires.env` | ❌ | Required environment variables |
| `metadata.openclaw.emoji` | ❌ | Icon for the skill in UI |

#### Registering Your Skill

```bash
# Option A: Place directly in workspace
cp -r polymarket-mm ~/.openclaw/workspace/skills/

# Option B: Install via ClawHub (if you publish it)
clawhub install your-username/polymarket-mm

# Option C: Tell OpenClaw to refresh
# In chat: "refresh skills" or restart the gateway
```

### Option 2: Fork and Extend PolyClaw

If you like PolyClaw's existing features but want to add market-making logic:

```bash
# Clone the official repo
git clone https://github.com/chainstacklabs/polyclaw
cd polyclaw

# Add your custom strategy module
# Edit: scripts/strategies/market_maker.py

# Register as modified skill
cp -r polyclaw ~/.openclaw/skills/polyclaw-custom
```

### Option 3: Standalone Bot (No OpenClaw)

You can run the official `poly-market-maker` or our custom bot completely independently:

```bash
# Official Polymarket bot
git clone https://github.com/Polymarket/poly-market-maker
cd poly-market-maker
./install.sh && ./run-local.sh

# Or our custom PRD bot (when built)
python bot/main.py --strategy market_maker --capital 100
```

---

## 9. Extending PolyClaw with Custom Trading Strategies

### What PolyClaw Already Has

| Built-in Feature | Available? |
|---|---|
| Market browsing & search | ✅ |
| Trade execution (split+CLOB) | ✅ |
| Position tracking & P&L | ✅ |
| LLM-powered hedge discovery | ✅ |
| Wallet management | ✅ |
| Strategy arena (paper trading competition) | ✅ |
| Market making (two-sided quoting) | ❌ Not built-in |
| Binance price feed | ❌ Not built-in |
| Latency arbitrage | ❌ Not built-in |
| Automated inventory management | ❌ Not built-in |

### What You Can Add (Custom Extensions)

#### Extension 1: Market Making Module

```python
# scripts/strategies/market_maker.py (sketch)

class MarketMaker:
    def __init__(self, market_id, capital, spread_bps=200):
        self.market_id = market_id
        self.capital = capital
        self.spread = spread_bps / 10000  # 200 bps = 2¢
        self.inventory = {"YES": 0, "NO": 0}
    
    def get_midpoint(self):
        """Fetch current midpoint from CLOB order book"""
        # Use polyclaw's existing market data functions
        pass
    
    def calculate_quotes(self):
        """Calculate bid/ask with inventory skew"""
        mid = self.get_midpoint()
        skew = self.inventory_skew()
        
        bid = mid - self.spread/2 - skew
        ask = mid + self.spread/2 - skew
        return bid, ask
    
    def inventory_skew(self):
        """Skew quotes based on inventory imbalance"""
        yes_val = self.inventory["YES"]
        no_val = self.inventory["NO"]
        imbalance = (yes_val - no_val) / max(yes_val + no_val, 1)
        return imbalance * 0.01  # 1¢ skew per unit imbalance
    
    def post_quotes(self, bid, ask, size):
        """Post both sides to CLOB"""
        # Use polyclaw's trade execution functions
        pass
    
    def run_loop(self):
        """Main market making loop"""
        while True:
            bid, ask = self.calculate_quotes()
            self.cancel_stale_orders()
            self.post_quotes(bid, ask, size=5)
            time.sleep(30)  # Sync every 30 seconds
```

#### Extension 2: Binance Price Feed

```python
# scripts/signals/binance_feed.py

import websocket
import json

class BinanceFeed:
    def __init__(self):
        self.current_price = None
        self.ws_url = "wss://stream.binance.com:9443/ws/btcusdt@ticker"
    
    def on_message(self, ws, message):
        data = json.loads(message)
        self.current_price = float(data['c'])
    
    def get_fair_value(self, strike_price, time_to_expiry):
        """Calculate fair YES/NO probability using current BTC price"""
        # Black-Scholes digital option formula
        pass
```

#### Extension 3: Combined Strategy (MM + Arb)

```python
# scripts/strategies/hybrid.py

class HybridStrategy:
    """
    70% Market Making + 30% Latency Arbitrage
    Same strategy the $115K/week bot used.
    """
    
    def __init__(self, capital):
        self.mm = MarketMaker(capital=capital * 0.7)
        self.arb = LatencyArb(capital=capital * 0.3)
    
    def run(self):
        # Run both strategies in parallel
        # MM captures spread passively
        # Arb captures directional moves aggressively
        pass
```

### How to Register as OpenClaw Skill

1. Create your skill directory:

```bash
mkdir -p ~/.openclaw/workspace/skills/polyclaw-mm
```

2. Write your SKILL.md:

```markdown
---
name: polyclaw_mm
description: Extended PolyClaw with market making, Binance price feed, and hybrid strategy support.
metadata:
  openclaw:
    requires:
      bins: [python3, uv]
      env: [POLYCLAW_PRIVATE_KEY, CHAINSTACK_NODE, BINANCE_WS]
    emoji: "📊"
---

# PolyClaw Market Maker

Extended version of PolyClaw with:
- Two-sided market making with inventory management
- Binance real-time price feed for BTC fair value
- Hybrid strategy: 70% MM + 30% latency arb
- All original PolyClaw features (browsing, hedging, etc.)

## Commands

- "start market making on BTC 15-min with $100"
- "show mm status and pnl"  
- "run hybrid strategy"
- "stop all trading"
```

3. Tell OpenClaw to load it:

```bash
# Restart OpenClaw or send "refresh skills" in chat
openclaw restart
```

---

## 10. Combined Strategy: Market Making + Our Custom Bot

### The Optimal Approach for $100

Given everything we've researched, here's the optimal combined strategy:

```
┌─────────────────────────────────────────────────────────────┐
│              OPTIMAL $100 STRATEGY                            │
│                                                               │
│  ┌───────────────────┐  ┌────────────────────────────────┐  │
│  │ LAYER 1: MM        │  │ LAYER 2: Directional           │  │
│  │ (Passive Income)   │  │ (Active Trading)                │  │
│  │                     │  │                                 │  │
│  │ Capital: $60 (60%) │  │ Capital: $40 (40%)              │  │
│  │                     │  │                                 │  │
│  │ • Two-sided quotes  │  │ • Latency arb (from PRD)       │  │
│  │ • Earn spread       │  │ • Buy mispriced side            │  │
│  │ • Earn rebates      │  │ • Sell after correction          │  │
│  │ • Earn LQ rewards   │  │ • Black-Scholes fair value      │  │
│  │ • 24/7 automated    │  │ • Event-driven triggers         │  │
│  │                     │  │                                 │  │
│  │ Expected: $0.10-$1  │  │ Expected: $0.50-$3/day          │  │
│  └───────────────────┘  └────────────────────────────────┘  │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ LAYER 3: Hedge Discovery (PolyClaw LLM)                  │  │
│  │ • Scan for cross-market logical arbitrage                 │  │
│  │ • Use when clear T1/T2 opportunities exist                │  │
│  │ • Expected: $0-$2/day (opportunistic, not daily)          │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                               │
│  COMBINED DAILY TARGET: $0.60 - $6.00                        │
│  REALISTIC MONTHLY: $18 - $180                               │
└─────────────────────────────────────────────────────────────┘
```

### Why This Is Better Than Any Single Strategy

| Approach | Daily P&L | Risk | Capital Efficiency |
|---|---|---|---|
| MM only ($100) | $0.10–$1.50 | Low | Medium (capital tied up on both sides) |
| Arb only ($100) | $0.50–$3.00 | Medium | High (concentrated bets) |
| Hedge only ($100) | $0–$2.00 | Low | Low (opportunities are rare) |
| **Combined** ($100) | **$0.60–$6.00** | **Medium** | **High (capital allocated dynamically)** |

### When to Graduate to $500+

| Milestone | Action |
|---|---|
| Week 1-2 | Paper trade all three strategies, validate bot logic |
| Week 3-4 | Live trade with $100, track real P&L vs projections |
| Month 2 | If profitable and consistent, add $400 to reach $500 |
| Month 3 | Scale to $1,000 if edge is proven |
| Month 6+ | Consider $5,000+ allocation if monthly returns exceed 15% |

---

## 11. Step-by-Step Action Plan

### Phase 1: Learn & Paper Trade (Week 1-2)

```bash
# 1. Study the official market maker bot
git clone https://github.com/Polymarket/poly-market-maker
# Read docs/strategies/bands.md and docs/strategies/amm.md

# 2. Install PolyClaw for market research
git clone https://github.com/chainstacklabs/polyclaw
cd polyclaw && uv sync
# Browse markets, study order books, run hedge scans

# 3. Paper trade market making mentally or in a spreadsheet
# Track: midpoint, your quotes, fills, P&L
```

### Phase 2: Build Custom Skill (Week 2-3)

```bash
# 1. Create custom OpenClaw skill
mkdir -p ~/.openclaw/workspace/skills/polymarket-mm

# 2. Write SKILL.md (see Section 8)

# 3. Build market making script
#    - Use py-clob-client for order management
#    - Use Binance WebSocket for price feed
#    - Implement bands strategy from poly-market-maker

# 4. Test in simulation mode
python scripts/market_maker.py --paper-trade
```

### Phase 3: Go Live with $100 (Week 3-4)

```bash
# 1. Fund dedicated hot wallet with $100 USDC + $1 POL for gas

# 2. Start market making on ONE BTC 15-min market
python scripts/market_maker.py --capital 100 --spread 3

# 3. Monitor for 48 hours before adding arb strategy

# 4. Add latency arb component
python scripts/hybrid.py --mm-capital 60 --arb-capital 40
```

### Phase 4: Optimize & Scale (Month 2+)

```bash
# 1. Analyze first month's data
python scripts/analyze_pnl.py

# 2. Optimize spread, sizing, and timing parameters

# 3. Add PolyClaw hedge discovery as supplementary strategy

# 4. Scale capital if profitable
```

---

## 12. Research Sources

### Market Making on Polymarket

| Source | URL |
|---|---|
| Polymarket Market Making Guide (Alphascope) | [alphascope.app/blog/polymarket-market-making](https://www.alphascope.app/blog/polymarket-market-making) |
| Polymarket Market Making Strategy (ManageBankroll) | [managebankroll.com/blog/polymarket-market-making-liquidity-strategy](https://managebankroll.com/blog/polymarket-market-making-liquidity-strategy) |
| Market Making Complete 2026 Guide (NYC Servers) | [newyorkcityservers.com/blog/prediction-market-making-guide](https://newyorkcityservers.com/blog/prediction-market-making-guide) |
| Market Making in Prediction Markets (QuantVPS) | [quantvps.com/blog/market-making-in-prediction-markets](https://www.quantvps.com/blog/market-making-in-prediction-markets) |
| Polymarket Market Making Simulation (GitHub) | [github.com/justin-theodorus/polymarket-take-home](https://github.com/justin-theodorus/polymarket-take-home) |

### Fees & Rewards

| Source | URL |
|---|---|
| Polymarket Fee Structure (ATS.io) | [ats.io/prediction-markets/polymarket/fees](https://ats.io/prediction-markets/polymarket/fees/) |
| Maker Rebates Program (GitHub docs) | [github.com/ank1015/polymarket-collector — maker-rebates](https://github.com/ank1015/polymarket-collector/blob/main/docs/developers/market-makers/maker-rebates-program.md) |
| Polymarket Taker Fee Model (ainvest) | [ainvest.com — taker-fee-model](https://www.ainvest.com/news/polymarket-taker-fee-model-strategic-shift-enhance-liquidity-short-term-crypto-markets-2601/) |
| Taker Fees Launch (Blockonomi) | [blockonomi.com — maker-rebates-program](https://blockonomi.com/polymarket-launches-maker-rebates-program-with-taker-fees-on-15-minute-crypto-markets/) |
| Liquidity Rewards Docs (Polymarket) | [docs.polymarket.com/market-makers/liquidity-rewards](https://docs.polymarket.com/market-makers/liquidity-rewards) |
| Liquidity Farming Guide (GuruPolymarket) | [gurupolymarket.com — liquidity-farm](https://gurupolymarket.com/en/tutorials/how-to-liquidity-farm-on-polymarket/) |
| Q-Score Optimizer (opt.markets) | [opt-markets.com/about](https://opt-markets.com/about) |

### Official Tools

| Source | URL |
|---|---|
| **poly-market-maker (Official Bot)** | [github.com/Polymarket/poly-market-maker](https://github.com/Polymarket/poly-market-maker) |
| AMM Strategy Docs | [github.com/Polymarket/poly-market-maker — amm.md](https://github.com/Polymarket/poly-market-maker/blob/main/docs/strategies/amm.md) |
| Polymarket API Docs | [docs.polymarket.com](https://docs.polymarket.com/) |
| Polymarket Trading Docs | [docs.polymarket.com/market-makers/trading](https://docs.polymarket.com/market-makers/trading) |
| Inventory Management Docs | [docs.polymarket.com/market-makers/inventory](https://docs.polymarket.com/market-makers/inventory) |
| py-clob-client SDK Reference | [agentbets.ai/guides/py-clob-client-reference](https://agentbets.ai/guides/py-clob-client-reference/) |

### OpenClaw Custom Skills

| Source | URL |
|---|---|
| OpenClaw: Creating Skills (Official) | [docs.openclaw.ai/tools/creating-skills](https://docs.openclaw.ai/tools/creating-skills/) |
| Skills Developer Guide (Meta Intelligence) | [meta-intelligence.tech — openclaw-skills](https://www.meta-intelligence.tech/en/insight-openclaw-skills) |
| Custom Skill Creation Guide (ZenVanRiel) | [zenvanriel.com — openclaw-custom-skill](https://zenvanriel.com/ai-engineer-blog/openclaw-custom-skill-creation-guide/) |
| Building Custom Skills (DataCamp) | [datacamp.com/tutorial/building-open-claw-skills](https://www.datacamp.com/tutorial/building-open-claw-skills) |
| Skill Tutorial with Image Processing | [eastondev.com — openclaw-skill-tutorial](https://eastondev.com/blog/en/posts/ai/20260205-openclaw-skill-tutorial/) |

### Small Capital Strategies

| Source | URL |
|---|---|
| Small Bankroll Strategies (TronieX) | [troniextechnologies.com — small-bankroll-strategy](https://www.troniextechnologies.com/blog/polymarket-small-bankroll-strategy) |
| How to Make Money on Polymarket (LaikaLabs) | [laikalabs.ai — how-to-make-money](https://laikalabs.ai/prediction-markets/how-to-make-money-on-polymarket) |
| Liquidity Risk Case Study (CamelliaVC) | [camelliavc.com — polymarket-case-studies](https://www.camelliavc.com/programs/publications/polymarket-case-studies/) |
| Automated Trading on Polymarket (QuantVPS) | [quantvps.com/blog/automated-trading-polymarket](https://www.quantvps.com/blog/automated-trading-polymarket) |
| Bot Development Guide (Kirchainlabs) | [kirchainlabs.com — polymarket-prediction-bot](https://www.kirchainlabs.com/blog/polymarket-prediction-bot-development/) |
| 4% Daily Rewards (Altcoin Buzz) | [altcoinbuzz.io — polymarket-4-daily-rewards](https://www.altcoinbuzz.io/cryptocurrency-news/polymarket-offers-4-daily-rewards-on-long-term-bets/) |

---

## Document History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | March 13, 2026 | Poly-Trade Research | Market making deep dive, $100 viability analysis, custom OpenClaw skills guide, PolyClaw extension patterns, poly-market-maker overview |

---

> ⚠️ **Disclaimer:** This is a research document, not financial advice. Market making involves real financial risk including inventory risk and adverse selection. The profit estimates in this document are based on mathematical models and reported data — actual returns will vary. Always start with amounts you can afford to lose. Use dedicated hot wallets and isolated environments for all automated trading.
