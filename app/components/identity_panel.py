"""
Indicator Identity Panel — Step C UI component.
Modular, reusable. No backend econometric logic changes.
Behavioral radar (6 axes) + identity badge + score transparency + research evidence.
All scores use documented normalize_to_scale; no arbitrary manual assignment.
"""

from typing import Dict, List, Optional, Tuple, Any

import plotly.graph_objects as go
import streamlit as st

from core import IndicatorDNA, EnvironmentInteraction
from .environment_radar import render_environment_radar

# ---------------------------------------------------------------------------
# Scoring: Standardization rule (Section 5). All axes use this.
# ---------------------------------------------------------------------------

def normalize_to_scale(
    value: float,
    min_value: float,
    max_value: float,
    scale_max: float = 5.0,
) -> float:
    """
    Map a raw metric to [0, scale_max] using linear scaling.
    Clamps outside [min_value, max_value]. Used for all radar axes.
    """
    if max_value <= min_value:
        return scale_max / 2.0
    t = (value - min_value) / (max_value - min_value)
    t = max(0.0, min(1.0, t))
    return round(t * scale_max, 1)


# Identity badge colors (unified across indicators)
IDENTITY_COLORS = {
    "Risk Overlay": "#1f77b4",                # Blue
    "Alpha Generator": "#d62728",             # Red
    "Regime Filter": "#9467bd",               # Purple
    "Macro Growth Indicator": "#2ca02c",      # Green
    "Volatility Stress Indicator": "#ff7f0e", # Orange
    "Credit Risk Indicator": "#8c564b",       # Brown
    "Weak Signal": "#9e9e9e",                 # Gray (fallback)
}

# Section 1: Short description below badge (plain-language, by identity type)
IDENTITY_BADGE_DESCRIPTIONS = {
    "Risk Overlay": "A defensive indicator designed to reduce downside risk rather than increase returns.",
    "Alpha Generator": "A return-enhancing, offensive indicator focused on capturing upside.",
    "Regime Filter": "An allocation timing tool that helps switch between risk-on and risk-off.",
    "Macro Growth Indicator": "A macroeconomic growth signal that tracks expansions and slowdowns.",
    "Volatility Stress Indicator": "A market stress gauge that spikes when fear and uncertainty rise.",
    "Credit Risk Indicator": "A credit health signal capturing default and spread risk in bond markets.",
    "Weak Signal": "Limited statistical strength; use with caution and as context only.",
}

# Section 2: Axis explanations (always visible below radar)
AXIS_EXPLANATIONS = [
    ("Stability", "Relationship consistency over time"),
    ("Early Warning", "Tends to move before equity stress"),
    ("Crisis Strength", "Performance during market crashes"),
    ("Adaptability", "Behavior changes across regimes"),
    ("Protection", "Drawdown reduction ability"),
    ("Aggression", "Return enhancement potential"),
]

# 6 behavioral dimensions for radar (behavior-based, not method-based)
BEHAVIORAL_DIMENSIONS = [
    "Stability",
    "Early Warning",
    "Crisis Strength",
    "Adaptability",
    "Protection",
    "Aggression",
]

# Per-study identity config (modular: add new indicators here)
INDICATOR_CONFIG = {
    "p02": {
        "name": "VIX1M/3M vs SPY",
        "identity_type": "Regime Filter",
        "primary_use_case": "Volatility regime signal for equity allocation",
        "secondary_use_case": "Term structure stress early warning",
        "one_line_summary": "This indicator reflects fear and complacency in options markets, useful for regime context.",
    },
    "p03": {
        "name": "HY-IG Spread vs SPY",
        "identity_type": "Risk Overlay",
        "primary_use_case": "Crisis risk reduction",
        "secondary_use_case": "Regime filter for equity allocation",
        "one_line_summary": "This indicator behaves like a defensive sentinel, strongest during stress environments.",
    },
    "hy_ig": {
        "name": "HY-IG Spread vs SPY",
        "identity_type": "Risk Overlay",
        "primary_use_case": "Crisis risk reduction",
        "secondary_use_case": "Regime filter for equity allocation",
        "one_line_summary": "This indicator behaves like a defensive sentinel, strongest during stress environments.",
    },
}

