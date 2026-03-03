# Analysis Brief: HY-IG Credit Spread vs S&P 500 Returns

**Author:** Alex (Lead Analyst)
**Date:** 2026-02-28
**Status:** Phase 0 — Distributed to all agents

---

## 1. Research Question

Does the high-yield minus investment-grade (HY-IG) credit spread predict S&P 500 equity returns? If so, through what mechanism, at what horizons, and can it be profitably traded?

## 2. Hypotheses

| # | Hypothesis | Identification Strategy |
|---|-----------|----------------------|
| H1 | HY-IG spread changes **lead** SPY returns, with stronger predictive power during stress | Toda-Yamamoto Granger causality, transfer entropy, local projections — tested in both directions and per regime |
| H2 | The relationship is **nonlinear** — it activates at stress thresholds that are regime-dependent, not fixed | Markov-switching, HMM, quantile regression, data-driven threshold detection (Jenks, GMM, CUSUM) |
| H3 | A credit-signal equity strategy **beats buy-and-hold** out-of-sample after transaction costs | Combinatorial tournament across signals, thresholds, strategies, lookbacks, and lead times; walk-forward validation with bootstrap significance |

## 3. Sample

- **Period:** 2000-01-01 to 2025-12-31 (daily, business-day calendar)
- **In-sample:** 2000-01-01 to 2017-12-31 (18 years, ~4,500 obs)
- **Out-of-sample:** 2018-01-01 to 2025-12-31 (8 years, ~2,000 obs)
- **Rationale:** OOS includes 2018 vol spike, 2020 COVID crash, 2022 rate shock, 2023-25 recovery — a rich stress-test window

## 4. Data Requirements

### 4.1 Core Series (23 raw)

| # | Variable | Source | Series ID / Ticker | Priority |
|---|----------|--------|--------------------|----------|
| 1 | HY OAS | FRED | BAMLH0A0HYM2 | Core |
| 2 | IG OAS | FRED | BAMLC0A0CM | Core |
| 3 | BB HY OAS | FRED | BAMLH0A1HYBB | Core |
| 4 | CCC HY OAS | FRED | BAMLH0A3HYC | Core |
| 5 | SPY | Yahoo | SPY | Core |
| 6 | VIX | Yahoo | ^VIX | Core |
| 7 | VIX3M | Yahoo | ^VIX3M | Core |
| 8 | 10Y Treasury | FRED | DGS10 | Core |
| 9 | 3M Treasury | FRED | DTB3 | Core |
| 10 | 2Y Treasury | FRED | DGS2 | Core |
| 11 | NFCI | FRED | NFCI | Core |
| 12 | KBE (Bank ETF) | Yahoo | KBE | Core |
| 13 | IWM (Small-Cap ETF) | Yahoo | IWM | Secondary |
| 14 | MOVE Index | Yahoo | ^MOVE | Secondary |
| 15 | Initial Claims | FRED | ICSA | Secondary |
| 16 | Fed Funds Rate | FRED | DFF | Secondary |
| 17 | BBB OAS | FRED | BAMLC0A4CBBB | Secondary |
| 18 | FSI (Financial Stress) | FRED | STLFSI2 | Secondary |
| 19 | Gold | Yahoo | GC=F | Secondary |
| 20 | Copper | Yahoo | HG=F | Secondary |
| 21 | DXY (Dollar Index) | Yahoo | DX-Y.NYB | Secondary |
| 22 | SOFR | FRED | SOFR | Secondary |
| 23 | HYG (HY Bond ETF) | Yahoo | HYG | Secondary |

### 4.2 Derived Series (15+)

