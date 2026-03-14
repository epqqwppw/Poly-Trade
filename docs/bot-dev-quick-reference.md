# Polymarket Bot Dev — Quick Reference Cheat Sheet

> **Focus:** BTC UP/DOWN directional & arbitrage bots on Polymarket  
> **Last updated:** March 13, 2026

---

## 1. Essential SDKs — Pick One

| Language | Repo | Install |
|---|---|---|
| **Python** | [Polymarket/py-clob-client](https://github.com/Polymarket/py-clob-client) | `pip install py-clob-client` |
| **TypeScript** | [Polymarket/clob-client](https://github.com/Polymarket/clob-client) | `npm install @polymarket/clob-client` |
| **Rust** | [Polymarket/rs-clob-client](https://github.com/Polymarket/rs-clob-client) | `cargo add rs-clob-client` |

---

## 2. API Endpoints

| Purpose | URL | Protocol |
|---|---|---|
| Order placement / cancellation | `https://clob.polymarket.com` | REST |
| Live order book & trades | `wss://ws-subscriptions-clob.polymarket.com/ws/` | WebSocket |
| Market metadata & prices | `https://gamma-api.polymarket.com/markets` | REST |
| Historical trade data | `https://gamma-api.polymarket.com/query` | GraphQL |
| Direct subgraph query | `https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/polymarket-subgraph/prod/gn` | GraphQL |

---

## 3. Authentication — Two Levels

### L1 Auth (wallet signature) — one-time setup
```python
from py_clob_client.client import ClobClient

client = ClobClient(
    host="https://clob.polymarket.com",
    key="YOUR_PRIVATE_KEY",   # Polygon wallet private key
    chain_id=137
)
api_creds = client.create_or_derive_api_creds()
```

### L2 Auth (API key) — for every request
```python
client = ClobClient(
    host="https://clob.polymarket.com",
    key="YOUR_PRIVATE_KEY",
    chain_id=137,
    creds=api_creds  # from L1 step above
)
```

---

## 4. Find BTC UP/DOWN Markets

### Via REST
```bash
# Get all open BTC 15-min markets
curl "https://gamma-api.polymarket.com/markets?tag_slug=bitcoin&active=true" | jq '.[] | select(.question | test("15-minute|15 minute"))'
```

### Via GraphQL (Goldsky subgraph)
```graphql
{
  fixedProductMarketMakers(
    where: { conditions_contains: "BTC" }
    orderBy: creationTimestamp
    orderDirection: desc
    first: 10
  ) {
    id
    collateralToken { symbol }
    conditions { id resolutionTimestamp }
    outcomeTokenPrices
  }
}
```

---

## 5. Arbitrage Strategy — Buy Both Sides

**Core logic:** If `price_YES + price_NO < $1.00`, guaranteed profit when market settles.

```python
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, OrderType

def check_arb_opportunity(client, market_id, threshold=0.97):
    book = client.get_order_book(market_id)
    best_ask_yes = float(book['asks'][0]['price'])  # cheapest YES
    best_ask_no  = float(book['asks'][0]['price'])  # cheapest NO (opposite token)
    total_cost   = best_ask_yes + best_ask_no
    
    if total_cost < threshold:
        profit_pct = (1.0 - total_cost) * 100
        return True, profit_pct
    return False, 0.0

def place_arb(client, yes_token_id, no_token_id, size_usdc):
    for token_id in [yes_token_id, no_token_id]:
        order = client.create_market_order(OrderArgs(
            token_id=token_id,
            price=0.99,
            size=size_usdc / 2,
            side="BUY"
        ))
        client.post_order(order)
```

---

## 6. Real-Time WebSocket Feed

```typescript
import { RealTimeDataClient } from "@polymarket/real-time-data-client";

const client = new RealTimeDataClient("wss://ws-subscriptions-clob.polymarket.com/ws/");

// Subscribe to order book updates for a market
client.subscribeOrderBook(tokenId, (update) => {
  const yesAsk = update.asks[0]?.price;
  const noAsk  = update.bids[0]?.price;  // best bid = implied NO price
  
  if (parseFloat(yesAsk) + parseFloat(noAsk) < 0.97) {
    console.log("ARB OPPORTUNITY:", { yesAsk, noAsk });
  }
});
```

---

## 7. Key Repos by Bot Type

| Bot Type | Repos You Need |
|---|---|
| **Python arb bot** | `py-clob-client` + `real-time-data-client` (for WS) |
| **TypeScript arb bot** | `clob-client` + `real-time-data-client` |
| **Rust HFT bot** | `rs-clob-client` (includes WS support) |
| **AI/LLM trading agent** | `agents` + `agent-skills` |
| **Market maker** | `poly-market-maker` (reference implementation) |
| **Data analysis** | `polymarket-subgraph` (GraphQL) via Goldsky endpoint |
| **CLI monitoring** | `polymarket-cli` (Rust binary, no code needed) |

---

## 8. Smart Contract ABIs (Polygon Mainnet)

| Contract | Address | Repo |
|---|---|---|
| CTF Exchange | `0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E` | [ctf-exchange](https://github.com/Polymarket/ctf-exchange) |
| Neg-Risk CTF Exchange | `0xC5d563A36AE78145C45a50134d48A1215220f80a` | [neg-risk-ctf-adapter](https://github.com/Polymarket/neg-risk-ctf-adapter) |
| UMA-CTF Adapter | `0xCB1822859cEF82Cd2Eb4E6276C7916e692995130` | [uma-ctf-adapter](https://github.com/Polymarket/uma-ctf-adapter) |
| Conditional Token Framework | `0x4D97DCd97eC945f40cF65F87097ACe5EA0476045` | Gnosis CTF |
| USDC (PoS) | `0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174` | — |

---

## 9. Market Resolution Flow (UMA Oracle)

```
Market end time reached
    └──► Assertor calls uma-ctf-adapter.assertMarket(marketId, outcome)
             └──► UMA OOv3 opens assertion (2h challenge window)
                      ├── No dispute → auto-resolves → CTF settles
                      └── Dispute → UMA token holders vote
                               └──► Vote result → CTF Exchange settles
                                         YES = $1.00 / NO = $0.00
```

Monitor disputes at: https://oracle.umaproject.org

---

## 10. Useful GraphQL Queries

### Get recent trades for a market
```graphql
{
  transactions(
    where: { market: "0xMAKET_ADDRESS" }
    orderBy: timestamp
    orderDirection: desc
    first: 50
  ) {
    id
    timestamp
    type
    outcomeIndex
    outcomeTokensAmount
    collateralAmount
    funder
  }
}
```

### Get market prices
```graphql
{
  fixedProductMarketMakers(where: { id: "0xMARKET_ADDRESS" }) {
    outcomeTokenPrices
    outcomeTokenAmounts
    collateralVolume
    tradesQuantity
  }
}
```

---

## 11. Reference Ecosystem Diagram

```
Your Bot
  │
  ├── Place orders ──────────────────► CLOB REST API
  │                                    (Polymarket/clob-client or py-clob-client)
  │
  ├── Live prices ───────────────────► WebSocket
  │                                    (Polymarket/real-time-data-client)
  │
  ├── Historical data ───────────────► Goldsky GraphQL
  │                                    (Polymarket/polymarket-subgraph → goldsky-io)
  │
  └── Market resolution ────────────► UMA OOv3
                                       (UMAprotocol/protocol + Polymarket/uma-ctf-adapter)
```

---

## 12. Community Bot Implementations (Non-Official)

| Repo | Language | Strategy | Activity |
|---|---|---|---|
| [sed000/polymarket-btc-1h](https://github.com/sed000/polymarket-btc-1h) | TypeScript | Directional 1h BTC | 🟢 Feb 2026 |
| [svnmcqueen/polymarket-bot](https://github.com/svnmcqueen/polymarket-bot) | Python | Arb (buy both sides) | 🟢 Dec 2025 |
| [taetaehoho/poly-kalshi-arb](https://github.com/taetaehoho/poly-kalshi-arb) | Rust | HFT arb BTC/ETH/SOL | 🟡 Dec 2025 |
| [francescods04/poly](https://github.com/francescods04/poly) | Python | Options model + paper trading | 🟡 |

---

> ⚠️ **Always use paper/dry-run mode first. Never share your private key. Audit any third-party code before use.**
