"""Finding 1 — The Story: HY-IG Credit Spread as Equity Signal (Layperson Narrative)."""

import os
import sys

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.charts import load_plotly_chart
from components.sidebar import render_sidebar
from components.narrative import render_narrative, render_transition, render_glossary_sidebar

st.set_page_config(
    page_title="The Story | AIG-RLIC+",
    page_icon="📖",
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
st.title("The Story: When Bonds Sound the Alarm")
st.markdown("*How credit spreads warned of stock market trouble — and what investors can learn from it*")
st.markdown("---")

# --- Annotated Spread History (Chart 5) at the top ---
st.markdown("### 25 Years of Credit Stress")
load_plotly_chart(
    "spread_history_annotated",
    fallback_text="Annotated HY-IG spread history (2000-2025) — will appear when visualization is complete.",
    caption="HY-IG credit spread with key events annotated. Higher values indicate greater financial stress.",
)

st.markdown("---")

# --- Why Should Stock Investors Care About Bonds? ---
SECTION_1 = """
### Why Should Stock Investors Care About Bonds?

Most people think of stocks and bonds as separate worlds. Stocks are for growth; bonds are for safety. But behind the scenes, the bond market is constantly making judgments about risk that stock investors often ignore — until it is too late.

When companies borrow money by issuing bonds, investors demand higher interest rates from riskier companies. The difference between what a risky company pays and what a safe company pays is called a **credit spread** (the extra yield investors require to compensate for the possibility that the risky company might not pay them back).

<!-- expander: What exactly is a credit spread? -->
A credit spread is measured in **basis points** (hundredths of a percentage point). If a risky company's bond yields 8% and a safe company's bond yields 4%, the credit spread is 400 basis points (4 percentage points). When investors become worried about the economy, they demand even higher yields from risky companies, causing spreads to **widen**. When confidence returns, spreads **tighten** (narrow).
<!-- /expander -->

### The Early Warning Signal

Our research examines one specific credit spread: the **HY-IG spread**, which is the difference between the yield on **high-yield bonds** (also called "junk bonds" — bonds from companies with lower credit ratings, like BB or CCC) and **investment-grade bonds** (bonds from companies with higher credit ratings, like AA or A).

This spread acts like a thermometer for financial stress. When the economy is healthy and investors are confident, the HY-IG spread is narrow — typically around 250-350 basis points. When fear rises, it widens dramatically.

The key insight from decades of academic research is this: **the bond market tends to detect trouble before the stock market reacts.** There are several reasons for this:

- **Bond investors are focused on downside risk.** Unlike stock investors who can profit from growth, bond investors can only lose their principal. This makes them more sensitive to early signs of deterioration.
- **Credit markets include "informed trading."** Banks that lend to companies have private information about their financial health. Research by Acharya & Johnson (2007) found evidence that this information appears in credit markets before it shows up in stock prices.
- **The bond market is less prone to bubbles.** Philippon (2009) showed that bond prices provide a cleaner signal of fundamental value than stock prices.

<!-- expander: The Merton Model — Why stocks and bonds are connected -->
In 1974, economist Robert Merton showed that a company's stock and debt are mathematically linked. Think of a company's stock as a bet that the company's total value will exceed its debts. When the company's value drops toward its debt level, two things happen simultaneously: the stock price falls, and the bond spread widens. This is why credit spreads and stock prices tend to move in opposite directions — they are both responding to the same underlying reality, just from different angles.
<!-- /expander -->
"""

render_narrative(SECTION_1)

st.markdown("---")

# --- What History Shows ---
st.markdown("### What History Shows")

st.markdown(
    '<div class="narrative-block">'
    "We analyzed 25 years of daily data (2000-2025), covering four major market disruptions:"
    "</div>",
    unsafe_allow_html=True,
)

# Returns by regime chart (Chart 3) embedded inline
load_plotly_chart(
    "returns_by_regime",
    fallback_text="SPY returns by spread regime chart — will appear when visualization is complete.",
    caption=(
        "Equity returns differ dramatically across spread regimes. "
        "When spreads are in their top quartile (stress), average equity returns are negative with extreme volatility."
    ),
)

HISTORY_TEXT = """
**The Dot-Com Bust (2001):** Credit spreads began widening well before the recession officially started in March 2001. High-yield spreads climbed from roughly 500 to over 1,000 basis points as the telecom and technology sectors imploded, highlighted by the WorldCom bankruptcy in 2002.

**The Global Financial Crisis (2007-2009):** This is the most dramatic example. Credit spreads started widening in mid-2007, following the collapse of two Bear Stearns hedge funds. The stock market did not peak until October 2007 — giving attentive investors roughly five months of warning. By the time Lehman Brothers collapsed in September 2008, the HY-IG spread had already reached roughly 800 basis points. It eventually peaked above 2,000 basis points in December 2008.

**The COVID Crash (2020):** Credit spreads surged from about 350 to 1,100 basis points in just five weeks (February to March 2020). This time, the credit and equity signals moved almost simultaneously — the speed of the pandemic shock compressed the usual lead time.

**The 2022 Rate Shock:** As the Federal Reserve raised interest rates at the fastest pace in decades, credit spreads widened from about 300 to 500 basis points. The stock market entered bear market territory, with the S&P 500 falling roughly 25%.

<!-- expander: The CCC-BB Quality Spread — A deeper signal -->
Not all high-yield bonds are equally risky. Within the high-yield universe, the spread between the riskiest bonds (rated CCC and below) and the least risky high-yield bonds (rated BB) provides an even more granular signal. When this "quality spread" widens, it means investors are specifically fleeing the weakest companies — often an early sign of distress that the broader HY-IG spread may not yet fully reflect.
<!-- /expander -->
"""

render_narrative(HISTORY_TEXT)

st.markdown("---")

# --- It Is Not a Simple Relationship ---
st.markdown("### It Is Not a Simple Relationship")

# Rolling correlation chart (Chart 4) inline
load_plotly_chart(
    "rolling_correlation",
    fallback_text="Rolling correlation chart — will appear when visualization is complete.",
    caption=(
        "The correlation between spread changes and equity returns is not constant. "
        "It strengthens during stress episodes and weakens during calm periods."
    ),
)

REGIME_TEXT = """
The connection between credit spreads and stock returns is not a straightforward "wider spreads = lower stocks." The relationship changes depending on the market regime (the overall state of financial conditions):

- **During calm periods** (when spreads are in their normal range), the predictive power of credit spreads for stock returns is modest. Stock prices tend to lead credit spreads, consistent with the idea that equity markets set the pace during good times.
- **During stress periods** (when spreads are in the top quartile of their historical range), the relationship strengthens and may reverse — credit markets appear to lead equity markets. This is consistent with informed trading in credit markets and the bond market's focus on downside risk.

This **regime dependence** is why simple trading rules based on credit spreads often fail. The signal is most powerful precisely when it is most needed — during periods of financial stress — but relatively quiet during the long stretches of calm in between.

<!-- expander: What is a regime? -->
In financial economics, a "regime" refers to a distinct state of the market characterized by its own set of statistical properties (average return, volatility, and correlations). The key insight from research by Hamilton (1989) and Guidolin & Timmermann (2007) is that financial markets do not behave the same way all the time — they switch between regimes. A model that assumes constant behavior will miss the most important signals.
<!-- /expander -->
"""

render_narrative(REGIME_TEXT)

# --- Transition ---
st.markdown("---")
render_transition(
    "History suggests a real connection, but anecdotes are not evidence. "
    "We subjected 25 years of daily data to a battery of statistical tests to separate "
    "genuine predictive power from coincidence."
)

st.page_link("pages/2_hy_ig_evidence.py", label="Continue to The Evidence", icon="🔬")

# --- Footer ---
st.markdown("---")
st.markdown(
    '<div class="portal-footer">'
    "Generated with AIG-RLIC+ | Data through 2025-12-31"
    "</div>",
    unsafe_allow_html=True,
)
