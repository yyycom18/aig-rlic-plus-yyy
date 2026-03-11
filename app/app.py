"""AIG-RLIC+ Research Portal — Executive Summary Landing Page."""

import os
import sys

import streamlit as st

# Ensure components are importable
sys.path.insert(0, os.path.dirname(__file__))

from components.charts import load_plotly_chart
from components.identity_panel import render_identity_panel
from components.metrics import kpi_row
from components.narrative import render_glossary_sidebar
from components.sidebar import render_sidebar
from components.dna_card import render_dna_card
from core import (
    IndicatorDNALoader,
    IndicatorDNACardLoader,
    EnvironmentInteractionLoader,
)

st.set_page_config(
    page_title="AIG-RLIC+ Research Portal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Indicator DNA loaders (Step C – Task 1) ---
_CONFIG_DIR = os.path.join(os.path.dirname(__file__), "..", "config")
_DNA_JSON_PATH = os.path.join(_CONFIG_DIR, "indicator_dna.json")
_dna_loader = IndicatorDNALoader(json_path=_DNA_JSON_PATH)
_ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
_ENV_JSON_PATH = os.path.join(_ROOT_DIR, "results", "environment_interaction_scores_hy_ig_spy.json")
_env_loader = EnvironmentInteractionLoader(json_path=_ENV_JSON_PATH)
_DNA_CARDS_PATH = os.path.join(_ROOT_DIR, "data", "indicator_dna_cards.json")
_DNA_MAPPING_PATH = os.path.join(_ROOT_DIR, "data", "indicator_mapping.json")
_dna_card_loader = IndicatorDNACardLoader(cards_path=_DNA_CARDS_PATH, mapping_path=_DNA_MAPPING_PATH)

# Load custom CSS
css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- Sidebar ---
render_sidebar()
render_glossary_sidebar()

# Sidebar: indicator selector powered by IndicatorDNALoader
with st.sidebar:
    try:
        _dna_map = _dna_loader.load()
        _indicator_ids = sorted(_dna_map.keys())
    except Exception:
        _dna_map = {}
        _indicator_ids = []

    try:
        _env_map = _env_loader.get_all()
    except Exception:
        _env_map = {}

    if _indicator_ids:
        default_id = "hy_ig_spread" if "hy_ig_spread" in _indicator_ids else _indicator_ids[0]

        def _format_indicator(ind_id: str) -> str:
            dna = _dna_map.get(ind_id)
            return dna.name if dna else ind_id

        selected_indicator_id = st.selectbox(
            "Select Indicator",
            _indicator_ids,
            index=_indicator_ids.index(default_id) if default_id in _indicator_ids else 0,
            format_func=_format_indicator,
        )
        selected_dna = _dna_map.get(selected_indicator_id)

        # For now, we always use SPY as the environment
        env_dict = _env_map.get(selected_indicator_id, {})
        selected_env = env_dict.get("SPY")
    else:
        selected_indicator_id = None
        selected_dna = None
        selected_env = None

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

# --- Indicator Identity Panel (Step C) ---
# For now, behavioral metrics are wired to HY-IG study; DNA panel uses selected_dna.
render_identity_panel(
    study="hy_ig",
    monthly_data=None,
    analysis_data=None,
    strategy_data=None,
    indicator_dna=selected_dna,
    env_interaction=selected_env,
)

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

# --- Indicator DNA cards (library preview for Task 1) ---
st.markdown("### Indicator DNA cards — library preview")
try:
    cards_map = _dna_card_loader.get_all()
except Exception as exc:  # pragma: no cover - defensive
    st.warning(f"Unable to load Indicator DNA cards: {exc}")
    cards_map = {}

if cards_map:
    indicator_names = sorted(cards_map.keys())
    # Prefer HY-IG spread card if present, otherwise first in list
    default_name = "OAS (Option-Adjusted Spread) HY - IG spread"
    default_index = indicator_names.index(default_name) if default_name in indicator_names else 0
    selected_card_name = st.selectbox(
        "Browse Indicator DNA cards",
        indicator_names,
        index=default_index,
    )

    # Apply any in-session overrides for admin edits
    card = cards_map[selected_card_name]
    overrides = st.session_state.get("dna_card_overrides", {}).get(selected_card_name, {})
    if overrides:
        if "confidence" in overrides:
            card.confidence = overrides["confidence"]
        if "last_updated" in overrides:
            card.last_updated = overrides["last_updated"]
        if "why_classified" in overrides:
            card.why_classified = overrides["why_classified"]

    # Admin controls are guarded by an env flag; by default, users cannot edit
    admin_enabled = bool(os.getenv("DNA_ADMIN_ENABLED"))
    render_dna_card(card, admin_enabled=admin_enabled)
else:
    st.caption("No Indicator DNA cards available. Please check data files under `data/`.")

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
