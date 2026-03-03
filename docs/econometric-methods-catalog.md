# Econometric & Statistical Methods Catalog
## Credit Spread / Equity Prediction Analysis — Reference Appendix

Here is a comprehensive catalogue of **40+ candidate econometric and statistical methods** organized by category, with relevance to credit-spread-to-equity analysis.

---

## 1. Correlation and Dependence

| # | Method | What It Does / When to Use | Relevance to Credit-Spread-to-Equity | Python Package | Complexity | Key Reference |
|---|--------|---------------------------|--------------------------------------|----------------|------------|---------------|
| 1 | **Spearman Rank Correlation** | Non-parametric monotonic association; no normality assumption needed | Captures monotonic but non-linear co-movement between spreads and returns | `scipy.stats.spearmanr` | Straightforward | Spearman (1904) |
| 2 | **Kendall's Tau** | Rank-based concordance measure; robust to outliers | More robust than Pearson when spread/equity data have fat tails or outliers | `scipy.stats.kendalltau` | Straightforward | Kendall (1938) |
| 3 | **Rolling / Expanding Window Correlation** | Time-varying Pearson or rank correlation over rolling windows | Reveals how the spread-equity relationship strengthens during stress periods | `pandas.DataFrame.rolling().corr()` | Straightforward | — |
| 4 | **Dynamic Conditional Correlation (DCC-GARCH)** | Multivariate GARCH that estimates time-varying correlations between series | Shows how credit-equity correlation spikes during crises; core tool for contagion analysis | `arch` (via `rmgarch` in R; custom in Python), or `mgarch` | Advanced | [Engle (2002)](https://www.researchgate.net/publication/5000337_Dynamic_Conditional_Correlation_-_A_Simple_Class_of_Multivariate_GARCH_Models) |
| 5 | **Gaussian Copula** | Models joint distribution with flexible marginals; measures dependence structure | Separates marginal behavior of spreads/equity from their dependence structure | [`pycop`](https://pypi.org/project/pycop/), [`copul`](https://pypi.org/project/copul/) | Moderate | [Embrechts, McNeil & Straumann (2002)](https://people.math.ethz.ch/~embrecht/ftp/copchapter.pdf) |
| 6 | **Student-t Copula** | Like Gaussian copula but captures symmetric tail dependence | Better than Gaussian copula when spreads and equities crash together (tail co-dependence) | `pycop`, `copul` | Moderate | Demarta & McNeil (2005) |
| 7 | **Clayton / Gumbel Copula** | Asymmetric copulas capturing lower-tail (Clayton) or upper-tail (Gumbel) dependence | Clayton captures joint distress (widening spreads + falling equities); Gumbel captures joint euphoria | `pycop`, `copul` | Moderate | [Nelsen (2006), *An Introduction to Copulas*](https://freakonometrics.hypotheses.org/2435) |
| 8 | **Time-Varying Copula** | Copula parameters evolve over time (e.g., via GAS or DCC dynamics) | Models how the dependence structure between spreads and equities shifts across regimes | `pycop`, custom implementation | Advanced | [Oh & Patton (2013)](https://ideas.repec.org/p/duk/dukeec/13-30.html) |
| 9 | **Tail Dependence Coefficients** | Probability that both series are in extreme quantiles simultaneously | Quantifies whether spread spikes and equity crashes tend to co-occur in the tails | `copul` (lambda_L, lambda_U), `pycop` | Moderate | Joe (1997), *Multivariate Models and Dependence Concepts* |
| 10 | **Distance Correlation (dCor)** | Measures both linear and non-linear dependence; equals zero iff independent | Detects non-linear spread-equity relationships that Pearson misses entirely | `dcor` | Moderate | Szekely, Rizzo & Bakirov (2007) |

---

## 2. Lead-Lag and Causality

| # | Method | What It Does / When to Use | Relevance to Credit-Spread-to-Equity | Python Package | Complexity | Key Reference |
|---|--------|---------------------------|--------------------------------------|----------------|------------|---------------|
| 11 | **Toda-Yamamoto Granger Causality** | Granger test valid even with non-stationary / cointegrated data (augmented lag approach) | Avoids pre-testing for unit roots in spread/equity levels; more robust than standard Granger | `statsmodels` (manual augmented VAR) | Moderate | Toda & Yamamoto (1995) |
| 12 | **Nonlinear Granger Causality** | Tests whether past values of X help predict Y beyond a linear model | Detects if credit spreads predict equity crashes through non-linear channels | Custom (kernel-based), `nolitsa` | Advanced | [Diks & Panchenko (2006)](https://www.nature.com/articles/s41598-021-87316-6) |
| 13 | **Spectral / Frequency-Domain Granger Causality** | Decomposes causality by frequency band (short-run vs. long-run) | Separates whether spreads predict equity at business-cycle frequencies vs. high-frequency noise | `spectral_connectivity_measures`, custom | Advanced | Breitung & Candelon (2006) |
| 14 | **Transfer Entropy** | Model-free, information-theoretic measure of directional information flow | Captures both linear and [non-linear causal flows from credit to equity markets](https://link.springer.com/article/10.1007/s10260-021-00614-1) without specifying a model | `pyinform`, `PyCausality`, [`TransferEntropy`](https://bookdown.org/souzatharsis/open-quant-live-book/how-to-measure-statistical-causality-a-transfer-entropy-approach-with-financial-applications.html) | Advanced | Schreiber (2000) |
| 15 | **Wavelet Coherence** | Time-frequency decomposition of co-movement; shows lead-lag at different scales | Reveals if spread-to-equity prediction is stronger at weekly vs. monthly vs. quarterly horizons | `pywt`, `waipy`, custom (Morlet wavelet) | Advanced | Torrence & Compo (1998); Grinsted et al. (2004) |
| 16 | **Cross-Correlation Function (CCF) with Pre-whitening** | Identifies optimal lag structure between two pre-whitened series | Simple first pass to find the lag at which spreads most predict returns | `statsmodels.tsa.stattools.ccf` | Straightforward | Box & Jenkins (1976) |
| 17 | **Convergent Cross Mapping (CCM)** | Detects causality in dynamical systems; works for weakly coupled non-separable systems | Alternative to Granger when spread-equity system has complex feedback loops | `pyEDM` | Advanced | Sugihara et al. (2012) |

---

## 3. Regime Identification

| # | Method | What It Does / When to Use | Relevance to Credit-Spread-to-Equity | Python Package | Complexity | Key Reference |
|---|--------|---------------------------|--------------------------------------|----------------|------------|---------------|
| 18 | **Markov-Switching Dynamic Regression (MS-DR)** | Regime-switching model where regression coefficients shift between states | Tests whether the spread-equity beta differs in crisis vs. calm regimes | `statsmodels.tsa.regime_switching.markov_regression` | Moderate | [Hamilton (1989)](https://homepage.ntu.edu.tw/~ckuan/pdf/Lec-Markov_note.pdf) |
| 19 | **Markov-Switching VAR (MS-VAR)** | VAR whose parameters switch between regimes governed by a Markov chain | Allows the entire spread-equity VAR dynamics (IRFs, etc.) to change across regimes | Custom, `statsmodels` (limited) | Advanced | Krolzig (1997), *Markov-Switching VARs* |
| 20 | **Hidden Markov Model (HMM)** | Unsupervised identification of latent states from observable data | Classifies market [into bull/bear/neutral regimes](https://www.quantstart.com/articles/market-regime-detection-using-hidden-markov-models-in-qstrader/) using returns + spreads as observables | [`hmmlearn`](https://datadave1.medium.com/detecting-market-regimes-hidden-markov-model-2462e819c72e) | Moderate | Rabiner (1989); [Ang & Bekaert (2002)](https://www.nber.org/system/files/working_papers/w17182/w17182.pdf) |
| 21 | **Threshold Autoregression (TAR / SETAR)** | Regime switch is triggered when an observable variable crosses a threshold | Tests if equity predictability "turns on" when spreads exceed a crisis threshold | `statsmodels` (manual), `tsDyn` (R) | Moderate | Tong (1978); Hansen (1999) |
| 22 | **Smooth Transition Autoregression (STAR / LSTAR)** | Like TAR but with gradual transition between regimes | Captures the gradual shift in spread-equity dynamics rather than an abrupt switch | Custom, `statsmodels` (limited) | Advanced | Terasvirta (1994); [Van Dijk et al. (2002)](https://www.mdpi.com/2227-7390/13/7/1128) |
| 23 | **Change-Point Detection (PELT / Binary Segmentation)** | Identifies structural breaks in mean, variance, or distribution | Detects when the [spread-equity relationship fundamentally changes](https://dl.acm.org/doi/10.1145/3773365.3773532) (e.g., GFC, COVID) | [`ruptures`](https://centre-borelli.github.io/ruptures-docs/) | Moderate | [Killick et al. (2012)](https://github.com/deepcharles/ruptures) |
| 24 | **CUSUM / MOSUM Tests** | Sequential tests for parameter constancy over time | Monitors in real time whether the spread-equity regression is stable or breaking down | `statsmodels.stats.diagnostic` | Straightforward | Brown, Durbin & Evans (1975) |

---

## 4. Time-Series Modeling

| # | Method | What It Does / When to Use | Relevance to Credit-Spread-to-Equity | Python Package | Complexity | Key Reference |
|---|--------|---------------------------|--------------------------------------|----------------|------------|---------------|
| 25 | **VECM (Vector Error Correction Model)** | VAR for cointegrated series; decomposes dynamics into short-run adjustment and long-run equilibrium | If spreads and equity are cointegrated, VECM captures the error-correction channel | [`statsmodels.tsa.vector_ar.vecm.VECM`](https://www.statsmodels.org/dev/generated/statsmodels.tsa.vector_ar.vecm.VECM.html) | Moderate | Johansen (1991); [Engle & Granger (1987)](https://mdpi.com/2079-3197/10/9/155/htm) |
| 26 | **Structural VAR (SVAR)** | VAR with contemporaneous restrictions derived from economic theory | Imposes structural identification (e.g., spreads react to equity within the day but not vice versa) | [`statsmodels.tsa.vector_ar.svar_model`](https://www.statsmodels.org/stable/vector_ar.html) | Moderate | Sims (1980); Blanchard & Quah (1989) |
| 27 | **Factor-Augmented VAR (FAVAR)** | Extracts latent factors from large panel of variables, includes them in VAR | Incorporates macro factors (inflation, industrial production) that jointly drive spreads and equities | Custom (PCA + VAR), [`TVP_FAVAR_Kalman_Filter`](https://github.com/fawdywahyu18/TVP_FAVAR_Kalman_Filter) | Advanced | [Bernanke, Boivin & Eliasz (2005)](https://hoagiet.github.io/portfolio/portfolio-6/) |
| 28 | **TVP-VAR (Time-Varying Parameter VAR)** | VAR where coefficients evolve over time via state-space / Kalman filter | Captures how the [spread-to-equity transmission mechanism changes](https://www.sciencedirect.com/science/article/abs/pii/S1057521918307555) across decades | Custom (Kalman), [`bvar`](https://blog.quantinsti.com/tvp-var-stochastic-volatility/) | Advanced | Primiceri (2005) |
| 29 | **Bayesian VAR (BVAR)** | VAR estimated with priors (Minnesota, SSVS, etc.) to handle over-parameterization | Better out-of-sample forecasting than unrestricted VAR when the spread-equity system has many lags/variables | `bvar`, custom (PyMC) | Advanced | Litterman (1986); [Koop & Korobilis (2010)](https://www.tandfonline.com/doi/full/10.1080/15140326.2024.2395114) |
| 30 | **Local Projections (Jorda)** | Directly estimates impulse responses at each horizon without VAR specification | More robust IRFs for the spread-to-equity effect; works with non-linearities and state dependence | Custom (OLS at each horizon), `linearmodels` | Moderate | Jorda (2005) |

---

## 5. Volatility and Risk

| # | Method | What It Does / When to Use | Relevance to Credit-Spread-to-Equity | Python Package | Complexity | Key Reference |
|---|--------|---------------------------|--------------------------------------|----------------|------------|---------------|
| 31 | **EGARCH** | Asymmetric GARCH; log-volatility ensures positivity; captures leverage effect | Models how equity volatility responds asymmetrically to spread shocks (bad news amplified) | [`arch`](https://arch.readthedocs.io/en/latest/univariate/univariate_volatility_modeling.html) | Moderate | Nelson (1991) |
| 32 | **GJR-GARCH (Threshold GARCH)** | Adds asymmetric term for negative shocks to conditional variance | [Captures the leverage effect](https://blog.quantinsti.com/garch-gjr-garch-volatility-forecasting-python/) where equity vol rises more after spread widening than spread tightening | `arch` | Moderate | Glosten, Jagannathan & Runkle (1993) |
| 33 | **DCC-GARCH** | Dynamic conditional correlations between multiple GARCH processes | The cornerstone model for tracking time-varying credit-equity correlation | `arch` (partial), `rmgarch` (R), custom Python | Advanced | Engle (2002) |
| 34 | **Realized Volatility (RV)** | Non-parametric volatility from high-frequency intraday returns | Provides a model-free benchmark for equity volatility; compare against spread-implied signals | `arch` (realized measures), `numpy` | Straightforward | Andersen & Bollerslev (1998) |
| 35 | **Stochastic Volatility (SV)** | Volatility follows its own latent stochastic process | More flexible than GARCH for modeling [equity volatility persistence and spread co-movement](https://github.com/ArturSepp/StochVolModels) | [`stochvolmodels`](https://pypi.org/project/stochvolmodels/), [`svolfit`](https://pypi.org/project/svolfit/), `PyMC` | Advanced | Taylor (1986); [Heston (1993)](https://www.codearmo.com/python-tutorial/heston-model-simulation-python) |
| 36 | **GARCH-MIDAS** | Decomposes volatility into short-run (daily GARCH) and long-run (macro) components | Long-run equity volatility component can be driven by credit spreads at lower frequency | `arch` (partial), custom | Advanced | Engle, Ghysels & Sohn (2013) |

---

## 6. Nonlinear and Machine Learning Methods

| # | Method | What It Does / When to Use | Relevance to Credit-Spread-to-Equity | Python Package | Complexity | Key Reference |
|---|--------|---------------------------|--------------------------------------|----------------|------------|---------------|
| 37 | **Random Forest + SHAP** | Ensemble tree model for feature importance and non-linear prediction | [Identifies which spread metrics](https://www.researchgate.net/publication/352394963_Credit_spread_approximation_and_improvement_using_random_forest_regression) (level, change, curvature) matter most for equity prediction; SHAP provides interpretability | `scikit-learn`, `shap` | Moderate | Breiman (2001); Lundberg & Lee (2017) |
| 38 | **Gradient Boosting (XGBoost / LightGBM)** | Sequential tree boosting with regularization; state-of-the-art tabular prediction | Best-in-class for [non-linear credit-spread-to-equity prediction](https://www.sciencedirect.com/science/article/abs/pii/S1544612323006451) with many candidate features; SHAP for explainability | `xgboost`, `lightgbm`, `shap` | Moderate | Chen & Guestrin (2016) |
| 39 | **LSTM (Long Short-Term Memory)** | Recurrent neural network for sequence prediction; captures long-range dependencies | Models complex temporal patterns in the spread-equity relationship that linear models miss | `tensorflow.keras`, `pytorch` | Advanced | Hochreiter & Schmidhuber (1997) |
| 40 | **Quantile Regression** | Estimates conditional quantiles rather than conditional mean | Asks: "Does a spread spike predict the 5th percentile of equity returns?" (tail risk focus) | [`statsmodels.regression.quantile_regression`](https://scikit-learn.org/stable/auto_examples/linear_model/plot_quantile_regression.html), `scikit-learn` | Moderate | Koenker & Bassett (1978) |
| 41 | **Quantile Random Forest** | Random forest that estimates the full conditional distribution | Combines non-linear flexibility of RF with distributional analysis of quantile regression | [`scikit-garden`](https://scikit-garden.github.io/examples/QuantileRegressionForests/), `quantile-forest` | Moderate | Meinshausen (2006) |

---

## 7. Signal Extraction and Filtering

| # | Method | What It Does / When to Use | Relevance to Credit-Spread-to-Equity | Python Package | Complexity | Key Reference |
|---|--------|---------------------------|--------------------------------------|----------------|------------|---------------|
| 42 | **Hodrick-Prescott Filter** | Decomposes series into trend and cycle components | Extracts the cyclical component of credit spreads that correlates with equity cycle | [`statsmodels.tsa.filters.hp_filter.hpfilter`](https://www.statsmodels.org/stable/generated/statsmodels.tsa.filters.hp_filter.hpfilter.html) | Straightforward | Hodrick & Prescott (1997) |
| 43 | **Baxter-King Band-Pass Filter** | Isolates fluctuations within a specified frequency band | Extracts business-cycle-frequency movements in spreads (e.g., 6-32 quarters) for equity prediction | [`statsmodels.tsa.filters.bk_filter.bkfilter`](https://www.statsmodels.org/stable/generated/statsmodels.tsa.filters.bk_filter.bkfilter.html) | Straightforward | Baxter & King (1999) |
| 44 | **Christiano-Fitzgerald Filter** | Asymmetric band-pass filter; works on full sample; handles random walks | [More flexible than Baxter-King](https://www.statsmodels.org/dev/generated/statsmodels.tsa.filters.cf_filter.cffilter.html) for non-stationary spread series; uses entire sample | `statsmodels.tsa.filters.cf_filter.cffilter` | Straightforward | Christiano & Fitzgerald (2003) |
| 45 | **Wavelet Decomposition (DWT/CWT)** | Multi-resolution analysis; decomposes into scale-specific approximations and details | Separates spread signal into [short-term noise vs. medium-term cycles vs. long-term trends](https://abouttrading.substack.com/p/financial-signal-processing-in-python-dd0) for equity forecasting | `pywt` (PyWavelets) | Moderate | Mallat (1989); Percival & Walden (2000) |
| 46 | **Kalman Filter / State-Space Model** | Optimal recursive estimation of unobserved states from noisy observations | Extracts the "true" unobservable credit risk signal from noisy spread data; time-varying parameter estimation | `statsmodels.tsa.statespace`, `filterpy` | Advanced | Kalman (1960); Harvey (1989) |
| 47 | **Hamilton Filter** | Regression-based alternative to HP filter; avoids spurious cyclicality | Cleaner business-cycle extraction from spreads than HP filter (which can create artificial cycles) | Custom (OLS), `statsmodels` | Moderate | Hamilton (2018) |

---

## 8. Event Study / Threshold / Tail Analysis

| # | Method | What It Does / When to Use | Relevance to Credit-Spread-to-Equity | Python Package | Complexity | Key Reference |
|---|--------|---------------------------|--------------------------------------|----------------|------------|---------------|
| 48 | **Extreme Value Theory (EVT) — Peaks Over Threshold** | Models the tail distribution of extreme events using Generalized Pareto Distribution | Estimates the probability that spread spikes exceed crisis thresholds and the associated equity tail risk | `pyextremes`, `scipy.stats.genpareto` | Moderate | McNeil & Frey (2000); Coles (2001) |
| 49 | **Kernel Density Estimation (KDE)** | Non-parametric estimation of the probability density function | Identifies the empirical distribution of spread changes; [locates regime boundaries as density modes](https://jakevdp.github.io/PythonDataScienceHandbook/05.13-kernel-density-estimation.html) | `scipy.stats.gaussian_kde`, `scikit-learn.neighbors.KernelDensity` | Straightforward | Silverman (1986) |
| 50 | **Quantile-Based Threshold Rules** | Define signal thresholds at percentiles of the spread distribution | Creates trading signals: "when spreads exceed the 90th percentile, equity returns are predictably negative" | `numpy.percentile`, `pandas.quantile` | Straightforward | — |
| 51 | **Event Study (Abnormal Returns)** | Measures cumulative abnormal returns around identified events | Quantifies equity market reaction around credit-spread-spike events (e.g., +2 sigma widening) | Custom (OLS market model), `eventstudy` | Moderate | MacKinlay (1997) |
| 52 | **Block Maxima / GEV Distribution** | Fits Generalized Extreme Value distribution to period maxima | Models the distribution of worst monthly spread widenings and their equity co-movement | `pyextremes`, `scipy.stats.genextreme` | Moderate | Fisher & Tippett (1928); Gnedenko (1943) |

---

## Summary Statistics

| Category | Count | Complexity Distribution |
|----------|-------|------------------------|
| Correlation & Dependence | 10 | 3 straightforward, 4 moderate, 3 advanced |
| Lead-Lag & Causality | 7 | 1 straightforward, 1 moderate, 5 advanced |
| Regime Identification | 7 | 1 straightforward, 4 moderate, 2 advanced |
| Time-Series Modeling | 6 | 0 straightforward, 3 moderate, 3 advanced |
| Volatility & Risk | 6 | 1 straightforward, 2 moderate, 3 advanced |
| Nonlinear & ML | 5 | 0 straightforward, 3 moderate, 2 advanced |
| Signal Extraction | 6 | 3 straightforward, 2 moderate, 1 advanced |
| Event Study / Tail | 5 | 2 straightforward, 3 moderate, 0 advanced |
| **Total** | **52** | **11 straightforward, 22 moderate, 19 advanced** |

---

## Recommended Prioritization

For maximum analytical value with manageable implementation effort, I would sequence the expansion as follows:

**Phase 1 — Quick wins (straightforward, high value):**
- Spearman/Kendall rank correlations (#1, #2)
- Rolling window correlation (#3)
- HP and CF filters (#42, #44)
- KDE for regime boundaries (#49)
- Quantile-based threshold rules (#50)

**Phase 2 — Core enhancements (moderate, fills major gaps):**
- VECM for cointegration (#25)
- Markov-Switching regression (#18)
- HMM for regime detection (#20)
- GJR-GARCH / EGARCH for asymmetric volatility (#31, #32)
- Change-point detection via `ruptures` (#23)
- Quantile regression (#40)
- Random Forest + SHAP (#37)

**Phase 3 — Advanced methods (high complexity, differentiated insights):**
- DCC-GARCH for time-varying correlation (#33)
- TVP-VAR for evolving transmission (#28)
- Transfer entropy for non-linear causality (#14)
- Wavelet coherence for multi-scale lead-lag (#15)
- Copula models with tail dependence (#5-9)
- EVT for tail risk (#48)

---

### Sources

- [Engle (2002) — Dynamic Conditional Correlation](https://www.researchgate.net/publication/5000337_Dynamic_Conditional_Correlation_-_A_Simple_Class_of_Multivariate_GARCH_Models)
- [Oh & Patton (2013) — Time-Varying Copula for CDS Spreads](https://ideas.repec.org/p/duk/dukeec/13-30.html)
- [Credit Spreads, Leverage and Volatility: A Cointegration Approach](https://mdpi.com/2079-3197/10/9/155/htm)
- [Effective Transfer Entropy in Credit Markets](https://link.springer.com/article/10.1007/s10260-021-00614-1)
- [Transfer Entropy for Financial Applications (Open Quant Live Book)](https://bookdown.org/souzatharsis/open-quant-live-book/how-to-measure-statistical-causality-a-transfer-entropy-approach-with-financial-applications.html)
- [Ang & Bekaert (2002) — Regime Changes and Financial Markets (NBER)](https://www.nber.org/system/files/working_papers/w17182/w17182.pdf)
- [QuantStart — HMM for Market Regime Detection](https://www.quantstart.com/articles/market-regime-detection-using-hidden-markov-models-in-qstrader/)
- [Predicting Equity Returns with TVP-VAR](https://www.sciencedirect.com/science/article/abs/pii/S1057521918307555)
- [FAVAR — Bernanke, Boivin & Eliasz](https://hoagiet.github.io/portfolio/portfolio-6/)
- [GARCH vs GJR-GARCH in Python](https://blog.quantinsti.com/garch-gjr-garch-volatility-forecasting-python/)
- [arch package — Volatility Modeling](https://arch.readthedocs.io/en/latest/univariate/univariate_volatility_modeling.html)
- [StochVolModels — Python SV implementation](https://github.com/ArturSepp/StochVolModels)
- [Credit Spread Approximation with Random Forest](https://www.researchgate.net/publication/352394963_Credit_spread_approximation_and_improvement_using_random_forest_regression)
- [XGBoost + SHAP for Sovereign Risk Determinants](https://www.sciencedirect.com/science/article/abs/pii/S1544612323006451)
- [Quantile Regression Forests — scikit-garden](https://scikit-garden.github.io/examples/QuantileRegressionForests/)
- [statsmodels — HP Filter](https://www.statsmodels.org/stable/generated/statsmodels.tsa.filters.hp_filter.hpfilter.html)
- [statsmodels — CF Filter](https://www.statsmodels.org/dev/generated/statsmodels.tsa.filters.cf_filter.cffilter.html)
- [statsmodels — BK Filter](https://www.statsmodels.org/stable/generated/statsmodels.tsa.filters.bk_filter.bkfilter.html)
- [ruptures — Change Point Detection](https://centre-borelli.github.io/ruptures-docs/)
- [PELT for Financial Time Series](https://dl.acm.org/doi/10.1145/3773365.3773532)
- [Wavelet Data Denoising for Finance](https://abouttrading.substack.com/p/financial-signal-processing-in-python-dd0)
- [Copula Tail Dependence](https://freakonometrics.hypotheses.org/2435)
- [pycop — Python Copula Package](https://pypi.org/project/pycop/)
- [copul — Python Copula Analysis](https://pypi.org/project/copul/)
- [KDE in Python Data Science Handbook](https://jakevdp.github.io/PythonDataScienceHandbook/05.13-kernel-density-estimation.html)
- [Embrechts et al. — Dependence Modeling with Copulas](https://people.math.ethz.ch/~embrecht/ftp/copchapter.pdf)
- [statsmodels — VECM](https://www.statsmodels.org/dev/generated/statsmodels.tsa.vector_ar.vecm.VECM.html)
- [statsmodels — VAR/SVAR](https://www.statsmodels.org/stable/vector_ar.html)

---
*Generated: 2026-02-28 | Source: Web research across academic papers, econometrics textbooks, and quant finance literature*
*Status: Reference catalog — methods selected per analysis based on data structure and research question*
