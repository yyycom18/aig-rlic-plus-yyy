# Econometrics Agent SOP

(rest of original content from main repo)

## [NEW COMPONENT – Indicator Evaluation Framework]
> The Indicator Evaluation Framework surfaces key econometric outputs as summary axes in the Environment Interaction and Strategy Survival radars, providing transparent mapping from modeling results to user-facing visual scores.

The econometrics agent provides the raw statistical evidence used by the evaluation layer. This includes correlation metrics, lead-lag analysis, stress sensitivity, causality tests, and strategy performance outputs.

**The econometrics agent does NOT compute radar scores directly. Score normalization and aggregation into radar axes are handled by the evaluation framework orchestration layer.**

This separation ensures that statistical analysis remains independent from UI-facing evaluation summaries.

**Econometrics Agent Responsibilities**:
- Maintain and provide results from correlation, lead-lag, stress sensitivity, and causality analyses for ingestion into the environment radar component (see: `results/correlation_analysis.csv`, `results/lead_lag_results.json`, `results/stress_sensitivity.json`, `results/causality_tests.json`).
- Supply strategy performance metrics and tournament stats for the Strategy Survival Radar (`results/tournament_results_*.csv`).
- Document calculation logic and mapping rules (e.g., in `mapping.json` or inline evidence panels) so App Dev and Viz agents can confidently trace UI scores to canonical econometric evidence.
- No changes to estimation, diagnostics, or modeling workflow are necessary—outputs now also feed the evaluation layer in parallel with existing charts and evidence tables.
