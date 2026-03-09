"""
Environment Interaction Radar component.

Renders a 4-axis radar chart summarizing:
- Correlation with benchmark (Co-movement)
- Lead / Lag timing advantage
- Sensitivity to market stress
- Causality strength

Visual style follows the behavioral radar in `identity_panel.py`:
- White background
- Subtle grid
- Single accent color
"""

from typing import Optional, List

import plotly.graph_objects as go
import streamlit as st

from core import EnvironmentInteraction


_AXES = [
    "Correlation with benchmark",
    "Lead / Lag timing advantage",
    "Sensitivity to market stress",
    "Causality strength",
]


def _scores_from_env(env: Optional[EnvironmentInteraction]) -> List[float]:
    """
    Extract scores from EnvironmentInteraction.

    If env is None, return neutral scores (2.5) for all axes.
    """
    if env is None:
        return [2.5, 2.5, 2.5, 2.5]
    return [
        float(env.correlation_score),
        float(env.lead_lag_score),
        float(env.stress_sensitivity_score),
        float(env.causality_score),
    ]


def render_environment_radar(env: Optional[EnvironmentInteraction]) -> None:
    """
    Render the Environment Interaction Radar inside the Identity Panel.

    This function does not run any econometric computation; it only visualizes
    pre-computed scores supplied in EnvironmentInteraction.
    """
    scores = _scores_from_env(env)
    # Clamp scores to [0, 5] range
    scores = [max(0.0, min(5.0, s)) for s in scores]

    # Close the polygon by repeating first point
    r_vals = scores + [scores[0]]
    theta_vals = _AXES + [_AXES[0]]

    fig = go.Figure()
    # Lighter style if this is a placeholder (env is None)
    if env is None:
        fillcolor = "rgba(102, 126, 234, 0.12)"
        line = dict(color="#a5b4fc", width=1)
    else:
        fillcolor = "rgba(102, 126, 234, 0.3)"
        line = dict(color="#667eea", width=2)

    fig.add_trace(
        go.Scatterpolar(
            r=r_vals,
            theta=theta_vals,
            fill="toself",
            fillcolor=fillcolor,
            line=line,
            name="Environment interaction",
        )
    )
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 5], tickvals=[1, 2, 3, 4, 5]),
        ),
        showlegend=False,
        height=380,
        margin=dict(l=60, r=60, t=24, b=24),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    st.plotly_chart(fig, use_container_width=True)

    # Caption / fallback handling + textual summary for accessibility
    if env is None:
        st.caption(
            "Environment interaction not yet evaluated. "
            "Showing placeholder neutral scores (2.5/5) on all axes until evidence is available."
        )
    else:
        st.caption("Regime-dependent interaction; scores summarize existing evidence only.")
        # Provide a short numeric summary for users who struggle with polar charts
        st.markdown(
            f"- **Correlation:** {env.correlation_score:.1f}/5  "
            f"- **Lead / Lag:** {env.lead_lag_score:.1f}/5  "
            f"- **Stress sensitivity:** {env.stress_sensitivity_score:.1f}/5  "
            f"- **Causality:** {env.causality_score:.1f}/5"
        )

