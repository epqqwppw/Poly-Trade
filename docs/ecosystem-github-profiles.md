# Polymarket Ecosystem — Official GitHub Profiles Reference

> **Last updated:** March 13, 2026  
> **Data source:** GitHub API — all repository counts, stars, forks, and push dates are live at time of research.

---

## Overview

The Polymarket prediction-market ecosystem is spread across four GitHub organisations (or profiles) that collectively own every layer of the stack a trading bot needs to know about:

| Layer | GitHub org | Role |
|---|---|---|
| **Platform / SDK** | [github.com/Polymarket](https://github.com/Polymarket) | Official Polymarket repos — CLOB clients, smart contracts, CLI, AI agents |
| **Labs / Experimental** | [github.com/polymarket-labs](https://github.com/polymarket-labs) | Secondary profile (currently only forks; no original public repos) |
| **Oracle / Resolution** | [github.com/UMAprotocol](https://github.com/UMAprotocol) | UMA Optimistic Oracle — resolves all Polymarket market outcomes |
| **Data / Indexing** | [github.com/goldsky-io](https://github.com/goldsky-io) | Real-time blockchain data pipelines & hosted subgraphs for Polymarket |

Together these organisations form a complete loop: Polymarket runs the exchange, UMA resolves markets, Goldsky indexes on-chain data, and the SDKs let bots interact with all three layers programmatically.

---

## 1. github.com/Polymarket (Official)

### Profile Summary

- **Type:** Official Polymarket organization
- **Total public repos:** 65
- **Primary languages:** Python, TypeScript, Rust, Solidity, Go
- **Focus areas:** CLOB trading clients, AI agent framework, smart contracts (CTF exchange, oracle adapters), CLI tooling, subgraph indexing, builder / relayer infrastructure

This is the single source-of-truth for every official Polymarket developer integration. It contains everything from low-level order-signing utilities to high-level AI-agent scaffolding.

### Complete Repository List

| Repo | Language | ⭐ Stars | 🍴 Forks | Last Push | Description | Use Case |
|---|---|---|---|---|---|---|
| [agents](https://github.com/Polymarket/agents) | Python | 2,483 | 579 | 2024-11-05 | Trade autonomously on Polymarket using AI Agents | AI agent framework for autonomous trading |
| [polymarket-cli](https://github.com/Polymarket/polymarket-cli) | Rust | 1,681 | 162 | 2026-03-10 | Official CLI tool | Command-line interface for trading & market management |
| [py-clob-client](https://github.com/Polymarket/py-clob-client) | Python | 893 | 318 | 2026-02-22 | Python client for the Polymarket CLOB | Primary Python SDK for order placement & market data |
| [rs-clob-client](https://github.com/Polymarket/rs-clob-client) | Rust | 604 | 174 | 2026-03-11 | Polymarket Rust CLOB Client | High-performance Rust SDK for the CLOB API |
| [clob-client](https://github.com/Polymarket/clob-client) | TypeScript | 469 | 153 | 2026-03-09 | TypeScript client for the Polymarket CLOB | Official TS SDK for CLOB — orders, book, fills |
| [ctf-exchange](https://github.com/Polymarket/ctf-exchange) | Solidity | 327 | 154 | 2026-02-03 | Polymarket CTF Exchange | On-chain exchange smart contracts (Polygon) |
| [poly-market-maker](https://github.com/Polymarket/poly-market-maker) | Python | 269 | 92 | 2024-07-05 | Market maker keeper for the Polymarket CLOB | Reference market-maker bot |
| [polymarket-subgraph](https://github.com/Polymarket/polymarket-subgraph) | TypeScript | 194 | 53 | 2026-02-13 | Subgraph for indexing on-chain trades, volume, users, liquidity | The Graph / Goldsky subgraph manifest |
| [real-time-data-client](https://github.com/Polymarket/real-time-data-client) | TypeScript | 183 | 52 | 2026-03-05 | TypeScript client to receive real-time data messages | WebSocket streaming of live order book & trade events |
| [uma-ctf-adapter](https://github.com/Polymarket/uma-ctf-adapter) | Solidity | 114 | 56 | 2025-09-03 | Adapter contract to resolve Polymarket markets via UMA OO | Smart contract bridging Polymarket ↔ UMA oracle |
| [neg-risk-ctf-adapter](https://github.com/Polymarket/neg-risk-ctf-adapter) | Solidity | 80 | 34 | 2026-01-08 | Negative-risk CTF adapter | Adapter for multi-outcome negative-risk markets |
| [examples](https://github.com/Polymarket/examples) | TypeScript | 72 | 23 | 2025-11-10 | Code examples for Polymarket | Official integration examples |
| [python-order-utils](https://github.com/Polymarket/python-order-utils) | Python | 60 | 11 | 2024-07-29 | Python utilities to generate and sign orders for the CLOB | Low-level Python order signing library |
| [polymarket-sdk](https://github.com/Polymarket/polymarket-sdk) | TypeScript | 57 | 22 | 2026-03-06 | SDK for interacting with Polymarket Wallets | Wallet / authentication layer SDK |
| [go-order-utils](https://github.com/Polymarket/go-order-utils) | Go | 55 | 12 | 2025-09-25 | Go utilities for generating & signing limit/market orders | Go order-signing library |
| [PolyLend](https://github.com/Polymarket/PolyLend) | Solidity | 40 | 13 | 2024-07-25 | PolyLend protocol | On-chain lending protocol using CTF positions as collateral |
| [agent-skills](https://github.com/Polymarket/agent-skills) | — | 40 | 7 | 2026-02-19 | Public repository for Polymarket Agent Skills | Skill extensions for the AI agents framework |
| [builder-relayer-client](https://github.com/Polymarket/builder-relayer-client) | TypeScript | 39 | 19 | 2025-12-06 | TypeScript Client for the Polymarket Relayer API | TS client for builder / relayer order submission |
| [py-builder-relayer-client](https://github.com/Polymarket/py-builder-relayer-client) | Python | 25 | 9 | 2026-02-22 | Python Client for the Polymarket Relayer API | Python client for builder / relayer order submission |
| [clob-order-utils](https://github.com/Polymarket/clob-order-utils) | TypeScript | 23 | 14 | 2026-02-26 | TypeScript utility to generate and sign orders for the CLOB | Low-level TS order signing (used by clob-client) |
| [builder-signing-sdk](https://github.com/Polymarket/builder-signing-sdk) | TypeScript | 21 | 10 | 2026-03-09 | TypeScript SDK for creating authenticated builder headers | Authentication header generation for builder API |
| [py-merge-split-positions](https://github.com/Polymarket/py-merge-split-positions) | Python | 19 | 7 | 2024-07-01 | Merge and split CTF positions | Python scripts for CTF position management |
| [amm-maths](https://github.com/Polymarket/amm-maths) | TypeScript | 19 | 5 | 2025-04-07 | AMM mathematics | AMM pricing math library |
| [wagmi-safe-builder-example](https://github.com/Polymarket/wagmi-safe-builder-example) | TypeScript | 17 | 12 | 2025-12-08 | Wagmi + Safe builder integration example | Example: Safe multisig wallet + wagmi builder pattern |
| [polymarket-liq-mining](https://github.com/Polymarket/polymarket-liq-mining) | TypeScript | 16 | 3 | 2023-12-07 | Payout scripts & merkle distributor for liquidity mining | Liquidity mining reward distribution |
| [conditional-token-examples-py](https://github.com/Polymarket/conditional-token-examples-py) | Python | 15 | 8 | 2023-12-05 | Interacting with CTF contracts using Web3py | Python examples for Gnosis CTF framework |
| [exchange-fee-module](https://github.com/Polymarket/exchange-fee-module) | Solidity | 13 | 10 | 2026-01-06 | Enables dynamic fees on Exchange | Fee module for the CTF exchange |
| [builder-signing-server](https://github.com/Polymarket/builder-signing-server) | TypeScript | 13 | 6 | 2025-10-10 | Express server for creating authenticated builder headers remotely | Remote signing server for builder auth |
| [uma-sports-oracle](https://github.com/Polymarket/uma-sports-oracle) | Solidity | 12 | 6 | 2025-06-20 | Oracle contract to resolve sports markets using UMA OO | Sports market resolution contract |
| [magic-proxy-builder-example](https://github.com/Polymarket/magic-proxy-builder-example) | TypeScript | 11 | 4 | 2025-12-29 | Magic proxy builder example | Example: Magic wallet + proxy builder integration |
| [privy-safe-builder-example](https://github.com/Polymarket/privy-safe-builder-example) | TypeScript | 11 | 7 | 2025-12-29 | Privy Safe builder integration example | Example: Privy embedded wallet + Safe builder pattern |
| [proxy-factories](https://github.com/Polymarket/proxy-factories) | Solidity | 10 | 18 | 2025-05-23 | Proxy factory contracts | Wallet proxy factory smart contracts |
| [polymarket-us-python](https://github.com/Polymarket/polymarket-us-python) | Python | 8 | 4 | 2026-01-22 | Official Polymarket US Python SDK | Python SDK for Polymarket US (geo-fenced) markets |
| [contract-security](https://github.com/Polymarket/contract-security) | — | 8 | 2 | 2024-08-29 | Smart contract security documentation | Security audits and docs |
| [poly-ct-scripts](https://github.com/Polymarket/poly-ct-scripts) | Solidity | 7 | 2 | 2023-02-10 | Forge scripts for Gnosis Conditional Tokens | Low-level CTF interaction scripts |
| [py-builder-signing-sdk](https://github.com/Polymarket/py-builder-signing-sdk) | Python | 6 | 5 | 2025-10-20 | Python SDK for creating authenticated builder headers | Python builder auth SDK |
| [conditional-token-examples](https://github.com/Polymarket/conditional-token-examples) | TypeScript | 5 | 1 | 2023-08-16 | Interacting with CTF contracts using Ethers | TS examples for CTF framework |
| [go-builder-signing-sdk](https://github.com/Polymarket/go-builder-signing-sdk) | Go | 4 | 3 | 2025-11-17 | Go SDK for authenticated builder headers | Go builder auth SDK |
| [py-clob-client-l2-auth](https://github.com/Polymarket/py-clob-client-l2-auth) | Python | 4 | 1 | 2024-04-10 | Python CLOB client with L2 auth | Python CLOB client variant with L2 authentication |
| [magic-safe-builder-example](https://github.com/Polymarket/magic-safe-builder-example) | TypeScript | 4 | 2 | 2025-12-29 | Magic + Safe builder example | Example: Magic wallet + Safe builder |
| [go-market-events](https://github.com/Polymarket/go-market-events) | Go | 4 | 2 | 2024-06-27 | Go market events listener | Go client for market event streaming |
| [polymarket-us-typescript](https://github.com/Polymarket/polymarket-us-typescript) | TypeScript | 3 | 3 | 2026-01-21 | Official Polymarket US TypeScript SDKs | TS SDK for Polymarket US markets |
| [relayer-deposits](https://github.com/Polymarket/relayer-deposits) | TypeScript | 3 | 2 | 2023-04-07 | Deposits to Polymarket through a custom relayer | Custom relayer deposit scripts |
| [go-redeemtions](https://github.com/Polymarket/go-redeemtions) | Go | 3 | 1 | 2024-05-24 | Go CTF redemption utilities | Go scripts for redeeming CTF positions |
| [resolution-subgraph](https://github.com/Polymarket/resolution-subgraph) | TypeScript | 3 | 1 | 2026-02-18 | Market resolution subgraph | Subgraph for tracking market resolution events |
| [safe-wallet-integration](https://github.com/Polymarket/safe-wallet-integration) | TypeScript | 2 | 1 | 2025-12-22 | Safe wallet integration | Safe multisig wallet integration example |
| [matic-withdrawal-batcher](https://github.com/Polymarket/matic-withdrawal-batcher) | Solidity | 2 | 1 | 2021-04-15 | Matic/Polygon withdrawal batcher | Legacy Polygon withdrawal batching contract |
| [turnkey-safe-builder-example](https://github.com/Polymarket/turnkey-safe-builder-example) | TypeScript | 2 | 3 | 2025-12-29 | Turnkey + Safe builder example | Example: Turnkey MPC wallet + Safe builder |
| [go-ctf-utils](https://github.com/Polymarket/go-ctf-utils) | Solidity | 1 | 0 | 2024-04-08 | Go utility to calculate CTF position IDs | Go CTF position ID calculator |
| [ts-merge-split-positions](https://github.com/Polymarket/ts-merge-split-positions) | TypeScript | 1 | 0 | 2024-04-17 | TypeScript merge/split CTF positions | TS equivalent of py-merge-split-positions |
| [vue-components](https://github.com/Polymarket/vue-components) | JavaScript | 1 | 1 | 2025-04-07 | Vue UI components | Frontend Vue components |
| [infra-challenge-sre](https://github.com/Polymarket/infra-challenge-sre) | HCL | 1 | 0 | 2025-08-11 | SRE infrastructure challenge | Infrastructure-as-code challenge repo |
| [uma-ctf-adapter-sdk](https://github.com/Polymarket/uma-ctf-adapter-sdk) | TypeScript | 1 | 1 | 2023-08-08 | SDK for the UMA CTF Adapter | TS SDK wrapping the UMA CTF adapter contract |
| [insta-exit-sdk](https://github.com/Polymarket/insta-exit-sdk) | TypeScript | 0 | 1 | 2021-05-24 | SDK for Biconomy instaExit | Legacy fast-exit bridge SDK |
| [polymarket-liquidity-requests](https://github.com/Polymarket/polymarket-liquidity-requests) | TypeScript | 0 | 0 | 2021-09-23 | Liquidity request scripts | Legacy liquidity request tooling |
| [cosmos-delegation-js](https://github.com/Polymarket/cosmos-delegation-js) | JavaScript | 0 | 2 | 2025-04-07 | Cosmos delegation JavaScript utilities | Cosmos chain delegation tooling |
| [leaderboard-username](https://github.com/Polymarket/leaderboard-username) | TypeScript | 0 | 0 | 2023-06-09 | Leaderboard username utilities | Leaderboard username management |
| [positions-subgraph](https://github.com/Polymarket/positions-subgraph) | TypeScript | 0 | 3 | 2023-12-08 | Positions subgraph | Subgraph for tracking user CTF positions |
| [ctf-utils](https://github.com/Polymarket/ctf-utils) | TypeScript | 0 | 1 | 2023-01-18 | Utility library to calculate CTF tokenIds | CTF token ID utilities |
| [clob-client-l2-auth](https://github.com/Polymarket/clob-client-l2-auth) | TypeScript | 0 | 0 | 2024-04-10 | TypeScript CLOB client with L2 auth | TS CLOB client variant with L2 authentication |
| [uma-binary-adapter-sdk](https://github.com/Polymarket/uma-binary-adapter-sdk) | TypeScript | 0 | 0 | 2022-10-26 | (deprecated) TS SDK for the Polymarket UMA CTF adapter | Deprecated — superseded by uma-ctf-adapter |
| [matic-withdrawal-batching-subgraph](https://github.com/Polymarket/matic-withdrawal-batching-subgraph) | TypeScript | 0 | 1 | 2025-04-07 | Matic withdrawal batching subgraph | Subgraph for legacy withdrawal batching |
| [tvl-subgraph](https://github.com/Polymarket/tvl-subgraph) | TypeScript | 0 | 0 | 2022-05-17 | TVL subgraph | Subgraph for total-value-locked tracking |
| [infra-challenge-devops](https://github.com/Polymarket/infra-challenge-devops) | Go | 0 | 0 | 2025-09-12 | DevOps infrastructure challenge | Infrastructure-as-code challenge repo |
| [multi-endpoint-provider](https://github.com/Polymarket/multi-endpoint-provider) | TypeScript | 0 | 1 | 2021-09-21 | ethers.js provider with RPC fallback | Legacy multi-RPC-endpoint provider |

### Key Repos for UP/DOWN Bot Developers

These are the repos a BTC UP/DOWN arbitrage or directional bot **actually needs**:

| Priority | Repo | Why You Need It |
|---|---|---|
| 🔴 Essential | [py-clob-client](https://github.com/Polymarket/py-clob-client) | Place, cancel, and query orders via Python — the most-used client |
| 🔴 Essential | [clob-client](https://github.com/Polymarket/clob-client) | Same as above but in TypeScript |
| 🔴 Essential | [rs-clob-client](https://github.com/Polymarket/rs-clob-client) | Rust CLOB client for ultra-low-latency bots |
| 🔴 Essential | [real-time-data-client](https://github.com/Polymarket/real-time-data-client) | Live WebSocket feed for order book & trade events — critical for arb timing |
| 🟠 Important | [polymarket-cli](https://github.com/Polymarket/polymarket-cli) | Inspect markets, balances, and orders from the command line |
| 🟠 Important | [polymarket-subgraph](https://github.com/Polymarket/polymarket-subgraph) | Query historical trades, volume, and market data via GraphQL |
| 🟠 Important | [python-order-utils](https://github.com/Polymarket/python-order-utils) | Sign orders correctly (EIP-712) — needed if building custom Python bots |
| 🟠 Important | [clob-order-utils](https://github.com/Polymarket/clob-order-utils) | Same as above but TypeScript |
| 🟡 Useful | [agents](https://github.com/Polymarket/agents) | Full AI agent framework — good reference architecture |
| 🟡 Useful | [poly-market-maker](https://github.com/Polymarket/poly-market-maker) | Reference market-maker bot to study |
| 🟡 Useful | [examples](https://github.com/Polymarket/examples) | Official working code examples for every common task |
| 🟡 Useful | [ctf-exchange](https://github.com/Polymarket/ctf-exchange) | On-chain contract ABI — useful for direct on-chain interaction |

### API & Integration Notes

- **CLOB REST API base:** `https://clob.polymarket.com`
- **WebSocket stream:** `wss://ws-subscriptions-clob.polymarket.com/ws/`
- **Authentication:** L1 (ECDSA wallet sig) for write operations; L2 (API key) for high-frequency trading
- **Network:** Polygon PoS (MATIC) — all trades settle on-chain
- **Quote currency:** USDC (6 decimals)
- **Order types:** GTC (Good-Till-Cancelled), FOK (Fill-or-Kill), GTD (Good-Till-Date)
- **Builder API:** For routers / aggregators — requires `builder-signing-sdk` for auth headers
- **Relayer API:** Submit orders without gas via `builder-relayer-client`

---

## 2. github.com/polymarket-labs

### Profile Summary

- **Type:** Secondary profile listed as "Polymarket Labs"
- **GitHub org ID:** 264698406
- **Total original public repos:** 0 (as of March 2026)
- **Activity:** The profile currently contains only **forked repositories** from unrelated third-party projects

### Complete Repository List

| Repo | Type | Language | Description |
|---|---|---|---|
| polymarket-copytrading-bot-sport | Fork (from dev-protocol) | TypeScript | Copy-trading bot for Polymarket sports markets |
| canton-dex-platform (×5 forks) | Fork (from 0xalberto) | TypeScript | Canton Network DEX platform — unrelated to Polymarket |

### How It Differs from the Main Polymarket Org

| Aspect | github.com/Polymarket | github.com/polymarket-labs |
|---|---|---|
| **Status** | Official, actively maintained | Dormant / inactive |
| **Original repos** | 65 public repos | 0 original repos |
| **Content** | SDKs, contracts, CLI, agents | Only forks of third-party projects |
| **Verified** | Yes (official Polymarket org) | Not verified |
| **Recommendation** | ✅ Use for all integrations | ⚠️ Do not rely on — not official tooling |

> **Note:** As of March 2026, `polymarket-labs` does not appear to be an active official Polymarket organization. Developers should use `github.com/Polymarket` for all integrations.

---

## 3. github.com/UMAprotocol

### Profile Summary

- **Type:** Official UMA Protocol organization
- **Total public repos:** 49
- **Primary languages:** JavaScript, TypeScript, Solidity
- **Focus areas:** Optimistic Oracle (OO), governance (UMIPs), token distribution, developer tooling, subgraph indexing
- **Polymarket relevance:** UMA's Optimistic Oracle V3 (OOv3) is the **dispute resolution and market settlement layer** for all Polymarket markets. Every market outcome (YES/NO) is verified and finalized through the UMA oracle.

### Complete Repository List

| Repo | Language | ⭐ Stars | 🍴 Forks | Last Push | Description | Polymarket Relevance |
|---|---|---|---|---|---|---|
| [protocol](https://github.com/UMAprotocol/protocol) | JavaScript | 458 | 205 | 2026-03-12 | Core UMA protocol on Ethereum | 🔴 High — contains OOv3 contracts used to settle Polymarket markets |
| [whitepaper](https://github.com/UMAprotocol/whitepaper) | — | 84 | 9 | 2020-06-29 | UMA whitepaper | 🟡 Background reading |
| [UMIPs](https://github.com/UMAprotocol/UMIPs) | — | 74 | 109 | 2025-12-03 | UMA Improvement Proposals | 🟠 Contains price identifier rules used to resolve Polymarket BTC/ETH markets |
| [token-distribution](https://github.com/UMAprotocol/token-distribution) | JavaScript | 26 | 189 | 2024-01-12 | UMA token distribution scripts | 🟡 Low — governance token distribution |
| [dev-quickstart-oov3](https://github.com/UMAprotocol/dev-quickstart-oov3) | Solidity | 29 | 15 | 2024-01-31 | OO v3 integration examples | 🔴 High — quickstart for integrating with OOv3 (same version Polymarket uses) |
| [emp-tools](https://github.com/UMAprotocol/emp-tools) | TypeScript | 17 | 27 | 2023-01-26 | Minting & managing expiring token positions | 🟡 Low — legacy EMP product |
| [dev-quickstart](https://github.com/UMAprotocol/dev-quickstart) | TypeScript | 14 | 8 | 2025-03-21 | General OO developer quickstart | 🟠 Medium — good introduction to OO integration |
| [launch-lsp](https://github.com/UMAprotocol/launch-lsp) | JavaScript | 14 | 13 | 2022-10-19 | CLI tool for launching Long-Short Pairs | 🟡 Low — LSP product, not directly used by Polymarket |
| [docs](https://github.com/UMAprotocol/docs) | JavaScript | 9 | 25 | 2023-05-26 | Official smart contract documentation | 🟠 Medium — reference documentation |
| [optimistic-oracle-dapp](https://github.com/UMAprotocol/optimistic-oracle-dapp) | TypeScript | 7 | 4 | 2023-03-23 | UI for UMA's Optimistic Oracle | 🟠 Medium — legacy OO UI |
| [website](https://github.com/UMAprotocol/website) | TypeScript | 7 | 8 | 2024-07-05 | UMA website | 🟡 Low |
| [subgraphs](https://github.com/UMAprotocol/subgraphs) | TypeScript | 6 | 4 | 2026-02-12 | Monorepo for all UMA subgraphs | 🔴 High — indexes oracle requests including Polymarket assertions |
| [oval-quickstart](https://github.com/UMAprotocol/oval-quickstart) | Solidity | 6 | 2 | 2024-07-08 | Oval deployment scripts & fork tests | 🟡 Low — OEV product |
| [oval-node](https://github.com/UMAprotocol/oval-node) | TypeScript | 6 | 4 | 2025-05-26 | Oval node for OEV auction backrun bundles | 🟡 Low — OEV product |
| [oval-contracts](https://github.com/UMAprotocol/oval-contracts) | Solidity | 5 | 3 | 2024-06-19 | Oval smart contracts for OEV auctions | 🟡 Low — OEV product |
| [managed-oracle](https://github.com/UMAprotocol/managed-oracle) | Solidity | 5 | 2 | 2025-08-25 | Oracle management contracts | 🟠 Medium — new managed oracle contracts |
| [umaverse](https://github.com/UMAprotocol/umaverse) | TypeScript | 5 | 2 | 2025-07-01 | UMA ecosystem explorer | 🟡 Low |
| [uma-docs](https://github.com/UMAprotocol/uma-docs) | — | 4 | 16 | 2026-03-11 | Official documentation | 🟠 Medium — actively updated docs |
| [across](https://github.com/UMAprotocol/across) | TypeScript | 4 | 1 | 2021-11-05 | Layer 2 bridge interface | 🟡 Low — Across bridge product |
| [oo-dispute-cli](https://github.com/UMAprotocol/oo-dispute-cli) | TypeScript | 4 | 1 | 2025-12-23 | CLI for OO disputes | 🟠 Medium — dispute oracle assertions from command line |
| [research](https://github.com/UMAprotocol/research) | Jupyter Notebook | 4 | 3 | 2021-10-20 | Research notebooks | 🟡 Low |
| [snapshot](https://github.com/UMAprotocol/snapshot) | Vue | 3 | 2 | 2024-11-16 | UMA execution with Snapshot | 🟡 Low — governance integration |
| [voter-dapp-v2](https://github.com/UMAprotocol/voter-dapp-v2) | TypeScript | 3 | 4 | 2026-02-27 | OO voting dApp v2 | 🟠 Medium — interface for UMA token holders to vote on disputed markets |
| [claim-dapp](https://github.com/UMAprotocol/claim-dapp) | TypeScript | 3 | 4 | 2021-09-29 | UMA token claiming dApp | 🟡 Low |
| [launch-emp](https://github.com/UMAprotocol/launch-emp) | JavaScript | 3 | 15 | 2021-12-29 | Jumping off point for launching EMP | 🟡 Low — legacy product |
| [voter-dapp](https://github.com/UMAprotocol/voter-dapp) | TypeScript | 2 | 4 | 2023-05-26 | OO voting dApp v1 | 🟡 Low — superseded by v2 |
| [launch-perpetual](https://github.com/UMAprotocol/launch-perpetual) | JavaScript | 2 | 5 | 2021-04-01 | Jumping off point for launching Perpetual | 🟡 Low — legacy product |
| [uma-blog](https://github.com/UMAprotocol/uma-blog) | TypeScript | 1 | 0 | 2026-02-10 | UMA blog | 🟡 Low |
| [optimistic-oracle-dapp-v2](https://github.com/UMAprotocol/optimistic-oracle-dapp-v2) | TypeScript | 1 | 6 | 2026-03-12 | OO dispute UI v2 | 🔴 High — primary UI for monitoring and disputing oracle assertions |
| [internal-ctf](https://github.com/UMAprotocol/internal-ctf) | Solidity | 1 | 1 | 2025-07-11 | Internal CTF contracts | 🟠 Medium — conditional token framework integration |
| [awesome-uma](https://github.com/UMAprotocol/awesome-uma) | — | 1 | 2 | 2020-07-09 | Curated UMA resources | 🟡 Low |
| [uma.xyz](https://github.com/UMAprotocol/uma.xyz) | TypeScript | 1 | 2 | 2026-01-29 | UMA website source | 🟡 Low |
| [dapp-boilerplate](https://github.com/UMAprotocol/dapp-boilerplate) | TypeScript | 0 | 1 | 2023-10-30 | dApp boilerplate | 🟡 Low |
| [redstone-contracts](https://github.com/UMAprotocol/redstone-contracts) | Solidity | 0 | 0 | 2024-05-30 | Redstone oracle contracts | 🟡 Low |
| [fast-resolution-rules](https://github.com/UMAprotocol/fast-resolution-rules) | — | 0 | 0 | 2025-09-09 | Rules for fast resolution assertions | 🟠 Medium — defines resolution rules used by Polymarket |
| [docs_ui](https://github.com/UMAprotocol/docs_ui) | HTML | 0 | 4 | 2023-01-10 | Documentation UI | 🟡 Low |
| [zodiac](https://github.com/UMAprotocol/zodiac) | TypeScript | 0 | 0 | 2024-04-16 | Composable tooling for onchain entities | 🟡 Low |
| [across-config-fill-times](https://github.com/UMAprotocol/across-config-fill-times) | — | 0 | 0 | 2024-07-24 | Across bridge config fill times | 🟡 Low |
| [voting-subgraph](https://github.com/UMAprotocol/voting-subgraph) | TypeScript | 0 | 0 | 2021-04-02 | Voting contract events subgraph | 🟡 Low |
| [dev-tools](https://github.com/UMAprotocol/dev-tools) | — | 0 | 0 | 2022-05-27 | Developer support tools monorepo | 🟡 Low |
| [osnap-safe-app](https://github.com/UMAprotocol/osnap-safe-app) | TypeScript | 0 | 0 | 2025-10-21 | oSnap Safe app | 🟡 Low |
| [tools-dapp](https://github.com/UMAprotocol/tools-dapp) | TypeScript | 0 | 0 | 2023-06-06 | Developer tools dApp | 🟡 Low |
| [poap-spreader](https://github.com/UMAprotocol/poap-spreader) | TypeScript | 0 | 0 | 2021-07-20 | POAP distribution tool | 🟡 Low |
| [hardhat-test](https://github.com/UMAprotocol/hardhat-test) | Solidity | 0 | 0 | 2022-07-29 | Hardhat test example | 🟡 Low |
| [generated_data](https://github.com/UMAprotocol/generated_data) | — | 0 | 0 | 2022-04-18 | Generated protocol data | 🟡 Low |
| [discord-mop](https://github.com/UMAprotocol/discord-mop) | TypeScript | 0 | 0 | 2023-07-11 | Discord history cleanup script | 🟡 Low |
| [oval-demo](https://github.com/UMAprotocol/oval-demo) | Solidity | 0 | 1 | 2024-02-22 | Oval demo | 🟡 Low |
| [Hackathon-Prizes-](https://github.com/UMAprotocol/Hackathon-Prizes-) | — | 0 | 0 | 2021-08-16 | Gitcoin hackathon prizes list | 🟡 Low |
| [uma-react](https://github.com/UMAprotocol/uma-react) | TypeScript | 0 | 2 | 2023-05-26 | UMA React component library | 🟡 Low |

### How UMA Connects to Polymarket

UMA provides the **dispute resolution / oracle layer** for Polymarket. Here is the full flow:

1. **Market creation:** Polymarket creates a binary market (YES/NO). Each outcome is represented by a conditional token (ERC-1155) managed by the Gnosis CTF framework.
2. **Market resolution:** When a market's end time is reached, anyone can submit a resolution assertion to the UMA Optimistic Oracle V3 via the `uma-ctf-adapter` contract (`Polymarket/uma-ctf-adapter`).
3. **Challenge window:** The assertion goes through a ~2-hour challenge window. Any UMA token holder can dispute the assertion.
4. **Dispute resolution:** If disputed, UMA token holders vote on the correct outcome (via `voter-dapp-v2`). The vote result is final.
5. **Settlement:** The adapter calls back into the CTF exchange to settle token prices to $1.00 (winner) or $0.00 (loser).

```
Market ends
    └──► uma-ctf-adapter.assertMarket()
             └──► UMA OOv3 assertion (challenge window ~2h)
                      ├── No dispute → auto-settle
                      └── Dispute → UMA voter vote
                               └──► CTF Exchange settles (YES=$1 / NO=$0)
```

### Oracle Integration Notes

- **OOv3 contract (Polygon):** `0x5953f2538F613E05bAED8A5AeFa8e6622467AD3D`
- **UMA-CTF adapter (Polygon):** `0xCB1822859cEF82Cd2Eb4E6276C7916e692995130`
- **Neg-risk adapter (Polygon):** Handles multi-outcome markets
- **Sports oracle:** `uma-sports-oracle` — dedicated contract for sports market resolution
- **Fast resolution rules:** `fast-resolution-rules` repo defines when assertors can bypass the full 2h window

---

## 4. github.com/goldsky-io

### Profile Summary

- **Type:** Official Goldsky organization
- **Total public repos:** 10
- **Primary languages:** TypeScript, Shell, JavaScript, MDX
- **Focus areas:** Blockchain data indexing pipelines, hosted subgraphs, mirror pipelines, developer tooling
- **Polymarket role:** Goldsky hosts the **production subgraph and real-time data pipelines** that power all of Polymarket's market data queries. This is the indexing infrastructure behind the `polymarket-subgraph` queries that bots and the Polymarket frontend use.

### Complete Repository List

| Repo | Language | ⭐ Stars | 🍴 Forks | Last Push | Description |
|---|---|---|---|---|---|
| [goldsky-deploy](https://github.com/goldsky-io/goldsky-deploy) | — | 5 | 0 | 2024-05-31 | Goldsky deployment configurations |
| [documentation-examples](https://github.com/goldsky-io/documentation-examples) | TypeScript | 4 | 3 | 2026-02-17 | Example implementations of Goldsky Mirror Pipelines and Subgraphs |
| [vpoap](https://github.com/goldsky-io/vpoap) | TypeScript | 3 | 0 | 2025-04-23 | POAP event feed demo |
| [agent-skills](https://github.com/goldsky-io/agent-skills) | Shell | 1 | 1 | 2026-03-09 | Agent SKILL.md files for Goldsky CLI |
| [Monet-compose](https://github.com/goldsky-io/Monet-compose) | TypeScript | 0 | 0 | 2026-01-30 | Compose app for Monet design partner |
| [goldsky-agent](https://github.com/goldsky-io/goldsky-agent) | Shell | 0 | 0 | 2026-03-11 | AI agent plugin for Goldsky — skills, agents, commands, and hooks for building blockchain data pipelines |
| [lisk-compose](https://github.com/goldsky-io/lisk-compose) | JavaScript | 0 | 0 | 2026-02-25 | Compose app for Lisk design partner |
| [sway-compose](https://github.com/goldsky-io/sway-compose) | TypeScript | 0 | 0 | 2026-01-21 | Compose app for Sway design partner |
| [docs-v1](https://github.com/goldsky-io/docs-v1) | JavaScript | 0 | 0 | 2023-10-20 | Legacy Goldsky documentation |
| [mintlify-docs](https://github.com/goldsky-io/mintlify-docs) | MDX | 0 | 0 | 2026-01-29 | Current Goldsky documentation (Mintlify) |

### Goldsky's Role in Polymarket Data Infrastructure

Goldsky is a **hosted blockchain data indexing platform** — the successor to The Graph's hosted service for many high-traffic applications. Polymarket uses Goldsky for two key services:

#### 1. Hosted Subgraph
The `Polymarket/polymarket-subgraph` manifest is deployed and served by Goldsky. This allows anyone to query historical and real-time trade data, volume, user positions, and market metadata via GraphQL.

- **Polymarket subgraph endpoint (Goldsky):**  
  `https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/polymarket-subgraph/prod/gn`

- **Alternative GraphQL query:**  
  `https://gamma-api.polymarket.com/query` (Polymarket's own GraphQL gateway, backed by Goldsky)

#### 2. Mirror Pipelines
Goldsky Mirror can stream decoded on-chain events directly to a database (PostgreSQL, Kafka, etc.) in real time. Polymarket uses this for the real-time data layer that powers their WebSocket feeds.

#### Subgraph / API Endpoints Relevant to Trading Bots

| Endpoint | Type | Use Case |
|---|---|---|
| `https://clob.polymarket.com` | REST | Place/cancel orders, query order book |
| `wss://ws-subscriptions-clob.polymarket.com/ws/` | WebSocket | Live order book, trade events, user order updates |
| `https://gamma-api.polymarket.com/markets` | REST | Market metadata, open interest, prices |
| `https://gamma-api.polymarket.com/query` | GraphQL | Historical trades, volume, user positions (via Goldsky) |
| `https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/polymarket-subgraph/prod/gn` | GraphQL | Direct Goldsky subgraph query |

---

## 5. Cross-Reference: How These Orgs Connect

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     POLYMARKET ECOSYSTEM                                │
│                                                                         │
│  ┌─────────────────────────────────────────────────────┐               │
│  │           github.com/Polymarket                      │               │
│  │  • ctf-exchange.sol   (on-chain exchange)            │               │
│  │  • py-clob-client     (Python SDK)                   │               │
│  │  • clob-client        (TypeScript SDK)               │               │
│  │  • rs-clob-client     (Rust SDK)                     │               │
│  │  • real-time-data-client (WebSocket)                 │               │
│  │  • polymarket-cli     (CLI)                          │               │
│  │  • agents             (AI trading agents)            │               │
│  │  • polymarket-subgraph (Graph manifest)              │               │
│  └──────────────┬──────────────────────┬───────────────┘               │
│                 │                      │                                │
│         Oracle Layer           Data / Indexing Layer                   │
│                 │                      │                                │
│  ┌──────────────▼────────┐  ┌──────────▼──────────────┐               │
│  │  github.com/UMAprotocol│  │   github.com/goldsky-io │               │
│  │  • protocol (OOv3)    │  │   • Hosted subgraph      │               │
│  │  • uma-ctf-adapter    │  │   • Mirror pipelines     │               │
│  │  │ (via Polymarket    │  │   • Real-time streaming  │               │
│  │  │  uma-ctf-adapter)  │  │                          │               │
│  │  • voter-dapp-v2      │  └──────────────────────────┘               │
│  │  • subgraphs          │                                              │
│  └───────────────────────┘                                              │
│                                                                         │
│  ┌─────────────────────────────────────────────────────┐               │
│  │         github.com/polymarket-labs                   │               │
│  │  (Currently inactive — no original repos)            │               │
│  └─────────────────────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────────────────────┘
```

### Dependency Map

| Component | Depends On | Provided By |
|---|---|---|
| Market creation & trading | CTF Exchange smart contracts | `Polymarket/ctf-exchange` |
| Order placement (Python) | py-clob-client → CLOB REST API | `Polymarket/py-clob-client` |
| Order placement (TypeScript) | clob-client → CLOB REST API | `Polymarket/clob-client` |
| Order placement (Rust) | rs-clob-client → CLOB REST API | `Polymarket/rs-clob-client` |
| Real-time prices | WebSocket feed | `Polymarket/real-time-data-client` |
| Market resolution | UMA OOv3 + uma-ctf-adapter | `UMAprotocol/protocol` + `Polymarket/uma-ctf-adapter` |
| Historical data (GraphQL) | Goldsky-hosted subgraph | `Polymarket/polymarket-subgraph` deployed on `goldsky-io` |
| Dispute monitoring | UMA voter dApp / dispute CLI | `UMAprotocol/optimistic-oracle-dapp-v2` |

---

## 6. Quick Reference for Bot Developers

> See also: [`bot-dev-quick-reference.md`](./bot-dev-quick-reference.md) — a focused one-page cheat sheet.

### By Task

| Task | Repo | Language |
|---|---|---|
| **Place a limit order** | [py-clob-client](https://github.com/Polymarket/py-clob-client) | Python |
| **Place a limit order** | [clob-client](https://github.com/Polymarket/clob-client) | TypeScript |
| **Place a limit order** | [rs-clob-client](https://github.com/Polymarket/rs-clob-client) | Rust |
| **Subscribe to live order book** | [real-time-data-client](https://github.com/Polymarket/real-time-data-client) | TypeScript |
| **Query historical trades** | [polymarket-subgraph](https://github.com/Polymarket/polymarket-subgraph) | GraphQL |
| **Sign orders manually** | [python-order-utils](https://github.com/Polymarket/python-order-utils) / [clob-order-utils](https://github.com/Polymarket/clob-order-utils) | Python / TS |
| **Browse markets from CLI** | [polymarket-cli](https://github.com/Polymarket/polymarket-cli) | Rust binary |
| **Build an AI trading agent** | [agents](https://github.com/Polymarket/agents) | Python |
| **Understand the exchange contracts** | [ctf-exchange](https://github.com/Polymarket/ctf-exchange) | Solidity |
| **Monitor oracle disputes** | [optimistic-oracle-dapp-v2](https://github.com/UMAprotocol/optimistic-oracle-dapp-v2) | Web UI |
| **Query via GraphQL** | Goldsky subgraph endpoint | GraphQL |

### By Language

| Language | Best Starting Repo |
|---|---|
| Python | [py-clob-client](https://github.com/Polymarket/py-clob-client) |
| TypeScript / JavaScript | [clob-client](https://github.com/Polymarket/clob-client) + [real-time-data-client](https://github.com/Polymarket/real-time-data-client) |
| Rust | [rs-clob-client](https://github.com/Polymarket/rs-clob-client) |
| Go | [go-order-utils](https://github.com/Polymarket/go-order-utils) |