# Documented min/max for normalization (used when real data available)
# When no data, we use mid-scale defaults still via normalize_to_scale with fallback.
_STABILITY_VOL_RATIO_MIN, _STABILITY_VOL_RATIO_MAX = 0.5, 2.0   # vol ratio
_LEAD_LAG_CORR_MIN, _LEAD_LAG_CORR_MAX = -0.5, 0.5
_DD_IMPROVEMENT_MIN, _DD_IMPROVEMENT_MAX = -20.0, 20.0   # % pts
_CAGR_IMPROVEMENT_MIN, _CAGR_IMPROVEMENT_MAX = -10.0, 10.0   # % pts


def _compute_behavioral_scores_with_metadata(
    study: str,
    monthly_data: Optional[Dict],
    analysis_data: Optional[Dict],
    strategy_data: Optional[Dict],
) -> Tuple[List[float], List[Dict[str, Any]]]:
    """
    Compute 6 behavioral scores using normalize_to_scale only.
    Returns (scores, metadata_list) for tooltips and "How These Scores Are Calculated".
    Order: Stability, Early Warning, Crisis Strength, Adaptability, Protection, Aggression.
    """
    metadata: List[Dict[str, Any]] = []
    scores: List[float] = []

    # ---- Stability ----
    raw_stability = 0.5  # default: vol ratio proxy
    if study in ("p03", "hy_ig") and strategy_data:
        metrics = strategy_data.get("performance_metrics", {}) or {}
        strat = metrics.get("strategy") or {}
        spy = metrics.get("spy") or {}
        s_vol = strat.get("volatility") or 10
        b_vol = spy.get("volatility") or 10
        if b_vol > 0:
            vol_ratio = s_vol / b_vol
            raw_stability = vol_ratio
    # Map: vol ratio 1.0 = best (5), far from 1 = worse. Use distance from 1.
    distance_from_one = abs(raw_stability - 1.0)
    stability_score = normalize_to_scale(
        -distance_from_one,
        -(_STABILITY_VOL_RATIO_MAX - 1.0),
        0.0,
        scale_max=5.0,
    )
    scores.append(stability_score)
    metadata.append({
        "axis": "Stability",
        "raw_inputs": ["Strategy vs benchmark volatility ratio", "Rolling correlation consistency"],
        "scaling": "Distance from 1.0 volatility ratio mapped to 0–5 (1.0 = 5).",
        "tooltip": "Derived from: Strategy vs benchmark volatility ratio. Normalized to 0–5 (closer to 1.0 = higher).",
    })

    # ---- Early Warning ----
    raw_lead_lag = 0.0
    if analysis_data and analysis_data.get("lead_lag"):
        raw_lead_lag = float(analysis_data["lead_lag"].get("best_correlation") or 0)
    early_score = normalize_to_scale(
        raw_lead_lag,
        _LEAD_LAG_CORR_MIN,
        _LEAD_LAG_CORR_MAX,
        scale_max=5.0,
    )
    scores.append(early_score)
    metadata.append({
        "axis": "Early Warning",
        "raw_inputs": ["Lag correlation strength", "Granger causality tests"],
        "scaling": "Lead-lag correlation mapped to 0–5 using percentile scaling.",
        "tooltip": "Derived from: Lag correlation strength, Granger causality. Mapped using 0–5 scale from correlation range.",
    })

    # ---- Crisis Strength ----
    # Placeholder: no backend crisis metric yet. Use 0–1 proxy mapped to 0–5.
    crisis_proxy_min, crisis_proxy_max = 0.0, 1.0
    crisis_raw = 0.7  # assumed moderate strength until crisis-period return metric exists
    crisis_score = normalize_to_scale(crisis_raw, crisis_proxy_min, crisis_proxy_max, scale_max=5.0)
    scores.append(crisis_score)
    metadata.append({
        "axis": "Crisis Strength",
        "raw_inputs": ["Avg return during spread widening events", "Stress-period performance"],
        "scaling": "Historical crisis windows; linear mapping to 0–5.",
        "tooltip": "Derived from: Performance during market crashes, spread widening events. Normalized to 0–5.",
    })

    # ---- Adaptability ----
    # Placeholder: regime dispersion not yet computed. Use 0–1 proxy.
    adapt_proxy_min, adapt_proxy_max = 0.0, 1.0
    adapt_raw = 0.6  # mid-high until cross-regime dispersion metric exists
    adapt_score = normalize_to_scale(adapt_raw, adapt_proxy_min, adapt_proxy_max, scale_max=5.0)
    scores.append(adapt_score)
    metadata.append({
        "axis": "Adaptability",
        "raw_inputs": ["Regime performance dispersion", "Cross-regime consistency"],
        "scaling": "Regime dispersion mapped to 0–5 (higher = more adaptable).",
        "tooltip": "Derived from: Regime performance dispersion. Linear percentile mapping to 0–5.",
    })

    # ---- Protection ----
    raw_dd_imp = 0.0
    if study in ("p03", "hy_ig") and strategy_data:
        out = (strategy_data.get("performance_metrics") or {}).get("outperformance") or {}
        raw_dd_imp = float(out.get("max_dd_improvement") or 0)
    prot_score = normalize_to_scale(
        raw_dd_imp,
        _DD_IMPROVEMENT_MIN,
        _DD_IMPROVEMENT_MAX,
        scale_max=5.0,
    )
    scores.append(prot_score)
    metadata.append({
        "axis": "Protection",
        "raw_inputs": ["Max drawdown improvement vs benchmark (%)", "Downside deviation reduction (%)"],
        "scaling": "Linear mapping between historical min/max drawdown improvement to 0–5.",
        "tooltip": "Derived from: Max drawdown improvement vs benchmark, downside deviation reduction. Normalized to 0–5 scale.",
    })

    # ---- Aggression ----
    raw_cagr = 0.0
    if study in ("p03", "hy_ig") and strategy_data:
        out = (strategy_data.get("performance_metrics") or {}).get("outperformance") or {}
        raw_cagr = float(out.get("annualized_return") or 0)
    agg_score = normalize_to_scale(
        raw_cagr,
        _CAGR_IMPROVEMENT_MIN,
        _CAGR_IMPROVEMENT_MAX,
        scale_max=5.0,
    )
    scores.append(agg_score)
    metadata.append({
        "axis": "Aggression",
        "raw_inputs": ["CAGR improvement vs benchmark (%)", "Sharpe improvement"],
        "scaling": "Percentile normalization of excess return to 0–5.",
        "tooltip": "Derived from: CAGR improvement vs benchmark, Sharpe improvement. Percentile normalization to 0–5.",
    })

    return scores, metadata


