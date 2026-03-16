# Engineering SOP: Indicator Evaluation Component Integration (YYY → Main Dashboard)

**Project:** aig-rlic-plus-yyy  
**Date:** 2026-03-08

---

## 1. Indicator Evaluation Framework Overview
This SOP provides an engineering-level specification and connectivity instructions for integrating three new indicator evaluation components from the YYY repository into the Main Dashboard repository.
- Components: (1) Indicator Identity & Use Case Layer, (2) Environment Interaction Radar, (3) Strategy Survival Radar
- Each must be placed in the top-level Apps section of each indicator overview page, above existing story/evidence/strategy/method modules.

---

## 2. Repository File Structure (YYY repository)

- **components/environment_radar.py**
  - Renders Environment Interaction Radar UI component; loads computed radar scores and supporting evidence/provenance for each indicator.
  - Handles axis scoring logic, provenance/evidence badge, and numeric accessibility summary.
- **components/strategy_radar.py**
  - Renders Strategy Survival Radar; loads and aggregates tournament result data for strategies built on the indicator.
  - Handles axis computation, summary statistics, confidence grading, and median aggregation logic.
- **components/identity_panel.py**
  - Implements Indicator Identity & Use Case UI: maps indicators to label taxonomy, displays use case text, and summarizes narrative identity block.
  - Connects to taxonomy file and use-case JSON for data.
- **data/indicator_taxonomy.json**
  - Canonical source-of-truth for economic label assignments to indicators (Credit & Financial Stress, Risk & Volatility, etc.).
- **data/indicator_use_cases.json**
  - Maps indicator_id to primary/secondary use cases and brief narrative summaries.

---

## 3. Source Data Files (from YYY pipeline)

- **Environment Interaction Radar sources:**
  - `results/correlation_analysis.csv`
    - Columns: indicator_id, benchmark_id, rolling_corr, fullsample_corr, distance_corr
  - `results/lead_lag_results.json`
    - Fields: indicator_id, lead_days, peak_lag_effect, local_proj_values
  - `results/stress_sensitivity.json`
    - Fields: indicator_id, garch_effect_size, regime_return_diff, bootstrap_p
  - `results/causality_tests.json`
    - Fields: indicator_id, granger_pval, transfer_entropy, stress_activation_flag
- **Strategy Survival Radar sources:**
  - `results/tournament_results_YYYYMMDD.csv`
    - Columns: strategy_id, indicator_id, benchmark_id, oos_sharpe, oos_ann_return, oos_max_dd, oos_win_rate, n_trades, backtest_years

All files are produced by the existing `evidence` and `strategy` research pipelines in YYY. File names, fields, and formats must match exactly for integration; additional validation/formatting may be handled in environment_radar.py and strategy_radar.py.

---

## 4. Calculation Logic
**Environment Interaction Radar (axes and formulae):**
- **Correlation:** Median(abs(level_corr)) and median(distance_corr) from `correlation_analysis.csv` (use mapping described in evidence pipeline; e.g., abs(level_corr) <0.05 → 0, 0.05–0.10 → 1, etc.)
- **Lead/Lag:** Based on peak "lead_days" from `lead_lag_results.json`:
    - lead_days ≤ 0 → 0–1
    - 1–3 → 2
    - 4–10 → 3
    - 11–30 → 4
    - >30 → 5
- **Stress Sensitivity:** Composite scaling from `stress_sensitivity.json` using garch_effect_size, regime_diff, and bootstrap_p; 0–5 scale per documented mapping function (see mapping.json).
- **Causality:** From `causality_tests.json`, combine evidence/activation as:
    - p-value + transfer-entropy + regime activation flag → 0–5. (p<0.05 in stress required for score ≥3.)

**Strategy Survival Radar (axes and formulae):**
- For top-20 OOS Sharpe strategies in `tournament_results_YYYYMMDD.csv` (per indicator_id):
  - **Return Advantage:** ReturnRatio = oos_ann_return / benchmark_annual_return; AxisValue = median(ReturnRatio)
  - **Sharpe Advantage:** SharpeRatio = oos_sharpe / benchmark_sharpe; AxisValue = median(SharpeRatio)
  - **Drawdown Control:** DDRatio = abs(benchmark_drawdown) / abs(oos_max_dd); AxisValue = median(DDRatio)
  - **Consistency:** WinRate = oos_win_rate; AxisValue = median(WinRate)
  - **Deployability:** TradesPerYear = n_trades / backtest_years; AxisValue = median(TradesPerYear)

All scaling, aggregation, and mapping logics are implemented in the corresponding components above and validated by included unit tests.

---

## 5. Indicator Labeling System (1A) and Data Files

- **data/indicator_taxonomy.json** stores the label taxonomy. Example structure:
  ```json
  {
    "hy_ig_spread": ["Credit & Financial Stress", "Relative Credit Premium"],
    "vix_index": ["Risk & Volatility"]
  }
  ```
- **Assignment:** identity_panel.py loads indicator_taxonomy.json and maps incoming indicator_id to the correct tags. UI displays labels as colored badges.
- **Future repository integration:** taxonomy file (or an export) should be accessible/shared in data/ in Main so that taxonomy is system-wide.

---

## 6. Output Files (produced by YYY components)

- **results/environment_interaction_scores.json**
  - Schema: indicator_id, axis_scores ({correlation, lead_lag, stress_sensitivity, causality}), provenance, confidence, updated_at
- **results/strategy_survival_scores.json**
  - Schema: indicator_id, strategy_medians ({return_adv, sharpe_adv, etc.}), confidence, top_strategies[], updated_at
- These files are loaded on indicator-dashboard render; app/components will reference these for live display.

---

## 7. Integration Mapping

**Indicator Identity & Use Case Layer**
- Import/instantiate identity_panel.py and map incoming indicator_id/metadata to taxonomy/use-case descriptions.
- Place this section at the very top of the indicator Apps overview in Main.

**Environment Interaction Radar**
- Import environment_radar.py; configure to read environment_interaction_scores.json.
- Surface radar/evidence summary directly below Identity Layer in the overview page. Ensure the evidence badge and source file drilldown point to canonical paths.

**Strategy Survival Radar**
- Import strategy_radar.py; configure to read strategy_survival_scores.json and tournament_results_*.csv.
- Display immediately following the environment radar. Summary, confidence, and detail popovers should all source from the shared data pipeline.

**Modularity Note:**
- All files and modules are self-contained; no main repository files are to be edited as part of this SOP.
- Mapping logic, taxonomy exports, and evidence/strategy result files must be kept in sync between Main and staging during/after integration.

---

Reference Implementation

The file paths referenced in this section refer to the YYY repository,
which serves as a prototype implementation of the indicator evaluation
components. During integration into the Main repository, equivalent
modules should be implemented following the Main architecture.

**[END ENGINEERING SOP – production-ready mapping for Main Dashboard integration teams.]**
