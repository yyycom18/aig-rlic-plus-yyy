# Evaluation Scoring Logic

Location: Doc/Feature upgrade/evaluation_logic.md

Purpose
-------
This document specifies the raw (pre-normalized) scoring logic used to produce the two evaluation artifacts:
- `environment_interaction_scores.json`
- `strategy_survival_scores.json`

It defines each radar axis: purpose, statistical method, required inputs, example formula/pseudocode, and the expected raw metric before normalization. It also defines normalization rules (to 0–100) and validation/guardrails so engineers can implement the scoring engine deterministically.

Global conventions & parameters
-------------------------------
- Default lookback window (market data): 3 years (or configurable `LOOKBACK_YEARS`, default 3).
- Frequency for aggregation: daily or the native freq of source series, resampled where needed.
- Benchmark: SPY (ticker) unless explicitly configured. Benchmark metrics must be computed over the same time window.
- Backtest years for trades → per-year conversion: 5 years by default (`BACKTEST_YEARS = 5`).
- Missing-value policy: compute on available data; require at least 60% non-null over the lookback window else return `None` for that axis (handled upstream). Do NOT silently impute large gaps.
- Output raw metric ranges: As defined per-axis (below). These raw metrics are later normalized to 0–100 using the Normalization section.
- Persist intermediate provenance: store inputs and intermediate values for audit (e.g., correlation values, regression betas, sample sizes).

Normalisation (raw → 0–100)
----------------------------
- Two-stage mapping:
  1. Map raw metric to a canonical bounded "score" range (often 0–5 or 0–1), using clamped linear or piecewise transforms specified per axis.
  2. Multiply by 20 (if 0–5) or 100 (if 0–1) to produce final 0–100 stored in JSON.
- All axes must define min/max/clamp rules in their section.
- For metrics where higher is better, map directly; where lower is better (e.g., drawdown), invert before mapping.
- If raw metric is `None` or insufficient data, set the JSON axis to `null` and include `metadata.missing_reason`.

Schema expectation
------------------
- Final JSON values are 0–100 integers (or floats), or null for missing.
- Engines should also write a companion `*_raw_debug.json` that contains raw intermediate numbers used for each axis (for reproducibility).

Environment Interaction Radar
-----------------------------
Axes:
- trend_alignment
- macro_sensitivity
- lead_lag
- stress_response
- causality_strength

1) trend_alignment
- Purpose: Measure whether the indicator moves in the same direction as the benchmark over medium-term horizons (signal alignment).
- Method: Rolling correlation of indicator vs benchmark returns aggregated into a stability metric.
- Inputs:
  - indicator_series (price or value time series)
  - benchmark_series (price series, e.g., SPY)
  - lookback_days (e.g., LOOKBACK_YEARS * 252)
  - rolling_window (e.g., 60 trading days)
- Formula / pseudocode:
  - Compute daily returns r_ind, r_bench over lookback.
  - Compute rolling Pearson correlation corr_t over `rolling_window`.
  - Raw metric = median(corr_t) across lookback (or trimmed mean).
- Expected raw metric:
  - Range: -1.0 ... +1.0 (Pearson r)
  - Mapping: map [-1, +1] → [0,5] by linear transform: score = normalize_to_scale(corr_median, -1, 1, 5)
  - Then 0–100 = score * 20
- Notes:
  - If the indicator is expected to be anti-correlated (e.g., defensive indicator), the sign expectation should be configurable per indicator and adjust mapping (flip sign before mapping if negative alignment is desired).

2) macro_sensitivity
- Purpose: Quantify magnitude of indicator response to broad macro moves (volatility of association).
- Method: Regression beta of indicator returns vs benchmark and macro variables; or absolute correlation magnitude.
- Inputs:
  - indicator returns
  - benchmark returns (SPY)
  - optional macro factors (VIX changes, term spread) — if available
- Formula / pseudocode:
  - Fit OLS: r_ind = alpha + beta * r_bench (+ gamma * macro_factors)
  - Use |beta| as sensitivity measure OR use R-squared explained by macro regressors
  - Raw metric = clamp(|beta|, 0, beta_cap) where beta_cap is e.g., 2.0
- Expected raw metric:
  - Range (recommended): 0.0 ... 2.0 (absolute beta); choose cap depending on indicator class
  - Mapping: map [0, beta_cap] → [0,5]
  - 0–100 = score * 20
- Notes:
  - If multi-factor regressions are used, compute weighted contribution of macro factors (sum of abs(gamma_i)*scale).

3) lead_lag
- Purpose: Measure whether the indicator leads benchmark movements (early-warning quality).
- Method: Cross-correlation / maximum cross-correlation with positive lag or Granger lead-lag summary.
- Inputs:
  - indicator returns or levels
  - benchmark returns or levels
  - max_lag_days (e.g., 20 trading days)
