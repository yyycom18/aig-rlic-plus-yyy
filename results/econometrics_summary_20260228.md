# Econometrics Summary: HY-IG Credit Spread vs S&P 500 Returns

**Author:** Evan (Econometrics Agent)
**Date:** 2026-02-28
**Dataset:** Dana's `data/hy_ig_spy_daily_20000101_20251231.parquet` (6,783 rows x 49 columns)
**Specification basis:** Ray's research brief (`docs/research_brief_hy_ig_spy_20260228.md`) and spec memo (`docs/spec_memo_hy_ig_spy_20260228.md`)

---

## Executive Summary

The HY-IG credit spread contains economically meaningful information about future S&P 500 returns, but the relationship is **regime-dependent, nonlinear, and dominated by reverse causality** (equity leading credit) in calm periods. A Long/Cash strategy gated by HMM regime states or Bollinger Band thresholds on the z-score achieves OOS Sharpe ratios of 1.1-1.2 (vs 0.77 buy-and-hold), surviving bootstrap significance tests and transaction costs. However, these strategies primarily add value by **avoiding drawdowns during stress episodes** rather than generating alpha from positive timing.

---

## Stage 1: Exploratory Findings

### Correlations
- HY-IG spread **levels** show moderate negative correlations with forward SPY returns (-0.10 to -0.20 at 21d-252d horizons). Wider spreads predict lower returns.
- **Spread changes** (momentum, RoC) correlate more strongly at short horizons. Distance correlation (0.39) confirms substantial nonlinear dependence between daily spread changes and SPY returns.
- The **CCC-BB quality spread** shows the strongest Spearman correlations at long horizons, consistent with Berndt et al. (2018) on distress migration signaling.

### Cross-Correlation Function
- 13 of 41 lags significant at 95%. Peak correlation is **contemporaneous** (lag 0), consistent with shared factor exposure. Modest evidence of credit leading equity at lags -1 to -3.

### Regime Descriptive Stats
- **Q1 (calm, spread ~2.25 bps):** Ann. return 16.9%, vol 11.6%, Sharpe 1.45, max DD -10.7%
- **Q4 (stress, spread ~6.37 bps):** Ann. return -1.0%, vol 28.7%, Sharpe -0.04, max DD -62.6%
- **So what:** Equity risk is dramatically asymmetric across spread regimes. Avoiding Q4 is worth more than being in Q1-Q3.

### KDE Regime Boundaries
- Primary mode at ~2.6 bps (calm), secondary mode at ~6.4 bps (moderate stress), with antimodes at ~6.0 and ~9.1 marking natural regime boundaries.

---

## Stage 2: Core Model Results

### 1. Toda-Yamamoto Granger Causality

**Key finding: Bidirectional causality, but asymmetric across regimes.**

| Direction | Full Sample | Stress (Q4) | Calm (Q1-Q3) |
|-----------|:-----------:|:-----------:|:------------:|
| Credit -> Equity | Significant (all lags) | Significant | **Not significant** |
| Equity -> Credit | Significant (all lags) | Significant | Significant |

**So what:** In calm markets, equities lead credit (Merton structural channel dominates). In stress, the causal arrow becomes bidirectional — credit markets contribute independent information, consistent with Acharya & Johnson (2007). This validates the regime-conditional approach.

### 2. Transfer Entropy
- Both directions significant at lag 1 and lag 5 (bootstrap p < 0.05).
- Equity->Credit transfer entropy (0.021 at lag 1) exceeds Credit->Equity (0.012), confirming equity dominance in the information flow, but the credit-to-equity channel is nonlinearly significant.

### 3. Johansen Cointegration
- **Cointegration found** between log(SPY) and HY-IG spread level (trace stat 18.0 > 15.5 CV at 5%).
- VECM adjustment: Alpha for HY-IG spread is -0.00082 (spread adjusts toward equilibrium), while alpha for log(SPY) is near zero (-0.000009). The spread does the adjusting, not equity prices.
- **So what:** There exists a long-run equilibrium between equity valuations and credit risk pricing. Deviations are corrected primarily through spread compression/expansion.

### 4. Markov-Switching Regression
- 3-state model (AIC -45,607) preferred over 2-state (AIC -45,028).
- **State 0 (low vol):** sigma^2 = 0.000025, positive mean return. ~40% of sample.
- **State 1 (medium vol):** sigma^2 = 0.00011, near-zero mean return.
- **State 2 (high vol/crisis):** sigma^2 = 0.00071, highest variance. ~21% of sample.
- The HY-IG spread change coefficient is negative and significant across all states (-0.047 to -0.069), indicating spread widening is contemporaneously negative for equity returns regardless of regime.