| # | Derived Variable | Computation |
|---|-----------------|-------------|
| D1 | HY-IG Spread | BAMLH0A0HYM2 − BAMLC0A0CM |
| D2 | HY-IG Z-Score (252d) | (spread − rolling_mean_252) / rolling_std_252 |
| D3 | HY-IG Z-Score (504d) | (spread − rolling_mean_504) / rolling_std_504 |
| D4 | HY-IG Percentile Rank (504d) | rolling_rank_504 / 504 |
| D5 | HY-IG Percentile Rank (1260d) | rolling_rank_1260 / 1260 |
| D6 | HY-IG RoC 21d | (spread / spread.shift(21) − 1) × 100 |
| D7 | HY-IG RoC 63d | (spread / spread.shift(63) − 1) × 100 |
| D8 | HY-IG RoC 126d | (spread / spread.shift(126) − 1) × 100 |
| D9 | HY-IG MoM Change (21d) | spread − spread.shift(21) |
| D10 | HY-IG QoQ Change (63d) | spread − spread.shift(63) |
| D11 | HY-IG YoY Change (252d) | spread − spread.shift(252) |
| D12 | Spread Acceleration | D6 − D6.shift(21) (diff of 21d RoC) |
| D13 | CCC-BB Quality Spread | BAMLH0A3HYC − BAMLH0A1HYBB |
| D14 | Spread Realized Vol (21d) | rolling_std(daily_diff, 21) |
| D15 | VIX Term Structure | VIX3M − VIX |
| D16 | 10Y-3M Spread | DGS10 − DTB3 |
| D17 | 10Y-2Y Spread | DGS10 − DGS2 |
| D18 | Bank/SmallCap Relative Strength | KBE / IWM (ratio) |
| D19 | NFCI Momentum (13w) | NFCI − NFCI.shift(13) (weekly, ffill to daily) |
| D20 | BBB-IG Spread | BAMLC0A4CBBB − BAMLC0A0CM |

### 4.3 Forward SPY Returns (Dependent Variables)

| Horizon | Computation |
|---------|-------------|
| 1d | SPY.pct_change(1).shift(-1) |
| 5d | (SPY.shift(-5) / SPY − 1) |
| 21d | (SPY.shift(-21) / SPY − 1) |
| 63d | (SPY.shift(-63) / SPY − 1) |
| 126d | (SPY.shift(-126) / SPY − 1) |
| 252d | (SPY.shift(-252) / SPY − 1) |

## 5. Combinatorial Tournament Design

### 5.1 Dimensions

**Signal (S1-S13):**

| ID | Signal | Variants |
|----|--------|----------|
| S1 | HY-IG Spread Level | Raw |
| S2 | HY-IG Spread Z-Score | 252d, 504d lookback |
| S3 | HY-IG Spread Percentile Rank | 504d, 1260d lookback |
| S4 | HY-IG Spread Rate of Change | 21d, 63d, 126d |
| S5 | CCC-BB Quality Spread | Raw |
| S6 | HMM Regime State | 2-state, 3-state |
| S7 | Markov-Switching Regime | 2-state, 3-state |
| S8 | Composite (Z-Score + VIX Term) | Equal weight, optimized weight |
| S9 | Random Forest Probability | Walk-forward predicted prob |
| S10 | HY-IG MoM Change (21d) | Monthly momentum |
| S11 | HY-IG QoQ Change (63d) | Quarterly momentum |
| S12 | HY-IG YoY Change (252d) | Annual momentum |
| S13 | Spread Acceleration | Diff of 21d RoC |

**Signal Lead Time (L0-L252):**

| ID | Lag | Meaning |
|----|-----|---------|
| L0 | 0d | Same-day signal |
| L1 | 1d | Previous day |
| L5 | 5d | 1-week lag |
| L10 | 10d | 2-week lag |
| L21 | 21d | 1-month lag |
| L42 | 42d | 2-month lag |
| L63 | 63d | 1-quarter lag |
| L126 | 126d | 6-month lag |
| L252 | 252d | 1-year lag |

A 21-day lagged signal means we use the spread indicator value from 21 trading days ago to make today's equity position decision. If the tournament winner uses L21, it means credit spreads lead equities by ~1 month.

**Threshold Method (T1-T7):**

| ID | Method | Variants |
|----|--------|----------|
| T1 | Fixed percentile | 75th, 80th, 85th, 90th, 95th |
| T2 | Rolling percentile (504d) | 75th, 80th, 85th, 90th, 95th |
| T3 | Bollinger Band (mean ± k*std) | k=1.5, 2.0, 2.5 |
| T4 | Jenks Natural Breaks | 2, 3, 4 clusters |
| T5 | GMM cluster boundaries | 2, 3 states |
| T6 | HMM posterior probability | p>0.5, p>0.7, p>0.9 |
| T7 | CUSUM change-point | Sensitivity sweep |