- Formula / pseudocode:
  - Compute cross-correlation series cc(lag) for lag in [0..max_lag], where positive lag means indicator leads.
  - Identify best_lead = max_{lag>0} cc(lag).
  - Raw metric = best_lead (or weighted mean of positive-lag correlations)
- Expected raw metric:
  - Range: -1.0 ... +1.0, but we expect positive lead is good → use raw = best_lead.
  - Mapping: map [0, max_expected] → [0,5]; treat negative or near-zero as 0.
  - 0–100 = score * 20
- Notes:
  - Alternatively implement Granger causality counts at multiple lags and convert p-values into a composite score (e.g., p < 0.05 → +1 per lag; aggregate).

4) stress_response
- Purpose: How strongly indicator reacts during market stress periods (sensitivity in drawdown windows).
- Method: Conditional average returns or abnormal returns during stress windows, or tail correlation.
- Inputs:
  - Indicator returns
  - Benchmark returns
  - Stress window definition (e.g., days when benchmark drawdown > 5% or VIX in top decile)
- Formula / pseudocode:
  - Identify stress days/times S.
  - Compute mean_ind_stress = mean(r_ind[S]), mean_ind_normal = mean(r_ind[~S])
  - Compute delta = mean_ind_stress - mean_ind_normal (direction depends on indicator purpose).
  - Alternatively use correlation during stress: corr_stress = corr(r_ind[S], r_bench[S])
  - Raw metric: choose magnitude of delta or |corr_stress| depending on axis definition.
- Expected raw metric:
  - Range: depends on measure. For delta in returns: -0.1 ... +0.1 (example). Map to 0–5 by specifying min/max (e.g., [-0.10, +0.10]).
  - 0–100 produced after scaling.
- Notes:
  - Define "positive" direction clearly: for a defensive indicator, a positive protective effect is higher returns or less negative returns during stress; for an amplifier, the opposite.

5) causality_strength
- Purpose: Evidence that indicator changes precede/Granger-cause benchmark changes beyond simple correlation.
- Method: Granger causality tests, transfer entropy (optional), robustness across regimes.
- Inputs:
  - indicator series
  - benchmark series
  - max_lag
- Formula / pseudocode:
  - Run Granger test for lags 1..L, collect p-values p_l and F-statistics f_l.
  - Define score_raw = sum_over_lags( weight(l) * (1 - p_l) * normalized_f_l ) or number_of_lags_with_p < 0.05
  - Clamp to maximum (e.g., L)
- Expected raw metric:
  - Range: 0 .. L (number of significant Granger lags) or continuous [0,1] if scaled.
  - Mapping: map [0, L] → [0,5] (or [0,1]→[0,5]) then to 0–100.
- Notes:
  - Include robustness check: test across sub-periods; if effect disappears in one sub-period reduce score.

Strategy Survival Radar
-----------------------
Axes:
- return_advantage
- sharpe_advantage
- drawdown_control
- consistency
- deployability

General approach
- Inputs: tournament results CSV (`results/tournament_results_20260228.csv`) with per-strategy metrics:
  - `oos_ann_return`, `oos_sharpe`, `oos_max_dd` (negative), `oos_win_rate`, `n_trades`
- Aggregation: use Top-N strategies by `oos_sharpe` (N configurable; default 20). Aggregate per-strategy metrics (median recommended) to derive the raw group metrics.
- Benchmark: buy-and-hold SPY (use its realized `annualized_return`, `sharpe`, `max_dd` over the same evaluation period).

1) return_advantage
- Purpose: Median annualized return improvement of strategies vs benchmark.
- Method: For each strategy i in Top-N, compute ratio or difference vs benchmark, aggregate (median).
- Inputs:
  - strategy_annual_return_i = `oos_ann_return`
  - benchmark_annual_return
- Formula / pseudocode:
  - ret_diff_i = strategy_annual_return_i - benchmark_annual_return
  - ret_ratio_i = strategy_annual_return_i / (benchmark_annual_return + eps)
  - raw_metric = median(ret_ratio_i) or median(ret_diff_i)
- Expected raw metric:
  - If ratio used: >0 (e.g., 0..3); choose cap (e.g., 0.0..2.0) then map to 0–5.
  - If diff used: in percentage points (e.g., -0.2..0.5). Map via specified min/max.

2) sharpe_advantage
- Purpose: Median Sharpe improvement vs benchmark.
- Method: Per-strategy Sharpe ratio divided by benchmark Sharpe, aggregated median.
- Inputs:
  - strategy_sharpe_i = `oos_sharpe`
  - benchmark_sharpe
