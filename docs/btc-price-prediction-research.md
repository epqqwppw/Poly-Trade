# Short-Term Bitcoin Price Movement Prediction — Research Report

> **Objective:** Build a binary classification model that predicts whether the closing
> price of a BTC/USDT candle will be **ABOVE** or **BELOW** its opening price — across
> three timeframes: 5-minute, 15-minute, and 1-hour.

---

## Table of Contents

1. [Research Findings by Timeframe](#1-research-findings-by-timeframe)
2. [Feature Engineering Blueprint](#2-feature-engineering-blueprint)
3. [Recommended Model Architecture](#3-recommended-model-architecture)
4. [Optimal Timeframe Decision](#4-optimal-timeframe-decision)
5. [Implementation Roadmap](#5-implementation-roadmap)
6. [Known Risks and Limitations](#6-known-risks-and-limitations)

---

## 1. Research Findings by Timeframe

### 1.1 Five-Minute (5m) Candles

**Signal-to-noise ratio:** Very low. The 5m timeframe is dominated by market
microstructure noise — random tick-level fluctuations, latency arbitrage, and
spoofing artefacts.

| Source / Approach | Key Finding |
|---|---|
| **Scanuto deep-learning live predictions** | 5m candle direction predictions using LSTM auto-encoders achieve ~52–54% accuracy in production — barely above random | 
| **Freqtrade community strategies** | Most profitable Freqtrade strategies operate on ≥15m data; 5m strategies require extremely tight stop-losses and high trade volume to overcome spread + slippage |
| **Academic (arXiv 2405.11431)** | Comparative review of deep learning for crypto: models trained on 1m–5m data consistently underperform those on 15m+ due to noise amplification |
| **QuantConnect forums** | Practitioners report that 5m BTC direction models overfit easily; walk-forward accuracy drops to ~50–51% after a few days without retraining |

**What compensates for noise at 5m:**
- High-frequency volume-imbalance features (bid/ask volume delta)
- Order-flow metrics (trade aggressor side, large-order detection)
- Very short look-back windows (5–20 bars) with frequent model retraining (daily or intra-day)
- Ensemble smoothing (majority vote across 3–5 independently trained models)

### 1.2 Fifteen-Minute (15m) Candles

**Signal-to-noise ratio:** Moderate. The 15m timeframe filters out the worst
microstructure noise while still capturing intraday momentum shifts.

| Source / Approach | Key Finding |
|---|---|
| **CNN-LSTM + Boruta feature selection (Financial Innovation, 2024)** | Binary direction accuracy of ~78–82% on 15m BTC/USDT with 47 technical + on-chain features; Boruta-selected subset of 18 features retained most predictive power |
| **XGBoost with technical indicators (MDPI Risks 13(10), 2025)** | XGBoost achieved highest directional accuracy among tested models on 15m data when using Bollinger Bands, EMA-12/26, and RSI as top-3 features |
| **Transformer + XGBoost hybrid (High Technology Letters, 2024)** | Transformer extracts sequential features → XGBoost classifies direction; MAE 0.011, outperforms standalone LSTM on 15m BTC |
| **TradingView community scripts** | Most popular BTC direction strategies use 15m RSI-divergence + VWAP cross signals; reported live win-rates 55–62% |
| **Reddit r/algotrading** | Consensus: 15m is the "sweet spot" for intraday crypto — enough data points per day (~96) for statistical significance while maintaining signal quality |

**What works at 15m:**
- Momentum indicators: RSI(14), MACD(12,26,9), Stochastic %K/%D
- Volatility envelopes: Bollinger Bands(20,2), Keltner Channels, ATR(14)
- Volume-price confirmation: OBV, VWAP deviation, Accumulation/Distribution
- Multi-timeframe confirmation: align 15m signal with 1h trend direction

### 1.3 One-Hour (1h) Candles

**Signal-to-noise ratio:** Highest among the three intraday timeframes.
Aggregation smooths microstructure noise and captures meaningful
supply/demand shifts.

| Source / Approach | Key Finding |
|---|---|
| **LSTM with conformal prediction (PLOS ONE, 2025)** | 1h BTC direction with calibrated confidence intervals; model achieves 64–68% accuracy with reliable uncertainty quantification — critical for risk management |
| **Random Forest + macroeconomic features (GitHub: BITCOIN-BEHAVIOUR-PREDICTION)** | 1h candle direction with global indices (S&P 500 futures, DXY, VIX) + BTC technicals; RF accuracy ~65% out-of-sample |
| **BiLSTM + attention (IEEE 2024)** | Bidirectional LSTM with attention on 1h OHLCV data; 67% direction accuracy; attention weights highlight close-to-open ratio and volume as most attended features |
| **Cascaded BERT classifier (Frontiers in Blockchain, 2025)** | News-headline sentiment → 1h direction; 79% accuracy when high-confidence sentiment aligns with technical signal |
| **On-chain + technical hybrid (ScienceDirect, 2025)** | Combining on-chain features (active addresses, exchange net flow, NVT) with technicals boosts 1h direction accuracy by 3–5 pp over technicals-only models |

**What works at 1h:**
- Trend indicators: EMA(21), EMA(55), Ichimoku cloud
- On-chain metrics: exchange inflow/outflow ratio, NVT signal, MVRV Z-score
- Cross-asset correlation: DXY (inverted), S&P 500 futures, Gold
- Sentiment: Crypto Fear & Greed Index, social-media NLP scores
- Regime detection: Hidden Markov Model overlay to switch strategy between trending and ranging modes

### 1.4 Cross-Timeframe Synthesis

| Factor | 5m | 15m | 1h |
|---|---|---|---|
| Signal-to-noise ratio | Low | Moderate | High |
| Samples per day | ~288 | ~96 | 24 |
| Overfitting risk | Very high | Moderate | Lower |
| Retraining frequency needed | Daily | Weekly | Bi-weekly |
| Best model family | Light ensembles (XGBoost) | CNN-LSTM / Transformer hybrids | LSTM + attention / ensemble + sentiment |
| Typical OOS accuracy | 50–54% | 58–68% | 60–68% |
| Practical edge after costs | Marginal | Moderate | Moderate-to-good |

---

## 2. Feature Engineering Blueprint

The features below are ranked by estimated predictive importance for binary
candle-direction classification, synthesised from academic studies, open-source
projects, and practitioner reports.

### Tier 1 — Core Price-Action Features (highest predictive power)

| # | Feature | Computation | Why It Matters |
|---|---|---|---|
| 1 | **Lagged returns** (1, 2, 3, 5, 10 bars) | `(close[t-k] - close[t-k-1]) / close[t-k-1]` | Direct momentum signal; captures auto-correlation in returns |
| 2 | **RSI(14)** | Wilder's smoothed relative strength | Most consistently cited directional indicator across all studies; extreme values (>70, <30) are predictive |
| 3 | **MACD histogram** | `MACD_line - Signal_line` | Captures acceleration/deceleration of momentum; zero-line crossovers align with direction changes |
| 4 | **Bollinger Band %B** | `(close - BB_lower) / (BB_upper - BB_lower)` | Normalised position within volatility envelope; mean-reversion signal at extremes |
| 5 | **ATR(14) ratio** | `ATR / close` | Relative volatility; high ATR → trending regime; low ATR → ranging |

### Tier 2 — Volume & Order-Flow Features

| # | Feature | Computation | Why It Matters |
|---|---|---|---|
| 6 | **Volume-weighted average price (VWAP) deviation** | `(close - VWAP) / VWAP` | Institutional reference level; price above/below VWAP indicates buy/sell pressure |
| 7 | **On-balance volume (OBV) slope** | Regression slope of OBV over N bars | Volume confirmation of price moves; divergence predicts reversals |
| 8 | **Buy/sell volume ratio** | `taker_buy_volume / total_volume` | Direct measure of buying pressure per candle (available from Binance API) |
| 9 | **Volume rate of change** | `volume[t] / SMA(volume, 20)` | Relative volume spikes precede breakouts |

### Tier 3 — Multi-Timeframe & Trend Context

| # | Feature | Computation | Why It Matters |
|---|---|---|---|
| 10 | **EMA cross signal** | `sign(EMA_fast - EMA_slow)` for (8/21) and (21/55) | Trend direction filter; align with higher-timeframe trend |
| 11 | **Ichimoku cloud displacement** | `close - Senkou_Span_A` (26-period ahead) | Forward-looking support/resistance |
| 12 | **Higher-TF candle direction** | Direction of the enclosing 1h or 4h candle | Multi-timeframe alignment improves win rate by 3–8 pp (Freqtrade community) |

### Tier 4 — On-Chain & Sentiment (primarily for ≥1h)

| # | Feature | Computation | Why It Matters |
|---|---|---|---|
| 13 | **Exchange net flow (1h)** | `inflow - outflow` to major exchanges | Large inflows precede sell pressure |
| 14 | **NVT signal** | `market_cap / SMA(tx_volume_usd, 90)` | Network valuation vs. usage; high → overvalued |
| 15 | **Active addresses (1h Δ)** | Hour-over-hour change in active addresses | Spike = increased on-chain activity = volatility likely |
| 16 | **Crypto Fear & Greed Index** | Aggregated sentiment score (0–100) | Extreme readings (>80 or <20) moderately predictive of mean-reversion |

### Tier 5 — Cross-Asset & Calendar Features

| # | Feature | Computation | Why It Matters |
|---|---|---|---|
| 17 | **DXY (US Dollar Index) return** | 1h lagged DXY return | Persistent inverse correlation with BTC |
| 18 | **S&P 500 futures return** | 1h lagged ES return | Risk-on/risk-off proxy |
| 19 | **Hour-of-day (cyclical encoding)** | `sin(2π·hour/24)`, `cos(2π·hour/24)` | Asian/EU/US session effects on BTC volatility and direction |
| 20 | **Day-of-week (cyclical encoding)** | `sin(2π·weekday/7)`, `cos(2π·weekday/7)` | Weekend liquidity effects |

### Feature Selection Guidance

- **For 5m models:** Use Tiers 1–2 only (10 features). More features → more
  overfitting. Apply Boruta or recursive feature elimination.
- **For 15m models:** Use Tiers 1–3 (12 features). Add multi-timeframe context.
  Boruta feature selection consistently outperforms manual selection.
- **For 1h models:** Use all Tiers (up to 20 features). On-chain and
  sentiment features become meaningful at this aggregation level.

---

## 3. Recommended Model Architecture

### 3.1 Primary Recommendation: Two-Stage Ensemble

Based on the convergence of academic results and practitioner experience, we
recommend a **two-stage architecture** that combines the strengths of gradient-
boosted trees for tabular features with a sequential model for temporal patterns.

```
┌──────────────────────────────────────────────────────────┐
│                    STAGE 1: Feature Branch                │
│                                                          │
│  OHLCV + Indicators ──► XGBoost / LightGBM              │
│                          (tabular features)              │
│                          Output: probability p₁          │
│                                                          │
│  OHLCV sequence ──► 1D-CNN(3 layers) → BiLSTM(2 layers) │
│                          (temporal patterns)             │
│                          Output: probability p₂          │
│                                                          │
├──────────────────────────────────────────────────────────┤
│                   STAGE 2: Meta-Learner                   │
│                                                          │
│  [p₁, p₂, regime_state] ──► Logistic Regression         │
│                              Output: final probability   │
│                              Threshold: 0.50 (tune)      │
└──────────────────────────────────────────────────────────┘
```

**Why this architecture:**

1. **XGBoost/LightGBM** excels at exploiting non-linear interactions among
   tabular features (indicators, ratios, sentiment scores). Studies consistently
   show XGBoost matches or beats deep learning for pure directional
   classification when features are well-engineered.

2. **1D-CNN → BiLSTM** captures local patterns (CNN convolutions) and longer
   temporal dependencies (BiLSTM) from raw OHLCV sequences. The CNN-LSTM
   family has achieved the highest reported accuracy (~82%) for BTC direction
   prediction.

3. **Meta-learner** (logistic regression or shallow neural net) combines both
   probabilities with a regime indicator (trending/ranging from HMM). This
   avoids the common failure mode of a single model that works in trends but
   fails in ranges (or vice versa).

### 3.2 Hyperparameter Guidelines

#### XGBoost / LightGBM Branch

| Parameter | Recommended Range | Notes |
|---|---|---|
| `n_estimators` | 200–500 | Use early stopping on validation set |
| `max_depth` | 4–7 | Shallow trees reduce overfitting on noisy financial data |
| `learning_rate` | 0.01–0.05 | Lower rates + more trees = better generalisation |
| `subsample` | 0.7–0.9 | Row sampling for robustness |
| `colsample_bytree` | 0.6–0.8 | Feature sampling to decorrelate trees |
| `scale_pos_weight` | Auto (balanced) | BTC candles are ~50/50 up/down; adjust if class imbalance exists |
| `eval_metric` | `logloss` | Binary classification; monitor AUC-ROC too |

#### CNN-BiLSTM Branch

| Parameter | Recommended Range | Notes |
|---|---|---|
| Input sequence length | 20–60 bars | 20 bars for 5m; 40 for 15m; 60 for 1h |
| 1D-CNN filters | [32, 64, 128] × kernel_size=3 | Three convolutional layers with batch norm |
| BiLSTM units | [64, 32] (2 layers) | Bidirectional captures both past and future context in sequence |
| Dropout | 0.3–0.5 | Between CNN and LSTM layers; after LSTM |
| Dense head | 64 → 1 (sigmoid) | Binary output |
| Optimiser | Adam, lr=1e-3 → 1e-4 (scheduler) | ReduceLROnPlateau with patience=5 |
| Batch size | 256–1024 | Larger batches stabilise gradients on noisy data |
| Epochs | 50–100 | With early stopping (patience=10) on validation loss |

#### Regime Detector (Hidden Markov Model)

| Parameter | Recommended Value | Notes |
|---|---|---|
| Number of hidden states | 2 (trending, ranging) | Start simple; 3 states add marginal value |
| Observable features | ATR ratio, ADX, return auto-correlation | Volatility and trend-strength proxies |
| Library | `hmmlearn` (Python) | Gaussian HMM with diagonal covariance |
| Refit frequency | Weekly | Regime parameters shift slowly |

### 3.3 Alternative Architectures (Considered)

| Architecture | Pros | Cons | When to Use |
|---|---|---|---|
| **Standalone XGBoost** | Fastest to iterate; strong baseline | Misses sequential patterns | MVP / rapid prototyping |
| **Transformer (encoder-only)** | Captures long-range dependencies without recurrence | Data-hungry; overkill for ≤60 bar sequences | If you have >1M training samples |
| **Temporal Fusion Transformer (TFT)** | Built-in attention + variable selection + multi-horizon | Complex; slow to train | Multi-step forecasting (not pure direction) |
| **Reinforcement learning (DQN/PPO)** | Directly optimises trading P&L | Unstable training; reward shaping is hard | When you want end-to-end strategy, not classification |

---

## 4. Optimal Timeframe Decision

### Recommendation: **15-minute candles**

The 15m timeframe offers the best trade-off between signal quality and sample
volume for binary candle-direction classification. Here is the rationale:

### 4.1 Evidence Summary

| Criterion | 5m | 15m ✓ | 1h |
|---|---|---|---|
| OOS direction accuracy (literature) | 50–54% | 58–68% | 60–68% |
| Samples per day | ~288 | ~96 | 24 |
| Statistical significance per week | ✓✓✓ | ✓✓ | ✗ (only 168) |
| Overfitting risk | Very high | Moderate | Lower |
| Latency to update model | Minutes | Minutes | Hours |
| Feature availability | OHLCV only | OHLCV + indicators | OHLCV + on-chain + sentiment |
| Practical trading cost impact | High (many trades, spread matters) | Moderate | Low |
| Retraining cadence | Daily | Weekly | Bi-weekly |

### 4.2 Detailed Rationale

1. **Accuracy ceiling is comparable to 1h but with 4× more samples.** The best
   reported 15m accuracy (~68%) is within the same range as 1h (~68%), but
   15m produces ~96 signals per day versus 24. More signals → more
   opportunities to compound a small edge, and more data for training.

2. **5m is noise-dominated.** Below 52–54% out-of-sample, the edge is consumed
   by trading costs (spread + slippage on Binance is ~0.02–0.05% per side).
   Even fee-free Polymarket CLOB markets have latency-driven adverse
   selection.

3. **15m strikes the balance for Polymarket BTC Up/Down markets.** These
   markets resolve in 5m or 15m windows. Having a model tuned to 15m
   resolution aligns directly with the dominant Polymarket settlement
   cadence, reducing the gap between prediction and resolution.

4. **Regime detection works at 15m.** A 2-state HMM requires ~50+ observations
   for reliable state estimation. At 15m, that is ~12.5 hours — short enough
   to be adaptive within a single trading day.

5. **Feature engineering is richer than 5m but does not depend on slow data.**
   Unlike 1h models that benefit from on-chain and sentiment data (which
   update hourly or slower), 15m models rely on OHLCV and technical
   indicators that are available in real time.

### 4.3 When to Reconsider

- If deploying on **Polymarket 5m markets**, build a separate thin model using
  Tiers 1–2 features only, with XGBoost and daily retraining.
- If you have **reliable real-time on-chain data** and sentiment feeds, the 1h
  model can achieve comparable accuracy with lower trading costs.

---

## 5. Implementation Roadmap

### Phase 1 — Data Pipeline (Week 1)

| Step | Task | Tools |
|---|---|---|
| 1.1 | Collect BTC/USDT 15m OHLCV data (≥2 years) | **CCXT** library → Binance REST API; store as Parquet files |
| 1.2 | Compute technical indicators | **pandas-ta** or **TA-Lib** (RSI, MACD, BB, ATR, OBV, VWAP, EMA, Stochastic, Ichimoku) |
| 1.3 | Compute volume features | Buy/sell ratio from Binance `aggTrades` or `klines` taker-buy fields |
| 1.4 | (Optional) Collect on-chain data | **Glassnode API** or **CryptoQuant API** for exchange flows, NVT, active addresses |
| 1.5 | Create target label | `y = 1 if close > open else 0` for each candle |
| 1.6 | Store dataset | Single Parquet file; schema: `timestamp, open, high, low, close, volume, [features...], y` |

### Phase 2 — Feature Engineering & Selection (Week 2)

| Step | Task | Tools |
|---|---|---|
| 2.1 | Compute all Tier 1–3 features (see §2) | pandas-ta, NumPy |
| 2.2 | Handle missing data | Forward-fill for indicators with warm-up periods; drop first N rows |
| 2.3 | Normalise features | Per-window z-score normalisation (fit on training window only) |
| 2.4 | Run Boruta feature selection | **boruta_py** (wrapper around Random Forest) |
| 2.5 | Analyse selected features | SHAP values from a preliminary XGBoost model for interpretability |

### Phase 3 — Model Training (Week 3)

| Step | Task | Tools |
|---|---|---|
| 3.1 | Split data: walk-forward scheme | `TimeSeriesSplit` from scikit-learn; 5 folds; optional 1-day gap between train/test |
| 3.2 | Train XGBoost branch | **xgboost** / **lightgbm**; hyperopt with **Optuna** |
| 3.3 | Train CNN-BiLSTM branch | **PyTorch** or **TensorFlow/Keras**; GPU recommended |
| 3.4 | Train HMM regime detector | **hmmlearn** Gaussian HMM on ATR ratio + ADX |
| 3.5 | Train meta-learner | Logistic regression on stacked out-of-fold predictions from 3.2–3.4 |
| 3.6 | Evaluate on held-out final test set (most recent 3 months) | Accuracy, precision, recall, F1, AUC-ROC, log-loss |

### Phase 4 — Backtesting (Week 4)

| Step | Task | Tools |
|---|---|---|
| 4.1 | Implement trading simulator | **Backtrader** or **Jesse** or custom; long-only or long/short on each candle |
| 4.2 | Define execution model | Enter at next-candle open; exit at candle close; include 0.04% round-trip cost |
| 4.3 | Run walk-forward backtest | Iterate over Phase 3 walk-forward folds; record P&L, Sharpe, max drawdown, win rate |
| 4.4 | Compare against baselines | (a) Always-long, (b) Random, (c) Buy-and-hold BTC |
| 4.5 | Statistical significance | Paired t-test or bootstrap confidence intervals on fold-level accuracy |

### Phase 5 — Validation & Deployment (Week 5+)

| Step | Task | Tools |
|---|---|---|
| 5.1 | Paper-trade for ≥2 weeks | Existing Poly-Trade `PaperEngine` or Binance testnet via CCXT |
| 5.2 | Monitor live vs. backtest metrics | Log predictions, actual outcomes, and P&L; compute rolling accuracy |
| 5.3 | Set up retraining pipeline | Weekly cron job: fetch new data → retrain → evaluate → deploy if improved |
| 5.4 | Integrate with Polymarket | Use `py-clob-client` to place directional bets on BTC Up/Down 15m markets |
| 5.5 | Alerting & kill switch | If rolling 50-trade accuracy < 52% or daily loss > threshold → stop trading |

### Evaluation Metrics Checklist

| Metric | Target | Notes |
|---|---|---|
| **Accuracy** | ≥ 58% OOS | Baseline is 50% (coin flip) |
| **AUC-ROC** | ≥ 0.60 | Measures ranking quality of probability |
| **Precision (bullish class)** | ≥ 0.57 | Avoid false bullish signals |
| **F1 score** | ≥ 0.57 | Harmonic mean of precision and recall |
| **Sharpe ratio (backtest)** | ≥ 1.0 | Risk-adjusted return |
| **Max drawdown** | ≤ 15% | Capital preservation |
| **Win rate** | ≥ 55% | Minimum for positive expectancy with 1:1 R:R |

---

## 6. Known Risks and Limitations

### 6.1 Data Leakage Pitfalls

| Risk | Description | Mitigation |
|---|---|---|
| **Look-ahead bias in indicators** | Indicators that use future data points (e.g., centred moving averages, Ichimoku spans plotted forward) | Use only causal (backward-looking) computations; audit every feature |
| **Leaking through normalisation** | Fitting StandardScaler or MinMaxScaler on the entire dataset before train/test split | Fit scaler on training window only; transform test window with training parameters |
| **Target leakage** | Accidentally including close price or close-derived features that encode the target | Remove `close` from features when predicting close-vs-open direction; only use lagged close |
| **Shuffled cross-validation** | Standard k-fold destroys temporal order, leaking future into past | Always use `TimeSeriesSplit` or walk-forward validation |

### 6.2 Overfitting Traps

| Risk | Description | Mitigation |
|---|---|---|
| **Too many features relative to samples** | 20+ features on 5m data with small windows → model memorises noise | Boruta/RFE feature selection; start with ≤10 features for 5m |
| **Hyperparameter over-optimisation** | Extensive grid search on limited data finds parameters that fit noise | Use Optuna with a separate validation fold; limit trials to 100 |
| **Survivorship bias in indicator choice** | Selecting indicators that "worked" in the past without out-of-sample confirmation | Walk-forward feature selection: re-run Boruta on each training window |
| **Backtesting on training period** | Reporting in-sample metrics as if they represent future performance | Always report out-of-sample metrics only; use final held-out test set |
| **Complexity creep** | Adding model layers or ensemble members until backtest Sharpe is artificially high | Monitor train-test gap; if train accuracy is 20+ pp above test → simplify |

### 6.3 Market Regime Shifts

| Risk | Description | Mitigation |
|---|---|---|
| **Bull/bear regime change** | Model trained in a bull market fails in a bear market (different volatility, correlation structure) | Include regime detector (HMM); retrain weekly with expanding window |
| **Volatility regime change** | Transition from low-vol range to high-vol breakout invalidates mean-reversion features | Use ATR-normalised features; add regime state as an input to the meta-learner |
| **Structural market changes** | Exchange fee changes, new derivatives (e.g., BTC ETF options), regulatory events | Monitor model performance continuously; retrain on regime shifts |
| **Black swan events** | Flash crashes, exchange hacks, protocol exploits | Implement a kill switch (daily loss limit + drawdown limit); size positions conservatively |

### 6.4 Latency Considerations

| Risk | Description | Mitigation |
|---|---|---|
| **Prediction latency** | Model inference must complete before candle close to act on the prediction | Benchmark inference time; XGBoost is <1ms; CNN-LSTM <50ms on GPU; schedule inference at T-10s |
| **Data latency** | Exchange WebSocket feed delay, on-chain data lag (blocks confirm every ~10 min) | Use OHLCV features that are complete by T-5s; avoid on-chain features for 5m models |
| **Execution latency** | Order placement and fill time on Polymarket CLOB | Use limit orders placed in advance; adjust for partial fills |

### 6.5 Polymarket-Specific Risks

| Risk | Description | Mitigation |
|---|---|---|
| **Low liquidity on BTC 5m/15m markets** | Thin order books → wide spreads, adverse selection | Check book depth before trading; skip low-liquidity markets |
| **Resolution oracle delay** | Chainlink oracle may report price slightly after candle close | Verify historical oracle timestamps vs. candle close times |
| **Fee curve** | `fee = max_fee × 4p(1-p)` — fees are highest at p=0.5 (maximum uncertainty) | Target trades where model confidence is high (p > 0.6 or p < 0.4) |
| **Counterparty concentration** | Market makers dominate BTC Up/Down books; trading against sophisticated MMs | Focus on time periods with higher retail flow; avoid low-liquidity overnight hours |

### 6.6 General Limitations

1. **No model predicts consistently above ~68% on OOS BTC data.** Any claim of
   >75% sustained accuracy should be treated with extreme scepticism — it
   likely reflects data leakage or in-sample reporting.

2. **Transaction costs erode thin edges.** A 55% win rate with 1:1 reward:risk
   yields 10% of capital returned per 100 trades before costs. At
   0.02–0.05% per trade, 100 trades cost 2–5% — a significant fraction
   of gross profits.

3. **The efficient market hypothesis applies.** BTC/USDT is one of the most
   liquid, most-traded pairs globally. Persistent edges attract capital
   until the edge disappears. Continuous retraining and adaptation are
   essential.

4. **Sentiment and on-chain data are noisy and lagging.** Their value is
   primarily for the 1h+ timeframe and for regime context, not for
   real-time direction calls.

5. **This is a binary classification task, not magnitude prediction.** A correct
   direction call on a 0.01% candle is scored the same as one on a 2%
   candle. Consider augmenting with a confidence/magnitude model for
   position sizing.

---

## References

### Academic Papers & Preprints

1. **Akyildirim et al.** "Deep learning for Bitcoin price direction prediction: models and trading strategies." *Financial Innovation* 10, 2024. [Springer](https://link.springer.com/article/10.1186/s40854-024-00643-1)
2. **Yao et al.** "Review of deep learning models for crypto price prediction." arXiv:2405.11431, 2024. [arXiv](https://arxiv.org/html/2405.11431v1)
3. **Lee et al.** "Bitcoin price direction prediction using on-chain data and feature selection." *Decision Analytics Journal*, 2025. [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S266682702500057X)
4. **Athari & Hung.** "Cryptocurrency Forecasting Using Deep Learning Models: A Comparative Analysis." *High Technology Letters*, 2024. [HTL](https://www.hightechjournal.org/index.php/HIJ/article/view/641)
5. **Chen et al.** "LSTM-conformal forecasting-based bitcoin forecasting method for enhanced reliability." *PLOS ONE*, 2025. [PLOS](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0319008)
6. **Santos et al.** "Short-term cryptocurrency price forecasting based on news sentiment." *Frontiers in Blockchain*, 2025. [Frontiers](https://www.frontiersin.org/journals/blockchain/articles/10.3389/fbloc.2025.1627769/full)
7. **Gülmez.** "The BTC Price Prediction Paradox Through Methodological Pluralism." *MDPI Risks* 13(10):195, 2025. [MDPI](https://www.mdpi.com/2227-9091/13/10/195)
8. **Li & Pasquier.** "Regime switching forecasting for cryptocurrencies." *Digital Finance*, 2024. [Springer](https://link.springer.com/article/10.1007/s42521-024-00123-2)
9. **Preprints.org.** "Markov and Hidden Markov Models for Regime Detection in Cryptocurrency Markets." 2026. [Preprints](https://www.preprints.org/manuscript/202603.0831/v1)

### GitHub Repositories

10. **independentmisfit/Bitcoin-Price-Prediction-Models** — ARIMA, XGBoost, LSTM comparison. [GitHub](https://github.com/independentmisfit/Bitcoin-Price-Prediction-Models)
11. **Vassilis-Dell/Bitcoin-price-prediction-with-Sentiment-Analysis-using-XGBoost** — Walk-forward XGBoost + GARCH + sentiment. [GitHub](https://github.com/Vassilis-Dell/Bitcoin-price-prediction-with-Sentiment-Analysis-using-XBGoost)
12. **AaronFlore/Forecasting-Bitcoin-Prices** — ARIMA, Prophet, XGBoost, LSTM notebook. [GitHub](https://github.com/AaronFlore/Forecasting-Bitcoin-Prices)
13. **TheRealMathematician/Deep-Learning-for-Financial-Time-Series-Prediction** — Walk-forward DL pipeline. [GitHub](https://github.com/TheRealMathematician/Deep-Learning-for-Financial-Time-Series-Prediction)
14. **saadrizvi09/Markov-Switching** — Hybrid HMM-SVR crypto regime detector. [GitHub](https://github.com/saadrizvi09/Markov-Switching)
15. **jesse-ai/jesse** — Advanced crypto trading bot with backtesting. [GitHub](https://github.com/jesse-ai/jesse)

### Tools & Libraries

16. **CCXT** — Unified API for 100+ crypto exchanges. [GitHub](https://github.com/ccxt/ccxt)
17. **pandas-ta** — 130+ technical indicators for pandas. [GitHub](https://github.com/twopirllc/pandas-ta)
18. **TA-Lib** — Technical analysis C library with Python wrapper. [ta-lib.org](https://ta-lib.org/)
19. **Freqtrade** — Open-source crypto trading bot with hyperopt. [freqtrade.io](https://www.freqtrade.io/)
20. **Backtrader** — Python backtesting framework. [backtrader.com](https://www.backtrader.com/)
21. **XGBoost** — Gradient boosted trees. [xgboost.readthedocs.io](https://xgboost.readthedocs.io/)
22. **hmmlearn** — Hidden Markov Models for Python. [GitHub](https://github.com/hmmlearn/hmmlearn)
23. **Optuna** — Hyperparameter optimisation framework. [optuna.org](https://optuna.org/)
24. **SHAP** — SHapley Additive exPlanations for model interpretability. [GitHub](https://github.com/shap/shap)

### Community & Practitioner Sources

25. **Reddit r/algotrading** — Practitioner discussions on crypto ML models.
26. **QuantConnect forums** — Walk-forward validation best practices.
27. **TradingView** — Community strategy scripts for BTC direction.
28. **Towards Data Science** — Backtesting best practices articles.
29. **QuantInsti Blog** — "Market Regime using Hidden Markov Model." [Blog](https://blog.quantinsti.com/regime-adaptive-trading-python/)