**Strategy Type (P1-P4):**

| ID | Strategy | Description |
|----|----------|-------------|
| P1 | Long/Cash | Long SPY when calm, cash when stressed |
| P2 | Signal-strength sizing | Weight = 1 − normalized_signal, floored at 0 |
| P3 | Vol-targeting (10%) | target_vol / realized_vol, gated by signal |
| P4 | Long/Short | Long calm, short stressed |

**Lookback Window:** 126d, 252d, 504d, 1260d

### 5.2 Tournament Rules

- **Prune nonsensical combinations** (e.g., HMM signal + HMM threshold is redundant)
- **Expected meaningful combinations:** ~800-1,200 after pruning
- **Primary ranking:** OOS Sharpe ratio (2018-2025)
- **Tiebreakers:** Sortino → Calmar → max drawdown (least negative)
- **Validity filters:** Reject OOS Sharpe < 0, turnover > 24x/year, < 30 OOS trades
- **Mandatory benchmark:** Buy-and-hold SPY

### 5.3 Validation on Top Combinations (Top 5)

| Validation | Details |
|-----------|---------|
| Walk-forward | 5yr train / 1yr test, roll annually |
| Bootstrap significance | 10,000 samples, p-value for Sharpe > 0 |
| Stress tests | GFC (2007-09), COVID (2020), Taper Tantrum (2013), 2022 Rate Shock |
| Transaction costs | 5 bps round-trip + breakeven analysis |
| Signal decay | 1, 2, 3, 5-day execution delay |

## 6. Lead/Lag & Causality Framework

### 6.1 Directionality

Test causality in **both directions**:
- Credit → Equity: Do spread changes predict SPY returns?
- Equity → Credit: Do SPY returns predict spread changes? (reverse causality check)

### 6.2 Methods

| Method | Purpose | Specification |
|--------|---------|--------------|
| Toda-Yamamoto Granger | Linear causality | Augmented VAR at lags 1, 5, 10, 21, 42, 63, 126, 252 days |
| Transfer entropy | Nonlinear causality | Both directions; compare to Granger |
| Cross-correlation function | Lead-lag structure | Pre-whitened CCF at lags −20 to +20 |
| Local projections (Jordà) | Impulse responses | h=1, 5, 10, 21, 42, 63 days; state-dependent version |

### 6.3 Regime-Conditional Causality

Repeat Granger and transfer entropy tests separately for:
- **Stress regime** (top quartile HY-IG spread or HMM stress state)
- **Calm regime** (bottom three quartiles or HMM calm state)
- Report whether causal direction or strength changes across regimes

## 7. Econometric Stages

### Stage 1 — Exploratory

- Pearson, Spearman, Kendall correlation
- Rolling 252d correlation (Pearson + distance correlation)
- Pre-whitened CCF at lags −20 to +20
- Descriptive stats by HY-IG spread quartile (SPY return, vol, Sharpe)
- KDE regime boundary detection

### Stage 2 — Core Models

| Model | Key Parameters |
|-------|---------------|
| Toda-Yamamoto Granger | Both directions, 8 lag orders, per-regime |
| Transfer entropy | Both directions, per-regime |
| Johansen cointegration + VECM | If cointegrated |
| Markov-switching regression | 2-state and 3-state, SPY ~ HY-IG spread changes |
| Gaussian HMM | 2 and 3-state on HY-IG + VIX jointly |
| PELT change-point detection | Compare to event timeline |
| GJR-GARCH | SPY returns, HY-IG change as exogenous |
| Quantile regression | SPY at τ = 0.05, 0.10, 0.25, 0.50, 0.75, 0.90 |
| Random Forest + SHAP | Walk-forward, feature importance |
| Local projections (Jordà) | h = 1, 5, 10, 21, 42, 63; state-dependent |

**Diagnostics for every model:** Jarque-Bera, Breusch-Pagan, Breusch-Godfrey, RESET, stationarity confirmation.