### 5. HMM Regime Detection
- 2-state HMM on [HY-IG spread change, VIX] identifies a low-VIX state (mean VIX ~15, 62% of time) and a high-VIX state (mean VIX ~27, 38% of time).
- Transition matrix is persistent: P(stay in calm) = 0.99, P(stay in stress) = 0.98.
- **This is the signal that wins the tournament (S6).**

### 6. Change-Point Detection (PELT)
- 48 structural breakpoints detected. Key clusters:
  - 2001-2002 (dot-com/Enron), 2007-2009 (GFC build-up through recovery), 2015-2016 (energy crisis), 2020 (COVID), 2022 (rate shock).
- These align well with Ray's event timeline, validating the data and methodology.

### 7. GJR-GARCH
- **HY-IG spread change coefficient: -5.70 (t = -27.1, p < 0.001).** A 1 bps daily widening in the HY-IG spread corresponds to a 5.7 bps decline in SPY returns. Massive economic significance.
- **Leverage effect confirmed:** gamma = 0.15 (significant), meaning negative shocks increase conditional volatility more than positive shocks.
- R-squared: 0.225 (very high for daily return prediction).

### 8. Quantile Regression
- The HY-IG z-score effect on forward 21d SPY returns is **asymmetric across quantiles:**
  - tau=0.05 (left tail): coefficient -0.014 (higher spread z-score predicts worse left-tail outcomes)
  - tau=0.50 (median): coefficient +0.001 (near zero)
  - tau=0.90 (right tail): coefficient +0.010 (higher spread z-score also predicts wider right tail)
- **So what:** Elevated credit spreads widen the **entire distribution** of future equity returns, increasing both downside risk and upside potential. This is consistent with Adrian et al. (2019) "Vulnerable Growth" findings.

### 9. Random Forest + SHAP
- Walk-forward accuracy ranges from 27% to 84% across yearly windows (highly variable).
- Average AUC: ~0.50 (barely better than random), suggesting **limited nonlinear predictability** beyond what linear models capture.
- Top features by importance: yield curve slope (12.4%), NFCI (11.3%), CCC-BB spread (11.1%), HY-IG spread (7.9%).
- **So what:** The RF does not provide incremental value over simpler indicators. The ML "black box" adds noise, not signal, for this problem.

### 10. Local Projections (Jorda)
- HY-IG spread change coefficient is **not statistically significant** at any horizon (h=1 through h=63) using HAC standard errors.
- State-dependent interaction (spread change x stress) is also insignificant.
- **So what:** After controlling for VIX and yield curve slope, the *incremental* predictive power of HY-IG spread changes for forward cumulative returns is weak. The GJR-GARCH result captures contemporaneous correlation, not genuine lead-lag predictability.

### Diagnostics
- LP h=21: Non-normal residuals (JB p < 0.001), heteroskedastic (BP p < 0.001), strong serial correlation (BG p < 0.001), and RESET misspecification (p < 0.001). All expected given overlapping forward returns and regime-dependent volatility. HAC standard errors are essential.

---

## Stage 3: Tournament Results

### Scale
- **2,304 combinations tested**, 1,149 valid (OOS Sharpe >= 0, turnover <= 24x/yr, >= 30 trades).
- **Buy-and-hold SPY benchmark:** OOS Sharpe = 0.77, ann. return ~13.8%, max DD -33.7%.

### Top-5 Winners

| Rank | Signal | Lead | Threshold | Strategy | OOS Sharpe | OOS Return | Max DD |
|:----:|--------|:----:|-----------|----------|:----------:|:----------:|:------:|
| 1 | HMM 2-state prob (S6) | 0d | p > 0.7 | Long/Cash | **1.17** | 11.0% | -11.6% |
| 2 | Composite Z+VTS (S8) | 0d | Bollinger 1.5x | Long/Cash | **1.17** | 16.2% | -29.1% |
| 3 | HMM 2-state prob (S6) | 0d | p > 0.5 | Long/Cash | **1.16** | 10.7% | -11.1% |
| 4 | Z-Score 252d (S2a) | 0d | Bollinger 2.0x | Long/Cash | **1.12** | 16.3% | -28.6% |
| 5 | Z-Score 252d (S2a) | 5d | Rolling 95th pctile | Long/Cash | **1.12** | 16.8% | -23.7% |

**Patterns:**
- **Long/Cash (P1) dominates.** No Long/Short or signal-strength strategy appears in the top 10.
- **HMM regime state is the best signal** — the tournament winner is a simple "be long when HMM says calm, cash when HMM says stress."
- **Z-score with Bollinger thresholds** is the best non-model-based approach.
- **Same-day (L0) signals dominate**, contradicting the hypothesis of multi-day lead times. The L5 z-score entry is a modest exception.