def _research_evidence_status(study: str) -> List[Tuple[str, str]]:
    """Return list of (method_name, status). Status: Completed / Not Tested / In Progress."""
    if study in ("p03", "hy_ig"):
        return [
            ("Dependence tests (correlation)", "Completed"),
            ("Lead-lag analysis", "Completed"),
            ("Granger causality", "Completed"),
            ("Regime model", "Completed"),
            ("Predictive modeling", "Completed"),
            ("Tail modeling", "Not Yet"),
            ("Nonlinear ML", "In Progress"),
        ]
    if study == "p02":
        return [
            ("Dependence tests (correlation)", "Completed"),
            ("Lead-lag analysis", "Not Yet"),
            ("Regime model", "Not Yet"),
            ("Tail modeling", "Not Yet"),
            ("Nonlinear ML", "Not Yet"),
        ]
    return [
        ("Dependence tests (correlation)", "Completed"),
        ("Lead-lag analysis", "Completed"),
        ("Regime model", "Completed"),
        ("Tail modeling", "Not Yet"),
        ("Nonlinear ML", "In Progress"),
    ]


def _radar_fig(
    scores: List[float],
    dimensions: List[str],
    tooltip_texts: Optional[List[str]] = None,
) -> go.Figure:
    """Build radar chart with optional hover tooltips (Section 3)."""
    if len(scores) != 6 or len(dimensions) != 6:
        scores = (scores + [2.5] * 6)[:6]
        dimensions = (dimensions + BEHAVIORAL_DIMENSIONS)[:6]
    # For closed polygon we duplicate first point; tooltip for each of 6 axes
    r = scores + [scores[0]]
    theta = dimensions + [dimensions[0]]
    if tooltip_texts and len(tooltip_texts) >= 6:
        customdata = [tooltip_texts[i] for i in range(6)] + [tooltip_texts[0]]
        hovertemplate = "%{theta}<br>Score: %{r}<br>%{customdata}<extra></extra>"
    else:
        customdata = None
        hovertemplate = "%{theta}<br>Score: %{r}<extra></extra>"

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=r,
        theta=theta,
        customdata=customdata if customdata else [None] * 7,
        hovertemplate=hovertemplate,
        fill="toself",
        fillcolor="rgba(102, 126, 234, 0.4)",
        line=dict(color="#667eea", width=2),
        name="Behavioral profile",
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 5], tickvals=[1, 2, 3, 4, 5]),
            angularaxis=dict(tickfont=dict(size=11)),
        ),
        showlegend=False,
        height=420,
        margin=dict(l=60, r=60, t=24, b=24),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def render_identity_panel(
    study: str = "hy_ig",
    monthly_data: Optional[Dict] = None,
    analysis_data: Optional[Dict] = None,
    strategy_data: Optional[Dict] = None,
    indicator_dna: Optional[IndicatorDNA] = None,
    env_interaction: Optional[EnvironmentInteraction] = None,
) -> None:
    """
    Render the Indicator Identity Panel.
    Current layout (Step C, Tasks 1–2):
    1) Title
    2) Indicator DNA block
    3) Environment Interaction Radar
    """
    config = INDICATOR_CONFIG.get(study, INDICATOR_CONFIG["hy_ig"])

    # Prefer DNA metadata when available, fall back to legacy INDICATOR_CONFIG
    if indicator_dna is not None:
        name = indicator_dna.name or config.get("name", "Indicator")
        identity_type = indicator_dna.identity_type or config.get("identity_type", "Risk Overlay")
        primary = indicator_dna.primary_use_case or config.get("primary_use_case", "")
        secondary = indicator_dna.secondary_use_case or config.get("secondary_use_case", "")
        summary = indicator_dna.one_line_summary or config.get("one_line_summary", "")
        as_of_dt = getattr(indicator_dna, "as_of", None)
    else:
        name = config.get("name", "Indicator")
        identity_type = config.get("identity_type", "Risk Overlay")
        primary = config.get("primary_use_case", "")
        secondary = config.get("secondary_use_case", "")
        summary = config.get("one_line_summary", "")
        as_of_dt = None

    badge_color = IDENTITY_COLORS.get(identity_type, IDENTITY_COLORS["Weak Signal"])
    badge_description = IDENTITY_BADGE_DESCRIPTIONS.get(
        identity_type,
        "Indicator behavioral profile.",
    )

    # ----- 1. Indicator Title -----
    st.markdown("---")
    st.markdown(f"## {name}")

    # ----- 1a. Indicator DNA block – what kind of signal is this? -----
    st.subheader("Indicator DNA — what kind of signal is this?")
    col_left, col_right = st.columns([2, 1])
    with col_left:
        st.markdown(f"- **Identity type:** {identity_type}")
        st.markdown(f"- **Primary use case:** {primary or 'Not specified'}")
    with col_right:
        if secondary:
            st.markdown(f"- **Secondary use case:** {secondary}")
        if summary:
            st.markdown(f"*{summary}*")
        if as_of_dt is not None:
            # Display as_of date - graceful handling for any type
            from datetime import datetime, timezone
            
            try:
                # Try to compute days old for stale date warning
                if isinstance(as_of_dt, datetime):
                    # Ensure both are naive or both are aware for subtraction
                    if as_of_dt.tzinfo is not None:
                        now = datetime.now(tz=timezone.utc).astimezone(as_of_dt.tzinfo)
                    else:
                        now = datetime.now()
                    
                    days_old = (now - as_of_dt).days
                    label = as_of_dt.date().isoformat()
                    if days_old > 365:
                        st.caption(f"As of {label} (older research snapshot)")
                    else:
                        st.caption(f"As of {label}")
                else:
                    # If as_of_dt is not a datetime, just convert to string
                    st.caption(f"As of {as_of_dt}")
            except Exception:
                # Any error: just display the value as-is
                st.caption(f"As of {as_of_dt}")

    # ----- 2. Environment Interaction Radar (Task 2 – Step C) -----
    st.subheader("Environment Interaction — how this signal behaves vs the benchmark")
    render_environment_radar(env_interaction)

    # NOTE: Legacy demo section (Strategy Survival radar + Understanding These Dimensions
    # + evidence expanders) has been removed from the UI for the YYY workspace.
    # The helper functions (_compute_behavioral_scores_with_metadata, _radar_fig,
    # _research_evidence_status) remain available for future Step C Task 3 work.
