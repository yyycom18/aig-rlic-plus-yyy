# Threshold and Regime Identification Methods Catalog

**Purpose:** Candidate methods for replacing fixed, ad-hoc thresholds (4%, 5%, 6%, 8% spread levels; Z-score > 3.0) with data-driven, robust, and adaptive approaches for credit-spread-based equity market signals.

**Date:** 2026-02-28

---

## Summary Statistics

- **Total methods cataloged:** 38
- **Categories:** 6 major + 1 robustness/meta category
- **Complexity distribution:** 12 Straightforward, 14 Moderate, 12 Advanced
- **Recommended starting points:** Rolling Percentile, Bollinger Band on Spread, Gaussian Mixture Model, Markov-Switching, CUSUM, Bai-Perron

---

## 1. Statistical Threshold Methods

These are non-parametric or semi-parametric approaches that derive thresholds directly from the empirical distribution of historical spread data.

| # | Method | What It Does | Advantage Over Fixed Thresholds | Python Package | Complexity | Key Reference |
|---|--------|-------------|--------------------------------|----------------|------------|---------------|
| 1 | **Percentile-Based Thresholds** | Sets threshold at a fixed quantile (e.g., 90th, 95th, 99th percentile) of the historical spread distribution. | Adapts to the data's own scale; no arbitrary level. | `numpy.percentile`, `pandas.quantile` | Straightforward | Hyndman & Fan (1996), "Sample Quantiles in Statistical Packages" |
| 2 | **Z-Score with Adaptive Lookback** | Computes (spread - rolling_mean) / rolling_std with a variable lookback window (e.g., 63d, 126d, 252d). Window can expand in calm periods and shrink in volatile ones. | Normalizes for time-varying volatility; regime-aware scaling. | `pandas.rolling`, `scipy.stats.zscore` | Straightforward | Bollerslev (1986); standard practice in stat-arb |
| 3 | **Bollinger Band on Spread** | Places upper/lower bands at mean +/- k*std of the spread using a rolling window. Signal fires when spread breaches the band. | Captures local volatility structure; visual and intuitive. | `pandas.rolling.mean`, `pandas.rolling.std`; [`arbitragelab`](https://hudson-and-thames-arbitragelab.readthedocs-hosted.com/en/latest/trading/z_score.html) | Straightforward | Bollinger (2001), *Bollinger on Bollinger Bands* |
| 4 | **Extreme Value Theory (EVT) -- Peaks Over Threshold** | Fits a Generalized Pareto Distribution to exceedances above a high threshold. Provides statistically principled tail quantiles. | Rigorous tail modeling; gives confidence intervals on extreme thresholds. | `scipy.stats.genpareto`, [`thresholdmodeling`](https://pypi.org/project/thresholdmodeling/) | Moderate | Balkema & de Haan (1974); Pickands (1975); McNeil, Frey & Embrechts (2005), *Quantitative Risk Management* |
| 5 | **Kernel Density Estimation (KDE)** | Estimates the continuous PDF of spread values. Local minima in the density identify natural "gaps" that serve as breakpoints between regimes. | Discovers natural clusters in the data without imposing structure. | `scipy.stats.gaussian_kde`, `sklearn.neighbors.KernelDensity` | Moderate | Silverman (1986), *Density Estimation for Statistics and Data Analysis* |
| 6 | **Otsu's Method** | Minimizes intra-class variance (equivalently, maximizes inter-class variance) to find a single threshold that best separates spread values into two groups. | Optimal binary threshold -- no parameter choice beyond "2 classes." | `skimage.filters.threshold_otsu`, `cv2.threshold` (with custom wrapper for 1D data) | Straightforward | Otsu (1979), "A Threshold Selection Method from Gray-Level Histograms" |
| 7 | **Jenks Natural Breaks** | Minimizes within-class variance across k classes using dynamic programming. Generalizes Otsu to k > 2. | Identifies multiple natural regime boundaries simultaneously. | [`jenkspy`](https://github.com/mthh/jenkspy) | Straightforward | Jenks (1967); Fisher (1958) -- Fisher-Jenks algorithm |
| 8 | **Automated EVT Threshold Selection** | Uses goodness-of-fit tests (Cramer-von Mises, Anderson-Darling) to automatically select the threshold above which the GPD fit is adequate. | Removes subjective threshold choice in EVT, fully data-driven. | [`threshr`](https://cran.r-project.org/web/packages/threshr/) (R); custom Python via `scipy.optimize` | Advanced | Northrop, Attalides & Jonathan (2017); Sakthivel & Nandhini (2025) |

---

## 2. Regime-Switching Models

These models explicitly specify that the data-generating process shifts between discrete states (regimes), each with its own parameters.

| # | Method | What It Does | Advantage Over Fixed Thresholds | Python Package | Complexity | Key Reference |
|---|--------|-------------|--------------------------------|----------------|------------|---------------|
| 9 | **Hamilton Markov-Switching Model** | Assumes the time series follows different AR processes in different regimes, with transition probabilities governed by a Markov chain. EM algorithm estimates regime probabilities. | Endogenous regime dating; probabilistic regime assignments; well-established theory. | [`statsmodels.tsa.regime_switching.markov_regression`](https://www.statsmodels.org/stable/markov_regression.html) | Moderate | Hamilton (1989), "A New Approach to the Economic Analysis of Nonstationary Time Series" |
| 10 | **Hidden Markov Model (HMM)** | Generalization where observed spread is emitted from hidden states. More flexible emission distributions (Gaussian, mixture). | Handles non-linear emission distributions; unsupervised regime discovery. | [`hmmlearn`](https://hmmlearn.readthedocs.io/) | Moderate | Rabiner (1989); Bulla (2011), "HMMs in Finance" |
| 11 | **Gaussian Mixture HMM** | Combines GMM emission distributions with HMM state dynamics. Each regime can have multi-modal spread distributions. | Captures within-regime heterogeneity that single-Gaussian HMM misses. | `hmmlearn.GMMHMM` | Advanced | Aigner (2023), ["A Gaussian Mixture HMM for the VIX"](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4389763) |
| 12 | **Threshold Autoregression (TAR)** | AR model where coefficients change when the threshold variable crosses a critical value. Threshold is estimated from data. | Explicit, interpretable regime boundary; directly estimates the spread level that triggers regime change. | `statsmodels` (SETAR module, [Chad Fulton implementation](http://www.chadfulton.com/topics/setar_model_functionality.html)) | Moderate | Tong (1983), *Threshold Models in Non-linear Time Series Analysis* |
| 13 | **Self-Exciting TAR (SETAR)** | TAR where the threshold variable is the series itself (i.e., lagged spread). Delay parameter selects which lag triggers switching. | Self-contained: no external trigger variable needed. | `statsmodels` SETAR; custom via `scipy.optimize` | Moderate | Tong & Lim (1980); Hansen (1997) |
| 14 | **Logistic STAR (LSTAR)** | Smooth transition between regimes using a logistic function. Transition speed parameter c controls how abruptly regimes change. | Avoids the discontinuity of TAR; smooth, realistic transition. | Custom implementation via `scipy.optimize`; R: `tsDyn` | Advanced | Terasvirta (1994), "Specification, Estimation, and Evaluation of STAR Models" |
| 15 | **Exponential STAR (ESTAR)** | Smooth transition using exponential function. Symmetric transition: deviations in either direction from a central value trigger the switch. | Better suited when spread extremes in both directions matter. | Custom implementation via `scipy.optimize` | Advanced | Terasvirta (1994); Granger & Terasvirta (1993) |
| 16 | **Gaussian Mixture Model (GMM)** | Fits k Gaussian components to spread data. Each component represents a regime. BIC/AIC selects k. Posterior probabilities give soft regime labels. | Fully data-driven regime count and boundaries; probabilistic assignments; trivial to implement. | `sklearn.mixture.GaussianMixture` | Straightforward | McLachlan & Peel (2000); [Two Sigma (2020)](https://www.twosigma.com/articles/a-machine-learning-approach-to-regime-modeling/) |
| 17 | **Bayesian Change-Point Detection** | Places a prior on change-point locations and estimates posterior probability of a regime change at each time step. | Principled uncertainty quantification; no pre-specified number of breaks. | [`bayesian_changepoint_detection`](https://github.com/hildensia/bayesian_changepoint_detection), [`Rbeast`](https://pypi.org/project/Rbeast/) | Moderate | Adams & MacKay (2007), ["Bayesian Online Changepoint Detection"](https://arxiv.org/abs/0710.3742) |

---

## 3. Adaptive / Dynamic Thresholds

These methods produce time-varying thresholds that evolve with market conditions.

| # | Method | What It Does | Advantage Over Fixed Thresholds | Python Package | Complexity | Key Reference |
|---|--------|-------------|--------------------------------|----------------|------------|---------------|
| 18 | **Rolling Percentile Threshold** | Computes the p-th percentile over a trailing window (e.g., 90th percentile of last 2 years). Threshold updates daily. | Automatically adjusts to secular drift in spread levels. | `pandas.core.window.rolling.Rolling.quantile` | Straightforward | Standard practice; no single paper |
| 19 | **Expanding Window Threshold** | Computes the p-th percentile using all available history up to time t. Becomes increasingly stable over time. | Uses maximum information; naturally conservative as history grows. | `pandas.expanding().quantile()` | Straightforward | Standard practice |
| 20 | **Exponentially Weighted Threshold** | Applies exponential decay to historical observations, giving recent data more weight. Threshold = EWMA + k * EW-std. | Reacts faster to regime shifts than equal-weighted rolling windows. | `pandas.DataFrame.ewm` | Straightforward | Hunter (1986); pandas EWMA documentation |
| 21 | **CUSUM (Cumulative Sum)** | Accumulates deviations from a target mean. Signals a change when the cumulative sum exceeds a control limit. | Classic quality-control tool; detects persistent shifts quickly; tunable sensitivity. | [`kats.detectors.cusum_detection`](https://github.com/facebookresearch/Kats) (Meta), `ruptures` | Straightforward | Page (1954), "Continuous Inspection Schemes" |
| 22 | **Bai-Perron Multiple Structural Breaks** | Tests for and estimates the dates and number of structural breaks in a regression relationship. Uses dynamic programming for global optimality. | Identifies multiple regime shifts simultaneously with formal statistical tests; provides confidence intervals on break dates. | [`ruptures`](https://github.com/deepcharles/ruptures) (via Pelt/Dynp), custom via `scipy`; Stata: `xtbreak` | Advanced | Bai & Perron (1998, 2003), "Estimating and Testing Linear Models with Multiple Structural Changes" |
| 23 | **PELT (Pruned Exact Linear Time)** | Exact change-point detection with O(n) complexity via pruning. Minimizes a penalized cost function over possible segmentations. | Fast exact solution; scalable to very long time series. | [`ruptures.Pelt`](https://centre-borelli.github.io/ruptures-docs/user-guide/detection/pelt/) | Moderate | Killick, Fearnhead & Eckley (2012), "Optimal Detection of Changepoints with a Linear Computational Cost" |
| 24 | **Online Change-Point Detection (BOCPD)** | Bayesian online algorithm that computes run-length probabilities in real time. Signals regime change when posterior shifts. | True real-time detection; no look-ahead bias; ideal for live trading. | [`bayesian_changepoint_detection`](https://github.com/hildensia/bayesian_changepoint_detection), [`changefinder`](https://pypi.org/project/changefinder/) | Advanced | Adams & MacKay (2007) |
| 25 | **Autoregressive Drift Detection (ADDM)** | Monitors for concept drift in an autoregressive model of the spread. Fires when model residuals exceed adaptive bounds. | Detects gradual regime drift, not just abrupt breaks. | Custom implementation; [`river`](https://riverml.xyz/) (online ML library) | Advanced | Baena-Garcia et al. (2006); [QuantInsti ADDM tutorial](https://blog.quantinsti.com/autoregressive-drift-detection-method/) |

---

## 4. Machine Learning Approaches

Data-driven methods that learn regime boundaries from features without explicit parametric assumptions.

| # | Method | What It Does | Advantage Over Fixed Thresholds | Python Package | Complexity | Key Reference |
|---|--------|-------------|--------------------------------|----------------|------------|---------------|
| 26 | **Decision Tree for Regime Boundaries** | Learns split points (thresholds) on spread and other features that best separate regimes defined by forward equity returns. Feature importances reveal which variables matter most. | Discovers non-obvious thresholds; provides interpretable if-then rules. | `sklearn.tree.DecisionTreeClassifier` | Straightforward | Breiman et al. (1984), *Classification and Regression Trees* |
| 27 | **Random Forest Regime Detection** | Ensemble of decision trees; averages over many split points for robust boundary estimation. Variable importance ranks features. | More robust than single tree; reduces overfitting; feature importance ranking. | `sklearn.ensemble.RandomForestClassifier` | Moderate | Breiman (2001); [QuantInsti RF regime detection](https://blog.quantinsti.com/epat-project-machine-learning-market-regime-detection-random-forest-python/) |
| 28 | **K-Means Clustering** | Partitions spread observations (possibly with additional features like volatility, slope) into k clusters. Cluster centers define regime centroids; boundaries fall between them. | Simple, fast; works in multi-dimensional feature space. | `sklearn.cluster.KMeans` | Straightforward | Lloyd (1982); MacQueen (1967) |
| 29 | **DBSCAN Clustering** | Density-based clustering that finds arbitrarily shaped clusters and identifies outliers as noise. Does not require pre-specifying k. | Discovers regimes of arbitrary shape; naturally identifies outlier/crisis observations. | `sklearn.cluster.DBSCAN` | Moderate | Ester et al. (1996), "A Density-Based Algorithm for Discovering Clusters" |
| 30 | **Support Vector Machine (SVM)** | Finds the hyperplane that maximally separates regime classes in feature space. Kernel trick allows non-linear boundaries. | Maximum-margin classifier; strong generalization; works in high-dimensional spaces. | `sklearn.svm.SVC` | Moderate | Cortes & Vapnik (1995); [CFA Institute SVM brief](https://rpc.cfainstitute.org/research/foundation/2025/chapter-3-support-vector-machines) |
| 31 | **LSTM Autoencoder Anomaly Detection** | Trains an LSTM autoencoder on "normal" spread behavior. Reconstruction error spikes indicate anomalous regimes (stress). | Learns complex temporal patterns; no need for labeled regimes; captures non-linear dynamics. | `keras`/`tensorflow`, `pytorch` | Advanced | Malhotra et al. (2016), "LSTM-based Encoder-Decoder for Multi-sensor Anomaly Detection" |
| 32 | **Reinforcement Learning (RL) for Adaptive Thresholds** | Formulates threshold selection as a sequential decision problem. An RL agent learns to adjust thresholds to maximize risk-adjusted returns. | Directly optimizes the economic objective; adapts to changing market structure. | [`stable-baselines3`](https://github.com/DLR-RM/stable-baselines3), `gymnasium` | Advanced | Sutton & Barto (2018); [FinRL library](https://github.com/AI4Finance-Foundation/FinRL) |

---

## 5. Multi-Dimensional Thresholds

Methods that combine spread levels with other market variables to form richer signal conditions.

| # | Method | What It Does | Advantage Over Fixed Thresholds | Python Package | Complexity | Key Reference |
|---|--------|-------------|--------------------------------|----------------|------------|---------------|
| 33 | **Joint Spread Level + Velocity** | Signals require both the spread level AND its rate of change (first difference or slope over n days) to exceed thresholds simultaneously. | Filters out slow, benign spread widening; catches rapid deterioration. | `pandas.diff`, `numpy.gradient` | Straightforward | Standard in technical analysis; see Saunders & Allen (2010), *Credit Risk Management In and Out of the Financial Crisis* |
| 34 | **Spread x VIX Interaction** | Defines a 2D regime map (spread level vs. VIX level). Crisis = both elevated. Uses GMM or decision tree on the joint distribution. | Cross-market confirmation reduces false positives from idiosyncratic spread moves. | `sklearn.mixture.GaussianMixture`, `sklearn.tree.DecisionTreeClassifier` on 2D features | Moderate | Adrian, Boyarchenko & Giannone (2019), "Vulnerable Growth" |
| 35 | **Credit Spread Term Structure** | Uses the slope and curvature of the credit spread term structure (e.g., 2Y-5Y-10Y CDS spreads) as regime indicators. Inversion signals stress. | Captures forward-looking market expectations, not just spot levels. | `numpy.polyfit` for slope/curvature; PCA via `sklearn.decomposition.PCA` | Moderate | Collin-Dufresne, Goldstein & Martin (2001) |
| 36 | **Cross-Market Confirmation** | Requires signals from multiple asset classes (credit spreads, equity vol, rates curve, funding markets) to align before declaring a regime. Weighted voting or scoring system. | Dramatically reduces false signals; captures systemic stress that single-market indicators miss. | Custom scoring; `pandas` for signal aggregation | Moderate | Kritzman et al. (2012), "Regime Shifts: Implications for Dynamic Strategies" |

---

## 6. Robustness and Sensitivity Framework

Meta-methods for evaluating and hardening any threshold/regime approach.

| # | Method | What It Does | Advantage Over Fixed Thresholds | Python Package | Complexity | Key Reference |
|---|--------|-------------|--------------------------------|----------------|------------|---------------|
| 37 | **Threshold Sensitivity Analysis** | Systematically varies the threshold by +/- increments (e.g., +/- 0.25%, 0.5%, 1.0%) and measures the change in strategy performance (Sharpe, drawdown, hit rate). | Identifies cliff effects -- thresholds where small changes cause large performance swings. | `pandas`, `numpy`; custom grid search | Straightforward | Harvey & Liu (2015), "Backtesting"; Lopez de Prado (2018), *Advances in Financial Machine Learning* |
| 38 | **Parameter Stability Over Time** | Re-estimates optimal thresholds on expanding or rolling sub-samples. Plots threshold evolution over time. Tests for stationarity of the optimal parameter. | Reveals whether the "optimal" threshold is stable or drifts, guiding recalibration frequency. | `pandas.rolling.apply`, custom bootstrap | Moderate | Pesaran & Timmermann (2002), "Market Timing and Return Prediction" |
| 39 | **Regime Persistence Analysis** | Measures the average duration of each identified regime. Applies minimum-duration filters (e.g., regime must persist >= 5 days to be actionable). | Prevents whipsaw from short-lived false regimes; aligns signal frequency with trading horizon. | `pandas.groupby` on regime labels; `scipy.stats.expon` for duration modeling | Straightforward | Ang & Bekaert (2002), "Regime Switches in Interest Rates" |
| 40 | **False Signal Filtering / Debounce** | Requires the signal to remain active for n consecutive periods (confirmation window) before acting. Alternatively, requires k-of-n confirmation across indicators. | Directly targets the false positive problem; tunable trade-off between responsiveness and reliability. | `pandas.rolling.min` (for consecutive True), custom logic | Straightforward | Standard in signal processing; Ehlers (2001), *Rocket Science for Traders* |

---

## Implementation Priority Matrix

Based on complexity, expected value-add, and ease of integration with the current analysis:

### Tier 1 -- Implement First (Quick Wins)

| Method | Why | Effort |
|--------|-----|--------|
| Rolling Percentile (#18) | Direct replacement for fixed levels; 3 lines of pandas | 1 hour |
| Bollinger Band on Spread (#3) | Already familiar paradigm; tunable | 1 hour |
| Jenks Natural Breaks (#7) | One-liner via `jenkspy`; discovers k natural levels | 1 hour |
| GMM Regime Classification (#16) | 10 lines of sklearn; immediate probabilistic regimes | 2 hours |
| Threshold Sensitivity Analysis (#37) | Essential validation of any threshold choice | 2 hours |
| False Signal Filtering (#40) | Debounce logic prevents whipsaw | 1 hour |

### Tier 2 -- Implement Next (Moderate Effort, High Value)

| Method | Why | Effort |
|--------|-----|--------|
| Hamilton Markov-Switching (#9) | Gold standard in economics; built into statsmodels | 4 hours |
| HMM (#10) | More flexible than Markov-switching; hmmlearn is mature | 4 hours |
| CUSUM (#21) | Classic; Meta's `kats` makes it trivial | 2 hours |
| Bai-Perron / PELT (#22, #23) | Formal structural break detection; `ruptures` is excellent | 3 hours |
| Joint Spread + Velocity (#33) | Simple multi-dimensional enhancement | 2 hours |
| Spread x VIX Interaction (#34) | Cross-market confirmation | 3 hours |
| Random Forest Boundaries (#27) | Feature importance reveals what drives regimes | 3 hours |

### Tier 3 -- Advanced / Research Phase

| Method | Why | Effort |
|--------|-----|--------|
| EVT Peaks Over Threshold (#4) | Rigorous tail analysis | 1 day |
| SETAR / TAR (#12, #13) | Estimates threshold endogenously | 1 day |
| LSTAR / ESTAR (#14, #15) | Smooth transition dynamics | 2 days |
| Bayesian Online CPD (#24) | Real-time regime detection | 1 day |
| LSTM Autoencoder (#31) | Non-linear anomaly detection | 2 days |
| RL Adaptive Thresholds (#32) | Directly optimizes trading objective | 3+ days |

---

## Key Python Package Summary

| Package | Install | Methods Covered |
|---------|---------|-----------------|
| `pandas` | (standard) | Rolling/expanding/EWM thresholds, signal filtering |
| `numpy`, `scipy` | (standard) | Percentiles, Z-scores, KDE, EVT (GPD fitting) |
| `scikit-learn` | `pip install scikit-learn` | GMM, K-Means, DBSCAN, SVM, Decision Trees, RF, PCA |
| `statsmodels` | `pip install statsmodels` | Markov-switching, SETAR, ARIMA diagnostics |
| `hmmlearn` | `pip install hmmlearn` | HMM, Gaussian Mixture HMM |
| `ruptures` | `pip install ruptures` | PELT, Bai-Perron, kernel CPD, binary segmentation |
| `jenkspy` | `pip install jenkspy` | Jenks natural breaks |
| `arch` | `pip install arch` | GARCH, unit root tests (supporting diagnostics) |
| `kats` | `pip install kats` | CUSUM, Bayesian online CPD |
| `bayesian_changepoint_detection` | `pip install bayesian-changepoint-detection` | Bayesian online/offline CPD |
| `Rbeast` | `pip install Rbeast` | Bayesian change-point + trend decomposition |
| `changefinder` | `pip install changefinder` | Online change-point detection |
| `river` | `pip install river` | Online ML, drift detection |
| `stable-baselines3` | `pip install stable-baselines3` | RL algorithms (PPO, A2C, SAC) |
| `keras`/`tensorflow` | `pip install tensorflow` | LSTM autoencoder |
| `arbitragelab` | `pip install arbitragelab` | Bollinger band spread trading |

---

## Sources

- [Extreme Value Theory and Credit Spreads (ResearchGate)](https://www.researchgate.net/publication/309149906_Extreme_Value_Theory_and_Credit_Spreads_A_Handbook_of_Extreme_Value_Theory_and_its_Applications)
- [Automated Threshold Selection for Univariate Extremes (Technometrics, 2024)](https://www.tandfonline.com/doi/full/10.1080/00401706.2024.2421744)
- [Dual-Phase Threshold Selection (Sakthivel & Nandhini, 2025)](https://journals.sagepub.com/doi/abs/10.1177/1471082X241307286)
- [Hamilton Regime-Switching Models (Palgrave)](https://econweb.ucsd.edu/~jhamilto/palgrav1.pdf)
- [HMM for Market Regime Detection (Medium)](https://datadave1.medium.com/detecting-market-regimes-hidden-markov-model-2462e819c72e)
- [SETAR Model in statsmodels (Chad Fulton)](http://www.chadfulton.com/topics/setar_model_functionality.html)
- [STAR Model (Wikipedia)](https://en.wikipedia.org/wiki/STAR_model)
- [Smooth Transition AR Models (Mastering Python for Finance)](https://www.oreilly.com/library/view/mastering-python-for/9781789346466/2bd115f7-434d-49cc-9367-75f7afc966c9.xhtml)
- [Two Sigma: ML Approach to Regime Modeling](https://www.twosigma.com/articles/a-machine-learning-approach-to-regime-modeling/)
- [GMM Regime Detection (Medium)](https://medium.com/@tballz/regime-detection-and-prediction-in-financial-markets-lesson-2-application-of-gaussian-mixture-5ee6c0199676)
- [Gaussian Mixture HMM for VIX (SSRN)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4389763)
- [Bayesian Online Changepoint Detection (Adams & MacKay, 2007)](https://arxiv.org/abs/0710.3742)
- [ruptures: Change Point Detection in Python](https://github.com/deepcharles/ruptures)
- [bayesian_changepoint_detection (GitHub)](https://github.com/hildensia/bayesian_changepoint_detection)
- [Rbeast: Bayesian Change-Point Detection](https://pypi.org/project/Rbeast/)
- [PELT Algorithm (ruptures docs)](https://centre-borelli.github.io/ruptures-docs/user-guide/detection/pelt/)
- [jenkspy: Jenks Natural Breaks (GitHub)](https://github.com/mthh/jenkspy)
- [Otsu's Method (Wikipedia)](https://en.wikipedia.org/wiki/Otsu%27s_method)
- [Bollinger Bands Z-Score Strategy (ArbitrageLab)](https://hudson-and-thames-arbitragelab.readthedocs-hosted.com/en/latest/trading/z_score.html)
- [RF for Market Regime Detection (QuantInsti)](https://blog.quantinsti.com/epat-project-machine-learning-market-regime-detection-random-forest-python/)
- [HMM + RF Regime-Adaptive Trading (QuantInsti)](https://blog.quantinsti.com/regime-adaptive-trading-python/)
- [DBSCAN for Financial Anomaly Detection](https://wjaets.com/content/anomaly-detection-financial-time-series-data-mapper-algorithm-and-dbscan-clustering)
- [SVM in Asset Management (CFA Institute, 2025)](https://rpc.cfainstitute.org/research/foundation/2025/chapter-3-support-vector-machines)
- [LSTM Autoencoder Anomaly Detection (Curiousily)](https://curiousily.com/posts/anomaly-detection-in-time-series-with-lstms-using-keras-in-python/)
- [Stable Baselines3 (GitHub)](https://github.com/DLR-RM/stable-baselines3)
- [ADDM Drift Detection (QuantInsti)](https://blog.quantinsti.com/autoregressive-drift-detection-method/)
- [Predicting Credit Spreads with ML (arXiv, 2025)](https://arxiv.org/pdf/2509.19042)
- [Clustering Approaches for Financial Data Analysis (arXiv)](https://arxiv.org/pdf/1609.08520)
- [Genetic Algorithm for Multi-Threshold Trading (Springer, 2025)](https://link.springer.com/article/10.1007/s10462-025-11419-z)
- [Multivariate Regime Identification via GMM and Gradient Boosting (Springer)](https://link.springer.com/chapter/10.1007/978-3-032-08462-0_27)
- [pandas Windowing Operations](https://pandas.pydata.org/docs/user_guide/window.html)
- [Structural Break Detection Overview (Towards Data Science)](https://towardsdatascience.com/understanding-time-series-structural-changes-f6a4c44cb13c/)
- [ECB: Predicting Financial Stress with Markov Models](https://www.ecb.europa.eu/pub/pdf/scpwps/ecb.wp2057.en.pdf)

---
*Generated: 2026-02-28 | Source: Web research across academic papers, econometrics literature, and Python documentation*
*Status: Reference catalog — methods selected per analysis based on data characteristics and regime complexity*
