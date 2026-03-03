# Research Brief: HY-IG Credit Spread vs S&P 500 Returns

**From:** Ray (Research Agent)
**To:** Evan (Econometrics), Dana (Data), Vera (Visualization), Ace (App Dev), Alex (Lead)
**Date:** 2026-02-28
**Status:** Stage 2 — Full Research Brief

---

## Executive Summary

- **Credit spreads — particularly the excess bond premium (EBP) component — are among the strongest financial predictors of future economic activity and equity returns.** The HY-IG spread captures the market's pricing of default risk migration and risk appetite, both of which lead equity market turning points (Gilchrist & Zakrajsek 2012; Faust et al. 2013).
- **The causal direction is contested and likely bidirectional.** Equity markets reflect firm-level fundamentals that mechanically move credit spreads via the Merton (1974) structural channel, while credit markets embed informed trading and risk appetite shifts that lead equities (Acharya & Johnson 2007; Norden & Weber 2009). Testing both directions is essential.
- **The relationship is regime-dependent and nonlinear.** Correlations between equity and credit change sign across bull, bear, and crisis regimes (Guidolin & Timmermann 2007; Ang & Bekaert 2002). Linear models understate predictive power during stress episodes, which is precisely when the signal is most valuable.
- **Spread changes and normalized transforms outperform raw spread levels as predictors.** Collin-Dufresne et al. (2001) show that spread changes are driven by a latent common factor, while Campbell & Taksler (2003) demonstrate that volatility-normalized measures have superior cross-sectional explanatory power.
- **A viable trading strategy must survive transaction costs, execution delay, and out-of-sample testing.** The literature documents in-sample predictability but out-of-sample profitability remains an open question requiring the combinatorial tournament approach specified in the analysis brief.

---

## Question

Does the high-yield minus investment-grade (HY-IG) credit spread predict S&P 500 equity returns? If so, through what mechanism, at what horizons, and can the signal be profitably traded?

---

## Key Findings from Literature

### A. Credit Spreads as Predictors of Economic Activity and Equity Returns

1. **Gilchrist & Zakrajsek (2012):** Constructed a credit spread index from micro-level corporate bond data and decomposed it into a component capturing expected default risk and a residual — the excess bond premium (EBP). The EBP has "considerable predictive power for future economic activity," and the predictive ability of credit spreads for recessions is due **entirely** to the EBP, not the default-risk component. Published in *American Economic Review* 102(4): 1692-1720. **Method:** Panel regression, VAR, probit. **Data:** Monthly, 1973-2010. **Relevance:** Core theoretical motivation — the EBP captures risk appetite/credit supply shocks that propagate to equities. **Limitation:** EBP requires micro-level bond data to construct; our HY-IG spread is a noisy proxy.

2. **Faust, Gilchrist, Wright & Zakrajsek (2013):** Used Bayesian model averaging (BMA) across a large set of credit spread predictors to forecast real-time GDP, investment, IP, and employment. Credit spreads consistently received the highest posterior probability among all financial predictors. Published in *Review of Economics and Statistics* 95(5): 1501-1519. **Method:** BMA. **Data:** Monthly/quarterly, 1985-2010. **Relevance:** Validates credit spreads as the premier financial predictor of real activity; gains stem almost exclusively from option-adjusted credit spreads. **Method sensitivity:** Results hold across multiple prior specifications.

3. **Philippon (2009):** Developed "Bond Market's q" — a Tobin's q analog using bond prices instead of equity prices. Bond q fits the corporate investment equation 6x better than equity q, consistent with the bond market being less susceptible to bubbles. Published in *Quarterly Journal of Economics* 124(3): 1011-1056. **Relevance:** Theoretical foundation for why credit markets may contain cleaner information than equity markets about fundamental value.

4. **Mueller (2009):** Demonstrated that a credit-spread factor is highly correlated with loan tightening standards and provides accurate out-of-sample GDP growth predictions. Published as working paper, later in *Review of Financial Studies*. **Relevance:** Links credit spreads to the bank lending channel.

5. **Gomes & Schmid (2010):** General equilibrium model showing that movements in credit risk premia are an important determinant of aggregate fluctuations, with credit and term spreads forecasting recessions by predicting corporate investment. Working paper, Wharton. **Relevance:** Provides structural economic model justifying credit-equity linkage.

### B. Lead-Lag Dynamics Between Credit and Equity Markets

