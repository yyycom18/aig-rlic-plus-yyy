"""
Reproduce Environment Interaction scores for HY–IG → SPY.

This script:
- Loads raw evidence files from results/
- Applies the mapping rules documented in results/mapping_rules.json
- Prints intermediate components and final mapped scores as JSON

Usage (from project root):
    python -m scripts.reproduce_score
or:
    python scripts/reproduce_score.py
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict

import pandas as pd

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


BASE_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = BASE_DIR / "results"


def _load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _safe_mean(series: pd.Series) -> float:
    s = pd.to_numeric(series, errors="coerce").dropna()
    if s.empty:
        return float("nan")
    return float(s.mean())


def reproduce_hy_ig_spy() -> Dict[str, Any]:
    """Compute mapped scores and components for HY–IG spread → SPY."""
    env_path = RESULTS_DIR / "environment_interaction_scores_hy_ig_spy.json"
    env_scores = _load_json(env_path)["hy_ig_spread"]["SPY"]

    # 1) Correlation
    corr_value = env_scores.get("correlation_value")
    corr_score = map_correlation_score(corr_value)

    # 2) Lead / Lag (from CCF)
    ccf_path = RESULTS_DIR / "exploratory_20260228" / "ccf.csv"
    ccf = pd.read_csv(ccf_path)
    # Best significant lag by |ccf|
    ccf_sig = ccf.copy()
    if "significant_95" in ccf_sig.columns:
        ccf_sig = ccf_sig[ccf_sig["significant_95"] == True]  # noqa: E712
    ccf_sig = ccf_sig.dropna(subset=["ccf"])
    if not ccf_sig.empty:
        best_row = ccf_sig.iloc[ccf_sig["ccf"].abs().values.argmax()]
        best_lag = float(best_row["lag"])
    else:
        best_lag = 0.0
    # Lead_days: positive lags only; contemporaneous or negative treated as 0
    lead_days = best_lag if best_lag > 0 else 0.0
    lead_lag_score = map_lead_lag_score(lead_days)

    # 3) Stress sensitivity components
    # 3a) GARCH beta from GJR-GARCH output
    garch_path = RESULTS_DIR / "core_models_20260228" / "gjr_garch.csv"
    gjr = pd.read_csv(garch_path)
    row_beta = gjr[gjr["parameter"] == "hy_ig_spread_chg"].iloc[0]
    beta_garch = float(row_beta["value"])

    # 3b) Regime asymmetry from regime_descriptive_stats
    regime_path = RESULTS_DIR / "exploratory_20260228" / "regime_descriptive_stats.csv"
    regimes = pd.read_csv(regime_path)
    dd_calm = float(
        regimes.loc[regimes["regime"] == "Q1_calm", "max_drawdown"].iloc[0]
    )
    dd_stress = float(
        regimes.loc[regimes["regime"] == "Q4_stress", "max_drawdown"].iloc[0]
    )

    # 3c) Stress strategy benefit from stress_tests
    stress_path = (
        RESULTS_DIR / "tournament_validation_20260228" / "stress_tests.csv"
    )
    stress = pd.read_csv(stress_path)
    # Use HY-IG overlay winner (W1) across classic stress windows
    stress_windows = ["GFC", "COVID", "Taper_Tantrum", "Rate_Shock_2022"]
    mask = (stress["winner_id"] == "W1") & (stress["period"].isin(stress_windows))
    stress_sel = stress.loc[mask]
    if stress_sel.empty:
        stress_sharpe_diff = float("nan")
    else:
        stress_sharpe_diff = _safe_mean(
            stress_sel["strat_sharpe"] - stress_sel["bh_sharpe"]
        )

    stress_components: StressComponents = compute_stress_components(
        beta_garch=beta_garch,
        maxdd_stress=dd_stress,
        maxdd_calm=dd_calm,
        stress_sharpe_diff=stress_sharpe_diff,
    )
    stress_composite, stress_score = map_stress_sensitivity_score(stress_components)

    # 4) Causality components
    granger_path = RESULTS_DIR / "core_models_20260228" / "granger_causality.csv"
    granger = pd.read_csv(granger_path)
    # Credit->Equity in stress and calm
    g_stress = granger[
        (granger["direction"] == "Credit->Equity")
        & (granger["regime"] == "stress")
    ]
    g_calm = granger[
        (granger["direction"] == "Credit->Equity")
        & (granger["regime"] == "calm")
    ]
    p_stress = float(g_stress["p_value"].min()) if not g_stress.empty else float("nan")
    p_calm = float(g_calm["p_value"].min()) if not g_calm.empty else float("nan")

    # Regime activation: causal only in stress (reject in stress, fail to reject in calm)
    regime_activation_flag = (p_stress < 0.05) and (p_calm >= 0.05)

    # Transfer entropy (lag=1, Credit->Equity)
    te_path = RESULTS_DIR / "core_models_20260228" / "transfer_entropy.csv"
    te_df = pd.read_csv(te_path)
    te_row = te_df[
        (te_df["direction"] == "Credit->Equity") & (te_df["lag"] == 1)
    ].iloc[0]
    te_val = float(te_row["transfer_entropy"])

    # Local projections: state-dependent spread_chg_x_stress term at horizon 1
    lp_path = RESULTS_DIR / "core_models_20260228" / "local_projections.csv"
    lp_df = pd.read_csv(lp_path)
    lp_row = lp_df[
        (lp_df["horizon"] == 1)
        & (lp_df["specification"] == "state_dependent")
        & (lp_df["variable"] == "spread_chg_x_stress")
    ].iloc[0]
    lp_t_stat = float(lp_row["t_stat"])

    causality_components: CausalityComponents = compute_causality_components(
        p_stress=p_stress,
        p_stress_loose=p_stress,  # no separate loose spec yet
        te_credit_to_equity=te_val,
        lp_t_stat=lp_t_stat,
        regime_activation_flag=regime_activation_flag,
    )
    causality_composite, causality_score = map_causality_score(
        causality_components,
        p_stress=p_stress,
    )

    return {
        "inputs": {
            "environment_interaction_scores_hy_ig_spy": env_scores,
        },
        "correlation": {
            "correlation_value": corr_value,
            "abs_r": abs(corr_value) if isinstance(corr_value, (int, float)) else None,
            "mapped_score": corr_score,
        },
        "lead_lag": {
            "best_lag_from_ccf": best_lag,
            "lead_days": lead_days,
            "mapped_score": lead_lag_score,
        },
        "stress_sensitivity": {
            "beta_garch": beta_garch,
            "maxdd_calm": dd_calm,
            "maxdd_stress": dd_stress,
            "stress_sharpe_diff": stress_sharpe_diff,
            "components": stress_components.to_dict(),
            "composite": stress_composite,
            "mapped_score": stress_score,
        },
        "causality": {
            "p_stress": p_stress,
            "p_calm": p_calm,
            "regime_activation_flag": regime_activation_flag,
            "transfer_entropy_lag1": te_val,
            "lp_t_stat_h1_state_dependent": lp_t_stat,
            "components": causality_components.to_dict(),
            "composite": causality_composite,
            "mapped_score": causality_score,
        },
    }


def main() -> None:
    result = reproduce_hy_ig_spy()
    print(json.dumps(result, indent=2, default=float))


if __name__ == "__main__":
    main()

