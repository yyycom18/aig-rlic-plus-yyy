# Specification Memo: HY-IG Credit Spread vs S&P 500 Returns

**From:** Ray (Research Agent)
**To:** Evan (Econometrics), Dana (Data), Alex (Lead)
**Date:** 2026-02-28
**Status:** Stage 1 — Quick Spec (Full research brief to follow)

---

## 1. Dependent Variable

**SPY forward returns at multiple horizons:** 1-day, 5-day (1 week), 21-day (1 month), 63-day (1 quarter), 126-day (6 months), and 252-day (1 year). Literature consistently uses excess or total equity returns as the outcome variable. Gilchrist & Zakrajsek (2012) use quarterly excess stock returns; Philippon (2009) uses annual equity returns; Mueller (2009) uses monthly S&P 500 excess returns. Multi-horizon analysis is essential because credit signals operate at different frequencies — short-horizon (days to weeks) for liquidity-driven moves, medium-horizon (months) for credit-cycle shifts, and long-horizon (quarters to years) for macroeconomic regime transitions.

## 2. Key Regressors

| Regressor | Transform | Literature Support |
|-----------|-----------|-------------------|
| HY-IG spread (level) | Raw OAS differential (BAMLH0A0HYM2 − BAMLC0A0CM) | Gilchrist & Zakrajsek (2012), Philippon (2009) |
| HY-IG spread z-score | 252d and 504d rolling standardization | Practitioner convention; controls for time-varying volatility |
| HY-IG rate of change | 21d, 63d, 126d log changes | Collin-Dufresne et al. (2001) — spread changes more informative than levels |
| HY-IG momentum | Month-over-month, QoQ, YoY absolute changes | Norden & Weber (2009) — CDS spread momentum leads equity |
| CCC-BB quality spread | BAMLH0A3HYC − BAMLH0A1HYBB | Berndt et al. (2018) — intra-HY quality spread signals distress migration |
| VIX term structure | VIX3M − VIX (contango/backwardation) | Mixon (2007), Johnson (2017) — vol term structure captures risk sentiment |
| Yield curve slope | 10Y-3M (DGS10 − DTB3) and 10Y-2Y (DGS10 − DGS2) | Estrella & Mishkin (1998), Ang et al. (2006) — recession predictor |
| NFCI | Chicago Fed National Financial Conditions Index | Adrian et al. (2019) — financial conditions predict tail risk |
| Spread realized vol | 21d rolling std of daily spread changes | Schaefer & Strebulaev (2008) — spread volatility as uncertainty proxy |
| Spread acceleration | Diff-of-RoC (second derivative of spread) | Novel, motivated by momentum-crash literature |

**Control variables:** Fed funds rate (DFF), initial claims (ICSA), dollar index (DX-Y.NYB), gold (GC=F), copper-gold ratio.

## 3. Identification Strategy

The literature employs several identification approaches for the credit-equity nexus:

- **Toda-Yamamoto Granger causality (both directions):** Test whether lagged HY-IG spread changes predict SPY returns (Credit → Equity) and vice versa (Equity → Credit). Use augmented VAR at multiple lag orders (1, 5, 10, 21, 42, 63, 126, 252 days). Toda-Yamamoto avoids pre-testing for unit roots, which is critical given the near-unit-root behavior of spread levels. Reference: Toda & Yamamoto (1995).
- **Transfer entropy (nonlinear causality):** Captures nonlinear information flow missed by linear Granger tests. Diks & Panchenko (2006) provide the nonparametric test; Schreiber (2000) establishes the information-theoretic framework. Run in both directions and compare to Granger results — divergence implies nonlinear dynamics.
- **Local projections (Jordà 2005):** Impulse responses at horizons h = 1, 5, 10, 21, 42, 63 days. State-dependent version conditions on HMM regime or spread quartile. Robust to misspecification of the full VAR system. Asymmetric effects testable by interacting shock with regime indicator.
- **Regime-switching models:** Markov-switching regression (Hamilton 1989) and Gaussian HMM (2- and 3-state) on joint HY-IG/VIX dynamics. Guidolin & Timmermann (2008) show regime-dependent equity-bond correlations. Ang & Bekaert (2002) demonstrate regime-switching in international equity returns.
- **Cointegration (if applicable):** Johansen (1991) trace and max-eigenvalue tests on HY-IG spread level and SPY log price. If cointegrated, use VECM for short-run dynamics and long-run equilibrium. If not cointegrated, proceed with VAR in differences.

## 4. Known Pitfalls

| Pitfall | Description | Mitigation |
|---------|-------------|------------|
| **Reverse causality** | Equity returns drive credit spreads (Merton 1974 structural model — firm value ↓ → spread ↑). This is the central endogeneity concern. | Test both directions explicitly. Report asymmetry. Use local projections which are robust to dynamic misspecification. |
| **Structural breaks** | GFC (2007-09) and COVID (2020-03) represent regime shifts where spread dynamics changed fundamentally. | Estimate models with and without these episodes. PELT change-point detection. Markov-switching to endogenize breaks. |
| **Non-stationarity** | Spread levels exhibit near-unit-root behavior (persistent but mean-reverting at very long horizons). | Use spread changes, z-scores, or percentile ranks rather than raw levels as regressors. Confirm stationarity with ADF, PP, and KPSS tests. |
| **Lookahead bias** | Threshold selection using full-sample percentiles introduces forward-looking information. | Walk-forward threshold estimation. Rolling percentiles (504d window). In-sample/OOS split at 2017/2018 boundary. |
| **Multiple testing** | Combinatorial tournament (~1,000 combinations) inflates false discovery rate. | Bootstrap significance tests (10,000 replications). Report p-values for Sharpe > 0. Familywise error correction where applicable. |
| **Liquidity effects** | Credit spreads include a liquidity premium that is not purely default-related. | Gilchrist & Zakrajsek (2012) decompose into credit and excess bond premium; the EBP component is the better equity predictor. |
| **Sample-period sensitivity** | Results from the 2000-2007 pre-crisis period may not generalize. | Sub-sample analysis: pre-GFC, post-GFC, pre-COVID, full. Walk-forward validation. |

## 5. Sample Conventions

- **Daily frequency, 2000-01-01 to 2025-12-31.** Most credit spread series from ICE BofA (via FRED) are available daily from ~1996. The 2000 start ensures adequate pre-crisis observations and avoids the 1998 LTCM regime, which was structurally different.
- **In-sample: 2000-01-01 to 2017-12-31 (~4,500 obs).** Covers dot-com bust, mid-2000s credit boom, GFC, and post-crisis recovery. Provides sufficient observations for regime-switching estimation (Hamilton 1989 recommends long samples for Markov-switching).
- **Out-of-sample: 2018-01-01 to 2025-12-31 (~2,000 obs).** Includes 2018 vol spike, 2020 COVID crash, 2022 rate-hike shock, 2023-25 recovery — a genuinely challenging test window.
- **Business-day calendar.** Align all series to NYSE trading days. Forward-fill FRED series (which have T+1 publication lags) to avoid lookahead.
- **Stationarity convention:** Use ADF, PP, and KPSS tests on all raw series. Transform non-stationary series to first differences or z-scores before modeling. Report test results in the stationarity table.

---

*Full research brief with 20+ citations, event timeline, data source recommendations, and portal narrative to follow.*