6. **Merton (1974):** The foundational structural model of credit risk. Firm equity is a call option on assets; when asset value falls toward the debt barrier, both equity declines and spreads widen simultaneously. This establishes the **endogeneity concern**: equity movements mechanically drive credit spreads. Published in *Journal of Finance* 29(2): 449-470. **Relevance:** Defines the reverse-causality channel that our identification strategy must address.

7. **Collin-Dufresne, Goldstein & Martin (2001):** Found that standard determinants (leverage, rates, equity returns, volatility) explain only a modest fraction of credit spread changes. A single latent common factor drives most of the residual variation, interpreted as local supply/demand shocks. Published in *Journal of Finance* 56(6): 2177-2207. **Method:** Panel regression. **Data:** Monthly, 1988-1997. **Relevance:** Spread changes contain information beyond what equity markets provide. **Limitation:** Pre-crisis sample period.

8. **Norden & Weber (2009):** Examined lead-lag relationships among CDS, bond, and equity markets using VAR and cointegration. Found that **stock returns lead CDS and bond spread changes**, but the CDS market is more sensitive to equity signals for low-quality issuers. The CDS market contributes more to price discovery than the bond market. Published in *European Financial Management* 15(3): 529-562. **Method:** VAR, Granger causality, VECM. **Data:** Daily, 2000-2002. **Relevance:** Suggests equity may lead credit in normal times, but this reverses in stress. **Limitation:** Short sample covering only the dot-com bust.

9. **Blanco, Brennan & Marsh (2005):** Studied CDS-bond arbitrage for 33 investment-grade firms. The theoretical equilibrium relationship holds for most firms, and the CDS market leads price discovery (~79% of new information originates in the CDS market). Published in *Journal of Finance* 60(5): 2255-2281. **Method:** VECM, Gonzalo-Granger decomposition. **Data:** Daily, 2001-2002. **Relevance:** Establishes that credit derivatives lead cash bond markets; suggests credit markets are faster at processing information.

10. **Acharya & Johnson (2007):** Found evidence of informed trading in CDS markets — recent CDS spread changes negatively predict stock returns over the next few days, consistent with banks exploiting private information through credit derivatives. Published in *Journal of Financial Economics* 84(1): 110-141. **Method:** Vector autoregression, event study. **Data:** Daily, 2001-2004. **Relevance:** Provides direct evidence for Credit → Equity information flow. **Limitation:** Effect is strongest for firms with many bank relationships.

### C. Regime-Dependent Relationships

11. **Hamilton (1989):** Introduced the Markov-switching model for time series, where parameters of an autoregression are governed by a discrete-state Markov process. Identified distinct recession and expansion regimes in US GDP. Published in *Econometrica* 57(2): 357-384. **Relevance:** Foundation for our regime-switching specification. Requires long samples for stable estimation.

12. **Ang & Bekaert (2002):** Found that international equity returns are characterized by two regimes — a normal regime and a **bear market regime** where returns are lower and much more volatile. Correlations between markets increase in bear regimes. Published in *Review of Financial Studies* 15(4): 1137-1187. **Relevance:** Motivates regime-conditional analysis of credit-equity relationships.

13. **Guidolin & Timmermann (2007):** Demonstrated that **four regimes** (crash, slow growth, bull, recovery) are required to capture the joint distribution of stock and bond returns. The equity-bond correlation ranges from **+0.37 in recovery to −0.40 in crash** states. Published in *Journal of Economic Dynamics and Control* 31(11): 3503-3544. **Relevance:** Justifies multi-state regime models and shows that constant-correlation models are deeply misleading.

14. **Adrian, Boyarchenko & Giannone (2019):** "Vulnerable Growth" — showed that deteriorating financial conditions shift the entire GDP growth distribution leftward and increase its volatility, with downside risks varying with financial conditions while upside risks remain stable. Published in *American Economic Review* 109(4): 1263-1289. **Relevance:** Financial conditions (which include credit spreads) predict tail risk in the real economy, supporting the hypothesis that credit signals are most informative in the left tail.

### D. Yield Curve as Complementary Predictor

15. **Estrella & Mishkin (1998):** Demonstrated that the yield curve slope (10Y-3M) is a valuable recession predictor, outperforming other financial indicators at 2-6 quarter horizons. Published in *Review of Economics and Statistics* 80(1): 45-61. **Method:** Probit. **Relevance:** The yield curve is a control variable in our specification; its interaction with credit spreads may improve predictive power.

