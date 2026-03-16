# Engineering SOP: Indicator Evaluation Component Integration (YYY → Main Dashboard)

**Project:** aig-rlic-plus-yyy  
**Date:** 2026-03-08

\---

## 1\. Indicator Evaluation Framework Overview

This SOP provides an engineering-level specification and connectivity instructions for integrating three new indicator evaluation components from the YYY repository into the Main Dashboard repository.

* Components: (1) Indicator Identity \& Use Case Layer, (2) Environment Interaction Radar, (3) Strategy Survival Radar
* Each must be placed in the top-level Apps section of each indicator overview page, above existing story/evidence/strategy/method modules.

\---

## 2\. Repository File Structure (YYY repository)

* **components/environment\_radar.py**

  * Renders Environment Interaction Radar UI component; loads computed radar scores and supporting evidence/provenance for each indicator.
  * Handles axis scoring logic, provenance/evidence badge, and numeric accessibility summary.
* **components/strategy\_radar.py**

  * Renders Strategy Survival Radar; loads and aggregates tournament result data for strategies built on the indicator.
  * Handles axis computation, summary statistics, confidence grading, and median aggregation logic.
* **components/identity\_panel.py**

  * Implements Indicator Identity \& Use Case UI: maps indicators to label taxonomy, displays use case text, and summarizes narrative identity block.
  * Connects to taxonomy file and use-case JSON for data.
* **data/indicator\_taxonomy.json**

  * Canonical source-of-truth for economic label assignments to indicators (Credit \& Financial Stress, Risk \& Volatility, etc.).
* **data/indicator\_use\_cases.json**

  * Maps indicator\_id to primary/secondary use cases and brief narrative summaries.

\---

## 3\. Source Data Files (from YYY pipeline)

* **Environment Interaction Radar sources:**

  * `results/correlation\_analysis.csv`

    * Columns: indicator\_id, benchmark\_id, rolling\_corr, fullsample\_corr, distance\_corr
  * `results/lead\_lag\_results.json`

    * Fields: indicator\_id, lead\_days, peak\_lag\_effect, local\_proj\_values
  * `results/stress\_sensitivity.json`

    * Fields: indicator\_id, garch\_effect\_size, regime\_return\_diff, bootstrap\_p
  * `results/causality\_tests.json`

    * Fields: indicator\_id, granger\_pval, transfer\_entropy, stress\_activation\_flag
* **Strategy Survival Radar sources:**

  * `results/tournament\_results\_YYYYMMDD.csv`

    * Columns: strategy\_id, indicator\_id, benchmark\_id, oos\_sharpe, oos\_ann\_return, oos\_max\_dd, oos\_win\_rate, n\_trades, backtest\_years

All files are produced by the existing `evidence` and `strategy` research pipelines in YYY. File names, fields, and formats must match exactly for integration; additional validation/formatting may be handled in environment\_radar.py and strategy\_radar.py.

\---

## 4\. Calculation Logic

**Environment Interaction Radar (axes and formulae):**

* **Correlation:** Median(abs(level\_corr)) and median(distance\_corr) from `correlation\_analysis.csv` (use mapping described in evidence pipeline; e.g., abs(level\_corr) <0.05 → 0, 0.05–0.10 → 1, etc.)
* **Lead/Lag:** Based on peak "lead\_days" from `lead\_lag\_results.json`:

  * lead\_days ≤ 0 → 0–1
  * 1–3 → 2
  * 4–10 → 3
  * 11–30 → 4
  * >30 → 5
* **Stress Sensitivity:** Composite scaling from `stress\_sensitivity.json` using garch\_effect\_size, regime\_diff, and bootstrap\_p; 0–5 scale per documented mapping function (see mapping.json).
* **Causality:** From `causality\_tests.json`, combine evidence/activation as:

  * p-value + transfer-entropy + regime activation flag → 0–5. (p<0.05 in stress required for score ≥3.)

**Strategy Survival Radar (axes and formulae):**

* For top-20 OOS Sharpe strategies in `tournament\_results\_YYYYMMDD.csv` (per indicator\_id):

  * **Return Advantage:** ReturnRatio = oos\_ann\_return / benchmark\_annual\_return; AxisValue = median(ReturnRatio)
  * **Sharpe Advantage:** SharpeRatio = oos\_sharpe / benchmark\_sharpe; AxisValue = median(SharpeRatio)
  * **Drawdown Control:** DDRatio = abs(benchmark\_drawdown) / abs(oos\_max\_dd); AxisValue = median(DDRatio)
  * **Consistency:** WinRate = oos\_win\_rate; AxisValue = median(WinRate)
  * **Deployability:** TradesPerYear = n\_trades / backtest\_years; AxisValue = median(TradesPerYear)

All scaling, aggregation, and mapping logics are implemented in the corresponding components above and validated by included unit tests.

\---

## 5\. Indicator Labeling System (1A) and Data Files

* **data/indicator\_taxonomy.json** stores the label taxonomy. Example structure:

```json
  {
    "hy\_ig\_spread": \["Credit \& Financial Stress", "Relative Credit Premium"],
    "vix\_index": \["Risk \& Volatility"]
  }
  ```

* **Assignment:** identity\_panel.py loads indicator\_taxonomy.json and maps incoming indicator\_id to the correct tags. UI displays labels as colored badges.
* **Future repository integration:** taxonomy file (or an export) should be accessible/shared in data/ in Main so that taxonomy is system-wide.

\---

## 6\. Output Files (produced by YYY components)

* **results/environment\_interaction\_scores.json**

  * Schema: indicator\_id, axis\_scores ({correlation, lead\_lag, stress\_sensitivity, causality}), provenance, confidence, updated\_at
* **results/strategy\_survival\_scores.json**

  * Schema: indicator\_id, strategy\_medians ({return\_adv, sharpe\_adv, etc.}), confidence, top\_strategies\[], updated\_at
* These files are loaded on indicator-dashboard render; app/components will reference these for live display.

\---

## 7\. Integration Mapping

**Indicator Identity \& Use Case Layer**

* Import/instantiate identity\_panel.py and map incoming indicator\_id/metadata to taxonomy/use-case descriptions.
* Place this section at the very top of the indicator Apps overview in Main.

**Environment Interaction Radar**

* Import environment\_radar.py; configure to read environment\_interaction\_scores.json.
* Surface radar/evidence summary directly below Identity Layer in the overview page. Ensure the evidence badge and source file drilldown point to canonical paths.

**Strategy Survival Radar**

* Import strategy\_radar.py; configure to read strategy\_survival\_scores.json and tournament\_results\_\*.csv.
* Display immediately following the environment radar. Summary, confidence, and detail popovers should all source from the shared data pipeline.

**Modularity Note:**

* All files and modules are self-contained; no main repository files are to be edited as part of this SOP.
* Mapping logic, taxonomy exports, and evidence/strategy result files must be kept in sync between Main and staging during/after integration.

\---

**\[END ENGINEERING SOP – production-ready mapping for Main Dashboard integration teams.]**

