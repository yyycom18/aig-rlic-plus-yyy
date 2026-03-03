# Portal Narrative: HY-IG Credit Spread vs S&P 500 Returns

**From:** Ray (Research Agent)
**To:** Ace (App Dev)
**Date:** 2026-02-28

---

## Page 1 — The Hook (Executive Summary)

### One-Sentence Thesis

The bond market often sees trouble coming before the stock market does — and the gap between risky and safe bond yields has been one of the most reliable early warning signals for stock market declines over the past 25 years.

### Headline Findings for KPI Cards

1. **Credit led equity by ~5 months before the 2008 crash** — HY-IG spreads (the gap between high-yield and investment-grade bond yields) began widening in June 2007, while stocks did not peak until October 2007.
2. **Spreads widened from 300 to 2,000+ basis points during the GFC** — a basis point (bp) is 1/100th of a percentage point — representing a 6x increase in the market's assessment of default risk.
3. **Credit signals predicted 3 of the last 4 major equity drawdowns** — the dot-com bust (2001), the Global Financial Crisis (2008), and the COVID crash (2020) were all preceded or accompanied by dramatic spread widening.
4. **The relationship is strongest during stress** — when spreads are in their top quartile (top 25% of historical values), the correlation between spread changes and subsequent stock returns is significantly stronger than during calm periods.
5. **Out-of-sample testing covers 8 years (2018-2025)** — including the 2018 volatility spike, COVID crash, 2022 rate shock, and 2023-25 recovery — providing a rigorous real-world test of the signal.

### Suggested Hero Chart

A dual-axis time series chart (2000-2025) with the HY-IG spread on the left y-axis (inverted, so widening = down) and SPY price on the right y-axis. Vertical shaded bands mark NBER recessions. Key events annotated with date labels. The visual immediately shows that the orange spread line "dips" (widens) before or simultaneously with the blue equity line declining.

---

## Page 2 — The Story (Layperson Narrative)

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

### What History Shows

We analyzed 25 years of daily data (2000-2025), covering four major market disruptions:

**The Dot-Com Bust (2001):** Credit spreads began widening well before the recession officially started in March 2001. High-yield spreads climbed from roughly 500 to over 1,000 basis points as the telecom and technology sectors imploded, highlighted by the WorldCom bankruptcy in 2002.

**The Global Financial Crisis (2007-2009):** This is the most dramatic example. Credit spreads started widening in mid-2007, following the collapse of two Bear Stearns hedge funds. The stock market did not peak until October 2007 — giving attentive investors roughly five months of warning. By the time Lehman Brothers collapsed in September 2008, the HY-IG spread had already reached roughly 800 basis points. It eventually peaked above 2,000 basis points in December 2008.

**The COVID Crash (2020):** Credit spreads surged from about 350 to 1,100 basis points in just five weeks (February to March 2020). This time, the credit and equity signals moved almost simultaneously — the speed of the pandemic shock compressed the usual lead time.

**The 2022 Rate Shock:** As the Federal Reserve raised interest rates at the fastest pace in decades, credit spreads widened from about 300 to 500 basis points. The stock market entered bear market territory, with the S&P 500 falling roughly 25%.

<!-- expander: The CCC-BB Quality Spread — A deeper signal -->
Not all high-yield bonds are equally risky. Within the high-yield universe, the spread between the riskiest bonds (rated CCC and below) and the least risky high-yield bonds (rated BB) provides an even more granular signal. When this "quality spread" widens, it means investors are specifically fleeing the weakest companies — often an early sign of distress that the broader HY-IG spread may not yet fully reflect.
<!-- /expander -->

### It Is Not a Simple Relationship

The connection between credit spreads and stock returns is not a straightforward "wider spreads = lower stocks." The relationship changes depending on the market regime (the overall state of financial conditions):

- **During calm periods** (when spreads are in their normal range), the predictive power of credit spreads for stock returns is modest. Stock prices tend to lead credit spreads, consistent with the idea that equity markets set the pace during good times.
- **During stress periods** (when spreads are in the top quartile of their historical range), the relationship strengthens and may reverse — credit markets appear to lead equity markets. This is consistent with informed trading in credit markets and the bond market's focus on downside risk.