16. **Ang, Piazzesi & Wei (2006):** Showed that the term structure contains information about future GDP growth through a no-arbitrage macro-finance model. Published in *Journal of Econometrics* 131(1-2): 359-403. **Relevance:** Validates yield curve slope as a predictor alongside credit spreads.

### E. Nonlinear Causality and Information Flow

17. **Schreiber (2000):** Introduced transfer entropy as an information-theoretic measure of directional information flow between time series, able to distinguish driving and responding elements in coupled systems. Published in *Physical Review Letters* 85(2): 461. **Relevance:** Methodological foundation for our nonlinear causality tests.

18. **Diks & Panchenko (2006):** Developed a consistent nonparametric test for Granger noncausality based on the first-order Taylor expansion of transfer entropy. Published in *Journal of Economic Dynamics and Control* 30(9-10): 1647-1669. **Relevance:** Provides the specific test statistic for our nonlinear Granger causality analysis.

19. **Toda & Yamamoto (1995):** Proposed an augmented VAR approach to test Granger causality that is valid regardless of whether series are integrated or cointegrated. Augment VAR(k) by d_max additional lags, then test restrictions on the first k lags only. Published in *Journal of Econometrics* 66(1-2): 225-250. **Relevance:** Our primary linear causality test, chosen because spread levels exhibit near-unit-root behavior.

### F. Econometric Methods

20. **Jordà (2005):** Introduced local projections as an alternative to VAR-based impulse response estimation. Estimates direct regressions of y_{t+h} on current shocks, avoiding specification of the full multivariate system. More robust to misspecification. Published in *American Economic Review* 95(1): 161-182. **Relevance:** Our method for estimating credit-to-equity impulse responses at multiple horizons.

21. **Johansen (1991):** Developed maximum likelihood methods for estimating and testing cointegration vectors in Gaussian VAR models. Published in *Econometrica* 59(6): 1551-1580. **Relevance:** If HY-IG spread and SPY log price are cointegrated, we use VECM; if not, proceed with VAR in differences.

### G. Credit Risk Decomposition and Spreads

22. **Longstaff, Mithal & Neis (2005):** Used CDS data to decompose corporate yield spreads into default and non-default (liquidity) components. The default component accounts for 51-83% of the spread depending on rating, with the remainder driven by liquidity. Published in *Journal of Finance* 60(5): 2213-2253. **Relevance:** Our HY-IG spread conflates default risk and liquidity; this decomposition matters for interpretation.

23. **Campbell & Taksler (2003):** Showed that idiosyncratic firm-level equity volatility explains as much cross-sectional variation in bond yield spreads as credit ratings. Published in *Journal of Finance* 58(6): 2321-2350. **Relevance:** Establishes the equity-volatility-to-credit-spread transmission channel (Merton channel in practice).

24. **Berndt, Douglas, Duffie & Ferguson (2018):** Measured credit risk premia using CDS and EDF data. Found dramatic time variation in premia, with peaks in 2002, 2008-09, and 2011. Credit risk premia per unit of expected loss fluctuate by more than a factor of 10 and comove with macroeconomic distress indicators. Published in *Review of Finance* 22(2): 419-454. **Relevance:** Demonstrates that the price of credit risk (not just expected losses) varies with the cycle — supporting the use of spread levels as risk appetite indicators.

25. **Huang, Zhou & Zhu (2009):** Developed a framework for assessing systemic risk of major financial institutions using CDS spreads and equity data. Published in *Journal of Banking & Finance* 33(11): 2036-2049. **Relevance:** Links individual CDS spread dynamics to systemic risk, relevant for our financial stress control variables (NFCI, FSI).

---

## Consensus View

**What the weight of evidence suggests (3+ studies agree):**

1. **Credit spreads contain predictive information for future economic activity and, by extension, equity returns.** This is the strongest consensus in the literature (Gilchrist & Zakrajsek 2012; Faust et al. 2013; Mueller 2009; Philippon 2009; Gomes & Schmid 2010). The predictive component is primarily the risk-appetite/credit-supply shock captured by the EBP, not expected default losses.

2. **The credit-equity relationship is bidirectional, with the dominant direction depending on the regime.** In normal times, equity tends to lead credit (Norden & Weber 2009; structural Merton channel). In stress periods, credit markets appear to lead, reflecting informed trading and risk appetite shifts (Acharya & Johnson 2007). At least 5 studies address this.

3. **The relationship is nonlinear and regime-dependent.** Constant-parameter linear models are inadequate (Guidolin & Timmermann 2007; Ang & Bekaert 2002; Adrian et al. 2019; Hamilton 1989). Stress regimes amplify the credit-equity nexus.

