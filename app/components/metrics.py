"""KPI card renderer components."""

import streamlit as st


def kpi_card(label: str, value: str, delta: str = None, delta_color: str = "normal"):
    """Render a single KPI metric card."""
    st.metric(label=label, value=value, delta=delta, delta_color=delta_color)


def kpi_row(metrics: list[dict]):
    """Render a row of KPI cards.

    Args:
        metrics: List of dicts with keys matching kpi_card params
                 (label, value, delta, delta_color).
    """
    cols = st.columns(len(metrics))
    for col, m in zip(cols, metrics):
        with col:
            kpi_card(**m)