- Formula / pseudocode:
  - sharpe_ratio_i = strategy_sharpe_i / (benchmark_sharpe + eps)
  - raw_metric = median(sharpe_ratio_i)
- Expected raw metric:
  - Range: e.g., 0..3 (cap at 3), map to 0–5 linearly.

3) drawdown_control
- Purpose: How much the strategy reduces max drawdown relative to benchmark.
- Method: Use ratio of abs(max drawdown) of benchmark to abs(strategy max drawdown).
- Inputs:
  - strategy_max_dd_i = `oos_max_dd` (negative; use abs)
  - benchmark_max_dd (abs)
- Formula / pseudocode:
  - dd_ratio_i = abs(benchmark_max_dd) / max(abs(strategy_max_dd_i), small_eps)
  - raw_metric = median(dd_ratio_i)
- Expected raw metric:
  - Range: 0..10 (but typical 0.5..3). Cap at e.g., 5. Map [0, cap] → [0,5].
  - Note: If strategy has 0 or near-zero drawdown (rare), clamp to max cap.

4) consistency
- Purpose: Stability of positive outcomes (win rate) across strategies.
- Method: Median `oos_win_rate`
- Inputs:
  - `oos_win_rate` per strategy (0..1 or %)
- Formula / pseudocode:
  - raw_metric = median(oos_win_rate_i) (in 0..1)
- Expected raw metric:
  - Range: 0.0..1.0 (or 0..100%); map to [0,5] by linear scaling; 0–100 final = median*100.

5) deployability
- Purpose: Practicality of deploying the strategy (trade frequency, liquidity requirements).
- Method: Median trades per year (n_trades / BACKTEST_YEARS) scaled to a deployability score curve favoring moderate trade frequencies (e.g., 4..20 trades/year best).
- Inputs:
  - `n_trades` per strategy
  - BACKTEST_YEARS (default 5)
  - desirable_trade_range = [4, 20] (configurable)
- Formula / pseudocode:
  - trades_per_year_i = n_trades_i / BACKTEST_YEARS
  - raw_metric = median(trades_per_year_i)
  - Map raw_metric to 0–5 using trapezoidal mapping:
    - below 1 trade/year => score 0
    - between 4 and 20 => score 5
    - between 1 and 4 => ramp 0→5 linearly
    - above 20 => degrade slightly (cap or declining mapping) to avoid overtrading being scored as perfect
- Expected raw metric:
  - Raw is trades_per_year (float)
  - Map custom piecewise to 0–5 then to 0–100

Example: per-axis pseudocode (implementation sketch)
----------------------------------------------------
# Helper normalizer (linear clamp)
def linear_clamp(x, xmin, xmax):
    if x is None: return None
    x_clamped = max(xmin, min(xmax, x))
    return (x_clamped - xmin) / (xmax - xmin)  # returns 0..1

# Trend alignment (example)
r_ind = returns(indicator_series, lookback)
r_bench = returns(benchmark_series, lookback)
corr_rolling = rolling_corr(r_ind, r_bench, window=60)
raw_trend = median(corr_rolling)  # -1..1
trend_score_0_1 = (raw_trend + 1) / 2  # map to 0..1
trend_score_0_100 = trend_score_0_1 * 100

# Return advantage (Top-N median ratio)
top_n = select_top_n(df_tournament, by='oos_sharpe', n=20)
ret_ratios = [s.oos_ann_return / (bench_ann_return + eps) for s in top_n]
raw_return_ratio = median(ret_ratios)
# map raw_return_ratio: assume target range [0, 2]; use linear clamp
ret_score_0_1 = linear_clamp(raw_return_ratio, 0.0, 2.0)
ret_score_0_100 = ret_score_0_1 * 100

Validation & tests
------------------
- Unit tests should assert:
  - Deterministic results for a fixed seed of synthetic data.
  - Edge cases: zero benchmark return (use eps), zero trades, missing values.
  - Aggregation stability: median vs mean differences noted.
- Integration tests:
  - Recompute JSON from raw data and compare with earlier precomputed outputs (roundtrip).
- QA output:
  - Each run writes `*_raw_debug.json` with intermediate variables (e.g., corr_median, beta, p-values, sample sizes).

Provenance & metadata
---------------------
- For each axis in JSON also include:
  - `raw_value`
  - `sample_size`
  - `lookback_window`
  - `method` (string e.g., "rolling_corr(60) median")
  - `notes` (if any data adjustments applied)
- Example JSON fragment for an axis:
  ```json
  "trend_alignment": {
    "value": 72.3,
    "raw_value": 0.61,
    "method": "rolling_corr(m=60) median",
    "sample_size": 720,
    "lookback_days": 756
  }