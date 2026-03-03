"""Plotly JSON chart loader and helper functions."""

import json
import os

import plotly.io as pio
import streamlit as st


CHART_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "output", "charts", "plotly")
METADATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "output", "charts", "metadata")


@st.cache_resource
def _load_plotly_json(json_path: str):
    """Load and parse a Plotly JSON file (cached)."""
    with open(json_path) as f:
        return pio.from_json(f.read())


def load_plotly_chart(
    chart_name: str,
    fallback_text: str = "Chart will appear when visualization is complete.",
    caption: str = None,
):
    """Load a Plotly chart from JSON file and render it.

    Args:
        chart_name: Filename without extension (e.g., 'hero_spread_vs_spy').
        fallback_text: Message shown if chart JSON not found.
        caption: Optional caption displayed below the chart.
    """
    json_path = os.path.normpath(os.path.join(CHART_DIR, f"{chart_name}.json"))
    if os.path.exists(json_path):
        fig = _load_plotly_json(json_path)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(f"📊 {fallback_text}")

    if caption:
        st.markdown(f'<p class="chart-caption">{caption}</p>', unsafe_allow_html=True)


def load_chart_metadata(chart_name: str) -> dict:
    """Load chart metadata sidecar JSON.

    Returns:
        dict with keys like 'title', 'caption', 'source', 'insight'.
        Empty dict if metadata file doesn't exist.
    """
    meta_path = os.path.normpath(os.path.join(METADATA_DIR, f"{chart_name}_meta.json"))
    if os.path.exists(meta_path):
        with open(meta_path) as f:
            return json.load(f)
    return {}


def chart_with_metadata(chart_name: str, default_caption: str = ""):
    """Load a chart and its metadata, rendering caption from metadata if available."""
    meta = load_chart_metadata(chart_name)
    caption = meta.get("caption", default_caption)
    load_plotly_chart(chart_name, caption=caption)