4. **Spread changes and normalized transforms are better predictors than raw levels.** Levels are near-unit-root; changes, z-scores, and percentile ranks provide stationary and more informative signals (Collin-Dufresne et al. 2001; practitioner convention).

**Single-study findings (flagged):**

- Acharya & Johnson (2007) is the primary evidence for CDS-to-equity information flow via insider trading. This is suggestive but based on a specific mechanism (bank relationships) that may not generalize to the aggregate HY-IG spread.
- The 6x improvement of bond q over equity q (Philippon 2009) is a strong result but from a single study.

---

## Open Questions / Debates

1. **Does aggregate HY-IG spread predict aggregate equity returns, or is this a cross-sectional phenomenon?** Most micro-level evidence (Acharya & Johnson, Norden & Weber) is firm-level. Aggregation may wash out the signal.

2. **Has the credit-equity relationship changed post-GFC?** The proliferation of credit ETFs (HYG, LQD), algorithmic trading, and central bank QE may have altered information flow dynamics. Sub-sample stability is an open question.

3. **What is the optimal horizon for credit-to-equity predictability?** The literature suggests multiple horizons matter differently: days (informed trading), months (credit cycle), quarters (macro). Our multi-horizon design addresses this.

4. **Can the signal be profitably traded after transaction costs?** Academic predictability ≠ tradability. The combinatorial tournament with 5 bps round-trip costs and signal decay tests is essential.

5. **How much of the HY-IG spread is liquidity vs. default risk?** Longstaff et al. (2005) show liquidity is 17-49% of the spread. If the liquidity component drives the equity signal, interpretation changes fundamentally.

---

## Implications for Our Analysis

1. **Test both causal directions explicitly.** Do not assume credit leads equity — the Merton (1974) structural channel creates reverse causality. Report Toda-Yamamoto and transfer entropy in both directions.

2. **Use spread transforms, not just levels.** Z-scores, percentile ranks, and rates of change should be primary regressors. Levels may be included for cointegration analysis only.

3. **Regime-condition all key results.** Run Granger causality and local projections separately for stress vs. calm regimes. The signal likely activates at stress thresholds.

4. **Include the CCC-BB quality spread.** Intra-HY quality migration (CCC-BB) captures distress concentration that the aggregate HY-IG spread may miss (Berndt et al. 2018).

5. **Control for the yield curve.** The 10Y-3M slope is an established recession predictor (Estrella & Mishkin 1998). Include it to isolate the marginal contribution of credit spreads.

6. **Interpret the EBP decomposition carefully.** Our HY-IG spread is a blend of expected default and risk appetite. Note this limitation explicitly — the predictive power may attenuate relative to the pure EBP.

7. **Be skeptical of in-sample results.** The literature shows strong in-sample predictability but limited out-of-sample evidence for profitability. Our IS/OOS split at 2017/2018 is critical.

---

## Recommended Specification Details

| Field | Recommendation | Source / Rationale |
|-------|---------------|--------------------|
| Dependent variable | SPY forward total returns at h = 1d, 5d, 21d, 63d, 126d, 252d | Multi-horizon approach follows Jordà (2005) local projections; Gilchrist & Zakrajsek (2012) use quarterly horizons |
| Key regressors | HY-IG spread z-score (252d, 504d), RoC (21d, 63d, 126d), momentum (MoM, QoQ, YoY), spread acceleration | Z-scores per practitioner convention; RoC motivated by Collin-Dufresne et al. (2001) emphasis on spread changes |
| Complementary regressors | CCC-BB quality spread, VIX term structure (VIX3M − VIX), yield curve slope (10Y-3M), NFCI, spread realized vol (21d) | Berndt et al. (2018) for quality spread; Estrella & Mishkin (1998) for yield curve; Adrian et al. (2019) for NFCI |
| Control variables | Fed funds rate, initial claims, dollar index | Standard macro controls |
| Instruments (if IV) | Not recommended for primary specification; Toda-Yamamoto avoids pre-testing. For robustness: lagged VIX term structure as instrument for contemporaneous spread changes | Toda & Yamamoto (1995) |
| Lag structure | Toda-Yamamoto: k + d_max where k selected by BIC from {1, 5, 10, 21} and d_max = 1. Local projections: direct regression at each h, no explicit lag structure beyond conditioning set | Toda & Yamamoto (1995); Jordà (2005) |
| Regime identification | Markov-switching 2-state and 3-state on joint HY-IG/VIX; Gaussian HMM as robustness check; also percentile-based thresholds (top quartile = stress) | Hamilton (1989); Guidolin & Timmermann (2007) |
| Functional form | Linear for base specifications; quantile regression at tau = {0.05, 0.10, 0.25, 0.50, 0.75, 0.90} for distributional effects; local projections with regime interactions for nonlinearity | Adrian et al. (2019) for distributional focus |
| Standard errors | HAC (Newey-West) with bandwidth = floor(0.75 * T^(1/3)) for time-series regressions; HC3 for cross-sectional | Standard robust inference |
| Notes | Results likely sensitive to sample period (pre/post GFC). Run sensitivity: full sample, excl. GFC (2007-09), excl. COVID (2020), pre-2008 only. Check for structural breaks with PELT. | Collin-Dufresne et al. (2001) — pre-crisis sample may differ |

