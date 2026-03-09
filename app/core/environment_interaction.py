"""Environment Interaction — Dataclass & Configuration Loader.

Implements the Environment Interaction layer for Step C (Task 2):
- Correlation with benchmark (co-movement)
- Lead / Lag timing advantage
- Sensitivity to market stress
- Causality strength

This module only ingests pre-computed scores from JSON; it does not run
any econometric computation.
"""

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional

import json
import os


@dataclass
class EnvironmentInteraction:
    """Environment interaction scores and evidence for an indicator in a given environment."""

    indicator_id: str
    environment: str
    correlation_score: float
    lead_lag_score: float
    stress_sensitivity_score: float
    causality_score: float

    # Optional evidence / interpretation (for collapsed details)
    correlation_value: Optional[float] = None
    correlation_evidence: Optional[List[str]] = None
    correlation_interpretation: Optional[str] = None

    lead_days: Optional[int] = None
    lead_lag_evidence: Optional[List[str]] = None
    lead_lag_interpretation: Optional[str] = None

    stress_sensitivity_evidence: Optional[List[str]] = None
    stress_sensitivity_interpretation: Optional[str] = None

    causality_evidence: Optional[List[str]] = None
    causality_interpretation: Optional[str] = None

    # Provenance / trust metadata
    score_source_files: Optional[List[str]] = None
    score_date: Optional[str] = None
    score_author: Optional[str] = None
    score_method: Optional[str] = None
    confidence_level: Optional[str] = None
    confidence_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a plain dict (useful for debugging or JSON export)."""
        return asdict(self)


class EnvironmentInteractionLoader:
    """
    Load EnvironmentInteraction scores from a JSON config.

    Expected JSON structure (per Evan's handoff):
    {
      "hy_ig_spread": {
        "SPY": {
          "correlation_score": 3.0,
          "lead_lag_score": 2.5,
          "stress_sensitivity_score": 4.5,
          "causality_score": 2.0,
          ...
        }
      }
    }
    """

    def __init__(self, json_path: str) -> None:
        self.json_path = json_path
        # Nested mapping: indicator_id -> environment -> EnvironmentInteraction
        self._cache: Dict[str, Dict[str, EnvironmentInteraction]] = {}

    def load(self) -> Dict[str, Dict[str, EnvironmentInteraction]]:
        """
        Load and cache environment interaction scores from JSON.

        Returns:
            Dict[indicator_id, Dict[environment, EnvironmentInteraction]]
        """
        if not os.path.exists(self.json_path):
            raise FileNotFoundError(f"Environment interaction file not found: {self.json_path}")

        with open(self.json_path, "r", encoding="utf-8") as f:
            raw = json.load(f) or {}

        result: Dict[str, Dict[str, EnvironmentInteraction]] = {}
        for ind_id, env_map in raw.items():
            env_dict: Dict[str, EnvironmentInteraction] = {}
            if not isinstance(env_map, dict):
                continue
            for env, payload in env_map.items():
                if not isinstance(payload, dict):
                    continue
                # Required scores; fall back to neutral 2.5 if missing
                corr_score = float(payload.get("correlation_score", 2.5))
                lead_score = float(payload.get("lead_lag_score", 2.5))
                stress_score = float(payload.get("stress_sensitivity_score", 2.5))
                causality_score = float(payload.get("causality_score", 2.5))
                env_dict[env] = EnvironmentInteraction(
                    indicator_id=ind_id,
                    environment=str(env),
                    correlation_score=corr_score,
                    lead_lag_score=lead_score,
                    stress_sensitivity_score=stress_score,
                    causality_score=causality_score,
                    correlation_value=payload.get("correlation_value"),
                    correlation_evidence=payload.get("correlation_evidence"),
                    correlation_interpretation=payload.get("correlation_interpretation"),
                    lead_days=payload.get("lead_days"),
                    lead_lag_evidence=payload.get("lead_lag_evidence"),
                    lead_lag_interpretation=payload.get("lead_lag_interpretation"),
                    stress_sensitivity_evidence=payload.get("stress_sensitivity_evidence"),
                    stress_sensitivity_interpretation=payload.get("stress_sensitivity_interpretation"),
                    causality_evidence=payload.get("causality_evidence"),
                    causality_interpretation=payload.get("causality_interpretation"),
                    score_source_files=payload.get("score_source_files"),
                    score_date=payload.get("score_date"),
                    score_author=payload.get("score_author"),
                    score_method=payload.get("score_method"),
                    confidence_level=payload.get("confidence_level"),
                    confidence_reason=payload.get("confidence_reason"),
                )
            if env_dict:
                result[ind_id] = env_dict

        self._cache = result
        return result

    def get(self, indicator_id: str, environment: str = "SPY") -> Optional[EnvironmentInteraction]:
        """
        Retrieve environment interaction scores for a given indicator/environment pair.

        Returns:
            EnvironmentInteraction or None if not found.
        """
        if not self._cache:
            try:
                self.load()
            except FileNotFoundError:
                return None
        env_map = self._cache.get(indicator_id, {})
        return env_map.get(environment)

    def get_all(self) -> Dict[str, Dict[str, EnvironmentInteraction]]:
        """Return the full cached mapping."""
        if not self._cache:
            self.load()
        return self._cache.copy()

