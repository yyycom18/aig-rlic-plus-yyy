# Reference Catalogs Index

## Credit Spread / Equity Prediction Analysis — Engine Parts Library

This index links to four reference catalogs that serve as a library of interchangeable "engine parts" for analysis design. Not all parts will be used in every analysis — they are here for selection, substitution, and future enrichment.

---

## Catalogs

| # | Catalog | File | Contents | Count |
|---|---------|------|----------|-------|
| A | **Data Series** | [`data-series-catalog.md`](data-series-catalog.md) | Candidate time series across credit, equity, macro, sentiment, alternative assets, and computed derivatives | 63 |
| B | **Econometric Methods** | [`econometric-methods-catalog.md`](econometric-methods-catalog.md) | Statistical and econometric techniques for correlation, causality, regime detection, volatility, ML, signal extraction, and tail analysis | 52 |
| C | **Backtesting Approaches** | [`backtesting-approaches-catalog.md`](backtesting-approaches-catalog.md) | Strategy evaluation frameworks spanning return metrics, risk metrics, long/short variants, validation methods, and practical considerations | 62 |
| D | **Threshold & Regime Methods** | [`threshold-regime-methods-catalog.md`](threshold-regime-methods-catalog.md) | Techniques for identifying market regimes and signal thresholds — statistical, adaptive, ML-based, and multi-dimensional | 40 |

**Total: 217 candidates across 4 dimensions**

---

## How to Use These Catalogs

### For Analysis Design

1. **Start with the question** — What economic hypothesis are we testing?
2. **Select data** from Catalog A — Choose base series and derivatives relevant to the hypothesis
3. **Select methods** from Catalog B — Match the method to the data structure (cross-section, time-series, panel) and the question type (correlation, causation, prediction, regime)
4. **Select threshold approach** from Catalog D — Choose how to identify regimes or signal boundaries
5. **Select backtest framework** from Catalog C — Choose metrics, strategy variants, and validation approach

### For Iterative Improvement

- **Add a data series:** Source it, add to Catalog A, re-run the pipeline
- **Swap a method:** Replace one technique with another from the same category in Catalog B
- **Change the backtest lens:** Switch from return-oriented to risk-oriented using Catalog C alternatives
- **Refine thresholds:** Move from fixed to adaptive using Catalog D options

### Priority Tags

Each catalog includes implementation priority recommendations:
- **Phase 1 (Quick wins)** — Low complexity, high value, can be done in hours
- **Phase 2 (Core enhancements)** — Moderate complexity, fills major analytical gaps
- **Phase 3 (Advanced)** — High complexity, provides differentiated insights
- **Phase 4 (Exploratory)** — Research-grade, may or may not yield actionable results

---

## Cross-Reference: Sample Analysis vs. Catalog Options

What the sample used and what we can upgrade to:

| Dimension | Sample Used | Catalog Upgrade Options |
|-----------|------------|------------------------|
| **Data** | HY-IG spread, SPY (2 series) | 63 candidates including credit tiers, macro conditions, volatility surfaces, cross-asset signals |
| **Correlation** | Pearson only | Spearman, Kendall, DCC-GARCH, copulas, distance correlation, rolling/time-varying |
| **Lead-lag** | Basic Granger (single spec) | Toda-Yamamoto, transfer entropy, wavelet coherence, frequency-domain Granger |
| **Regimes** | Fixed thresholds (4/6/8%) | Markov-switching, HMM, TAR, change-point detection, adaptive percentiles, ML clustering |
| **Time-series model** | Basic VAR (no diagnostics reported) | VECM, SVAR, TVP-VAR, BVAR, local projections, GARCH-MIDAS |
| **Backtest: metrics** | Total return, max drawdown only | Sharpe, Sortino, Calmar, Omega, VaR, CVaR, Ulcer index, stress tests |
| **Backtest: strategy** | Long/cash only | Long/short, volatility targeting, drawdown control, put hedging, pairs trading |
| **Backtest: validation** | In-sample only | Walk-forward, expanding window, bootstrap, White's Reality Check, CPCV |

---

## Maintenance

- **Owner:** Alex (lead analyst) maintains the index; individual catalogs are updated by the relevant agent
- **Update frequency:** After each major analysis, review catalogs and add new discoveries
- **Deprecation:** Mark entries as `[DEPRECATED]` rather than deleting — future analyses may revisit
- **Version control:** All catalogs are tracked in git; use commit messages to document additions/removals

---
*Created: 2026-02-28*
*Last updated: 2026-02-28*
