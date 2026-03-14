# Polymarket Deep Research: Market Makers, CTF Operations, and BTC Up/Down Markets

> **Purpose:** A complete, example-driven reference covering how Polymarket market makers work, how to set one up, what those mysterious "zero-price / positive P&L" profiles really are, and how Split / Merge / Redeem operations work under the hood.

---

## Table of Contents

1. [Polymarket Architecture Overview](#1-polymarket-architecture-overview)
2. [How the CLOB Works](#2-how-the-clob-works)
3. [Maker vs Taker — Fees, Rebates, and Rewards](#3-maker-vs-taker--fees-rebates-and-rewards)
4. [Conditional Token Framework (CTF) — Positions & Tokens](#4-conditional-token-framework-ctf--positions--tokens)
5. [Split, Merge, and Redeem — Deep Dive](#5-split-merge-and-redeem--deep-dive)
6. [Market Making on Polymarket — How It Really Works](#6-market-making-on-polymarket--how-it-really-works)
7. [The "Zero Price / Zero Bought / Positive P&L" Mystery Explained](#7-the-zero-price--zero-bought--positive-pl-mystery-explained)
8. [BTC Up/Down Markets — 5-Minute and 15-Minute](#8-btc-updown-markets--5-minute-and-15-minute)
9. [Setting Up a Market Maker Bot — Complete Guide](#9-setting-up-a-market-maker-bot--complete-guide)
10. [Bands Strategy — Deep Dive](#10-bands-strategy--deep-dive)
11. [AMM Strategy — Deep Dive](#11-amm-strategy--deep-dive)
12. [Inventory Management — The Core Skill](#12-inventory-management--the-core-skill)
13. [Liquidity Rewards and Maker Rebates Program](#13-liquidity-rewards-and-maker-rebates-program)
14. [Analytics Tools and Resources](#14-analytics-tools-and-resources)
15. [Quick Reference — Smart Contract Addresses](#15-quick-reference--smart-contract-addresses)

---

## 1. Polymarket Architecture Overview

Polymarket is a decentralized prediction market platform built on the **Polygon** blockchain. Every market resolves to either YES ($1) or NO ($0) per share. The platform has three major technical layers:

```
┌─────────────────────────────────────────────────────────────┐
│                     USER / BOT / API                        │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│         CLOB (Central Limit Order Book)                     │
│    Off-chain matching engine + on-chain settlement          │
│    REST API: https://clob.polymarket.com                    │
│    WebSocket: wss://clob-ws.polymarket.com                  │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│    CTF Exchange Contract (Polygon Mainnet)                  │
│    Gnosis Conditional Token Framework                       │
│    ERC-1155 tokens for YES / NO positions                   │
│    Collateral: USDC.e                                       │
└─────────────────────────────────────────────────────────────┘
```

### Key APIs

| API | Base URL | Purpose |
|-----|----------|---------|
| CLOB API | `https://clob.polymarket.com` | Trading — place/cancel orders |
| Data API | `https://data-api.polymarket.com` | Analytics — positions, P&L, history |
| Gamma API | `https://gamma-api.polymarket.com` | Market metadata, event discovery |

---

## 2. How the CLOB Works

### 2.1 What is a CLOB?

A **Central Limit Order Book** is the same matching mechanism used by stock exchanges like NASDAQ. Buyers and sellers post limit orders at specific prices; the exchange matches them by price-time priority.

```
BUY SIDE (Bids)          SELL SIDE (Asks)
------------------        -------------------
$0.53  x 500             $0.54  x 200
$0.52  x 1000            $0.55  x 800
$0.51  x 2000            $0.56  x 1200
$0.50  x 5000            $0.57  x 3000
       ↑                         ↑
    Best Bid                  Best Ask
    (Highest buy)             (Lowest sell)
```

- **Spread** = Best Ask − Best Bid = $0.54 − $0.53 = **$0.01**
- **Midpoint** = (Best Bid + Best Ask) / 2 = **$0.535**

### 2.2 Order Types

| Type | Full Name | Behavior | Best Used For |
|------|-----------|----------|---------------|
| **GTC** | Good-Til-Cancelled | Sits on the book until filled or cancelled | Passive market making, providing liquidity |
| **FOK** | Fill-or-Kill | Must fill entirely and immediately, or cancel | Arbitrage, risk-sensitive entries |
| **FAK** | Fill-and-Kill | Fill whatever is available now, cancel the rest | Partial exits, unwinding positions |

### 2.3 Price-Time Priority

When two orders have the same price, the earlier order gets filled first. This creates a queue:

```
Example: Three market makers all post Sell at $0.54

Queue (time-ordered):
1. Trader A: Sell 200 @ $0.54  ← filled first
2. Trader B: Sell 500 @ $0.54  ← filled second
3. Trader C: Sell 300 @ $0.54  ← filled third
```

This incentivizes being early and maintaining orders on the book (which is what bots do well).

### 2.4 How a Trade Executes

When a taker hits a maker's order, the CLOB engine:
1. Matches the orders off-chain
2. Calls the CTF exchange contract on Polygon
3. The contract transfers YES/NO tokens between wallets
4. All of this settles on-chain within seconds

---

## 3. Maker vs Taker — Fees, Rebates, and Rewards

### 3.1 Who is a Maker vs Taker?

| Role | Action | Liquidity Effect |
|------|--------|-----------------|
| **Maker** | Posts a limit order to the book; waits to be filled | **Adds** liquidity |
| **Taker** | Places a market order or a limit order that immediately matches | **Removes** liquidity |

### 3.2 Fee Structure (as of 2025–2026)

| Role | Standard Markets | High-Frequency Crypto Markets (5m/15m) |
|------|-----------------|----------------------------------------|
| **Maker** | **$0 (zero fees)** | $0 + eligible for **daily USDC rebates** |
| **Taker** | $0 (most markets) | Up to **1.56%** taker fee |

The taker fee follows a curved formula — it is highest (~1.56%) at 50% probability and drops toward zero at extreme prices (near 0% or 100%).

### 3.3 Liquidity Rewards Program

For most Polymarket markets, there is a **daily USDC rewards pool** (typically $10,000–$16,000/day across all eligible markets) distributed to liquidity providers:

```
Your Daily Reward = (Your Eligible Filled Volume / Total Eligible Volume) × Daily Pool

Example:
- Daily pool: $10,000
- Your filled maker volume: $5,000
- Total market filled maker volume: $500,000
- Your reward: ($5,000 / $500,000) × $10,000 = $100/day
```

**Eligibility criteria:**
- Orders must be within a certain distance of the midpoint
- Both sides (YES and NO) must be quoted simultaneously (two-sided quoting)
- Orders must stay on the book for minimum time periods

### 3.4 Maker Rebates Program

For 5-minute and 15-minute crypto markets and certain sports markets:
- Rebate pool = 20–25% of all taker fees collected
- Paid **daily** in USDC directly to your wallet
- Based on your proportion of total maker-filled volume in that market

---

## 4. Conditional Token Framework (CTF) — Positions & Tokens

### 4.1 What is CTF?

The **Conditional Token Framework** is a smart contract standard (originally by Gnosis, adopted by Polymarket) that represents prediction market positions as **ERC-1155 tokens** on-chain.

Every binary market has exactly two outcome tokens:
- **YES token** — redeemable for $1 USDC.e if the event occurs
- **NO token** — redeemable for $1 USDC.e if the event does NOT occur

### 4.2 The Core Invariant

```
Price(YES) + Price(NO) = $1.00  (always, at any time)
```

This is enforced by the ability to split and merge tokens at will:
- If YES = $0.60 and NO = $0.45, the pair costs $1.05. Arbitrageurs will split $1 USDC to get YES+NO, sell YES at $0.60 and sell NO to push its price down to ~$0.40, restoring the sum to $1.00 and pocketing the $0.05 difference.
- If YES = $0.55 and NO = $0.40 (sum = $0.95), arbitrageurs will buy both tokens for $0.95 and immediately merge them into $1.00 USDC, pocketing $0.05 per pair and driving both prices back up to sum to $1.00.

### 4.3 Token IDs — How Positions are Identified

Each position has a unique ERC-1155 token ID computed as:

```
Step 1: conditionId = keccak256(oracleAddress, questionId, outcomeCount)
Step 2: collectionId = keccak256(parentCollectionId, conditionId, indexSet)
          where indexSet = 1 for YES, 2 for NO (bitmasks)
Step 3: positionId = keccak256(collateralTokenAddress, collectionId)
```

The `positionId` is what you see in ERC-1155 transfers and wallet balances on Polygon.

### 4.4 Fully-Backed Collateral

The CTF contract at all times holds exactly:

```
USDC.e_in_contract = (Total YES tokens in existence) = (Total NO tokens in existence)
```

This means the system is always solvent by design — no fractional reserve, no leverage.

---

## 5. Split, Merge, and Redeem — Deep Dive

### 5.1 SPLIT — Creating Positions from Collateral

**What it does:** Converts USDC.e → YES tokens + NO tokens

```
Input:  100 USDC.e
Output: 100 YES tokens + 100 NO tokens
Cost:   Nothing (1:1:1 conversion)
```

**When to use:**
- Market maker needs inventory on both sides
- Trader wants to sell one side while keeping the other as a hedge
- Capital efficient: you own both sides, total value = $100 regardless of outcome

**Smart contract function:**
```solidity
function splitPosition(
    address collateralToken,    // USDC.e address on Polygon
    bytes32 parentCollectionId, // bytes32(0) for simple binary markets
    bytes32 conditionId,        // unique market identifier
    uint256[] partition,        // [1, 2] — bitmask array: 1 = YES index set, 2 = NO index set
    uint256 amount              // number of token sets to create
) external;
```

**Example workflow:**
```python
# Python using py-clob-client
from py_clob_client.clob_types import ApiCreds

# Step 1: Approve CTF contract to spend your USDC.e
# Step 2: Call splitPosition
# The SDK handles this automatically when you post orders that require inventory
```

**Step-by-step visual:**
```
Before Split:
  Wallet: 1000 USDC.e, 0 YES, 0 NO

Split 1000 USDC.e:
  → CTF contract locks 1000 USDC.e
  → Mints 1000 YES tokens to your wallet
  → Mints 1000 NO tokens to your wallet

After Split:
  Wallet: 0 USDC.e, 1000 YES, 1000 NO
  CTF Contract: holds 1000 USDC.e as collateral
```

---

### 5.2 MERGE — Reclaiming Collateral from Positions

**What it does:** Converts YES tokens + NO tokens → USDC.e

```
Input:  100 YES tokens + 100 NO tokens
Output: 100 USDC.e
Requirement: Must provide EQUAL amounts of both tokens
```

**When to use:**
- Market maker has excess inventory on both sides after trading
- Exit a market before resolution without waiting for oracle
- Recover capital to deploy elsewhere

**Smart contract function:**
```solidity
function mergePositions(
    address collateralToken,    // USDC.e address
    bytes32 parentCollectionId, // bytes32(0)
    bytes32 conditionId,        // market ID
    uint256[] partition,        // [1, 2]
    uint256 amount              // number of complete pairs to burn
) external;
```

**Example workflow:**
```
Market maker has: 500 YES (cost: $200), 800 NO (cost: $300)

Strategy: Merge the minimum (500 pairs) to recover capital

Merge 500 YES + 500 NO:
  → Burns 500 YES + 500 NO
  → Returns 500 USDC.e to wallet

After Merge:
  Wallet: 500 USDC.e, 0 YES, 300 NO
  Capital recovered: $500 (originally cost $350 for those 500 pairs)
  Profit: $150 locked in
  Still holds: 300 NO tokens (residual position)
```

---

### 5.3 REDEEM — Claiming Winnings After Resolution

**What it does:** Burns winning tokens → USDC.e, after the oracle resolves the market

```
Input:  Winning outcome tokens (YES if event occurred, NO if not)
Output: 1 USDC.e per winning token
Timing: Only available AFTER market resolution
```

**Smart contract function:**
```solidity
function redeemPositions(
    address collateralToken,    // USDC.e address
    bytes32 parentCollectionId, // bytes32(0)
    bytes32 conditionId,        // market ID
    uint256[] indexSets         // [1] for YES, [2] for NO
) external;
```

**Example:**
```
Market: "Will BTC be above $100k by end of 2024?"
Resolution: NO (BTC did not cross $100k in time)

You hold: 200 NO tokens (bought at $0.40 avg = $80 total invested)

Redeem 200 NO tokens:
  → Burns 200 NO tokens
  → Returns 200 USDC.e ($200)
  
Profit: $200 - $80 = $120 (150% return)

Your 0 YES tokens: worthless (do not redeem)
```

---

### 5.4 The Full Lifecycle — All Three Operations Together

```
Timeline of a Market Maker's Position

Day 0: Market opens — "Will BTC hit $150k in Q1?"
  ├── BTC price: $45,000
  ├── YES price: $0.10 (10% probability)
  └── NO price: $0.90

Action 1: SPLIT
  → Split 1000 USDC.e
  → Get: 1000 YES + 1000 NO
  → Now quote both sides

Day 1: BTC surges — YES rises to $0.35
  ├── Sold 600 YES at ~$0.30 avg = $180 received
  └── Accumulated: 1600 NO (from trades + remaining)

Action 2: MERGE (partial capital recovery)
  → Merge 400 YES + 400 NO
  → Recover 400 USDC.e
  → Remaining: 0 YES, 1200 NO

Day 30: Market resolves — NO wins (BTC didn't hit $150k)

Action 3: REDEEM
  → Redeem 1200 NO tokens
  → Receive 1200 USDC.e

Total in: 1000 USDC.e (initial split)
Total out: $180 (YES sales) + $400 (merge) + $1200 (redeem) = $1780
Profit: $780 (78% return)
```

---

### 5.5 Summary Table

| Operation | Input | Output | On-chain? | Timing |
|-----------|-------|--------|-----------|--------|
| **Split** | USDC.e | YES + NO tokens (equal amounts) | Yes | Anytime market is live |
| **Merge** | YES + NO tokens (equal amounts) | USDC.e | Yes | Anytime market is live |
| **Redeem** | Winning tokens | USDC.e | Yes | Only after resolution |
| **Trade (buy)** | USDC.e | YES or NO tokens | Via CLOB | Anytime market is live |
| **Trade (sell)** | YES or NO tokens | USDC.e | Via CLOB | Anytime market is live |

---

## 6. Market Making on Polymarket — How It Really Works

### 6.1 The Core Business Model

A market maker makes money by **capturing the spread** — repeatedly buying at the bid price and selling at the ask price:

```
Round Trip Example:
  Buy 100 YES at $0.48  →  Cost: $48.00
  Sell 100 YES at $0.52 →  Revenue: $52.00
  Profit: $4.00 (8.3% on capital deployed)
```

The market maker does not need to predict who wins. They profit from the *difference between bid and ask*, multiplied by volume.

### 6.2 Two-Sided Quoting

A market maker simultaneously quotes BOTH sides:

```
Market: "Will Biden win 2024 election?"
Current probability estimate (fair value): 0.45

Market Maker's Quotes:
  BUY YES at $0.43  (2 cents below fair value)
  SELL YES at $0.47  (2 cents above fair value)
  — spread = $0.04, centered on $0.45

Equivalently (since YES + NO = $1):
  SELL NO at $0.57  (= 1 - 0.43)
  BUY NO at $0.53   (= 1 - 0.47)
```

When both sides get filled, profit = spread × size (minus any inventory accumulation risk).

### 6.3 What "Fair Value" Means

The market maker doesn't predict outcomes — they track the **midpoint** of the current order book as a proxy for fair value. More sophisticated approaches use:
- External price feeds (e.g., Chainlink for BTC price)
- Bayesian probability models
- News sentiment
- On-chain flow data

### 6.4 The Risks

| Risk | Description | Mitigation |
|------|-------------|------------|
| **Adverse selection** | A better-informed trader fills your order and the price immediately moves against you | Widen spreads, monitor flows |
| **Inventory accumulation** | You keep accumulating one side as price trends against you | Inventory skewing, position limits |
| **Resolution risk** | Holding large position when market resolves against you | Merge excess inventory, hedge on other platforms |
| **Liquidity risk** | Can't exit a large position quickly | Split/merge for capital efficiency |
| **Oracle risk** | Market resolves in unexpected way (disputed) | Diversify across many markets |

### 6.5 Why Be a Market Maker on Polymarket vs Traditional Exchanges?

| Factor | Polymarket | Traditional Exchange |
|--------|-----------|---------------------|
| Maker fees | **$0** | Usually 0.01–0.05% |
| Maker rebates | **Yes (USDC)** | Sometimes |
| Position limits | Soft (risk-based) | Hard (regulatory) |
| Settlement | Blockchain (irreversible) | Central counterparty |
| Market types | Binary (YES/NO) | Continuous prices |
| Capital efficiency | High (split/merge) | Standard |
| Regulatory overhead | Low (prediction market) | High |

---

## 7. The "Zero Price / Zero Bought / Positive P&L" Mystery Explained

This is one of the most confusing things to see when browsing Polymarket user profiles, especially in the BTC Up/Down positions tab.

### 7.1 What You're Seeing

When you visit another user's profile and look at their positions in a BTC Up/Down market, you may see:

```
Position Details:
  Average Price: $0.00
  Amount Bought: $0.00
  Positions Value: $X.XX   (some positive amount)
  P&L: +$Y.YY              (positive)

Profile Activity:
  Total P&L: (empty)
  Closed Positions: (empty)
  Activity: (empty)
```

This looks paradoxical. How can someone have a positive P&L with zero invested?

### 7.2 The Explanation — They Are Market Makers Using the API

These are **programmatic market makers** who primarily operate through the CLOB API, not the web UI. Here's exactly what's happening:

#### Reason 1: Split-Acquired Inventory (Zero UI Cost Basis)

The market maker splits USDC.e directly via the CTF smart contract (not through a buy order). When the UI calculates "Average Price" and "Amount Bought," it only tracks **CLOB order fills** — it does NOT track tokens received via direct CTF splits.

```
Market Maker's Actual Steps:
  1. Calls CTF.splitPosition(1000 USDC.e)
     → Gets 1000 YES + 1000 NO tokens
     → UI shows: bought $0, avg price $0 (split is not a "buy")

  2. Places sell orders for both YES and NO via CLOB
     → Sells YES at various prices, accumulates USDC
     → UI still shows avg price $0 for the remaining NO tokens

  3. NO tokens remain in wallet
     → UI shows "Positions Value" = 300 NO × current NO price
     → UI shows "P&L" based on current value vs $0 cost basis = pure profit
```

The key insight: **CTF splits are not recorded as purchases in the UI's cost basis calculations.** The tokens appear to have been acquired for free.

#### Reason 2: Realized Profit Already Withdrawn

Market makers frequently merge their paired positions and withdraw USDC to trading capital:

```
Original: Split 1000 USDC.e → 1000 YES + 1000 NO
Trading:  Sold 600 YES at avg $0.35 = $210 revenue (YES fills reduce YES holdings)
          Received 400 extra NO via taker fills buying NO from you
Holdings: 400 YES remaining, 1400 NO total

After merge: Merge 400 YES + 400 NO → recover 400 USDC.e
Remaining: 0 YES, 1000 NO tokens (cost basis = $0 by UI logic)

UI view:
  Amount Bought: $0
  Avg Price: $0
  Positions Value: 1000 × current_NO_price
  P&L: +positive (all value appears as pure gain)
```

#### Reason 3: The Empty Profile Problem

The profile looks mostly empty because:

1. **Activity tab**: Only shows UI-initiated transactions. API-based splits, merges, and batch orders via the CLOB API don't always populate the UI activity feed the same way.

2. **Total P&L tab**: This aggregates closed positions. Market makers who operate via API may resolve positions off-chain (merge back to USDC) in ways the UI doesn't track as "closed positions."

3. **Closed Positions tab**: Shows history of positions that resolved when a market ended. Active market makers often exit positions via merge BEFORE market resolution (to recover capital), so few "closed positions" appear.

4. **Only "Positions Value" shows**: The one thing that IS visible is current open ERC-1155 token holdings, because those are on-chain and queryable directly from the blockchain — the UI can't hide them.

### 7.3 Who Are These People?

In 99% of cases, they are one of:

1. **Official Polymarket-affiliated market makers**: Large LPs contracted to provide liquidity, operating institutional-scale bots with millions in capital.

2. **Professional algorithmic traders**: Individuals or small firms running the official `poly-market-maker` bot (GitHub: `Polymarket/poly-market-maker`) or custom forks.

3. **Liquidity farming bots**: Traders running delta-neutral strategies (quote both YES and NO) purely to earn the daily USDC liquidity rewards without taking directional risk.

4. **Arbitrageurs**: Traders who exploit price discrepancies between YES/NO tokens (the $1 invariant) or between Polymarket and external price feeds.

### 7.4 How to Confirm (Investigate Any Wallet)

To see the true picture of any wallet on Polymarket:

```bash
# Get all open positions (what the UI shows)
curl "https://data-api.polymarket.com/positions?user=0xWALLET_ADDRESS"

# Get closed/resolved positions
curl "https://data-api.polymarket.com/closed-positions?user=0xWALLET_ADDRESS"

# Get all activity (trades, splits, merges, redemptions)
curl "https://data-api.polymarket.com/activity?user=0xWALLET_ADDRESS"

# Get portfolio total value
curl "https://data-api.polymarket.com/value?user=0xWALLET_ADDRESS"
```

You can also look up the wallet on **Polygonscan** (`https://polygonscan.com/address/0xWALLET`) to see all raw ERC-1155 token transfers, including splits and merges.

### 7.5 Can You Do This Too? (Yes)

If you want to replicate this approach:

1. **For liquidity rewards**: Set up a bot that quotes both YES and NO simultaneously (delta-neutral). Your P&L comes from rewards, not from predicting outcomes.

2. **For spread capture**: Run the market maker bot, which continuously splits, quotes, and merges. Your "cost basis" in the UI will appear to be $0 for split-derived inventory.

3. **Capital efficiency trick**: Split $1000 USDC → 1000 YES + 1000 NO. Sell the side you expect to be "wrong." If NO wins, your NO tokens redeem at $1 each (you recover your $1000). If YES wins, you sell YES tokens early, buy NO cheaply, merge, and recover capital plus profit.

---

## 8. BTC Up/Down Markets — 5-Minute and 15-Minute

### 8.1 What Are These Markets?

BTC Up/Down markets are **ultra-short-duration prediction markets** where you predict the price direction of Bitcoin over a fixed interval. They are Polymarket's highest-frequency markets.

| Market Type | Duration | Resolution | Oracle |
|-------------|----------|------------|--------|
| BTC 5M Up/Down | 5 minutes | End-of-interval price | Chainlink BTC/USD |
| BTC 15M Up/Down | 15 minutes | End-of-interval price | Chainlink BTC/USD |

### 8.2 How Resolution Works

```
Market: "BTC Up or Down — 3:00 PM to 3:05 PM"

Start price (3:00:00 PM): $45,000.00
End price   (3:04:59 PM): $45,150.00

Result: UP (+$150 from open)
  → UP tokens: $1.00 each (winners)
  → DOWN tokens: $0.00 (losers)
```

The oracle is **Chainlink's decentralized BTC/USD price feed** — this ensures no manipulation by Polymarket or any single party.

### 8.3 Why Market Makers Dominate These Markets

5-minute markets are **perfectly suited for algorithmic market making** because:

1. **Rapid resolution** = fast capital turnover (market makers don't need to lock up capital for long)
2. **High volume** = more spread opportunities per day
3. **Fee structure** = taker fees go to maker rebates, so MMs earn more
4. **Predictable timing** = bots can time quote placement/withdrawal precisely

### 8.4 How to Trade BTC 5M/15M Markets

**As a directional trader:**
```
You think BTC will go UP in the next 5 minutes:
  → Buy UP tokens
  → If UP wins: get $1 per token (profit = $1 - entry price)
  → If DOWN wins: token expires worthless (loss = entry price)

Example:
  Buy 100 UP tokens at $0.55 = $55 invested
  BTC goes up → 100 × $1.00 = $100 received
  Profit: $45 (81.8% return in 5 minutes)
```

**As a market maker (delta-neutral):**
```
Quote both sides around midpoint:
  BUY UP at $0.48, SELL UP at $0.52
  BUY DOWN at $0.48, SELL DOWN at $0.52

  (Remember: UP_price + DOWN_price = $1 always)
  When UP = $0.50, DOWN = $0.50 — symmetric market

Earn spread on fills + daily maker rebates
```

### 8.5 Strategy Notes for BTC Markets

| Strategy | Approach | Risk Level |
|----------|----------|------------|
| Delta-neutral MM | Quote both UP and DOWN symmetrically | Low (spread income + rebates) |
| Momentum | Buy the side trending via Chainlink feed | Medium |
| Fade the crowd | Sell the overbought side when pricing is extreme | High |
| Arbitrage | Cross-market vs Binance/Coinbase futures | Very High (latency-sensitive) |

---

## 9. Setting Up a Market Maker Bot — Complete Guide

### 9.1 Prerequisites

```
✓ Python 3.11+
✓ Polygon wallet (funded with USDC.e and MATIC)
✓ Polymarket account (for API credential generation)
✓ Docker (optional but recommended)
✓ VPS or cloud server for 24/7 operation
```

**Wallet Funding:**
- At minimum $500–$1,000 USDC.e to make meaningful spreads
- ~5–10 MATIC for gas fees (though gasless flow is available via relayer)
- Bridge from Ethereum: https://wallet.polygon.technology/

### 9.2 Option A: Official Polymarket Market Maker Bot

The official bot is at: `https://github.com/Polymarket/poly-market-maker`

```bash
# Clone repository
git clone https://github.com/Polymarket/poly-market-maker.git
cd poly-market-maker

# Install dependencies
pip install -r requirements.txt
```

**Create your `.env` file:**
```env
# ========== REQUIRED ==========
PRIVATE_KEY=your_wallet_private_key_here

# Polymarket API credentials (get these from the Polymarket UI)
CLOB_API_KEY=your_api_key
CLOB_SECRET=your_api_secret
CLOB_PASS_PHRASE=your_api_passphrase

# Which market to make on (conditionId from the market URL)
CONDITION_ID=0xabc123...

# Strategy type: "bands" or "amm"
STRATEGY=bands

# Strategy config file path
STRATEGY_CONFIG=config/bands_config.json

# ========== OPTIONAL ==========
# Polygon RPC (defaults work, but use your own for reliability)
POLYGON_RPC_URL=https://polygon-rpc.com

# CLOB API URL (default: production)
CLOB_HOST=https://clob.polymarket.com

# Chain ID (137 = Polygon mainnet)
CHAIN_ID=137
```

**Generate API credentials (one-time setup):**
```python
from py_clob_client.client import ClobClient

# Initialize with just private key first
client = ClobClient(
    host="https://clob.polymarket.com",
    chain_id=137,
    key="YOUR_PRIVATE_KEY"
)

# Create API credentials (signs with your wallet)
creds = client.create_or_derive_api_creds()
print(f"API Key: {creds.api_key}")
print(f"API Secret: {creds.api_secret}")
print(f"Passphrase: {creds.api_passphrase}")
# Save these to your .env file
```

**Run the bot:**
```bash
# Standard run
python -m main

# With Docker
docker-compose up -d

# Check logs
docker-compose logs -f
```

### 9.3 Option B: Community Bot (lorine93s/polymarket-market-maker-bot)

A popular, well-documented community fork with additional features:

```bash
git clone https://github.com/lorine93s/polymarket-market-maker-bot.git
cd polymarket-market-maker-bot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
python src/main.py
```

### 9.4 How the Bot Cycle Works

Every 30 seconds (configurable), the bot runs this cycle:

```
┌─────────────────────────────────────────────────────┐
│                  BOT CYCLE (every 30s)              │
├─────────────────────────────────────────────────────┤
│ 1. Fetch current CLOB order book via WebSocket      │
│    → Get best bid, best ask, midpoint               │
├─────────────────────────────────────────────────────┤
│ 2. Fetch current open orders (your orders on book)  │
│    → Identify stale orders (outside acceptable band)│
├─────────────────────────────────────────────────────┤
│ 3. Cancel stale orders                              │
│    → Batch cancel API call                         │
├─────────────────────────────────────────────────────┤
│ 4. Calculate new target prices                      │
│    → Based on strategy (bands or AMM)              │
│    → Apply inventory skew if needed                │
├─────────────────────────────────────────────────────┤
│ 5. Place new orders                                 │
│    → Batch post (up to 15 orders/request)          │
│    → GTC orders at calculated prices               │
├─────────────────────────────────────────────────────┤
│ 6. Update inventory tracking                        │
│    → Track fills, update position size             │
│    → Trigger splits/merges if thresholds crossed   │
└─────────────────────────────────────────────────────┘
```

### 9.5 Finding Your Market's conditionId

Every market has a `conditionId` (bytes32 hash). You can find it:

1. **Via Polymarket URL**: Go to the market, look at the URL — markets list their event slug
2. **Via Gamma API**:
```bash
# Search for BTC 15-minute market
curl "https://gamma-api.polymarket.com/markets?search=btc+15+minute"
# Response includes conditionId field
```

3. **Via Data API**:
```bash
curl "https://data-api.polymarket.com/markets?limit=10&sort=volume"
# Returns markets with conditionIds
```

### 9.6 Approvals Required (One-Time Setup)

Before the bot can trade, you must approve the CTF and CLOB exchange contracts to spend your tokens:

```python
from py_clob_client.client import ClobClient

client = ClobClient(...)

# Approve USDC spending for CTF contract (for splits)
# Approve CTF token spending for CLOB exchange (for selling)
# These are one-time on-chain transactions

await client.approve_collateral()   # USDC.e → CTF
await client.approve_conditional_tokens()  # YES/NO → CLOB
```

---

## 10. Bands Strategy — Deep Dive

The Bands strategy is the recommended approach for most market makers. It places multiple limit orders at different price levels around the midpoint, creating a "ladder" of liquidity.

### 10.1 How Bands Work

```
Midpoint: $0.50

Band 1 (tightest):
  Buy at: $0.49  (1 cent below midpoint)
  Sell at: $0.51 (1 cent above midpoint)
  Size: 200 shares each side

Band 2 (medium):
  Buy at: $0.47  (3 cents below midpoint)
  Sell at: $0.53 (3 cents above midpoint)
  Size: 400 shares each side

Band 3 (widest):
  Buy at: $0.44  (6 cents below midpoint)
  Sell at: $0.56 (6 cents above midpoint)
  Size: 800 shares each side
```

Result: A symmetric order book that provides deep liquidity:

```
ASK SIDE (Sell orders):
  $0.56 x 800  ← Band 3
  $0.53 x 400  ← Band 2
  $0.51 x 200  ← Band 1
  ─────────────── SPREAD
  $0.49 x 200  ← Band 1
  $0.47 x 400  ← Band 2
  $0.44 x 800  ← Band 3
BID SIDE (Buy orders):
```

### 10.2 Band Configuration File

```json
{
  "strategy": "bands",
  "targetPrice": "midpoint",
  "bands": [
    {
      "minMargin": 0.01,
      "avgMargin": 0.01,
      "maxMargin": 0.015,
      "minSize": 100,
      "avgSize": 200,
      "maxSize": 300
    },
    {
      "minMargin": 0.02,
      "avgMargin": 0.03,
      "maxMargin": 0.04,
      "minSize": 200,
      "avgSize": 400,
      "maxSize": 600
    },
    {
      "minMargin": 0.05,
      "avgMargin": 0.06,
      "maxMargin": 0.07,
      "minSize": 400,
      "avgSize": 800,
      "maxSize": 1200
    }
  ]
}
```

**Parameters explained:**
- `minMargin / maxMargin`: Price range from midpoint where orders in this band should be (e.g., 0.01 = 1 cent)
- `minSize / maxSize`: Target order size range in shares (the bot adjusts orders to stay within this range)
- `avgSize`: Target "steady state" size per band

### 10.3 Band Order Management Logic

For each band, every cycle:

```
IF current_size > maxSize:
    Cancel excess orders until current_size = avgSize

IF current_size < minSize:
    Post new orders until current_size = avgSize

IF midpoint moved significantly:
    Cancel all orders outside acceptable range
    Repost at new midpoint-relative prices
```

### 10.4 Why Multiple Bands?

- **Band 1** (tight): Captures most fills, earns maximum rebates (highest volume at best prices)
- **Band 2** (medium): Backup liquidity when price moves 2-3%
- **Band 3** (wide): Protection/backstop — rarely fills but prevents running out of liquidity in volatile markets

---

## 11. AMM Strategy — Deep Dive

The AMM strategy mimics a constant-product automated market maker (like Uniswap) but implemented as CLOB limit orders.

### 11.1 AMM Price Curve

Instead of discrete bands, the AMM places orders along a continuous curve:

```
For a constant product AMM with k = x × y:
  If YES reserve = 1000, NO reserve = 1000 (k = 1,000,000)
  
  To buy 100 YES:
    New YES reserve = 900
    New NO reserve = k / 900 = 1,111
    Cost = 1,111 - 1,000 = 111 NO tokens (effective price = 111 NO / 100 YES = 1.11 NO per YES)
```

Applied to Polymarket (where prices are between 0 and 1):
- Orders are placed at prices derived from the AMM curve formula
- The curve naturally widens the spread near extremes (0% or 100% probability) and tightens near 50%

### 11.2 AMM Config

```json
{
  "strategy": "amm",
  "minPrice": 0.02,
  "maxPrice": 0.98,
  "spread": 0.04,
  "size": 500
}
```

**Parameters:**
- `minPrice / maxPrice`: Price range the bot will actively quote in (avoids extreme prices)
- `spread`: Minimum spread percentage maintained
- `size`: Total liquidity deployed per side

### 11.3 AMM vs Bands Comparison

| Feature | Bands | AMM |
|---------|-------|-----|
| Setup complexity | Higher (configure each band) | Lower (few parameters) |
| Granular control | High (per-band sizing) | Low (curve determines it) |
| Behavior at extremes | Configurable | AMM naturally widens spread |
| Good for | Volatile, illiquid markets | Stable, balanced markets |
| Capital efficiency | Very high | High |
| Adverse selection protection | Better (can widen specific bands) | Weaker |

---

## 12. Inventory Management — The Core Skill

Inventory management is what separates profitable market makers from those who lose. It's about controlling HOW MUCH of each side you hold at any time.

### 12.1 Why Inventory Accumulation Is Dangerous

```
Scenario: Market starts at YES = $0.50

Round 1: You quote $0.48 / $0.52
  → Taker buys from your ask (they take YES at $0.52)
  → You now hold NO tokens (inventory)

Round 2: YES falls to $0.48
  → More takers hit your bids (they sell YES to you)
  → You now hold MORE YES tokens

Round 3: YES falls to $0.45
  → Your YES inventory is losing value
  → If YES keeps falling to $0, you lose everything
```

The core risk: when you accumulate one side, you have directional exposure.

### 12.2 Inventory Skewing

The solution is to **skew your quotes away from the side you're overexposed to**:

```python
def calculate_skewed_quotes(fair_value, spread, inventory, max_inventory):
    """
    If long YES (positive inventory), shift quotes UP to sell more YES
    If long NO (negative inventory), shift quotes DOWN to sell more NO
    """
    imbalance = inventory / max_inventory  # -1 to +1
    skew = imbalance * spread * 0.5       # shift by up to half the spread
    
    bid = fair_value - (spread / 2) - skew  # shifted bid
    ask = fair_value + (spread / 2) - skew  # shifted ask
    
    return bid, ask

# Example: Long 200 YES, max position 500, fair value $0.50, spread $0.04
# imbalance = 200/500 = 0.4
# skew = 0.4 * 0.04 * 0.5 = 0.008
# bid = 0.50 - 0.02 - 0.008 = 0.472  (lower bid → less buying)
# ask = 0.50 + 0.02 - 0.008 = 0.512  (lower ask → more selling)
```

### 12.3 Merge-Based Capital Management

Smart market makers use merge strategically to recycle capital:

```
Scenario: After trading, holding:
  800 YES (cost basis: bought at avg $0.42 = $336 total)
  1200 NO (acquired via splits and fills)

Strategy:
  1. Merge 800 YES + 800 NO → receive 800 USDC.e
  2. Remaining: 0 YES, 400 NO (pure inventory)
  3. Redeploy USDC.e: split again or use directly for new orders

Capital recovered: $800 vs $336 invested in that YES → $464 locked in profit
Remaining risk: 400 NO tokens × current NO price
```

### 12.4 Position Limits and Risk Management

```python
# Example risk parameters (from config)
MAX_POSITION_USD = 500      # Maximum value of single-side inventory
DAILY_LOSS_LIMIT = 100      # Stop trading if daily loss exceeds $100
MAX_DRAWDOWN_PCT = 20       # Stop if portfolio drops 20% from peak
SPREAD_MULTIPLIER = 1.0     # Widen spread in volatile markets

# Risk check before placing orders
def should_trade(current_inventory, daily_loss, peak_value, current_value):
    if abs(current_inventory) > MAX_POSITION_USD:
        return False, "Position limit exceeded"
    if daily_loss > DAILY_LOSS_LIMIT:
        return False, "Daily loss limit hit"
    drawdown = (peak_value - current_value) / peak_value * 100
    if drawdown > MAX_DRAWDOWN_PCT:
        return False, "Max drawdown exceeded"
    return True, "OK"
```

---

## 13. Liquidity Rewards and Maker Rebates Program

### 13.1 Two Types of Incentives

Polymarket has two distinct programs, often confused:

| Program | Markets | How You Earn | Payout |
|---------|---------|-------------|--------|
| **Liquidity Rewards** | Most prediction markets | Post orders near midpoint (even unfilled) | Daily USDC from pool |
| **Maker Rebates** | 5m/15m crypto, select sports | Orders must be FILLED (taker takes your order) | Daily USDC from taker fees |

### 13.2 Liquidity Rewards Details

```
Eligibility criteria for each order:
  ✓ Within X% of current midpoint
  ✓ Two-sided quote (must quote both YES and NO)
  ✓ Minimum order size (typically 25 shares)
  ✓ Must stay on book for minimum time (anti-spam)

Reward calculation (approximate):
  Score = size × time_on_book × (1 - distance_from_midpoint)
  Your share = Your score / Sum of all scores × Daily pool
```

**Example calculation:**
```
Market: "Will X happen by 2025?"
Daily reward pool: $150

Your orders:
  YES: 500 shares @ $0.48 (2 cents from midpoint $0.50)
  NO: 500 shares @ $0.52 (2 cents from midpoint)
  Time on book: 18 hours

Your score contribution: 500 × 18h × (1 - 0.02/0.50) = 8,280 "score units"
Total market score: 200,000 score units

Your daily reward: (8,280 / 200,000) × $150 = $6.21/day
```

### 13.3 Maker Rebates (5m/15m Markets) Details

```
How taker fees fund rebates:
  Taker buys 1000 YES at $0.50 (midpoint)
  Taker fee: 1.56% × $500 = $7.80 in fees
  Rebate pool gets: 20% × $7.80 = $1.56

  If your order was the one filled (you were the maker):
  Your rebate: $1.56 × (your volume / total maker volume today)
```

### 13.4 Delta-Neutral Strategy to Earn Rewards Risk-Free

The goal is to earn rewards without taking directional risk:

```python
# Delta-neutral market making
# Quote both sides equally — no net directional exposure

def delta_neutral_quotes(midpoint, spread_size):
    """
    Place equal-size quotes on both sides.
    P&L = rewards earned - spread losses (usually positive)
    """
    yes_bid = midpoint - spread_size / 2
    yes_ask = midpoint + spread_size / 2
    
    no_bid = (1 - midpoint) - spread_size / 2   # NO price is 1 - YES price
    no_ask = (1 - midpoint) + spread_size / 2
    
    # Post orders
    orders = [
        {"side": "BUY",  "token": "YES", "price": yes_bid, "size": 500},
        {"side": "SELL", "token": "YES", "price": yes_ask, "size": 500},
        {"side": "BUY",  "token": "NO",  "price": no_bid,  "size": 500},
        {"side": "SELL", "token": "NO",  "price": no_ask,  "size": 500},
    ]
    return orders
```

**Risk with this approach**: If price moves sharply (e.g., breaking news), you could fill on the wrong side before you cancel. Always use stop-losses.

---

## 14. Analytics Tools and Resources

### 14.1 Official Analytics

| Tool | URL | Purpose |
|------|-----|---------|
| Polymarket Data API | `https://data-api.polymarket.com` | Raw positions, P&L, activity |
| Polymarket Gamma API | `https://gamma-api.polymarket.com` | Market metadata |
| Polygonscan | `https://polygonscan.com` | On-chain verification |

### 14.2 API Endpoints Reference

```bash
# Get user positions (open)
GET https://data-api.polymarket.com/positions?user={wallet_address}

# Get closed positions (history)
GET https://data-api.polymarket.com/closed-positions?user={wallet_address}

# Get user activity (all events)
GET https://data-api.polymarket.com/activity?user={wallet_address}

# Get portfolio value
GET https://data-api.polymarket.com/value?user={wallet_address}

# Get order book for a market
GET https://clob.polymarket.com/book?token_id={token_id}

# Get market price history
GET https://clob.polymarket.com/prices-history?market={condition_id}&interval=1h

# Get current midpoint
GET https://clob.polymarket.com/midpoint?token_id={token_id}

# List markets
GET https://gamma-api.polymarket.com/markets?limit=20&sort=volume
```

### 14.3 Community Tools

| Tool | URL | Purpose |
|------|-----|---------|
| PredictFolio | https://predictfolio.com | Portfolio tracking |
| Hashdive | https://www.hashdive.com | P&L leaderboard |
| Polyfolio | https://azariak.github.io/Polyfolio | Open-source tracker |
| Polymarket Trade Tracker | https://github.com/leolopez007/polymarket-trade-tracker | Custom analysis |
| GuruPolymarket | https://gurupolymarket.com | Tutorials + analytics |
| Polyblock | https://polyblock.trade | Developer guides + stats |

### 14.4 Monitoring Your Bot

```python
# Simple monitoring script
import requests
import time

WALLET = "0xYourWalletAddress"

def check_positions():
    # Current open positions
    positions = requests.get(
        f"https://data-api.polymarket.com/positions?user={WALLET}"
    ).json()
    
    total_value = sum(p["currentValue"] for p in positions)
    print(f"Open positions: {len(positions)}, Total value: ${total_value:.2f}")
    
    # Check for any unusual concentrations
    for p in positions:
        if p["currentValue"] > 500:
            print(f"⚠️  Large position: {p['title']} = ${p['currentValue']:.2f}")

def check_orders():
    # Orders currently on the CLOB
    # Requires authenticated CLOB client
    pass

while True:
    check_positions()
    time.sleep(60)
```

---

## 15. Quick Reference — Smart Contract Addresses

| Contract | Address (Polygon Mainnet) |
|----------|--------------------------|
| CTF Exchange | `0x4D97DCd97eC945f40cF65F87097ACe5EA0476045` |
| USDC.e | `0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174` |
| Neg Risk CTF Exchange | `0xC5d563A36AE78145C45a50134d48A1215220f80a` |
| Neg Risk Adapter | `0xd91E80cF2E7be2e162c6513ceD06f1dD0dA35296` |

> **Note:** Always verify contract addresses via the official Polymarket documentation (`docs.polymarket.com`) before interacting with them. Never send funds to unverified contracts.

---

## Appendix A: Common Questions

### "Can I lose money market making?"

Yes. The main risk is **adverse selection and inventory accumulation**:
- If you're consistently filled when wrong (price moves against you after fill), you'll accumulate losing positions
- A news event that moves the market sharply before you cancel orders can cause large losses
- Always use position limits and daily loss limits

### "How much capital do I need?"

- Minimum viable: **$500 USDC.e** (any less and spread income doesn't cover the effort)
- Recommended starting: **$2,000–$5,000 USDC.e**
- Professional level: **$50,000+**

At $1,000 with a 1-cent spread on 5m BTC markets, you might earn $5–$30/day in liquidity rewards depending on market competition. Rewards scale approximately linearly with capital.

### "Do I need to understand blockchain to run this?"

Not deeply. The bot handles all on-chain interactions automatically. You need to:
1. Create a Polygon wallet (MetaMask works fine)
2. Fund it with USDC.e and a small amount of MATIC
3. Generate API credentials once
4. Configure and run the bot

### "How do I get my conditionId?"

```bash
# Method 1: Gamma API search
curl "https://gamma-api.polymarket.com/markets?search=btc+15+up+down&limit=5"
# Look for "conditionId" in the response

# Method 2: Look at the order book URL
# Market URL: https://polymarket.com/event/btc-15m-up-down-XYZ
# Get orderbook: https://clob.polymarket.com/book?token_id=TOKEN_ID
```

### "What is a proxy wallet / Safe?"

Polymarket uses **proxy wallets** (based on Gnosis Safe) for security. When you connect your EOA (regular wallet) to Polymarket:
1. A new proxy wallet is created and linked to your EOA
2. Trades happen through the proxy wallet
3. Your EOA signs transaction requests but isn't directly exposed

The proxy wallet address is what shows up in Polymarket profiles and on-chain.

### "Why does my bot need MATIC?"

Gas fees on Polygon are paid in MATIC. While Polymarket offers a "gasless" option (meta-transactions via their relayer), having your own MATIC gives you:
- Independence from the relayer
- Ability to call CTF contracts directly (split/merge)
- Faster transactions in congested periods

~0.5 MATIC is usually sufficient for several weeks of bot operation.

---

## Appendix B: Key Formulas

### Spread P&L (per round trip)
```
Profit per round trip = spread × size
Example: 2-cent spread on 500 shares = $0.02 × 500 = $10
```

### Inventory Imbalance
```
Imbalance = (YES_holdings - NO_holdings) / max_position
Range: -1.0 (max long NO) to +1.0 (max long YES)
```

### Skew Formula
```
quote_shift = imbalance × spread × skew_factor
bid = midpoint - half_spread - quote_shift
ask = midpoint + half_spread - quote_shift
```

### Taker Fee Curve (5m/15m markets)
```
fee_rate = max_fee × 4 × p × (1 - p)
where p = probability (price) of the outcome (0 to 1)

At p=0.50: fee_rate = 1.56% × 4 × 0.5 × 0.5 = 1.56% (maximum)
At p=0.10: fee_rate = 1.56% × 4 × 0.1 × 0.9 = 0.56%
At p=0.01: fee_rate = 1.56% × 4 × 0.01 × 0.99 ≈ 0.06%
```

### Liquidity Reward Scoring (approximate)
```
score_i = Σ_j (size_j × time_j × proximity_weight_j)
proximity_weight = max(0, 1 - |price - midpoint| / midpoint)

daily_reward_i = (score_i / Σ_all score) × daily_pool
```

---

## Appendix C: Glossary

| Term | Definition |
|------|------------|
| **CLOB** | Central Limit Order Book — a price-time priority matching engine |
| **CTF** | Conditional Token Framework — Gnosis's smart contract for prediction market tokens |
| **ERC-1155** | Ethereum token standard for multi-token contracts; Polymarket uses this for YES/NO tokens |
| **Maker** | Trader who posts limit orders to the book, adding liquidity |
| **Taker** | Trader who immediately fills against existing orders, removing liquidity |
| **Split** | CTF operation: convert USDC.e → equal YES + NO tokens |
| **Merge** | CTF operation: convert equal YES + NO tokens → USDC.e |
| **Redeem** | CTF operation: burn winning tokens for USDC.e after market resolution |
| **conditionId** | Bytes32 hash uniquely identifying a Polymarket market |
| **positionId** | ERC-1155 token ID for a specific outcome in a specific market |
| **Midpoint** | Average of best bid and best ask; used as "fair value" estimate |
| **Spread** | Difference between best ask and best bid; market maker earns this per round trip |
| **Inventory skew** | Adjusting bid/ask prices to reduce exposure on the over-held side |
| **Delta-neutral** | Holding equal value of YES and NO so market direction doesn't affect P&L |
| **Proxy wallet** | Gnosis Safe-based wallet created by Polymarket for each user account |
| **Adverse selection** | Risk that the counterparty is better-informed and the price moves against you after fill |
| **GTC** | Good-Til-Cancelled — order type that stays on book until manually removed |
| **FOK** | Fill-or-Kill — must fill entirely right now or cancel |
| **FAK** | Fill-and-Kill — fill as much as possible now, cancel the rest |
| **Neg Risk Market** | A special Polymarket market structure where outcomes are mutually exclusive (e.g., "which candidate wins?") |
| **USDC.e** | Bridged USDC on Polygon, the collateral token for all Polymarket positions |

---

*Last updated: March 2026 | Sources: Polymarket official docs (docs.polymarket.com), GitHub repositories (github.com/Polymarket), community guides, and on-chain analysis.*
