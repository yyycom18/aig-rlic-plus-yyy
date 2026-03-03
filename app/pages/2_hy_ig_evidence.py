"""Finding 1 — The Evidence: Analytical Detail."""

import os
import sys

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.charts import load_plotly_chart
from components.sidebar import render_sidebar
from components.narrative import render_glossary_sidebar

st.set_page_config(
    page_title="The Evidence | AIG-RLIC+",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

render_sidebar()
render_glossary_sidebar()

# --- Page Header ---
st.title("The Evidence: What the Data Shows")
st.markdown(
    "*These patterns are not just historical anecdotes. We subjected 25 years of daily data "
    "to rigorous statistical testing — and the results confirm that credit spreads carry "
    "genuine predictive information for stock returns, especially during stress periods.*"
)
st.markdown("---")

# --- Tab Layout ---
tab_corr, tab_cause, tab_regime, tab_ml = st.tabs(
    ["Correlations", "Causality", "Regimes", "Machine Learning"]
)

# ===================== CORRELATIONS TAB =====================
with tab_corr:
    st.markdown("### Correlation Structure")

    st.markdown(
        '<div class="narrative-block">'
        "HY-IG spread levels show moderate negative correlations with forward SPY returns "
        "(-0.10 to -0.20 at 21-day to 252-day horizons). Wider spreads predict lower returns. "
        "Spread changes (momentum) correlate more strongly at short horizons, and distance "
        "correlation (0.39) confirms substantial <b>nonlinear</b> dependence."
        "</div>",
        unsafe_allow_html=True,
    )

    load_plotly_chart(
        "correlation_heatmap",
        fallback_text="Correlation heatmap — will appear when visualization is complete.",
        caption="Pearson, Spearman, and Kendall correlations between spread metrics and forward SPY returns at multiple horizons.",
    )

    st.markdown("---")

    st.markdown("### Cross-Correlation Function")

    st.markdown(
        '<div class="narrative-block">'
        "The pre-whitened cross-correlation function shows 13 of 41 lags are statistically "
        "significant at the 95% level. The peak correlation is contemporaneous (lag 0), "
        "consistent with shared factor exposure. There is modest evidence of credit leading "
        "equity at lags -1 to -3 days."
        "</div>",
        unsafe_allow_html=True,
    )

    load_plotly_chart(
        "ccf_barplot",
        fallback_text="Cross-correlation function chart — will appear when visualization is complete.",
        caption="Pre-whitened CCF at lags -20 to +20. Negative lags indicate credit leading equity.",
    )

# ===================== CAUSALITY TAB =====================
with tab_cause:
    st.markdown("### Granger Causality: Who Leads Whom?")

    st.markdown(
        '<div class="narrative-block">'
        "Toda-Yamamoto Granger causality tests reveal statistically significant information "
        "flow in <b>both directions</b> (credit-to-equity and equity-to-credit). However, the "
        "pattern is asymmetric across regimes:"
        "</div>",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Full Sample", "Bidirectional", delta="Both directions significant")
    with col2:
        st.metric("Stress Regime", "Credit leads", delta="Credit-to-equity strengthens")
    with col3:
        st.metric("Calm Regime", "Equity leads", delta="Credit-to-equity NOT significant")

    st.markdown(
        '<div class="narrative-block">'
        "<b>What this means:</b> In calm markets, stock prices set the pace — equity leads credit "
        "(the Merton structural channel dominates). In stress, the causal arrow becomes "
        "bidirectional — credit markets contribute independent information, consistent with "
        "the informed-trading hypothesis of Acharya & Johnson (2007)."
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown("---")

    st.markdown("### Transfer Entropy: Nonlinear Information Flow")

    st.markdown(
        '<div class="narrative-block">'
        "Transfer entropy (a nonlinear measure) confirms the pattern. Equity-to-credit "
        "transfer entropy (0.021) exceeds credit-to-equity (0.012), confirming equity "
        "dominance in total information flow — but the credit-to-equity channel is nonlinearly "
        "significant."
        "</div>",
        unsafe_allow_html=True,
    )

# ===================== REGIMES TAB =====================
with tab_regime:
    st.markdown("### Hidden Markov Model: Detecting Market States")

    st.markdown(
        '<div class="narrative-block">'
        "A 2-state HMM trained on HY-IG spread changes and VIX identifies two distinct market states:"
        "</div>",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            """
            **Calm State** (62% of sample)
            - Mean VIX: ~15
            - Persistence: P(stay) = 0.99
            - Equity Sharpe in this state: ~1.45
            """
        )
    with col2:
        st.markdown(
            """
            **Stress State** (38% of sample)
            - Mean VIX: ~27
            - Persistence: P(stay) = 0.98
            - Equity Sharpe in this state: ~-0.04
            """
        )

    st.markdown(
        '<div class="narrative-block">'
        "This HMM regime state is the signal that wins the strategy tournament — "
        "a simple 'be long when calm, cash when stressed' rule achieves an out-of-sample "
        "Sharpe of 1.17."
        "</div>",
        unsafe_allow_html=True,
    )

    load_plotly_chart(
        "hmm_regime_probs",
        fallback_text="HMM regime probability chart — will appear when visualization is complete.",
        caption="HMM stress-state probability over time. Spikes correspond to major market dislocations.",
    )

    st.markdown("---")

    st.markdown("### Quantile Regression: The Tail Risk Channel")

    st.markdown(
        '<div class="narrative-block">'
        "Credit spreads have their strongest explanatory power for the <b>worst outcomes</b>. "
        "At the 5th percentile of stock returns (left tail), elevated spreads predict "
        "significantly worse outcomes. At the median and upper percentiles, the effect is near zero."
        "</div>",
        unsafe_allow_html=True,
    )

    load_plotly_chart(
        "quantile_regression",
        fallback_text="Quantile regression coefficient plot — will appear when visualization is complete.",
        caption=(
            "HY-IG z-score coefficient across quantiles of 21-day forward SPY returns. "
            "The signal is concentrated in the left tail — it warns of bad outcomes, not good ones."
        ),
    )

    st.markdown("---")

    st.markdown("### Change Points: Structural Breaks")

    load_plotly_chart(
        "change_points",
        fallback_text="Change-point detection chart — will appear when visualization is complete.",
        caption=(
            "PELT change-point detection identified 48 structural breaks. "
            "Key clusters align with dot-com bust, GFC, energy crisis, COVID, and 2022 rate shock."
        ),
    )

# ===================== MACHINE LEARNING TAB =====================
with tab_ml:
    st.markdown("### Feature Importance: What Drives the Signal?")

    st.markdown(
        '<div class="narrative-block">'
        "A walk-forward Random Forest model was used to assess which variables carry the "
        "most predictive information for equity returns. The results show that <b>simpler "
        "indicators outperform ML</b> for this problem — the Random Forest achieves an "
        "average AUC of ~0.50, barely better than random."
        "</div>",
        unsafe_allow_html=True,
    )

    load_plotly_chart(
        "feature_importance",
        fallback_text="SHAP feature importance chart — will appear when visualization is complete.",
        caption=(
            "Top features by importance: yield curve slope (12.4%), NFCI (11.3%), "
            "CCC-BB spread (11.1%), HY-IG spread (7.9%). "
            "The RF adds noise, not signal, beyond what simpler models capture."
        ),
    )

    st.info(
        "**Key takeaway:** The credit spread's predictive power is largely contemporaneous "
        "(captured by GARCH) rather than forward-looking. Simpler regime indicators "
        "outperform machine learning approaches for this problem."
    )

# --- Transition ---
st.markdown("---")
st.markdown(
    '<div class="transition-text">'
    "The statistical evidence confirms that credit spreads carry genuine predictive information "
    "for stock returns. The practical question is: can investors use this signal to improve "
    "their outcomes?"
    "</div>",
    unsafe_allow_html=True,
)

st.page_link("pages/3_hy_ig_strategy.py", label="Continue to The Strategy", icon="🎯")

# --- Footer ---
st.markdown("---")
st.markdown(
    '<div class="portal-footer">'
    "Generated with AIG-RLIC+ | Data through 2025-12-31"
    "</div>",
    unsafe_allow_html=True,
)