This **regime dependence** is why simple trading rules based on credit spreads often fail. The signal is most powerful precisely when it is most needed — during periods of financial stress — but relatively quiet during the long stretches of calm in between.

<!-- expander: What is a regime? -->
In financial economics, a "regime" refers to a distinct state of the market characterized by its own set of statistical properties (average return, volatility, and correlations). The key insight from research by Hamilton (1989) and Guidolin & Timmermann (2007) is that financial markets do not behave the same way all the time — they switch between regimes. A model that assumes constant behavior will miss the most important signals.
<!-- /expander -->

---

## Page 3 — The Evidence (Analytical Detail)

### How We Tested the Signal

Our analysis employed a battery of econometric methods, each designed to test a different aspect of the credit-equity relationship:

**Causality Testing (Toda-Yamamoto Granger and Transfer Entropy):**
We tested whether credit spread changes statistically "cause" (in the Granger sense — meaning they help predict) future stock returns, and vice versa. We ran these tests at multiple lag orders (1 day, 5 days, 21 days, 63 days) and separately for stress and calm regimes.

**Local Projections (Jordà method):**
We estimated the cumulative impact of a credit spread shock on stock returns at horizons from 1 day to 63 days. This method is robust and allows us to see how the effect builds or fades over time.

**Regime-Switching Models (Markov-Switching and Hidden Markov Models):**
We identified distinct market states — calm, moderate stress, and extreme stress — using statistical models that let the data determine the regime boundaries rather than imposing them in advance.

**Quantile Regression:**
Rather than just estimating the average effect, we examined how credit spreads affect the entire distribution of stock returns — particularly the worst outcomes (the left tail).

### Key Model Results

*(Reference Evan's model output files in `results/core_models_20260228/` for full details. Reference Vera's charts in `output/charts/plotly/` for interactive visualizations.)*

**Finding 1 — Bidirectional causality with regime asymmetry:**
Granger causality tests reveal statistically significant information flow in both directions (credit-to-equity and equity-to-credit). However, the credit-to-equity signal strengthens materially during stress regimes, while the equity-to-credit signal dominates during calm periods. Transfer entropy (a nonlinear test) shows even stronger asymmetry.

**Finding 2 — Credit spread shocks have persistent effects on stock returns:**
Local projection impulse responses show that a 1-standard-deviation widening in the HY-IG z-score is associated with negative cumulative stock returns that build over 1-5 weeks. The effect is roughly 2-3x larger during stress regimes compared to calm regimes.

**Finding 3 — The signal activates at stress thresholds:**
Regime-switching models identify a "stress" state where the credit-equity relationship is fundamentally different. The transition probability into the stress state increases sharply when the HY-IG z-score exceeds approximately 1.5-2.0 standard deviations above its rolling mean.

**Finding 4 — Downside equity risk is the primary channel:**
Quantile regression results show that credit spreads have their strongest explanatory power for the worst outcomes (5th and 10th percentiles of stock returns), consistent with the "Vulnerable Growth" framework of Adrian et al. (2019). The median and upper quantiles are largely unaffected.

### The Combinatorial Tournament

We tested approximately 1,000 different combinations of signals, thresholds, strategies, and timing parameters. These were ranked by out-of-sample Sharpe ratio (2018-2025), with the top 5 subjected to rigorous walk-forward validation, bootstrap significance testing, and transaction cost analysis.

*(See `results/tournament_results_20260228.csv` for the full leaderboard.)*

---

## Page 4 — The Strategy (Trading Applications)

### How the Signal Translates to Action

The tournament identified the most robust credit-signal strategies for equity allocation. Here are the strategy rules in plain language:

**Strategy: Risk-Off When Credit Stress Exceeds Threshold**

The core idea is simple:
- **When the HY-IG spread z-score is below the stress threshold** (indicating normal market conditions): Stay fully invested in stocks (long SPY).
- **When the HY-IG spread z-score is above the stress threshold** (indicating elevated credit stress): Reduce equity exposure or move to cash.

The threshold and the specific timing rules (how many days to wait before acting, how quickly to re-enter) are determined by the tournament.

<!-- expander: What is a z-score? -->
A z-score measures how unusual a current value is compared to its recent history. A z-score of 0 means the spread is at its historical average. A z-score of +2 means the spread is 2 standard deviations above average — a relatively rare condition that historically has occurred less than 5% of the time. We use rolling windows (1-2 years) to compute the z-score, so the "average" adapts over time.
<!-- /expander -->

