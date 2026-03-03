"""Finding 1 — Methodology: Technical Appendix."""

import os
import sys

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.charts import load_plotly_chart
from components.sidebar import render_sidebar
from components.narrative import render_glossary_sidebar

st.set_page_config(
    page_title="Methodology | AIG-RLIC+",
    page_icon="📐",
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
st.title("Methodology: Technical Appendix")
st.markdown(
    "*For the skeptical reader — and healthy skepticism is essential in finance — "
    "here is exactly how we arrived at these conclusions.*"
)
st.markdown("---")

# ===================== STATIONARITY TESTS =====================
st.markdown("### Stationarity and Unit Root Tests")

st.markdown(
    '<div class="narrative-block">'
    "Every time-series variable was tested for stationarity using ADF, Phillips-Perron, "
    "and KPSS tests before entering any model. Variables were differenced or transformed "
    "as necessary to ensure valid inference."
    "</div>",
    unsafe_allow_html=True,
)

load_plotly_chart(
    "stationarity_table",
    fallback_text="Stationarity test results table — will appear when visualization is complete.",
    caption="Unit root test results for all key variables. ADF, PP, and KPSS with recommended transformations.",
)

st.markdown("---")

# ===================== GRANGER CAUSALITY DETAIL =====================
st.markdown("### Granger Causality: Full Results")

load_plotly_chart(
    "granger_table",
    fallback_text="Granger causality results table — will appear when visualization is complete.",
    caption=(
        "Toda-Yamamoto Granger causality tests at lag orders 1, 5, 21, 63. "
        "Tested in both directions (credit-to-equity and equity-to-credit) and by regime."
    ),
)

st.markdown("---")

# ===================== DATA SOURCES =====================
st.markdown("### Data Sources")

st.markdown(
    """
    All data is sourced from publicly available databases:

    | Category | Source | Series |
    |:---------|:-------|:-------|
    | **Credit spreads** | FRED (ICE BofA indices) | BAMLH0A0HYM2 (HY OAS), BAMLC0A0CM (IG OAS), BAMLH0A1HYBB (BB OAS), BAMLH0A3HYC (CCC OAS) |
    | **Equity prices** | Yahoo Finance | SPY ETF |
    | **Volatility** | Yahoo Finance | ^VIX, ^VIX3M |
    | **Treasury yields** | FRED | DGS10, DGS2, DTB3 |
    | **Macro indicators** | FRED | NFCI, ICSA, DFF, STLFSI2, SOFR |
    | **Sector ETFs** | Yahoo Finance | KBE, IWM, HYG |
    | **Commodities** | Yahoo Finance | GC=F (Gold), HG=F (Copper) |
    | **Dollar index** | Yahoo Finance | DX-Y.NYB |
    """
)

st.markdown("---")

# ===================== SAMPLE PERIOD =====================
st.markdown("### Sample Period")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Full Sample", "2000-01 to 2025-12", delta="~6,500 business days")
with col2:
    st.metric("In-Sample", "2000-01 to 2017-12", delta="Model estimation (18 years)")
with col3:
    st.metric("Out-of-Sample", "2018-01 to 2025-12", delta="Strategy evaluation (8 years)")

st.markdown(
    '<div class="narrative-block">'
    "The out-of-sample period includes the 2018 volatility spike, COVID crash, "
    "2022 rate shock, and 2023-25 recovery — a rich stress-test window."
    "</div>",
    unsafe_allow_html=True,
)

st.markdown("---")

# ===================== ECONOMETRIC METHODS TABLE =====================
st.markdown("### Econometric Methods")

st.markdown(
    """
    | Method | Purpose | Key Parameter |
    |:-------|:--------|:-------------|
    | Toda-Yamamoto Granger causality | Test linear predictive relationship (both directions) | Augmented VAR with BIC lag selection + d_max = 1 |
    | Transfer entropy (Diks-Panchenko) | Test nonlinear information flow | Bandwidth per Diks & Panchenko (2006) |
    | Johansen cointegration + VECM | Long-run equilibrium relationship | Trace and max-eigenvalue tests |
    | Local projections (Jorda) | Impulse responses at multiple horizons | h = 1, 5, 10, 21, 42, 63 days |
    | Markov-switching regression | Regime identification | 2-state and 3-state |
    | Gaussian HMM | Joint regime identification on HY-IG + VIX | 2-state and 3-state |
    | GJR-GARCH | Volatility dynamics with leverage effect | SPY returns with HY-IG exogenous |
    | Quantile regression | Distributional effects on return tails | tau = 0.05, 0.10, 0.25, 0.50, 0.75, 0.90 |
    | Random Forest + SHAP | Nonlinear feature importance | Walk-forward, 1-year test windows |
    | PELT change-point detection | Structural break identification | Sensitivity sweep |
    | Combinatorial tournament | Strategy optimization across 2,304 combinations | OOS Sharpe ranking |
    """
)

st.markdown("---")

# ===================== DIAGNOSTICS =====================
st.markdown("### Diagnostic Tests")

st.markdown(
    """
    Every model undergoes the following diagnostic battery:

    | Test | Purpose | Null Hypothesis |
    |:-----|:--------|:----------------|
    | Jarque-Bera | Residual normality | Residuals are normally distributed |
    | Breusch-Pagan | Heteroskedasticity | Constant variance |
    | Breusch-Godfrey | Serial correlation | No autocorrelation in residuals |
    | RESET | Functional form | Model is correctly specified |
    | ADF / PP / KPSS | Stationarity | Unit root present (ADF/PP) or stationary (KPSS) |

    **Note:** HAC (Newey-West) standard errors are used throughout to account for
    heteroskedasticity and autocorrelation. This is essential given the overlapping
    forward returns and regime-dependent volatility.
    """
)

st.markdown("---")

# ===================== SENSITIVITY ANALYSIS =====================
st.markdown("### Sensitivity Analysis")

st.markdown(
    """
    Results were tested for robustness across multiple dimensions:

    - **Sub-sample stability:** Full sample vs. excluding GFC (2007-2009) vs. excluding COVID (2020)
    - **Pre/post structural break:** Pre-2008 vs. post-2008 sub-samples
    - **Alternative lag structures:** Multiple lag orders tested for all causality and regression models
    - **Alternative thresholds:** Fixed percentiles, rolling percentiles, Bollinger bands, Jenks breaks, GMM, HMM, CUSUM
    - **Transaction cost sensitivity:** 0 to 50 bps round-trip
    - **Execution delay:** 0 to 5 business days
    """
)

st.markdown("---")

# ===================== REFERENCES =====================
st.markdown("### Key References")

st.markdown(
    """
    <div class="reference-list">

    - Acharya, V. V., & Johnson, T. C. (2007). Insider trading in credit derivatives. *Journal of Financial Economics*, 84(1), 110-141.
    - Adrian, T., Boyarchenko, N., & Giannone, D. (2019). Vulnerable Growth. *American Economic Review*, 109(4), 1263-1289.
    - Berndt, A., Douglas, R., Duffie, D., & Ferguson, M. (2018). Corporate credit risk premia. *Review of Finance*, 22(2), 419-454.
    - Diks, C., & Panchenko, V. (2006). A new statistic and practical guidelines for nonparametric Granger causality testing. *Journal of Economic Dynamics and Control*, 30(9-10), 1647-1669.
    - Faust, J., Gilchrist, S., Wright, J. H., & Zakrajsek, E. (2013). Credit spreads as predictors of real-time economic activity. *Review of Economics and Statistics*, 95(5), 1441-1455.
    - Gilchrist, S., & Zakrajsek, E. (2012). Credit spreads and business cycle fluctuations. *American Economic Review*, 102(4), 1692-1720.
    - Guidolin, M., & Timmermann, A. (2007). Asset allocation under multivariate regime switching. *Journal of Economic Dynamics and Control*, 31(11), 3503-3544.
    - Hamilton, J. D. (1989). A new approach to the economic analysis of nonstationary time series and the business cycle. *Econometrica*, 57(2), 357-384.
    - Jorda, O. (2005). Estimation and inference of impulse responses by local projections. *American Economic Review*, 95(1), 161-182.
    - Merton, R. C. (1974). On the pricing of corporate debt: The risk structure of interest rates. *Journal of Finance*, 29(2), 449-470.
    - Mueller, P. (2009). Credit spreads and real activity. Working paper, Columbia Business School.
    - Philippon, T. (2009). The bond market's q. *Quarterly Journal of Economics*, 124(3), 1011-1056.

    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="narrative-block">'
    "See the full research brief "
    "(<code>docs/research_brief_hy_ig_spy_20260228.md</code>) for the complete "
    "reference list with 25 academic citations."
    "</div>",
    unsafe_allow_html=True,
)

st.markdown("---")

# ===================== DATA DICTIONARY LINK =====================
st.markdown("### Data Dictionary")

st.markdown(
    '<div class="narrative-block">'
    "The complete data dictionary with variable definitions, sources, transformations, "
    "and known quirks is available at "
    "<code>data/data_dictionary_hy_ig_spy_20260228.csv</code>."
    "</div>",
    unsafe_allow_html=True,
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