---

## Variables Used in Key Studies

| Study | Dependent Variable | Key Regressors | Data Source | Period |
|-------|--------------------|----------------|-------------|--------|
| Gilchrist & Zakrajsek (2012) | GDP growth, investment, employment | GZ credit spread, EBP | Micro-level corporate bonds | 1973-2010, monthly |
| Faust et al. (2013) | Real GDP, IP, employment, unemployment | Portfolio credit spreads (maturity × rating) | Micro-level corporate bonds | 1985-2010, monthly/quarterly |
| Philippon (2009) | Corporate investment | Bond market q | Compustat, FISD | 1953-2003, annual |
| Mueller (2009) | GDP growth | Credit spread factor | Merrill Lynch indices | 1990-2008, monthly |
| Collin-Dufresne et al. (2001) | Credit spread changes | Equity returns, leverage, rates, volatility | Dealer quotes, industrial bonds | 1988-1997, monthly |
| Norden & Weber (2009) | CDS/bond spread changes, equity returns | Lagged CDS/equity/bond returns | Bloomberg, Datastream | 2000-2002, daily |
| Acharya & Johnson (2007) | Equity returns (next 1-5 days) | Lagged CDS spread changes | CDS dealers, CRSP | 2001-2004, daily |
| Ang & Bekaert (2002) | International equity returns | Regime state | MSCI indices | 1975-1997, monthly |
| Guidolin & Timmermann (2007) | Stock and bond returns | Regime state (4 regimes) | CRSP, Ibbotson | 1973-2004, monthly |
| Adrian et al. (2019) | GDP growth distribution | NFCI, term spread | FRED, Chicago Fed | 1973-2015, quarterly |
| Estrella & Mishkin (1998) | Recession probability | 10Y-3M term spread | Federal Reserve | 1959-1995, quarterly |
| Campbell & Taksler (2003) | Corporate bond yield spreads | Equity volatility (idiosyncratic) | TRACE, CRSP | 1995-1999, daily |
| Berndt et al. (2018) | Credit risk premia | CDS spreads, EDF | Markit CDS, Moody's EDF | 2002-2015, monthly |
| Longstaff et al. (2005) | Yield spread decomposition | CDS-implied default, bond liquidity | CDS dealers, TRACE | 2001-2002, monthly |

---

## Recommended Data Sources