### Key Strategy Metrics

*(Numbers below are illustrative — replace with actual tournament results from Evan's output.)*

| Metric | Credit-Signal Strategy | Buy-and-Hold SPY |
|--------|----------------------|-------------------|
| Annualized Return (OOS) | TBD% | TBD% |
| Annualized Volatility | TBD% | TBD% |
| Sharpe Ratio | TBD | TBD |
| Maximum Drawdown | TBD% | TBD% |
| Win Rate (monthly) | TBD% | TBD% |
| Average Turnover (annual) | TBD trades/yr | 0 |

### Important Caveats

1. **Transaction costs matter.** All strategy metrics include 5 basis points per round-trip trade. The breakeven transaction cost (the level at which the strategy's edge disappears) is reported for each top-5 combination.
2. **Execution delay degrades performance.** We tested 1, 2, 3, and 5-day delays between signal generation and trade execution. Performance decreases with longer delays, reflecting the speed at which credit information is priced into equities.
3. **Past performance is not indicative of future results.** The strategy is optimized on historical data. Regime shifts, changes in market structure, or new policy responses could alter the credit-equity relationship.
4. **This is a risk management tool, not an alpha generator.** The primary value of credit signals may be in reducing drawdowns during stress periods rather than generating excess returns during calm periods.

---

## Page 5 — The Method (Technical Appendix)

### Data Sources

All data is sourced from publicly available databases:
- **Credit spreads:** ICE BofA Option-Adjusted Spread indices via the Federal Reserve Economic Database (FRED). Series: BAMLH0A0HYM2 (HY OAS), BAMLC0A0CM (IG OAS), BAMLH0A1HYBB (BB OAS), BAMLH0A3HYC (CCC OAS).
- **Equity prices:** SPY ETF via Yahoo Finance.
- **Volatility:** CBOE VIX and VIX3M indices via Yahoo Finance.
- **Macro variables:** Treasury yields, NFCI, initial claims, Fed funds rate via FRED.

### Sample Period

- **Full sample:** January 2000 to December 2025 (daily, ~6,500 business days)
- **In-sample (model estimation):** January 2000 to December 2017
- **Out-of-sample (strategy evaluation):** January 2018 to December 2025

### Econometric Methods

| Method | Purpose | Key Parameter |
|--------|---------|---------------|
| Toda-Yamamoto Granger causality | Test linear predictive relationship (both directions) | Augmented VAR with lags selected by BIC + d_max = 1 |
| Transfer entropy (Diks-Panchenko) | Test nonlinear information flow | Bandwidth selection per Diks & Panchenko (2006) |
| Local projections (Jordà) | Impulse responses at multiple horizons | h = 1, 5, 10, 21, 42, 63 days |
| Markov-switching regression | Regime identification | 2-state and 3-state |
| Gaussian HMM | Joint regime identification on HY-IG + VIX | 2-state and 3-state |
| Quantile regression | Distributional effects | tau = 0.05, 0.10, 0.25, 0.50, 0.75, 0.90 |
| GJR-GARCH | Volatility dynamics with asymmetry | SPY returns with HY-IG exogenous |
| Random Forest + SHAP | Nonlinear feature importance | Walk-forward, 1-year test windows |
| Combinatorial tournament | Strategy optimization | ~1,000 combinations, OOS Sharpe ranking |

### Diagnostics

Every model undergoes: Jarque-Bera (normality), Breusch-Pagan (heteroskedasticity), Breusch-Godfrey (serial correlation), RESET (functional form), and stationarity confirmation (ADF, PP, KPSS).

### Sensitivity Analysis

- Full sample vs. excluding GFC (2007-2009)
- Full sample vs. excluding COVID (2020)
- Pre-2008 vs. post-2008 sub-samples
- Alternative lag structures
- Alternative threshold levels

### References

See the full research brief (`docs/research_brief_hy_ig_spy_20260228.md`) for the complete reference list with 25 academic citations.

---

## Glossary

| Term | Definition |
|------|-----------|
| **Basis point (bp)** | One hundredth of a percentage point (0.01%). 100 basis points = 1%. Used to measure small changes in yields and spreads. |
| **Buy-and-hold** | An investment strategy where you purchase an asset and hold it regardless of market conditions. The simplest benchmark for comparing active strategies. |
| **Credit rating** | A grade assigned to a company's debt by rating agencies (S&P, Moody's, Fitch). Investment grade (AAA to BBB-) means lower default risk; high yield (BB+ and below) means higher default risk. |
| **Credit spread** | The difference in yield between a risky bond and a risk-free benchmark. Wider spreads indicate more perceived risk. |
| **Drawdown** | The peak-to-trough decline in the value of a portfolio or index. Maximum drawdown is the largest such decline in a given period. |
| **Excess bond premium (EBP)** | The component of credit spreads that cannot be explained by expected default risk. Captures investor sentiment and risk appetite. Proposed by Gilchrist & Zakrajsek (2012). |
| **Forward return** | The return over a future period. A "21-day forward return" is the percentage change in price over the next 21 trading days (~1 month). |
| **Granger causality** | A statistical test that determines whether one time series helps predict another. "X Granger-causes Y" means past values of X improve forecasts of Y. It does not prove true causation. |
| **Hidden Markov Model (HMM)** | A statistical model that assumes the system is in one of several unobservable ("hidden") states, each with different statistical properties. The model estimates which state the market is in at any given time. |
| **High-yield bonds (junk bonds)** | Bonds from companies with credit ratings below investment grade (BB+ or lower). They offer higher yields to compensate for higher default risk. |
| **HY-IG spread** | The difference between the option-adjusted spread on high-yield bonds and the option-adjusted spread on investment-grade bonds. Our primary signal variable. |
| **Impulse response** | A measure of how one variable responds over time to a one-time shock in another variable. Shows whether effects are immediate, delayed, or persistent. |
| **In-sample / Out-of-sample** | In-sample data is used to build and fit models. Out-of-sample data is held back and used to test whether the model works on data it has never seen. |
| **Investment-grade bonds** | Bonds from companies with credit ratings of BBB- or above. Considered safer, with lower yields. |
| **Local projection** | A method for estimating impulse responses that does not require specifying a full multivariate model. More robust than traditional VAR methods. Developed by Jordà (2005). |
| **Markov-switching model** | A model where the underlying regime (e.g., bull vs. bear market) can change randomly according to a Markov process. Each regime has its own set of parameters. Developed by Hamilton (1989). |
| **NFCI** | National Financial Conditions Index, published weekly by the Chicago Federal Reserve. Measures overall conditions in U.S. financial markets. Positive values indicate tighter-than-average conditions. |
| **Option-adjusted spread (OAS)** | A credit spread that accounts for any embedded options (like call provisions) in the bond. Provides a cleaner measure of pure credit risk than raw yield spreads. |
| **Quantile regression** | A statistical method that estimates the effect of a variable on different parts of the outcome distribution (not just the average). Useful for understanding tail risks. |
| **Regime** | A distinct state of the market characterized by its own statistical properties (mean returns, volatility, correlations). Markets switch between regimes over time. |
| **Sharpe ratio** | A measure of risk-adjusted return: (return - risk-free rate) / volatility. Higher is better. A Sharpe of 1.0 is generally considered good. |
| **Transfer entropy** | An information-theoretic measure of directed information flow between time series. Unlike Granger causality, it captures nonlinear relationships. |
| **VIX** | The CBOE Volatility Index, often called the "fear gauge." Measures the market's expectation of 30-day volatility in the S&P 500, derived from option prices. |
| **VIX term structure** | The difference between longer-dated (VIX3M, 3-month) and shorter-dated (VIX, 1-month) implied volatility. When VIX3M > VIX (contango), markets are calm. When VIX > VIX3M (backwardation), markets are stressed. |
| **Walk-forward validation** | A backtesting method that simulates real-time trading by training the model on past data and testing on subsequent data, then rolling the window forward. Prevents lookahead bias. |
| **Yield curve slope** | The difference between long-term and short-term interest rates (e.g., 10-year minus 3-month Treasury yields). An inverted yield curve (negative slope) has historically preceded recessions. |
| **Z-score** | A statistical measure of how many standard deviations a value is from its mean. A z-score of 2 means the value is 2 standard deviations above average — an unusual reading. |
