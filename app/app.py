"""AIG-RLIC+ Research Portal — Executive Summary Landing Page."""

import os
import sys

import streamlit as st

# Ensure components are importable
sys.path.insert(0, os.path.dirname(__file__))

from components.charts import load_plotly_chart
from components.metrics import kpi_row
from components.sidebar import render_sidebar
from components.narrative import render_glossary_sidebar

st.set_page_config(
    page_title="AIG-RLIC+ Research Portal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load custom CSS
css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- Sidebar ---
render_sidebar()
render_glossary_sidebar()

# --- Header ---
st.title("AIG-RLIC+ Research Portal")
st.markdown("### Credit Market Signals for Equity Investors")

st.markdown(
    '<div class="narrative-block">'
    "The bond market often sees trouble coming before the stock market does — "
    "and the gap between risky and safe bond yields has been one of the most reliable "
    "early warning signals for stock market declines over the past 25 years."
    "</div>",
    unsafe_allow_html=True,
)

st.markdown("---")

# --- KPI Cards ---
kpi_row(
    [
        {"label": "OOS Sharpe Ratio", "value": "1.17", "delta": "+0.40 vs buy-and-hold"},
        {
            "label": "Max Drawdown",
            "value": "-11.6%",
            "delta": "-33.7% buy-and-hold",
            "delta_color": "inverse",
        },
        {"label": "Combinations Tested", "value": "2,304"},
        {"label": "Academic Citations", "value": "25"},
        {"label": "OOS Window", "value": "8 years", "delta": "2018-2025"},
    ]
)

st.markdown("---")

# --- Hero Chart ---
st.markdown("### The Big Picture: Credit Spreads vs. Equity Prices (2000-2025)")
load_plotly_chart(
    "hero_spread_vs_spy",
    fallback_text="Hero chart — HY-IG spread vs SPY (2000-2025) — will appear when visualization is complete.",
    caption=(
        "Dual-axis view: HY-IG credit spread (left, inverted) and S&P 500 price (right). "
        "Gray bands mark NBER recessions. Notice how the spread widens (falls on inverted axis) "
        "before or during equity declines."
    ),
)

st.markdown("---")

# --- Finding Index ---
st.markdown("### Current Findings")

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
        **Finding 1: HY-IG Credit Spread as Equity Signal**

        Does the gap between high-yield and investment-grade bond yields
        predict stock market returns? We tested this with 25 years of daily data,
        12 econometric methods, and a 2,304-combination strategy tournament.
        """
    )

    st.page_link(
        "pages/1_hy_ig_story.py",
        label="Read the full story",
        icon="📖",
    )

with col2:
    st.markdown(
        """
        **Key Results:**

        - Credit leads equity during stress, but equity leads credit during calm periods
        - HMM regime detection is the strongest signal — a simple Long/Cash strategy
          achieves OOS Sharpe of 1.17 with max drawdown of -11.6%
        - Value comes from drawdown avoidance, not alpha generation
        - The signal does not protect against rate-driven selloffs (2022)
        """
    )

# --- Footer ---
st.markdown("---")
st.markdown(
    '<div class="portal-footer">'
    "Generated with AIG-RLIC+ | Data through 2025-12-31 | "
    "Sample: 2000-01-01 to 2025-12-31 (6,783 daily observations)"
    "</div>",
    unsafe_allow_html=True,
)