### Validation Results

**Bootstrap:** All 5 winners are statistically significant at p < 0.01 for OOS Sharpe > 0.

**Transaction costs:** At 5 bps round-trip, Sharpe drops ~0.03. All winners remain above 1.0 through 20 bps. Breakeven costs are high (50+ bps), confirming robustness.

**Signal decay:** Adding 1-day execution delay drops Sharpe by 0.15-0.25 (material but not fatal). 5-day delay costs 0.3-0.5 in Sharpe.

**Stress tests:**
- **GFC:** HMM strategies (W1, W3) dramatically outperform — max DD only -6% vs -55% for buy-and-hold. This is the primary value-add.
- **COVID:** Mixed results. HMM strategies underperform (HMM lagged the V-shaped recovery). Z-score strategies outperform.
- **2022 Rate Shock:** All strategies underperform buy-and-hold (spread-based signals did not predict the rate-driven selloff).

---

## Key Takeaways

1. **H1 (Credit leads equity) is partially supported.** Granger causality confirms bidirectional flow with credit-to-equity causality **activated only during stress**. In calm markets, equity leads credit. The information is more about regime identification than lead-lag timing.

2. **H2 (Nonlinear, regime-dependent) is strongly supported.** Markov-switching, HMM, and quantile regression all confirm that the credit-equity relationship is fundamentally different across regimes. The KDE and PELT analyses validate natural breakpoints.

3. **H3 (Tradable signal) is conditionally supported.** Credit-signal strategies beat buy-and-hold OOS (Sharpe 1.1-1.2 vs 0.77) with lower drawdowns, surviving transaction costs and bootstrap tests. However:
   - Value comes from **drawdown avoidance**, not alpha generation.
   - The HMM signal is **not leading** — it reflects current state, not prediction.
   - **2022 failure** shows the strategy does not protect against rate-driven selloffs where credit spreads widen alongside equities.

4. **The Random Forest and local projections add little.** The spread's predictive power is largely contemporaneous (captured by GARCH) rather than forward-looking. Simpler regime indicators outperform ML.

5. **Departures from Ray's specification:**
   - IV estimation not pursued (Toda-Yamamoto made pre-testing unnecessary).
   - SHAP analysis was inconclusive due to a library compatibility issue (logged but non-blocking).
   - Per-regime transfer entropy was computed at the full-sample level due to subsample size constraints.

---

## Files Delivered

### Exploratory (`results/exploratory_20260228/`)
- `correlations.csv` — Pearson/Spearman/Kendall + distance correlation
- `rolling_252d_correlation.csv` — Rolling Pearson correlation time series
- `ccf.csv` — Pre-whitened cross-correlation function
- `regime_descriptive_stats.csv` — SPY stats by spread quartile
- `kde_density.csv`, `kde_boundaries.csv` — KDE distribution and natural breakpoints

### Core Models (`results/core_models_20260228/`)
- `granger_causality.csv` — Toda-Yamamoto tests (both directions, 3 regimes, 4 lag orders)
- `transfer_entropy.csv` — Nonlinear causality (both directions, 2 lags)
- `cointegration.csv`, `vecm_coefficients.csv` — Johansen + VECM
- `markov_switching_2state.csv`, `markov_switching_3state.csv` — MS parameters
- `markov_regime_probs_2state.parquet`, `markov_regime_probs_3state.parquet` — Regime probabilities
- `hmm_states_2state.parquet`, `hmm_states_3state.parquet` — HMM states and probabilities
- `hmm_transition_matrix_2state.csv`, `hmm_transition_matrix_3state.csv`
- `change_points.csv` — PELT breakpoints
- `gjr_garch.csv` — GJR-GARCH parameters
- `quantile_regression.csv` — Quantile regression coefficients (6 quantiles)
- `rf_walk_forward.csv`, `rf_feature_importance.csv`, `rf_probabilities.csv`
- `local_projections.csv` — Jorda LP coefficients (6 horizons, base + state-dependent)
- `diagnostics_summary.csv` — All diagnostic tests
- Model objects: `.pkl` files for Markov-switching, HMM, GARCH

### Tournament (`results/`)
- `tournament_results_20260228.csv` — 2,305 rows (2,304 strategies + benchmark)

### Validation (`results/tournament_validation_20260228/`)
- `walk_forward.csv` — Annual rolling Sharpe for top-5
- `bootstrap.csv` — 10,000-sample bootstrap significance
- `transaction_costs.csv` — Net Sharpe at 0-50 bps costs
- `signal_decay.csv` — Sharpe with 0-5 day execution delays
- `stress_tests.csv` — GFC, COVID, Taper Tantrum, 2022 stress periods