**Sensitivity:** Alternative lags, excl. GFC, excl. COVID, alternative thresholds.

### Stage 3 — Combinatorial Tournament Backtest

See Section 5 above.

## 8. Deliverables by Agent

### Ray (Research)
1. Spec memo → `docs/spec_memo_hy_ig_spy_20260228.md`
2. Full research brief → `docs/research_brief_hy_ig_spy_20260228.md` (20+ citations)
3. Event timeline → embedded in research brief (15+ events, 2000-2025)
4. Portal narrative → `docs/portal_narrative_hy_ig_spy_20260228.md`
5. Storytelling arc → `docs/storytelling_arc_hy_ig_spy_20260228.md`

### Dana (Data)
1. Master dataset → `data/hy_ig_spy_daily_20000101_20251231.parquet`
2. Data dictionary → `data/data_dictionary_hy_ig_spy_20260228.csv`
3. Stationarity tests → `results/stationarity_tests_20260228.csv`
4. Missing value report → `data/missing_value_report_20260228.md`
5. Latest alias → `data/hy_ig_spy_daily_latest.parquet` (symlink)

### Evan (Econometrics)
1. Exploratory results → `results/exploratory_20260228/`
2. Core model results → `results/core_models_20260228/`
3. Tournament results → `results/tournament_results_20260228.csv`
4. Top-5 validation → `results/tournament_validation_20260228/`
5. Chart request templates → `results/chart_requests_20260228/`

### Vera (Visualization)
1. Plotly JSON files → `output/charts/plotly/`
2. PNG fallbacks → `output/charts/png/`
3. Chart metadata → `output/charts/metadata/`

### Ace (App Dev)
1. Streamlit portal → `app/`
2. Deployed URL → Streamlit Community Cloud

## 9. Portal Architecture

```
app/
  app.py                    # Landing: finding index + executive summary
  pages/
    1_hy_ig_story.py        # Finding 1 — Story (layperson narrative)
    2_hy_ig_evidence.py     # Finding 1 — Evidence (interactive charts)
    3_hy_ig_strategy.py     # Finding 1 — Strategy (tournament winner + alternatives)
    4_hy_ig_methodology.py  # Finding 1 — Methodology (technical appendix)
  components/
    charts.py               # Plotly JSON loader + interactive controls
    metrics.py              # KPI card renderer
    narrative.py            # Markdown with glossary tooltips
    sidebar.py              # Navigation, finding selector, date filter
    glossary.py             # Tooltip definitions
    tournament.py           # Interactive leaderboard component
  assets/style.css
  requirements.txt
  .streamlit/config.toml
```

**All charts are interactive Plotly.** Hover tooltips, zoom, pan, date-range selection, regime filter toggle. No static charts in the portal.

## 10. Quality Standards

- Every quantitative claim has a p-value or confidence interval
- Every qualitative claim cites Author (Year) — 3+ studies = consensus, 1 study = flagged
- Every result has a plain-English "so what" interpretation
- OOS performance is the primary evaluation criterion, not in-sample
- Transaction costs included in all strategy metrics

## 11. Timeline Dependencies

```
Phase 0 (Alex Brief) ─────────────────────────┐
                                                │
Phase 1A (Ray: Research) ──────────────────┐   │
Phase 1B (Dana: Data)     ─────────────────┤   │ parallel
                                            │   │
Gate 1 (Alex Review) ──────────────────────┤   │
                                            │   │
Phase 2 (Evan: Econometrics) ──────────────┤   │
                                            │   │
Gate 2 (Alex Review) ──────────────────────┤   │
                                            │   │
Phase 3 (Vera: Visualization) ─────────────┤   │
                                            │   │
Gate 3 (Alex Review) ──────────────────────┤   │
                                            │   │
Phase 4 (Ace: Portal Assembly) ────────────┤   │
                                            │   │
Gate 4 (Alex Final Review) ────────────────┘   │
                                                │
Phase 5 (Lessons Learned — All) ───────────────┘
```

---

**Distribution:** This brief has been distributed to Ray, Dana, Evan, Vera, and Ace. All agents should read this document plus their individual SOP plus the team coordination protocol before beginning work.