| Variable | Concept | Series ID | MCP Server | Frequency | SA | Availability |
|----------|---------|-----------|------------|-----------|-----|-------------|
| HY OAS | ICE BofA US HY Option-Adjusted Spread | BAMLH0A0HYM2 | fred | Daily | N | Confirmed |
| IG OAS | ICE BofA US IG Option-Adjusted Spread | BAMLC0A0CM | fred | Daily | N | Confirmed |
| BB HY OAS | ICE BofA BB US HY OAS | BAMLH0A1HYBB | fred | Daily | N | Confirmed |
| CCC HY OAS | ICE BofA CCC & Lower US HY OAS | BAMLH0A3HYC | fred | Daily | N | Confirmed |
| BBB OAS | ICE BofA BBB US Corporate OAS | BAMLC0A4CBBB | fred | Daily | N | Confirmed |
| SPY | SPDR S&P 500 ETF Trust | SPY | yahoo-finance | Daily | N | Confirmed |
| VIX | CBOE Volatility Index | ^VIX | yahoo-finance | Daily | N | Confirmed |
| VIX3M | CBOE 3-Month Volatility Index | ^VIX3M | yahoo-finance | Daily | N | Confirmed (avail. from ~2007) |
| 10Y Treasury | 10-Year Treasury Constant Maturity Rate | DGS10 | fred | Daily | N | Confirmed |
| 3M Treasury | 3-Month Treasury Bill Secondary Market Rate | DTB3 | fred | Daily | N | Confirmed |
| 2Y Treasury | 2-Year Treasury Constant Maturity Rate | DGS2 | fred | Daily | N | Confirmed |
| NFCI | Chicago Fed National Financial Conditions Index | NFCI | fred | Weekly | N | Confirmed |
| KBE | SPDR S&P Bank ETF | KBE | yahoo-finance | Daily | N | Confirmed (avail. from 2005-11) |
| IWM | iShares Russell 2000 ETF | IWM | yahoo-finance | Daily | N | Confirmed |
| MOVE Index | ICE BofA MOVE Index | ^MOVE | yahoo-finance | Daily | N | Availability: UNCONFIRMED — Dana to verify (may require alternative source) |
| Initial Claims | Initial Claims, SA | ICSA | fred | Weekly | Y | Confirmed |
| Fed Funds Rate | Effective Federal Funds Rate | DFF | fred | Daily | N | Confirmed |
| FSI | St. Louis Fed Financial Stress Index | STLFSI2 | fred | Weekly | N | Confirmed |
| Gold | Gold Futures | GC=F | yahoo-finance | Daily | N | Confirmed |
| Copper | Copper Futures | HG=F | yahoo-finance | Daily | N | Confirmed |
| Dollar Index | US Dollar Index | DX-Y.NYB | yahoo-finance | Daily | N | Confirmed |
| SOFR | Secured Overnight Financing Rate | SOFR | fred | Daily | N | Confirmed (avail. from 2018-04) |
| HYG | iShares iBoxx $ HY Corp Bond ETF | HYG | yahoo-finance | Daily | N | Confirmed (avail. from 2007-04) |

**Notes for Dana:**
- VIX3M (^VIX3M): Available from ~2007. For 2000-2007, consider constructing a proxy using VIX + historical term structure or using VXV if available.
- KBE: Available from 2005-11 only. For 2000-2005, this series will be missing. Discuss with Evan whether to use an alternative bank index.
- SOFR: Available from 2018-04 only. For the in-sample period (2000-2017), use Fed Funds Rate (DFF) as the short-rate proxy. SOFR is secondary priority.
- MOVE Index (^MOVE): **Availability unconfirmed** via Yahoo Finance. Dana to verify; if unavailable, consider FRED's BAMLH0A0HYM2EY (HY effective yield) or drop this variable.
- HYG: Available from 2007-04. Not available for early in-sample period.

---

## Event Timeline (for Visualization)

