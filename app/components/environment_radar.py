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
            f"(value {env.correlation_value:+.2f} vs benchmark)  "
            f"- **Lead / Lag:** {env.lead_lag_score:.1f}/5  "
            f"(lead ≈ {env.lead_days or 0} days)  "
            f"- **Stress sensitivity:** {env.stress_sensitivity_score:.1f}/5  "
            f"- **Causality:** {env.causality_score:.1f}/5"
        )

        # Evidence & mapping details (collapsed)
        with st.expander("Evidence & mapping (Environment Interaction)", expanded=False):
            # Provenance header
            if env.score_date or env.score_author or env.score_method:
                meta_lines = []
                if env.score_date:
                    meta_lines.append(f"**Score date:** {env.score_date}")
                if env.score_author:
                    meta_lines.append(f"**Analyst:** {env.score_author}")
                if env.score_method:
                    meta_lines.append(f"**Method:** {env.score_method}")
                st.markdown("  \n".join(meta_lines))
                st.markdown("---")

            # Axis-wise explanations
            st.markdown("**Why these scores?**")
            st.markdown(
                f"- **Correlation (Co-movement):** {env.correlation_score:.1f}/5 — "
                f"{env.correlation_interpretation or ''}"
            )
            st.markdown(
                f"- **Lead / Lag timing advantage:** {env.lead_lag_score:.1f}/5 — "
                f"{env.lead_lag_interpretation or ''}"
            )
            st.markdown(
                f"- **Sensitivity to market stress:** {env.stress_sensitivity_score:.1f}/5 — "
                f"{env.stress_sensitivity_interpretation or ''}"
            )
            st.markdown(
                f"- **Causality strength:** {env.causality_score:.1f}/5 — "
                f"{env.causality_interpretation or ''}"
            )

            # High-level mapping explanation (0–5 scale, no formulas)
            st.markdown("---")
            st.markdown("**How these scores are mapped (0–5 scale)**")
            st.markdown(
                "- **Correlation:** 0 means almost no link to the benchmark, "
                "3 means a noticeable relationship at multi‑week horizons, "
                "5 means an unusually strong and persistent co‑movement."
            )
            st.markdown(
                "- **Lead / Lag:** 1 means no reliable lead over the benchmark, "
                "3 means a short but useful timing edge, "
                "5 means the signal tends to move well ahead of the benchmark in a repeatable way."
            )
            st.markdown(
                "- **Sensitivity to market stress:** 0 means the signal barely reacts to market crises, "
                "3 means it clearly strengthens in stress, "
                "5 means it behaves almost like an on/off switch for stress regimes."
            )
            st.markdown(
                "- **Causality strength:** 0 means no directional evidence from the signal to the benchmark, "
                "3 means solid stress‑regime evidence but with caveats, "
                "5 means a very strong, regime‑aware causal channel that is rare in macro data."
            )

            # Provenance and reproducibility
            st.caption(
                "Mapping rules are documented in `results/mapping_rules.json` (v1, 2026‑03‑10) "
                "and can be reproduced with `scripts/reproduce_score.py`."
            )

            # Source files
            paths = env.score_source_files or []
            if paths:
                st.markdown("---")
                st.markdown("**Source files used for these scores:**")
                for p in paths:
                    st.markdown(f"- `{p}`")

