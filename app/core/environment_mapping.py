"""
Environment Interaction mapping helpers.

This module implements the numeric mapping rules described in
results/mapping_rules.json for:

- correlation_score
- lead_lag_score
- stress_sensitivity_score
- causality_score

All functions are pure and operate on already-computed summary statistics.
Raw-file loading (CSV, parquet, etc.) is delegated to higher-level scripts.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional, Tuple

import math


def _safe_float(x: Any) -> Optional[float]:
    """Return float(x) or None if x is None/NaN/empty."""
    if x is None:
        return None
    try:
        val = float(x)
    except (TypeError, ValueError):
        return None
    if math.isnan(val):
        return None
    return val


def map_correlation_score(correlation_value: Optional[float]) -> int:
    """
    Map absolute Pearson correlation → 0–5 score.

    Bands (Evan-confirmed):
    [0, 0.05)   → 0
    [0.05, 0.10)→ 1
    [0.10, 0.20)→ 3
    [0.20, 0.35)→ 4
    [0.35, ∞)   → 5
    """
    val = _safe_float(correlation_value) or 0.0
    abs_r = abs(val)
    if abs_r < 0.05:
        return 0
    if abs_r < 0.10:
        return 1
    if abs_r < 0.20:
        return 3
    if abs_r < 0.35:
        return 4
    return 5


def map_lead_lag_score(lead_days: Optional[float]) -> int:
    """
    Map effective lead_days → 0–5 score.

    Rules (Evan-confirmed):
    lead_days <= 0 → 1
    1–3            → 2
    4–10           → 3
    11–30          → 4
    >30            → 5
    """
    val = _safe_float(lead_days)
    if val is None:
        return 1
    # Negative or zero → no reliable lead advantage
    if val <= 0:
        return 1
    if val <= 3:
        return 2
    if val <= 10:
        return 3
    if val <= 30:
        return 4
    return 5


@dataclass
class StressComponents:
    """Container for stress sensitivity components (already normalized to [0, 1])."""

    garch_effect: float
    regime_asymmetry: float
    stress_strategy_benefit: float

    def to_dict(self) -> Dict[str, float]:
        return asdict(self)


def compute_stress_components(
    beta_garch: Any,
    maxdd_stress: Any,
    maxdd_calm: Any,
    stress_sharpe_diff: Any,
) -> StressComponents:
    """
    Compute normalized stress components from raw estimates.

    Normalization (Evan-confirmed):
    - GARCH_effect          = min(1, |beta_garch| / 0.10)
    - Regime_Asymmetry      = min(1, (|maxdd_stress - maxdd_calm| * 100) / 60)
    - Stress_Strategy_Benefit = min(1, max(0, stress_sharpe_diff) / 1.0)
    """
    b = _safe_float(beta_garch)
    garch_effect = 0.0 if b is None else min(1.0, abs(b) / 0.10)

    dd_stress = _safe_float(maxdd_stress)
    dd_calm = _safe_float(maxdd_calm)
    if dd_stress is None or dd_calm is None:
        regime_asymmetry = 0.0
    else:
        diff_pct = abs(dd_stress - dd_calm) * 100.0
        regime_asymmetry = min(1.0, diff_pct / 60.0)

    sdiff = _safe_float(stress_sharpe_diff)
    if sdiff is None:
        stress_benefit = 0.0
    else:
        stress_benefit = min(1.0, max(0.0, sdiff) / 1.0)

    return StressComponents(
        garch_effect=garch_effect,
        regime_asymmetry=regime_asymmetry,
        stress_strategy_benefit=stress_benefit,
    )


def map_stress_sensitivity_score(components: StressComponents) -> Tuple[float, int]:
    """
    Map stress components → (CompositeScore ∈ [0,1], 0–5 score).

    Composite:
        CompositeScore = 0.50 * GARCH_effect
                       + 0.30 * Regime_Asymmetry
                       + 0.20 * Stress_Strategy_Benefit

    Score bands:
        [0.00, 0.20) → 0
        [0.20, 0.40) → 1
        [0.40, 0.60) → 2
        [0.60, 0.75) → 3
        [0.75, 0.90) → 4
        [0.90, 1.00] → 5
    """
    g = max(0.0, min(1.0, components.garch_effect))
    r = max(0.0, min(1.0, components.regime_asymmetry))
    s = max(0.0, min(1.0, components.stress_strategy_benefit))
    composite = 0.50 * g + 0.30 * r + 0.20 * s
    # Clamp numeric noise
    composite = max(0.0, min(1.0, composite))

    if composite < 0.20:
        score = 0
    elif composite < 0.40:
        score = 1
    elif composite < 0.60:
        score = 2
    elif composite < 0.75:
        score = 3
    elif composite < 0.90:
        score = 4
    else:
        score = 5
    return composite, score


@dataclass
class CausalityComponents:
    """Container for causality components (each in [0, 1])."""

    toda_yamamoto_score: float
    transfer_entropy_norm: float
    local_projections_component: float
    regime_activation_flag: float

    def to_dict(self) -> Dict[str, float]:
        return asdict(self)


def compute_causality_components(
    p_stress: Any,
    p_stress_loose: Any,
    te_credit_to_equity: Any,
    lp_t_stat: Any,
    regime_activation_flag: bool,
) -> CausalityComponents:
    """
    Compute normalized causality components from raw estimates.

    - Toda_Yamamoto_score:
        1.0 if p_stress < 0.05
        0.5 if p_stress < 0.10
        0.0 otherwise

      p_stress_loose is kept for completeness (e.g. additional lags or specs),
      but the primary thresholding uses p_stress.

    - TransferEntropy_norm = min(1, TE / 0.03)
    - LocalProjections_component = min(1, |t_stat| / 3.0)
    - Regime_activation_flag = 1.0 if regime_activation_flag else 0.0
    """
    p_strict = _safe_float(p_stress)
    p_loose = _safe_float(p_stress_loose)
    # Use the minimum of strict/loose where both exist, to be conservative.
    p = p_strict
    if p is None and p_loose is not None:
        p = p_loose
    elif p is not None and p_loose is not None:
        p = min(p, p_loose)

    if p is None:
        toda_score = 0.0
    elif p < 0.05:
        toda_score = 1.0
    elif p < 0.10:
        toda_score = 0.5
    else:
        toda_score = 0.0

    te = _safe_float(te_credit_to_equity)
    if te is None:
        te_norm = 0.0
    else:
        te_norm = min(1.0, max(0.0, te) / 0.03)

    t = _safe_float(lp_t_stat)
    if t is None:
        lp_comp = 0.0
    else:
        lp_comp = min(1.0, abs(t) / 3.0)

    raf = 1.0 if regime_activation_flag else 0.0

    return CausalityComponents(
        toda_yamamoto_score=toda_score,
        transfer_entropy_norm=te_norm,
        local_projections_component=lp_comp,
        regime_activation_flag=raf,
    )


def map_causality_score(
    components: CausalityComponents,
    p_stress: Optional[float],
) -> Tuple[float, int]:
    """
    Map causality components → (CompositeCausality ∈ [0,1], 0–5 score).

    Composite:
        CompositeCausality = 0.45 * Toda_Yamamoto_score
                           + 0.30 * TransferEntropy_norm
                           + 0.15 * LocalProjections_component
                           + 0.10 * Regime_activation_flag

    Score bands:
        Composite < 0.20 → 0
        0.20–<0.40       → 1
        0.40–<0.60       → 2
        0.60–<0.80       → 3
        0.80–<0.90       → 4
        >=0.90           → 5

    Additional rule:
        To assign score >= 3, require evidence of stress-sub-sample
        significance: p_stress < 0.05. If not satisfied, clamp score to 2.
    """
    t = max(0.0, min(1.0, components.toda_yamamoto_score))
    te = max(0.0, min(1.0, components.transfer_entropy_norm))
    lp = max(0.0, min(1.0, components.local_projections_component))
    raf = max(0.0, min(1.0, components.regime_activation_flag))

    composite = 0.45 * t + 0.30 * te + 0.15 * lp + 0.10 * raf
    composite = max(0.0, min(1.0, composite))

    if composite < 0.20:
        score = 0
    elif composite < 0.40:
        score = 1
    elif composite < 0.60:
        score = 2
    elif composite < 0.80:
        score = 3
    elif composite < 0.90:
        score = 4
    else:
        score = 5

    p_val = _safe_float(p_stress)
    if p_val is None or p_val >= 0.05:
        # Clamp to at most 2 if we do not have strong stress-regime significance
        score = min(score, 2)

    return composite, score

