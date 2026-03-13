# OpenClaw Deep Research — Can It Really Make Money on Polymarket?

> **Last updated:** March 13, 2026  
> **Scope:** Deep research on OpenClaw AI, its capabilities, GitHub ecosystem, and real-world Polymarket trading performance  
> **Related doc:** [`PRD-polymarket-btc-trading-bot.md`](./PRD-polymarket-btc-trading-bot.md) for our custom bot strategy

---

## Table of Contents

1. [Executive Summary & Verdict](#1-executive-summary--verdict)
2. [What Is OpenClaw?](#2-what-is-openclaw)
3. [GitHub Ecosystem](#3-github-ecosystem)
4. [PolyClaw — The Polymarket Trading Skill](#4-polyclaw--the-polymarket-trading-skill)
5. [Documented Earnings — The Headline Numbers](#5-documented-earnings--the-headline-numbers)
6. [How the Profitable Bots Actually Work](#6-how-the-profitable-bots-actually-work)
7. [Security Risks — The Dark Side](#7-security-risks--the-dark-side)
8. [OpenClaw vs Custom Bot — Honest Comparison](#8-openclaw-vs-custom-bot--honest-comparison)
9. [Can It Really Help Us Make Money on Polymarket?](#9-can-it-really-help-us-make-money-on-polymarket)
10. [How to Get Started (If You Decide to Use It)](#10-how-to-get-started-if-you-decide-to-use-it)
11. [Final Conclusion & Recommendation](#11-final-conclusion--recommendation)
12. [Research Sources](#12-research-sources)

---

## 1. Executive Summary & Verdict

**Yes, OpenClaw is a legitimate open-source AI agent framework that has been used to build highly profitable Polymarket trading bots — but the headline numbers ($115K/week, $116K/day) are extreme outliers achieved with large capital, sophisticated strategies, and significant technical expertise. The average user will NOT replicate those results.**

### The Honest Truth

| Claim | Reality |
|---|---|
| "People are making thousands daily" | ✅ True for a few sophisticated operators with large capital ($50K-$500K+) |
| "OpenClaw makes it easy" | ⚠️ Partially true — PolyClaw skill works, but profitable trading requires deep market knowledge |
| "It's risk-free money" | ❌ False — only ~30% of Polymarket wallets are profitable long-term |
| "The software is safe" | ⚠️ The core is MIT-licensed and reputable, but **341+ malicious skills** have been found in the marketplace |
| "Anyone can do it" | ❌ False — requires coding skills, market knowledge, and robust security practices |

### Bottom Line for Our Project

OpenClaw is **genuinely useful** for Polymarket trading, but as an **infrastructure tool**, not a magic money printer. The PolyClaw skill specifically provides production-ready market browsing, trade execution, hedge discovery, and position tracking that could **accelerate our custom bot development by 2-4 weeks**. However, we should use it as a reference/component rather than blindly trusting third-party automation with our funds.

---

## 2. What Is OpenClaw?

### Overview

OpenClaw is an **open-source, self-hosted, autonomous AI agent framework** that runs on your own devices. Unlike typical chatbots, it can actually execute tasks — browse the web, run shell commands, manage files, control applications, and interact with APIs autonomously.

### Core Identity

| Attribute | Detail |
|---|---|
| **Type** | Autonomous AI agent framework |
| **License** | MIT (fully open source) |
| **Runtime** | Node.js (npm package) |
| **Platforms** | macOS, Windows, Linux, iOS, Android |
| **Architecture** | Local-first, privacy-focused, model-agnostic |
| **Install** | `npm install -g openclaw@latest` |
| **Website** | [openclaw.ai](https://openclaw.ai/) |
| **Docs** | [docs.openclaw.ai](https://docs.openclaw.ai/) |

### Key Capabilities

#### 1. Multi-Channel Messaging Gateway
Connects to **20+ messaging platforms** as a unified AI assistant:
- WhatsApp, Telegram, Discord, Slack, Signal, iMessage, Microsoft Teams, Matrix, IRC, and more
- Single gateway handles all channels — your AI responds everywhere

#### 2. Autonomous Task Execution
- Receives tasks, breaks them into steps, plans, invokes tools, and executes
- Persistent memory across sessions — learns preferences over time
- Supports 24/7 background operation with scheduled/triggered workflows ("Heartbeats")

#### 3. Extensible Skills System
- **3,286 skills** available on ClawHub (skill marketplace, after security cleanup)
- Categories: productivity, developer tools, communication, AI models, smart home, finance, trading, and more
- Skills can automate anything: file operations, shell commands, web browsing, API calls, browser control, email, GitHub, and smart home devices

#### 4. Model Agnostic
- Works with commercial LLMs: OpenAI GPT-4, Anthropic Claude, Google Gemini, DeepSeek
- Works with local/open-source models: Llama, Mistral (via Ollama, LM Studio)
- Switch models per task based on privacy, cost, or capability needs

#### 5. Self-Hosted & Private
- All data stays local on your hardware
- No external servers required (unless you choose cloud LLMs)
- Full control over what the agent can access

### Architecture

```
┌─────────────────────────────────────────────────────┐
│                    OPENCLAW CORE                      │
│                                                       │
│  ┌────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Gateway     │  │ Agent Engine  │  │ Skill Loader │  │
│  │ (WebSocket) │  │ (Autonomous   │  │ (ClawHub)    │  │
│  │             │  │  planning &   │  │              │  │
│  │ WhatsApp    │  │  execution)   │  │ 3,286 skills │  │
│  │ Telegram    │  │              │  │              │  │
│  │ Discord     │  │ Persistent   │  │ polyclaw     │  │
│  │ Slack       │  │ memory       │  │ crypto       │  │
│  │ Signal      │  │              │  │ web-browse   │  │
│  │ iMessage    │  │ Heartbeats   │  │ shell        │  │
│  │ Teams       │  │ (scheduled)  │  │ email        │  │
│  │ Matrix      │  │              │  │ ...          │  │
│  │ IRC         │  │              │  │              │  │
│  │ 20+ more    │  │              │  │              │  │
│  └────────────┘  └──────────────┘  └──────────────┘  │
│                                                       │
│  ┌────────────────────────────────────────────────┐   │
│  │ LLM Provider (model-agnostic)                   │   │
│  │ GPT-4 | Claude | Gemini | Llama | Mistral | ... │   │
│  └────────────────────────────────────────────────┘   │
│                                                       │
│  Local WebSocket control: ws://127.0.0.1:18789        │
└─────────────────────────────────────────────────────┘
```

---

## 3. GitHub Ecosystem

### Main Repository

| Attribute | Value |
|---|---|
| **Repo** | [github.com/openclaw/openclaw](https://github.com/openclaw/openclaw) |
| **Stars** | ⭐ 250,000–308,000+ (one of the fastest-growing repos in GitHub history) |
| **Forks** | 🍴 32,000–57,000+ |
| **Contributors** | 900+ |
| **License** | MIT |
| **Language** | TypeScript / JavaScript (Node.js) |
| **Last Active** | Continuously updated (daily commits) |

### Supporting Repositories

| Repo | Purpose |
|---|---|
| [openclaw/openclaw](https://github.com/openclaw/openclaw) | Core AI agent framework |
| [openclaw/openclaw.ai](https://github.com/openclaw/openclaw.ai) | Website and installer scripts |
| [openclaw/clawhub](https://github.com/openclaw/clawhub) | Skill directory and registry |
| [openclaw/lobster](https://github.com/openclaw/lobster) | Workflow engine for automations |
| [openclaw/nix-openclaw](https://github.com/openclaw/nix-openclaw) | Nix-based packaging |
| [openclaw-install/openclaw-installer](https://github.com/openclaw-install/openclaw-installer) | Automated Ansible setup scripts |

### Polymarket-Specific Repository

| Attribute | Value |
|---|---|
| **Repo** | [github.com/chainstacklabs/polyclaw](https://github.com/chainstacklabs/polyclaw) |
| **Maintainer** | Chainstacklabs (enterprise blockchain infra company) |
| **Language** | Python |
| **Purpose** | Trading-enabled Polymarket skill for OpenClaw |
| **Features** | Market browsing, trade execution, position tracking, LLM-powered hedge discovery |

### Growth Context

OpenClaw surpassed **250,000 GitHub stars in ~4 months** — faster than React, Vue, or the Linux kernel. This explosive growth is partly organic (the tool is genuinely useful) and partly driven by aggressive community marketing. The speed of adoption is both a strength (active community) and a risk (attracts malicious actors).

---

## 4. PolyClaw — The Polymarket Trading Skill

PolyClaw is the most important piece of the puzzle for our use case. It's a dedicated Polymarket trading skill built by [Chainstacklabs](https://chainstack.com/) that plugs directly into OpenClaw.

### Features

| Feature | Description |
|---|---|
| **Market Browsing** | Browse trending markets, search by keyword, view market details with odds |
| **Trade Execution** | Buy YES/NO positions on-chain with USDC on Polygon via CLOB |
| **Split + CLOB** | Splits USDC into YES+NO tokens, sells unwanted side on CLOB for optimal pricing |
| **Position Tracking** | Track entry prices, live prices, P&L across all open positions |
| **Wallet Management** | Check balances (USDC, POL), manage contract approvals |
| **LLM-Powered Hedging** | AI discovers logical hedge pairs across markets with coverage tiers (85-95%+) |
| **Autonomous Trading** | Agents can trade independently with risk controls and confidence thresholds |
| **Output Formats** | Human-friendly tables or machine-readable JSON for automation pipelines |

### How Trade Execution Works

```
User: "Buy $100 of YES on market X"

PolyClaw:
  1. Convert $100 USDC → split into 100 YES + 100 NO tokens
  2. Sell 100 NO tokens on Polymarket CLOB at market price
  3. Net result: ~137 YES tokens for ~$73 effective cost (at $0.73/share)
  4. Track position in local database
  5. Report P&L on demand
```

### Installation

```bash
# Via ClawHub
clawhub install polyclaw
cd ~/.openclaw/skills/polyclaw
uv sync

# Or from source
git clone https://github.com/chainstacklabs/polyclaw
cd polyclaw
uv sync
```

### Key Commands

| Command | What It Does |
|---|---|
| `polyclaw.py markets trending` | Show trending markets by 24h volume |
| `polyclaw.py markets search "bitcoin"` | Search markets by keyword |
| `polyclaw.py market <id>` | Detailed view of a specific market |
| `polyclaw.py buy <market_id> YES 100` | Buy $100 of YES shares |
| `polyclaw.py positions` | View all open positions with P&L |
| `polyclaw.py wallet status` | Check wallet balances |
| `polyclaw.py hedge scan` | LLM-powered hedge pair discovery |
| `polyclaw.py hedge scan --query "crypto"` | Hedge scan filtered by topic |

### Environment Setup

```bash
# .env file
CHAINSTACK_NODE="https://polygon-mainnet.core.chainstack.com/YOUR_KEY"
POLYCLAW_PRIVATE_KEY="0xYOUR_PRIVATE_KEY"
OPENROUTER_API_KEY="sk-or-YOUR_KEY"  # Optional, for LLM hedge analysis
```

---

## 5. Documented Earnings — The Headline Numbers

### Case 1: $115,000 in One Week

| Metric | Value |
|---|---|
| **Profit** | $115,000 in 7 days |
| **Trades** | 47,000+ trades across 31 markets |
| **Strategy** | Automated market making + arbitrage |
| **Profit per trade** | ~$2.45 average (thousands of small wins) |
| **Capital** | Not disclosed (likely $100K-$500K+) |
| **Source** | [openclaws.io/blog/polymarket-trading-bot](https://openclaws.io/blog/polymarket-trading-bot) |

### Case 2: $116,280.60 in One Day ("Bidou28old")

| Metric | Value |
|---|---|
| **Profit** | $116,280.60 in 24 hours |
| **Trades** | 52 trades |
| **Win rate** | 83% (43 wins / 52 trades) |
| **Markets** | 5-minute BTC and XRP prediction markets |
| **Strategy** | Black-Scholes pricing + momentum signals |
| **Biggest single win** | $15,700 on a 5-min "BTC down" bet |
| **Capital** | Large (inferred from trade sizes of $5K-$15K per position) |
| **Source** | [finbold.com](https://finbold.com/trading-bot-makes-over-100000-on-polymarket-in-a-day/) |

### Reality Check

| Headline | What They Don't Tell You |
|---|---|
| "$115K in a week" | Required $100K-$500K+ capital and 47,000 automated trades |
| "$116K in a day" | Used $5K-$15K per trade position — far from a $100 start |
| "Thousands daily" | Only the top ~5-10% of bot operators achieve this |
| "83% win rate" | On a specific day with favorable volatility — not every day |
| "Anyone can do it" | Only ~30% of ALL Polymarket wallets are profitable long-term |

### Scaled-Down Math for $100 Capital

If we assume the same edge percentage (not absolute dollar amount):

| Metric | $100K Capital (Reported) | $100 Capital (Ours) |
|---|---|---|
| Weekly profit (Case 1) | $115,000 (115% return) | $115 (same % — unlikely) |
| Daily profit (Case 2) | $116,280 (116% return) | $116 (same % — unlikely) |
| **Realistic daily expectation** | **1-5% daily return** | **$1-$5/day ($0.04-$0.21/hr)** |
| **Conservative monthly** | **$30K-$150K** | **$30-$150** |

> **Key insight:** The strategies are real and profitable, but they scale with capital. With $100, OpenClaw can help earn $1-5/day through automated trading — **which is actually impressive for prediction market returns** but far from "thousands daily."

---

## 6. How the Profitable Bots Actually Work

### Strategy 1: Automated Market Making (Spread Capture)

```
The bot acts as a liquidity provider:
  1. Posts BUY orders slightly below market consensus
  2. Posts SELL orders slightly above market consensus
  3. Profits from the spread on every pair of fills
  4. Runs across 30+ markets simultaneously
  
  Example:
    Market consensus: YES = $0.55
    Bot BUY at: $0.53
    Bot SELL at: $0.57
    Profit per round trip: $0.04 per share
    
    × 1,000 trades/day = $40/day (with $10K capital)
```

### Strategy 2: Quantitative Edge Trading (Black-Scholes)

```
The bot calculates "fair value" using math:
  1. Fetch real-time BTC price from Binance
  2. Calculate fair YES/NO probability using Black-Scholes digital option formula
  3. Compare against Polymarket order book
  4. Buy when market price is >6¢ below calculated fair value
  5. Sell when market corrects or at expiry
  
  This is the strategy "Bidou28old" used for the $116K day.
```

### Strategy 3: LLM-Powered Hedge Discovery

```
PolyClaw's unique feature:
  1. Scans all active Polymarket markets
  2. Uses Claude/GPT to find logical contradictions
     (e.g., Market A implies Market B, but prices disagree)
  3. Buys the underpriced side of the pair
  4. Guaranteed profit when logical relationship holds
  
  Coverage tiers: T1 (≥95%), T2 (90-95%), T3 (85-90%)
```

### Strategy 4: Latency Arbitrage (same as our PRD)

```
Same strategy we designed in our PRD:
  1. Monitor Binance for BTC price movements
  2. Detect 30-90 second lag on Polymarket
  3. Buy mispriced contracts before market corrects
  4. Sell for profit after correction
  
  OpenClaw makes this easier by handling messaging + scheduling,
  but the core trading logic still needs custom implementation.
```

---

## 7. Security Risks — The Dark Side

### ⚠️ CRITICAL: Malicious Skills Are a Major Threat

This is the single most important section. **OpenClaw's skill marketplace has been weaponized.**

### The Numbers

| Threat Metric | Value |
|---|---|
| **Malicious skills found** | 341–1,100+ (audits vary) |
| **Percentage of ecosystem** | ~20% of all skills were malicious (before cleanup) |
| **Skills removed** | 2,400+ suspicious skills purged in Feb 2026 ("ClawHavoc" incident) |
| **Exposed instances** | 42,900 OpenClaw instances found on public IPs |
| **Users affected** | Hundreds of drained wallets and stolen API keys reported |
| **Malware families** | Atomic Stealer (AMOS) targeting 60+ crypto wallet types |

### What Malicious Skills Do

| Attack Vector | Description |
|---|---|
| **Wallet seed exfiltration** | Steals your private key from .env files or memory |
| **API credential theft** | Exfiltrates exchange API keys, OpenAI keys, etc. |
| **Browser data theft** | Steals saved passwords, cookies, session tokens |
| **Reverse shells** | Opens backdoor access to your entire system |
| **Social engineering** | Polished docs trick users into running trojan installers |
| **Supply chain attacks** | Legitimate-looking skills with hidden malicious payloads |

### Named Malicious Polymarket Skills

The following skill names have been **explicitly identified** as malicious lures:
- `polymarket-trader`
- `polymarket-pro`
- `better-polymarket`

These masquerade as Polymarket trading tools but actually steal wallet keys.

### Why It's So Dangerous

1. **No sandboxing** — Once installed, a skill has the SAME access as OpenClaw itself (full system, all files, all credentials)
2. **No vetting process** — Anyone can publish a skill to ClawHub with no security review
3. **Deep system access** — OpenClaw needs shell access, file access, and API keys to function, so malicious skills inherit all of this
4. **Rapid adoption** — Viral growth means many non-technical users install skills without auditing code

### How to Stay Safe

| Rule | Why |
|---|---|
| **Only use official/verified skills** | `chainstacklabs/polyclaw` is from a reputable company |
| **Run in isolated VM/container** | Limit blast radius if compromised |
| **Use a dedicated hot wallet** | Never expose your main wallet's private key |
| **Fund wallet with minimum balance** | Only what you're willing to lose |
| **Audit ALL skill code before install** | Read the source — every file |
| **Never install from random GitHub forks** | Even popular-looking ones may be traps |
| **Monitor PolygonScan for unexpected txns** | Watch your wallet for unauthorized activity |

---

## 8. OpenClaw vs Custom Bot — Honest Comparison

### For Our Specific Use Case ($1/hr with $100 Capital on BTC 15-min Markets)

| Factor | OpenClaw + PolyClaw | Custom Python Bot (Our PRD) |
|---|---|---|
| **Setup time** | Hours to days | 2-4 weeks (Phase 1-2 of PRD) |
| **Market browsing** | ✅ Built-in | Must implement market scanner |
| **Trade execution** | ✅ Split+CLOB built-in | Must implement with py-clob-client |
| **Hedge discovery** | ✅ LLM-powered | Not in our PRD (Phase 4 maybe) |
| **Latency arb** | ❌ Not built-in | ✅ Core of our strategy |
| **Same-platform arb** | ❌ Not built-in | ✅ Secondary strategy |
| **Binance price feed** | ❌ Not built-in | ✅ Core data source |
| **Risk management** | ⚠️ Basic (position limits) | ✅ 5-level hierarchy in our PRD |
| **Circuit breaker** | ❌ Not built-in | ✅ In our PRD |
| **BTC 15-min focus** | ❌ General-purpose | ✅ Purpose-built |
| **Security** | ⚠️ Risk from skill ecosystem | ✅ We audit all code |
| **Customization** | Limited to skill API | Unlimited |
| **Messaging/alerts** | ✅ Built-in (20+ platforms) | Must add Discord webhooks |
| **Paper trading** | ⚠️ Some skills offer it | ✅ Built into our design |
| **Backtesting** | ❌ Not built-in | Phase 4 of our PRD |

### Verdict

**OpenClaw is great for general Polymarket trading** (browsing, hedging, manual-ish trading) but **lacks the specific features we need for our BTC 15-min latency arbitrage strategy**. Our custom bot design in the PRD is better suited for the $1/hour target because:

1. **Latency arb requires Binance price feeds** — PolyClaw doesn't have this
2. **Sub-100ms execution matters** — OpenClaw adds abstraction overhead
3. **Our 5-level risk hierarchy** — not available in any OpenClaw skill
4. **BTC 15-min market specialization** — PolyClaw is general-purpose

However, PolyClaw's code is an **excellent reference implementation** for:
- How to interact with Polymarket's CLOB API in Python
- Split+CLOB trade execution pattern
- LLM-powered hedge discovery logic
- Contract approval management

---

## 9. Can It Really Help Us Make Money on Polymarket?

### Yes — In These Ways

| Use Case | How It Helps | Value to Us |
|---|---|---|
| **Learning tool** | Study PolyClaw's Python code for CLOB interaction patterns | 🟢 High — saves dev time |
| **Market research** | Browse and monitor markets through natural language | 🟢 High — faster research |
| **Manual trading assistant** | Execute trades via chat commands while developing our bot | 🟡 Medium — convenient |
| **Hedge discovery** | Find logical arbitrage opportunities across markets | 🟢 High — unique capability |
| **Alert system** | Monitor price/volume spikes via messaging channels | 🟡 Medium — nice to have |
| **Reference implementation** | Study how production bots handle execution, state, errors | 🟢 High — architecture reference |

### No — In These Ways

| Expectation | Reality |
|---|---|
| "Install PolyClaw and make $1000/day" | ❌ Requires massive capital + custom strategy |
| "OpenClaw replaces custom development" | ❌ Our latency arb strategy needs purpose-built components |
| "It's safe to trust with wallet keys" | ❌ Security model is risky without strict isolation |
| "The documented earnings are typical" | ❌ They're extreme outliers with 100-5000× our capital |
| "Set and forget money maker" | ❌ Markets change, edges erode, monitoring is essential |

### Realistic Earning Potential with OpenClaw + $100

| Approach | Expected Return | Risk Level |
|---|---|---|
| **Manual trading with PolyClaw assistance** | $0-3/day | Medium |
| **Automated market making (needs more capital)** | Not viable with $100 | High |
| **LLM hedge discovery + manual execution** | $0-5/day (if opportunities exist) | Medium |
| **Our custom latency arb bot (from PRD)** | $1/hr target ($24/day) | Medium-High |
| **Hybrid: PolyClaw hedging + custom arb** | $1-5/day realistic | Medium |

---

## 10. How to Get Started (If You Decide to Use It)

### Recommended Safe Approach

#### Step 1: Install OpenClaw (Isolated Environment)

```bash
# Create an isolated environment (Docker or VM recommended)
npm install -g openclaw@latest
openclaw onboard --install-daemon
```

#### Step 2: Install PolyClaw (Official Repo Only)

```bash
# ONLY use the official Chainstacklabs repo
git clone https://github.com/chainstacklabs/polyclaw
cd polyclaw
uv sync
```

**⚠️ DO NOT install any Polymarket skill from ClawHub or random GitHub repos. Only use `chainstacklabs/polyclaw`.**

#### Step 3: Configure (Dedicated Hot Wallet)

```bash
# Create .env with a DEDICATED hot wallet (not your main wallet!)
CHAINSTACK_NODE="https://polygon-mainnet.core.chainstack.com/YOUR_KEY"
POLYCLAW_PRIVATE_KEY="0xDEDICATED_HOT_WALLET_KEY"
OPENROUTER_API_KEY="sk-or-YOUR_KEY"  # Optional
```

#### Step 4: Start with Research Only (No Trading)

```bash
# Browse markets (no wallet access needed)
uv run python scripts/polyclaw.py markets trending
uv run python scripts/polyclaw.py markets search "bitcoin 15"
uv run python scripts/polyclaw.py hedge scan --query "bitcoin"
```

#### Step 5: Paper Trade First

Test the full workflow with minimum funds ($5-10) before scaling.

---

## 11. Final Conclusion & Recommendation

### Is OpenClaw Helpful for Polymarket Trading?

**Yes, but not in the way most people think.**

| For... | Verdict |
|---|---|
| **Making thousands daily with $100** | ❌ No. The headline numbers require 100-5000× more capital. |
| **Automating market research** | ✅ Excellent. PolyClaw's market browsing and hedge discovery are production-ready. |
| **Learning Polymarket CLOB integration** | ✅ Excellent. PolyClaw's Python code is a clean reference implementation. |
| **Building a custom trading bot faster** | ✅ Yes. Study PolyClaw's patterns to save 1-2 weeks of development. |
| **Running a safe automated trading system** | ⚠️ Possible, but security risks require strict isolation and careful skill vetting. |
| **Achieving our $1/hour target** | ⚠️ Not directly. Our PRD's latency arb strategy is better suited — but PolyClaw can complement it. |

### Our Recommendation: Hybrid Approach

1. **Use PolyClaw as a research/reference tool** — study its code for CLOB API patterns, trade execution flow, and hedge discovery logic
2. **Build our custom bot per the PRD** — latency arbitrage requires purpose-built components that OpenClaw doesn't provide
3. **Integrate PolyClaw's hedge discovery** — add LLM-powered hedge scanning as a Phase 4 enhancement to our bot
4. **Use OpenClaw for alerts** — leverage its messaging integration for trade notifications (alternative to our Discord webhooks)
5. **Never trust OpenClaw skills blindly** — audit ALL code, run in isolation, use dedicated wallets

### What to Take from PolyClaw into Our Bot

| PolyClaw Feature | How to Use |
|---|---|
| Split+CLOB trade execution | Study and adapt for our `order_manager.py` |
| Hedge discovery logic | Add as Phase 4 feature for cross-market opportunities |
| Contract approval flow | Reference for wallet setup in our bot |
| Market browsing/filtering | Study for our `market_scanner.py` |

---

## 12. Research Sources

### Official OpenClaw

| Source | URL |
|---|---|
| OpenClaw Website | [openclaw.ai](https://openclaw.ai/) |
| OpenClaw Docs | [docs.openclaw.ai](https://docs.openclaw.ai/) |
| OpenClaw GitHub | [github.com/openclaw/openclaw](https://github.com/openclaw/openclaw) |
| OpenClaw Features | [openclaw-ai.com/en/features](https://openclaw-ai.com/en/features) |

### PolyClaw (Polymarket Skill)

| Source | URL |
|---|---|
| PolyClaw GitHub | [github.com/chainstacklabs/polyclaw](https://github.com/chainstacklabs/polyclaw) |
| PolyClaw SKILL.md | [github.com/chainstacklabs/polyclaw/blob/main/SKILL.md](https://github.com/chainstacklabs/polyclaw/blob/main/SKILL.md) |
| Chainstack Integration Guide | [docs.chainstack.com — Polymarket OpenClaw skill](https://docs.chainstack.com/docs/polygon-creating-a-polymarket-trading-openclaw-skill) |
| Chainstack Blog | [chainstack.com — Integrating with OpenClaw](https://chainstack.com/integrating-chainstack-with-openclaw-bot-for-polymarket/) |
| PolyClaw Autonomous Agents | [polyclaw.ai](https://www.polyclaw.ai/) |

### Earnings Reports & Analysis

| Source | URL |
|---|---|
| $115K/week Bot Report | [openclaws.io/blog/polymarket-trading-bot](https://openclaws.io/blog/polymarket-trading-bot) |
| $116K/day Bot (Finbold) | [finbold.com — Trading bot $100K+ in a day](https://finbold.com/trading-bot-makes-over-100000-on-polymarket-in-a-day/) |
| $116K/day Analysis | [theworldmag.com — OpenClaw Polymarket Bot](https://theworldmag.com/en/openclaw-polymarket-bot/) |
| KuCoin Report | [kucoin.com — OpenClaw tens of thousands monthly](https://www.kucoin.com/news/flash/openclaw-on-polymarket-generates-tens-of-thousands-monthly-via-automated-trading) |
| Gate.io Analysis | [gate.com — OpenClaw betting against humans](https://www.gate.com/learn/articles/openclaw-is-now-making-tens-of-thousands-a-month-betting-against-humans-on-polymarket) |

### Security Warnings

| Source | URL |
|---|---|
| The Hacker News — 341 Malicious Skills | [thehackernews.com — ClawHub malicious skills](https://thehackernews.com/2026/02/researchers-find-341-malicious-clawhub.html) |
| InfoSecurity Magazine | [infosecurity-magazine.com — Malicious crypto trading add-ons](https://www.infosecurity-magazine.com/news/malicious-crypto-trading-skills/) |
| 42,900 Exposed Instances | [elephas.app — OpenClaw security risks](https://elephas.app/resources/openclaw-ai-agent-security-risks) |
| OpenClaw Security Nightmare | [blog.barrack.ai — Vulnerabilities 2026](https://blog.barrack.ai/openclaw-security-vulnerabilities-2026/) |
| Cybernews Review | [cybernews.com — OpenClaw review](https://cybernews.com/ai-tools/openclaw-review/) |
| Risk vs Reward Analysis | [aisuperior.com — OpenClaw Polymarket trading](https://aisuperior.com/openclaw-polymarket-trading/) |

### Comparison & Tutorials

| Source | URL |
|---|---|
| OpenClaw vs Custom Bot | [team400.ai — When to use each](https://team400.ai/blog/2026-02-openclaw-vs-custom-ai-agent) |
| Step-by-Step Setup | [openclawlauncher.com — Trade on Polymarket with AI](https://www.openclawlauncher.com/blog/how-to-trade-on-polymarket-using-ai-agents-openclaw-launcher) |
| Zero-Coding Bot Tutorial | [YouTube — Polymarket Bot with OpenClaw](https://www.youtube.com/watch?v=2eACyYW9OXg) |
| Trading Skills Guide 2026 | [aurpay.net — Complete guide](https://aurpay.net/aurspace/openclaw-ai-trading-skills-complete-guide-2026/) |
| Polymarket Automation Guide | [predictionmarket.tools — Build AI trading bot](https://www.predictionmarket.tools/openclaw-polymarket-trading-bot) |

---

## Document History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | March 13, 2026 | Poly-Trade Research | Initial deep research — OpenClaw capabilities, PolyClaw analysis, earnings verification, security audit |

---

> ⚠️ **Disclaimer:** This is a research document, not financial advice. Trading prediction markets involves real financial risk. The earnings reported in this document are for specific accounts with unknown starting capital and are not guaranteed or typical. OpenClaw's skill ecosystem has documented security vulnerabilities — always audit code and use isolated environments. Never risk money you cannot afford to lose.
