"""
Indicator Identity Panel — Step C UI component.
Modular, reusable. No backend econometric logic changes.
Behavioral radar (6 axes) + identity badge + research evidence (collapsible).
"""

from typing import Dict, List, Optional, Tuple

import plotly.graph_objects as go
import streamlit as st

# Identity badge colors (as specified)
IDENTITY_COLORS = {
    "Risk Overlay": "#2196F3",   # Blue
    "Alpha Generator": "#f44336",  # Red
    "Regime Filter": "#9C27B0",    # Purple
    "Weak Signal": "#9e9e9e",     # Gray
}

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


def _placeholder_behavioral_scores(
    study: str,
    monthly_data: Optional[Dict],
    analysis_data: Optional[Dict],
    strategy_data: Optional[Dict],
) -> List[float]:
    """
    Map existing computed metrics to 0–5 scale for radar. Heuristic placeholder.
    Order: Stability, Early Warning, Crisis Strength, Adaptability, Protection, Aggression.
    """
    scores = [2.5] * 6  # default mid
    if study in ("p03", "hy_ig") and strategy_data:
        metrics = strategy_data.get("performance_metrics", {}) or {}
        strat = (metrics.get("strategy") or {})
        spy = (metrics.get("spy") or {})
        out = (metrics.get("outperformance") or {})
        # Stability: use inverse of volatility ratio as proxy (heuristic)
        s_vol = strat.get("volatility") or 10
        b_vol = spy.get("volatility") or 10
        if b_vol > 0:
            stability = max(0, min(5, 5 - abs((s_vol / b_vol) - 1) * 2))
        else:
            stability = 2.5
        scores[0] = round(stability, 1)
        # Early Warning: lead-lag from analysis (if present)
        if analysis_data and analysis_data.get("lead_lag"):
            best = analysis_data["lead_lag"].get("best_correlation") or 0
            scores[1] = max(0, min(5, 2.5 + (best * 2.5)))
        else:
            scores[1] = 2.5
        # Crisis Strength: assume moderate for risk overlay
        scores[2] = 3.5
        # Adaptability: regime dispersion placeholder
        scores[3] = 3.0
        # Protection: max drawdown improvement (positive = strategy shallower drawdown)
        dd_imp = out.get("max_dd_improvement") or 0
        if isinstance(dd_imp, (int, float)):
            scores[4] = max(0, min(5, 2.5 + dd_imp / 10))
        # Aggression: CAGR improvement
        cagr_imp = out.get("annualized_return") or 0
        if isinstance(cagr_imp, (int, float)):
            scores[5] = max(0, min(5, 2.5 + cagr_imp / 2))
    elif study == "p02":
        scores = [3.0, 3.0, 2.5, 3.0, 2.5, 2.5]
    else:
        # hy_ig / default when no strategy data: use sensible placeholders
        scores = [3.0, 3.0, 3.5, 3.0, 3.2, 2.8]
    return [max(0, min(5, s)) for s in scores]


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


def _radar_fig(scores: List[float], dimensions: List[str]) -> go.Figure:
    """Build a clean radar chart. scores and dimensions same length (6)."""
    if len(scores) != 6 or len(dimensions) != 6:
        scores = (scores + [2.5] * 6)[:6]
        dimensions = (dimensions + BEHAVIORAL_DIMENSIONS)[:6]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=scores + [scores[0]],
        theta=dimensions + [dimensions[0]],
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
        height=380,
        margin=dict(l=80, r=80, t=40, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def render_identity_panel(
    study: str = "hy_ig",
    monthly_data: Optional[Dict] = None,
    analysis_data: Optional[Dict] = None,
    strategy_data: Optional[Dict] = None,
) -> None:
    """
    Render the Indicator Identity Panel above all charts/analysis.
    Identity badge, short description, 6-axis behavioral radar, expandable research evidence.
    """
    config = INDICATOR_CONFIG.get(study, INDICATOR_CONFIG["hy_ig"])
    name = config.get("name", "Indicator")
    identity_type = config.get("identity_type", "Risk Overlay")
    primary = config.get("primary_use_case", "")
    secondary = config.get("secondary_use_case", "")
    summary = config.get("one_line_summary", "")

    badge_color = IDENTITY_COLORS.get(identity_type, IDENTITY_COLORS["Weak Signal"])

    # Section 1 — Layout: [ Indicator Name ] [ Identity Badge ]
    st.markdown("---")
    col_title, col_badge = st.columns([3, 1])
    with col_title:
        st.markdown(f"## {name}")
    with col_badge:
        st.markdown(
            f'<span style="display:inline-block; padding: 0.4rem 0.8rem; border-radius: 8px; '
            f'background-color: {badge_color}; color: white; font-weight: 600;">{identity_type}</span>',
            unsafe_allow_html=True,
        )
    st.markdown("---")

    st.markdown(f"**Suggested identity:** {identity_type}")
    st.markdown(f"**Primary use case:** {primary}")
    st.markdown(f"**Secondary use case:** {secondary}")
    st.markdown(f"*{summary}*")
    st.markdown("---")

    # Section 2 — Radar chart (behavioral dimensions)
    scores = _placeholder_behavioral_scores(study, monthly_data, analysis_data, strategy_data)
    fig = _radar_fig(scores, BEHAVIORAL_DIMENSIONS)
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "**Behavioral dimensions:** Stability (relationship consistency) · Early Warning (leads stress) · "
        "Crisis Strength (during crashes) · Adaptability (across regimes) · Protection (drawdown reduction) · "
        "Aggression (return enhancement)"
    )
    st.markdown("---")

    # Section 3 — Expandable Research Evidence
    with st.expander("View Research Evidence", expanded=False):
        rows = _research_evidence_status(study)
        for method, status in rows:
            if status == "Completed":
                icon = "✓"
            elif status == "In Progress":
                icon = "◐"
            else:
                icon = "—"
            st.markdown(f"- **{method}:** {icon} {status}")
