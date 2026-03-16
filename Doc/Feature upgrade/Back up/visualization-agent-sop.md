# Visualization Agent SOP

(rest of original content from main repo)

## [NEW COMPONENT – Indicator Evaluation Framework]
> The Indicator Evaluation Framework receives pre-aggregated evidence and strategy result files for each indicator, and the Visualization Agent is responsible for rendering the Environment Interaction Radar and Strategy Survival Radar using these outputs, following established UI/UX, color, and accessibility conventions.

The visualization agent renders radar charts using the canonical score outputs defined by the evaluation layer schema.

**Visualization agents must treat evaluation scores as canonical outputs and must not modify or recompute radar scores during rendering.**

The role of visualization is strictly presentational: transforming normalized evaluation scores into accessible and interpretable visual components.

**Visualization Agent Responsibilities**:
- Render radar chart components for environment and strategy scores using data from standardized outputs (`results/environment_interaction_scores.json`, `results/strategy_survival_scores.json`).
- Ensure visualizations match prior stylistic conventions (color palette, interactivity, axis scaling, and accessible labeling).
- Collaborate with App Dev to provide chart JSON/Plotly objects for portal integration.
- Maintain tooling for evidence badge, source list, confidence label, numeric summary, and micro-explanation overlays, in line with the engineering SOP.
- No changes to core input validation, chart design, or asset delivery protocols—the evaluation framework is purely an overlay, not a workflow modification.
