# Data Agent SOP

... (original content preserved) ...

## [NEW COMPONENT – Indicator Evaluation Framework]
> The Indicator Evaluation Framework consumes structured metadata for indicator taxonomy (classification and use-case), evidence summary, and strategy result files. Data agents enable seamless integration by curating and maintaining these foundational datasets.

Schema ownership for evaluation-layer datasets belongs to the Data Agent.

The Data Agent is responsible for validating the structure of all evaluation-layer input files against the definitions in `docs/evaluation_schema.md`.

This includes ensuring consistency for:

* `results/environment_interaction_scores.json`
* `results/strategy_survival_scores.json`

The Data Agent must verify that all fields, naming conventions, and data types conform to the schema contract before these files are consumed by Visualization or App Dev components.

Data agents must ensure that all evaluation-layer input files adhere to the schema contracts defined in docs/evaluation_schema.md.

Breaking schema compatibility may cause failures in downstream visualization or application rendering.

**The data agent is responsible for validating file structure and ensuring consistency across indicator taxonomy, evidence summary files, and radar input datasets.**

**Data Agent Responsibilities**:
- Manage and update the indicator taxonomy source file (`data/indicator_taxonomy.json`) and use-case file (`data/indicator_use_cases.json`), ensuring all indicators are consistently and accurately classified.
- Support data refresh, format standardization, and completeness for result files feeding the environment and strategy radars (`results/environment_interaction_scores.json`, `results/strategy_survival_scores.json`).
- Ensure that files adhere to naming, column, and schema conventions required by downstream components (`identity_panel.py`, `environment_radar.py`, `strategy_radar.py`).
- Coordinate with research/evidence pipeline to map new indicators, keeping the taxonomy synchronized for the Main repository integration.

No changes to data acquisition, cleaning, or econometric data prep workflows are required; this layer builds on existing pipelines.
