from __future__ import annotations

import math

import numpy as np

from app.core.environment_mapping import (
    StressComponents,
    CausalityComponents,
    compute_stress_components,
    compute_causality_components,
    map_correlation_score,
    map_lead_lag_score,
    map_stress_sensitivity_score,
    map_causality_score,
)


def test_map_correlation_score_bands():
    # Below 0.05 → 0
    assert map_correlation_score(0.0) == 0
    assert map_correlation_score(0.049) == 0
    # [0.05, 0.10) → 1
    assert map_correlation_score(0.05) == 1
    assert map_correlation_score(0.099) == 1
    # [0.10, 0.20) → 3
    assert map_correlation_score(0.10) == 3
    assert map_correlation_score(0.199) == 3
    # [0.20, 0.35) → 4
    assert map_correlation_score(0.20) == 4
    assert map_correlation_score(0.349) == 4
    # >= 0.35 → 5
    assert map_correlation_score(0.35) == 5
    assert map_correlation_score(0.8) == 5


def test_map_lead_lag_score_bands():
    assert map_lead_lag_score(0) == 1
    assert map_lead_lag_score(-5) == 1
    assert map_lead_lag_score(1) == 2
    assert map_lead_lag_score(3) == 2
    assert map_lead_lag_score(4) == 3
    assert map_lead_lag_score(10) == 3
    assert map_lead_lag_score(11) == 4
    assert map_lead_lag_score(30) == 4
    assert map_lead_lag_score(31) == 5


def test_compute_stress_components_and_mapping_basic():
    # Simple non-edge inputs
    comps = compute_stress_components(
        beta_garch=0.05,  # → 0.5
        maxdd_stress=-0.40,
        maxdd_calm=-0.10,  # diff = 30pp → 0.5
        stress_sharpe_diff=0.5,  # → 0.5
    )
    assert math.isclose(comps.garch_effect, 0.5, rel_tol=1e-6)
    assert math.isclose(comps.regime_asymmetry, 0.5, rel_tol=1e-6)
    assert math.isclose(comps.stress_strategy_benefit, 0.5, rel_tol=1e-6)

    composite, score = map_stress_sensitivity_score(comps)
    # Composite = 0.5*0.5 + 0.3*0.5 + 0.2*0.5 = 0.5
    assert math.isclose(composite, 0.5, rel_tol=1e-6)
    assert score == 2  # in [0.40, 0.60)


def test_compute_stress_components_handles_nans():
    comps = compute_stress_components(
        beta_garch=np.nan,
        maxdd_stress=None,
        maxdd_calm=None,
        stress_sharpe_diff="NaN",
    )
    assert comps.garch_effect == 0.0
    assert comps.regime_asymmetry == 0.0
    assert comps.stress_strategy_benefit == 0.0
    composite, score = map_stress_sensitivity_score(comps)
    assert composite == 0.0
    assert score == 0


def test_compute_causality_components_and_mapping_basic():
    comps = compute_causality_components(
        p_stress=0.01,
        p_stress_loose=0.02,
        te_credit_to_equity=0.015,  # → 0.5
        lp_t_stat=2.0,  # → 2/3
        regime_activation_flag=True,
    )
    assert comps.toda_yamamoto_score == 1.0
    assert math.isclose(comps.transfer_entropy_norm, 0.5, rel_tol=1e-6)
    assert math.isclose(comps.local_projections_component, 2.0 / 3.0, rel_tol=1e-6)
    assert comps.regime_activation_flag == 1.0

    composite, score = map_causality_score(comps, p_stress=0.01)
    assert 0.6 <= composite <= 1.0
    assert score >= 3  # strong stress‑regime significance allows high scores


def test_map_causality_score_clamps_without_stress_significance():
    comps = CausalityComponents(
        toda_yamamoto_score=1.0,
        transfer_entropy_norm=1.0,
        local_projections_component=1.0,
        regime_activation_flag=1.0,
    )
    composite, score = map_causality_score(comps, p_stress=0.20)
    assert 0.0 <= composite <= 1.0
    # Without p_stress < 0.05 we should never exceed score 2
    assert score <= 2