| Date | Event | Relevance | Type |
|------|-------|-----------|------|
| 2001-03-01 | NBER recession begins (dot-com bust) | HY spreads widen from ~600 to ~1000 bps; equity decline already underway since 2000-03 | Recession start |
| 2001-09-11 | September 11 attacks | Sharp liquidity shock; HY spreads spike; equity markets closed for 4 days | Exogenous shock |
| 2001-11-01 | NBER recession ends | Recovery begins; spreads begin compressing | Recession end |
| 2002-07-01 | WorldCom bankruptcy | Largest bankruptcy at the time; credit markets reprice default risk for telecoms | Credit event |
| 2003-06-25 | Fed cuts to 1.00% (lowest since 1958) | Begins the credit boom; HY spreads compress toward historic tights | Policy change |
| 2007-06-01 | Bear Stearns hedge fund collapse | First visible crack in structured credit; HY-IG spread begins widening | Crisis onset |
| 2007-12-01 | NBER recession begins (GFC) | Credit spreads already elevated; equity peak was Oct 2007 — credit led by ~5 months | Recession start |
| 2008-03-16 | Bear Stearns rescue (JPM acquisition) | HY spreads at ~800 bps; signaled systemic risk | Crisis escalation |
| 2008-09-15 | Lehman Brothers bankruptcy | HY spreads explode to ~2,000+ bps; equity crash accelerates | Structural break |
| 2008-11-25 | QE1 announced ($600B MBS + $200B agency) | Credit markets begin stabilizing; spreads peak Dec 2008 | Policy intervention |
| 2009-06-01 | NBER recession ends | Spreads still elevated (~1,000 bps) but compressing rapidly | Recession end |
| 2010-11-03 | QE2 announced ($600B Treasuries) | Further spread compression; search for yield intensifies | Policy intervention |
| 2012-09-13 | QE3 announced (open-ended $40B/mo MBS) | Spreads compress to post-crisis lows; HY-IG reaches ~300 bps | Policy intervention |
| 2013-05-22 | Taper Tantrum (Bernanke testimony) | Sudden repricing of rate expectations; HY-IG widens ~50 bps in weeks | Policy shock |
| 2015-08-11 | China yuan devaluation | Global risk-off; HY-IG widens alongside equity selloff | Exogenous shock |
| 2015-12-16 | First Fed rate hike (0-0.25% → 0.25-0.50%) | End of ZIRP era; HY spreads had already widened due to energy sector stress | Policy change |
| 2016-02-11 | Energy/commodity credit crisis trough | HY OAS peaks at ~880 bps driven by oil; SPY bottoms within days | Sector crisis |
| 2018-02-05 | VIX spike ("Volmageddon") | VIX hits 50; mechanical short-vol unwind; HY-IG widens briefly | Vol regime shift |
| 2018-12-24 | Q4 2018 selloff trough | Fed pivot (from tightening to pause); SPY drops ~20% from peak; HY-IG widens ~150 bps | Policy-driven reversal |
| 2020-02-20 | COVID-19 selloff begins | SPY falls 34% in 23 trading days; HY spreads reach ~1,100 bps by 2020-03-23 | Pandemic shock |
| 2020-03-23 | Fed announces unlimited QE + corporate credit facilities | Market bottom; HY spreads compress from ~1,100 to ~500 bps within weeks | Policy intervention |
| 2020-04-01 | NBER recession ends (shortest on record, 2 months) | V-shaped recovery begins | Recession end |
| 2021-11-01 | Fed signals taper | Beginning of tightening cycle; credit spreads at post-GFC lows (~300 bps HY-IG) | Policy change |
| 2022-03-16 | First Fed rate hike (0-0.25% → 0.25-0.50%) | Aggressive tightening cycle begins; HY-IG widens | Policy change |
| 2022-06-16 | 75 bps rate hike (largest since 1994) | Risk-off intensifies; SPY enters bear market territory | Policy shock |
| 2022-10-13 | SPY bear market trough | CPI print begins moderation narrative; HY-IG at ~500 bps | Regime shift |
| 2023-03-10 | SVB collapse + regional bank crisis | Credit spreads spike briefly; KBE drops ~30% in 2 weeks; contagion fears | Bank crisis |
| 2023-07-26 | Last Fed rate hike (5.25-5.50%) | Terminal rate reached; credit spreads begin compressing | Policy change |
| 2024-09-18 | First Fed rate cut (50 bps) | Easing cycle begins; HY-IG at tight levels (~280 bps) | Policy change |

*NBER recession dates: 2001-03 to 2001-11, 2007-12 to 2009-06, 2020-02 to 2020-04.*

---

## Domain Visualization Conventions

From the literature review, the following charting conventions are standard:

1. **Credit spreads plotted with inverted y-axis convention:** Many practitioners plot spreads on the left y-axis (ascending = wider = more stress) and equity prices on the right y-axis (ascending = higher prices). When credit leads equity, spread widening visually precedes equity decline.

2. **Regime shading:** Recession periods (NBER) shaded in gray. Stress regimes (HMM-identified) can be shaded in red/orange for additional context. Guidolin & Timmermann (2007) use distinct colors for each of their four regimes.

3. **Time series alignment:** Plot credit spreads and equity returns on the same time axis with dual y-axes. Use lead/lag offsets to visually demonstrate predictive relationships.

4. **Scatter plots by regime:** Ang & Bekaert (2002) use regime-colored scatter plots showing how the return-volatility relationship changes across states. Effective for our spread-return analysis.

5. **Impulse response functions:** Jordà (2005) local projections displayed with confidence bands (typically 68% and 95%). X-axis is horizon (days), y-axis is cumulative response. State-dependent IRFs shown as separate lines on the same plot.

6. **Quantile regression fan charts:** Adrian et al. (2019) "Vulnerable Growth" style — plot the 5th, 25th, 50th, 75th, and 95th conditional quantiles of equity returns as a function of the credit spread signal. This creates a "fan" that widens during stress.

---

## References

1. Acharya, V.V. & Johnson, T.C. (2007). "Insider Trading in Credit Derivatives." *Journal of Financial Economics*, 84(1): 110-141.

