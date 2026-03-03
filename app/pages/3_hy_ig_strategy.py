"""Finding 1 — The Strategy: Tournament Winner and Alternatives."""

import os
import sys

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.charts import load_plotly_chart
from components.metrics import kpi_row
from components.sidebar import render_sidebar
from components.narrative import render_glossary_sidebar
from components.tournament import render_tournament_leaderboard

st.set_page_config(
    page_title="The Strategy | AIG-RLIC+",
    page_icon="🎯",
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
st.title("The Strategy: Translating Signals to Action")
st.markdown(
    "*So what should an investor do with this information? We tested 2,304 strategy "
    "combinations to find the most robust answer.*"
)
st.markdown("---")

# ===================== TOURNAMENT WINNER SPOTLIGHT =====================
st.markdown("### Tournament Winner: HMM Long/Cash (W1)")

st.markdown(
    '<div class="spotlight-card">'
    "<b>Strategy Rule in Plain English:</b><br>"
    "When the Hidden Markov Model assigns a probability greater than 70% to the 'stress' "
    "regime (based on credit spread changes and VIX levels), move to cash. When the stress "
    "probability drops below 70%, return to full equity exposure."
    "</div>",
    unsafe_allow_html=True,
)

st.markdown("")

# Winner KPI cards
kpi_row(
    [
        {"label": "OOS Sharpe Ratio", "value": "1.17", "delta": "+52% vs buy-and-hold"},
        {"label": "OOS Annualized Return", "value": "11.0%"},
        {
            "label": "Max Drawdown",
            "value": "-11.6%",
            "delta": "vs -33.7% B&H",
            "delta_color": "inverse",
        },
        {"label": "Annual Turnover", "value": "~5 trades/yr"},
        {"label": "Bootstrap p-value", "value": "< 0.001"},
    ]
)

st.markdown("---")

# ===================== INTERACTIVE TOURNAMENT LEADERBOARD =====================
load_plotly_chart(
    "tournament_leaderboard",
    fallback_text="Interactive tournament leaderboard chart — will appear when visualization is complete.",
)

render_tournament_leaderboard()

st.markdown(
    """
    **Key patterns from the tournament:**
    - **Long/Cash (P1) dominates.** No Long/Short or signal-strength strategy appears in the top 10.
    - **HMM regime state is the best signal** — the tournament winner is a simple "be long when calm, cash when stressed."
    - **Z-score with Bollinger thresholds** is the best non-model-based approach.
    - **Same-day (L0) signals dominate**, contradicting the hypothesis of multi-day lead times.
    """
)

st.markdown("---")

# ===================== EQUITY CURVES =====================
st.markdown("### Equity Curves: Top Strategies vs. Buy-and-Hold")

load_plotly_chart(
    "equity_curves",
    fallback_text="Equity curves for top 3 strategies vs buy-and-hold — will appear when visualization is complete.",
    caption=(
        "Cumulative returns for the top 3 tournament winners compared to buy-and-hold SPY (2018-2025). "
        "Note how HMM strategies avoid the major drawdowns while capturing most of the upside."
    ),
)

st.markdown("---")

# ===================== DRAWDOWN COMPARISON =====================
st.markdown("### Drawdown Comparison")

load_plotly_chart(
    "drawdown_comparison",
    fallback_text="Drawdown comparison chart — will appear when visualization is complete.",
    caption=(
        "Peak-to-trough drawdown profiles. The HMM Long/Cash strategy (W1) limits maximum "
        "drawdown to -11.6%, compared to -33.7% for buy-and-hold during the same period."
    ),
)

st.markdown("---")

# ===================== VALIDATION =====================
st.markdown("### Validation: Stress Tests, Signal Decay, and Walk-Forward")

val_tab1, val_tab2, val_tab3 = st.tabs(["Stress Tests", "Signal Decay", "Walk-Forward"])

with val_tab1:
    st.markdown("#### Performance Across Stress Episodes")

    load_plotly_chart(
        "stress_test_table",
        fallback_text="Stress test results table — will appear when visualization is complete.",
    )

    st.markdown(
        """
        | Stress Episode | HMM W1 Max DD | Buy-and-Hold Max DD | Outcome |
        |:---------------|:-------------:|:-------------------:|:--------|
        | GFC (2007-09) | -6% | -55% | **HMM dramatically outperforms** |
        | COVID (2020) | Mixed | -34% | HMM lagged the V-shaped recovery |
        | 2022 Rate Shock | Underperforms | -25% | Signal did not detect rate-driven selloff |
        """
    )

    st.markdown(
        '<div class="narrative-block">'
        "<b>Honest assessment:</b> The HMM strategy excels at credit-driven crises (GFC) "
        "but does not protect against rate-driven selloffs (2022) where credit spreads "
        "widen alongside equities for different reasons."
        "</div>",
        unsafe_allow_html=True,
    )

with val_tab2:
    st.markdown("#### Signal Decay with Execution Delay")

    load_plotly_chart(
        "signal_decay",
        fallback_text="Signal decay chart — will appear when visualization is complete.",
        caption=(
            "Adding a 1-day execution delay drops Sharpe by 0.15-0.25 (material but not fatal). "
            "A 5-day delay costs 0.3-0.5 in Sharpe."
        ),
    )

    st.markdown(
        '<div class="narrative-block">'
        "Execution speed matters. The signal degrades with delay, reflecting the speed at "
        "which credit information is priced into equities. Same-day or next-day execution "
        "is recommended."
        "</div>",
        unsafe_allow_html=True,
    )

with val_tab3:
    st.markdown("#### Walk-Forward Sharpe Ratio Over Time")

    load_plotly_chart(
        "walk_forward_sharpe",
        fallback_text="Walk-forward Sharpe ratio chart — will appear when visualization is complete.",
        caption="Rolling annual Sharpe ratio from walk-forward validation (5yr train / 1yr test, rolled annually).",
    )

    st.markdown(
        '<div class="narrative-block">'
        "Walk-forward validation confirms that the strategy's outperformance is not an artifact "
        "of a single favorable period. The Sharpe ratio varies year to year but remains "
        "positive across the majority of test windows."
        "</div>",
        unsafe_allow_html=True,
    )

st.markdown("---")

# ===================== CAVEATS =====================
st.warning(
    """
    **Important Caveats**

    1. **Transaction costs matter.** All strategy metrics include 5 bps per round-trip trade. Breakeven cost is 50+ bps — robust, but not infinite.

    2. **Execution delay degrades performance.** A 1-day delay reduces Sharpe by ~0.2. Timely execution is essential.

    3. **Past performance is not indicative of future results.** The strategy is optimized on historical data. Regime shifts, changes in market structure, or new policy responses could alter the credit-equity relationship.

    4. **This is a risk management tool, not an alpha generator.** The primary value of credit signals is in reducing drawdowns during stress periods rather than generating excess returns during calm periods.
    """
)

# --- Transition ---
st.markdown("---")
st.markdown(
    '<div class="transition-text">'
    "For readers who want to understand exactly how we reached these conclusions — "
    "or who want to replicate and extend the analysis — the methodology section provides "
    "full details on data, methods, and diagnostics."
    "</div>",
    unsafe_allow_html=True,
)

st.page_link("pages/4_hy_ig_methodology.py", label="Continue to Methodology", icon="📐")

# --- Footer ---
st.markdown("---")
st.markdown(
    '<div class="portal-footer">'
    "Generated with AIG-RLIC+ | Data through 2025-12-31"
    "</div>",
    unsafe_allow_html=True,
)
