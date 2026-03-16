# Evaluation Framework Output Schema

## Schema Ownership and Governance

The schema definitions in this document represent the canonical contract for all evaluation-layer outputs.

Schema ownership belongs to the **Data Agent**, which is responsible for validating schema structure and ensuring that all upstream artifacts conform to the expected format.

Schema governance is shared between the **Data Agent** and the **App Dev Agent**:

* The Data Agent ensures structural consistency and validation of evaluation-layer datasets.
* The App Dev Agent ensures that schema definitions remain compatible with dashboard rendering and evaluation-layer orchestration.

Any schema changes must be coordinated between these agents and documented in this file before implementation.

Breaking schema compatibility without updating this document may cause failures in downstream visualization or application rendering.

---

This document defines the canonical schema for the two main output files of the Indicator Evaluation Layer:

- results/environment_interaction_scores.json
- results/strategy_survival_scores.json

These schemas are the contract between Data, Econometrics, Visualization, and App Dev agents. Any change must be coordinated and documented here before implementation.

---

## Environment Interaction Scores Schema

```json
[
  {
    "indicator": "string",                  // Indicator identifier, e.g. "hy_ig_spread"
    "axis_scores": {
      "trend_alignment": "number (0-100)",    // Trend alignment score
      "macro_sensitivity": "number (0-100)",  // Macro environment sensitivity
      "lead_lag": "number (0-100)",          // Lead/lag behavior
      "stress_response": "number (0-100)",    // Stress regime reactivity
      "causality_strength": "number (0-100)"  // Causality evidence strength
    },
    "confidence": "number (0-1)",             // Agent-scored confidence for this output
    "source_files": [                          // List of source file names (CSV, JSON, etc)
      "string"
    ],
    "last_updated": "timestamp (ISO 8601)",   // e.g. "2026-03-08T12:34:56Z"
    "provenance": {
      "author": "string",
      "method": "string (summary, e.g. 'percentile-mapping')"
    }
  }
]
```
**Notes:**
- Axis keys must be present for all radars. If a value is missing, use `null` and note in provenance.
- Confidence and metadata fields are required for cross-agent compatibility and reproducibility.

---

## Strategy Survival Scores Schema

```json
[
  {
    "indicator": "string",                     // Indicator identifier
    "strategy_medians": {
      "return_advantage": "number (0-100)",     // Median return advantage
      "sharpe_advantage": "number (0-100)",     // Median Sharpe advantage
      "drawdown_control": "number (0-100)",     // Median drawdown control
      "consistency": "number (0-100)",          // Median win rate / stability
      "deployability": "number (0-100)"          // Median trades-per-year/robustness
    },
    "confidence": "number (0-1)",               // Diagnostic confidence
    "top_strategies": [                          // Optional: IDs or hashes of Top-20 OOS strategies
      "string"
    ],
    "source_files": [                            // Results/tournament filenames used
      "string"
    ],
    "last_updated": "timestamp (ISO 8601)",     // e.g. "2026-03-08T12:34:56Z"
    "provenance": {
      "author": "string",
      "method": "string (aggregation logic, e.g. 'median-of-top20')"
    }
  }
]
```
**Notes:**
- Both files should be valid JSON arrays (one entry per indicator).
- All numeric axis values must be normalized to the 0–100 scale (if your calculation is 0–5 or 0–1, scale accordingly).
- Confidence is a float between 0 and 1 (optional explanation in provenance).
- Do not invent new fields without alignment between Data, Econometrics, and App Dev agents.

---

**Schema changes must be reflected in this documentation before code, data, or rendering updates occur.**