2. Adrian, T., Boyarchenko, N. & Giannone, D. (2019). "Vulnerable Growth." *American Economic Review*, 109(4): 1263-1289.

3. Ang, A. & Bekaert, G. (2002). "International Asset Allocation With Regime Shifts." *Review of Financial Studies*, 15(4): 1137-1187.

4. Ang, A., Piazzesi, M. & Wei, M. (2006). "What Does the Yield Curve Tell Us About GDP Growth?" *Journal of Econometrics*, 131(1-2): 359-403.

5. Berndt, A., Douglas, R., Duffie, D. & Ferguson, M. (2018). "Corporate Credit Risk Premia." *Review of Finance*, 22(2): 419-454.

6. Blanco, R., Brennan, S. & Marsh, I.W. (2005). "An Empirical Analysis of the Dynamic Relationship Between Investment-Grade Bonds and Credit Default Swaps." *Journal of Finance*, 60(5): 2255-2281.

7. Campbell, J.Y. & Taksler, G.B. (2003). "Equity Volatility and Corporate Bond Yields." *Journal of Finance*, 58(6): 2321-2350.

8. Collin-Dufresne, P., Goldstein, R.S. & Martin, J.S. (2001). "The Determinants of Credit Spread Changes." *Journal of Finance*, 56(6): 2177-2207.

9. Diks, C. & Panchenko, V. (2006). "A New Statistic and Practical Guidelines for Nonparametric Granger Causality Testing." *Journal of Economic Dynamics and Control*, 30(9-10): 1647-1669.

10. Estrella, A. & Mishkin, F.S. (1998). "Predicting U.S. Recessions: Financial Variables as Leading Indicators." *Review of Economics and Statistics*, 80(1): 45-61.

11. Faust, J., Gilchrist, S., Wright, J.H. & Zakrajsek, E. (2013). "Credit Spreads as Predictors of Real-Time Economic Activity: A Bayesian Model-Averaging Approach." *Review of Economics and Statistics*, 95(5): 1501-1519.

12. Gilchrist, S. & Zakrajsek, E. (2012). "Credit Spreads and Business Cycle Fluctuations." *American Economic Review*, 102(4): 1692-1720.

13. Gomes, J.F. & Schmid, L. (2010). "Equilibrium Credit Spreads and the Macroeconomy." Working Paper, Wharton School, University of Pennsylvania.

14. Guidolin, M. & Timmermann, A. (2007). "Asset Allocation Under Multivariate Regime Switching." *Journal of Economic Dynamics and Control*, 31(11): 3503-3544.

15. Hamilton, J.D. (1989). "A New Approach to the Economic Analysis of Nonstationary Time Series and the Business Cycle." *Econometrica*, 57(2): 357-384.

16. Huang, X., Zhou, H. & Zhu, H. (2009). "A Framework for Assessing the Systemic Risk of Major Financial Institutions." *Journal of Banking & Finance*, 33(11): 2036-2049.

17. Johansen, S. (1991). "Estimation and Hypothesis Testing of Cointegration Vectors in Gaussian Vector Autoregressive Models." *Econometrica*, 59(6): 1551-1580.

18. Jordà, O. (2005). "Estimation and Inference of Impulse Responses by Local Projections." *American Economic Review*, 95(1): 161-182.

19. Longstaff, F.A., Mithal, S. & Neis, E. (2005). "Corporate Yield Spreads: Default Risk or Liquidity? New Evidence from the Credit Default Swap Market." *Journal of Finance*, 60(5): 2213-2253.

20. Merton, R.C. (1974). "On the Pricing of Corporate Debt: The Risk Structure of Interest Rates." *Journal of Finance*, 29(2): 449-470.

21. Mueller, P. (2009). "Credit Spreads and Real Activity." Working Paper, London School of Economics. (Later published in *Review of Financial Studies*.)

22. Norden, L. & Weber, M. (2009). "The Co-movement of Credit Default Swap, Bond and Stock Markets: An Empirical Analysis." *European Financial Management*, 15(3): 529-562.

23. Philippon, T. (2009). "The Bond Market's q." *Quarterly Journal of Economics*, 124(3): 1011-1056.

24. Schreiber, T. (2000). "Measuring Information Transfer." *Physical Review Letters*, 85(2): 461.

25. Toda, H.Y. & Yamamoto, T. (1995). "Statistical Inference in Vector Autoregressions with Possibly Integrated Processes." *Journal of Econometrics*, 66(1-2): 225-250.
