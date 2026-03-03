# Backtesting Approaches & Frameworks Catalog

## Purpose

Candidate approaches for enriching a credit-spread-as-equity-signal trading strategy backtest. The current baseline is in-sample only, return-oriented, long-favoured (long or cash), with no risk-adjusted metrics and no transaction costs. This catalog identifies 50+ approaches across six dimensions.

---

## 1. Return-Oriented Approaches

| # | Approach | What It Does / Question It Answers | Why It Matters for Credit-Spread Strategies | Python Package / Implementation | Complexity | Key Reference |
|---|----------|-------------------------------------|---------------------------------------------|--------------------------------|------------|---------------|
| 1 | **CAGR (Compound Annual Growth Rate)** | Annualizes total return to enable comparison across different holding periods | Normalizes the credit-signal strategy return so it can be compared to buy-and-hold or other signal-based strategies over different sample windows | `quantstats.stats.cagr()`, or manual: `(ending/starting)^(1/years) - 1` | Low | Bacon, *Practical Portfolio Performance* |
| 2 | **Total Return** | Cumulative return over the full sample period | Baseline measure; confirms whether the credit signal adds value versus passive SPY holding | `numpy.prod(1 + returns) - 1` | Low | Any introductory finance text |
| 3 | **Sharpe Ratio** | Excess return per unit of total volatility; answers "is the return compensating for the risk taken?" | Credit-spread signals may reduce volatility by avoiding drawdowns; Sharpe captures this dual benefit (higher return AND lower vol) | `quantstats.stats.sharpe()`, `empyrical.sharpe_ratio()` | Low | Sharpe (1966, 1994) |
| 4 | **Sortino Ratio** | Excess return per unit of downside deviation only | Credit-spread strategies are asymmetric -- they aim to avoid crashes. Sortino rewards this by ignoring upside volatility | `quantstats.stats.sortino()`, `empyrical.sortino_ratio()` | Low | Sortino & van der Meer (1991) |
| 5 | **Calmar Ratio** | CAGR divided by maximum drawdown | Directly measures return efficiency relative to worst-case pain -- critical for strategies that claim to avoid drawdowns | `quantstats.stats.calmar()` | Low | Young (1991) |
| 6 | **Omega Ratio** | Ratio of probability-weighted gains to probability-weighted losses above/below a threshold | Considers the entire return distribution, not just first two moments; captures fat tails and skewness inherent in credit-signal switching | `quantstats.stats.omega()`, or manual integration of gain/loss areas | Medium | Keating & Shadwick (2002) |
| 7 | **Information Ratio** | Active return divided by tracking error vs. benchmark | Measures whether credit-signal timing adds value per unit of deviation from buy-and-hold benchmark | `quantstats.stats.information_ratio()`, `empyrical.information_ratio()` | Low | Grinold & Kahn, *Active Portfolio Management* |
| 8 | **Rolling Sharpe / Rolling Returns** | Sharpe ratio or returns computed over rolling windows (e.g., 1Y, 3Y) | Reveals whether credit-signal alpha is persistent or concentrated in specific crisis episodes; exposes regime dependence | `quantstats.stats.rolling_sharpe()`, pandas `.rolling()` | Medium | Standard practice |
| 9 | **Benchmark-Relative Alpha** | Jensen's alpha: intercept from regressing strategy excess returns on benchmark excess returns | Isolates the pure timing value of the credit signal after controlling for market exposure | `statsmodels` OLS regression, `linearmodels` | Medium | Jensen (1968) |
| 10 | **Beta to Benchmark** | Slope of strategy returns regressed on benchmark returns | Reveals whether the credit signal reduces market exposure during stress (beta < 1 in downturns) | `quantstats.stats.greeks()`, `statsmodels` | Low | Standard CAPM |
| 11 | **Tracking Error** | Standard deviation of active returns (strategy minus benchmark) | Quantifies how different the credit-signal strategy is from passive; high tracking error + low IR = noise, not skill | `empyrical.tracking_error()` | Low | Standard practice |
| 12 | **Modigliani-Modigliani (M2)** | Adjusts strategy return to match benchmark volatility, enabling direct return comparison | Allows apples-to-apples comparison: "if credit-signal strategy had SPY's volatility, what would the return be?" | Manual: `Sharpe * benchmark_vol + rf` | Medium | Modigliani & Modigliani (1997) |

---

## 2. Risk-Oriented Approaches

| # | Approach | What It Does / Question It Answers | Why It Matters for Credit-Spread Strategies | Python Package / Implementation | Complexity | Key Reference |
|---|----------|-------------------------------------|---------------------------------------------|--------------------------------|------------|---------------|
| 13 | **Maximum Drawdown (Depth)** | Largest peak-to-trough decline | The primary claim of credit-signal timing is drawdown avoidance; this is the direct test | `quantstats.stats.max_drawdown()`, `empyrical.max_drawdown()` | Low | Standard practice |
| 14 | **Drawdown Duration** | How long (in days/months) the strategy stays underwater | Long underwater periods destroy investor conviction even if depth is moderate | `quantstats.stats.drawdown_details()` | Low | Standard practice |
| 15 | **Drawdown Recovery Time** | Time from trough back to previous high-water mark | Credit signals should accelerate recovery by re-entering the market early | Manual from drawdown series | Low | Standard practice |
| 16 | **Value-at-Risk (VaR)** | The loss threshold not exceeded with a given probability (e.g., 95% or 99%) over a given horizon | Quantifies daily/weekly tail risk; answers "how bad can a single day/week be?" | `quantstats.stats.value_at_risk()`, `scipy.stats.norm.ppf()`, historical percentile | Medium | Jorion, *Value at Risk* (2006) |
| 17 | **Conditional VaR / Expected Shortfall (CVaR)** | Average loss beyond the VaR threshold | More informative than VaR because it asks "when things go wrong, how bad is the average bad day?" | `quantstats.stats.conditional_value_at_risk()`, `riskfolio-lib` | Medium | Rockafellar & Uryasev (2000) |
| 18 | **Tail Risk Ratio** | Ratio of left-tail returns to right-tail returns at a given percentile | Credit signals should improve tail symmetry by truncating left-tail events | `quantstats.stats.tail_ratio()` | Low | Standard practice |
| 19 | **Downside Deviation** | Standard deviation of returns below a target (usually 0 or rf) | Denominator of Sortino; isolates "bad" volatility that credit signals aim to eliminate | `quantstats.stats.downside_deviation()` | Low | Sortino & van der Meer (1991) |
| 20 | **Ulcer Index** | Root mean square of percentage drawdowns over the period | Weights deeper drawdowns more heavily; sensitive to sustained pain, which is what investors actually feel | `quantstats.stats.ulcer_index()` | Low | Martin & McCann (1989) |
| 21 | **Ulcer Performance Index (UPI)** | Excess return divided by Ulcer Index | Risk-adjusted return using drawdown-based risk; more intuitive than Sharpe for drawdown-avoidance strategies | `quantstats.stats.ulcer_performance_index()` | Low | Martin & McCann (1989) |
| 22 | **Historical Stress Testing (GFC)** | Replay strategy through Aug 2007 -- Mar 2009 period | The acid test: did the credit signal fire early enough to avoid the worst of the financial crisis? | Subset returns to crisis window, compute metrics | Medium | Standard institutional practice |
| 23 | **Historical Stress Testing (COVID)** | Replay strategy through Feb -- Mar 2020 | Tests speed of signal: COVID crash was fast (34 days peak to trough); did credit spreads lead equities? | Same as above | Medium | Standard institutional practice |
| 24 | **Historical Stress Testing (Taper Tantrum)** | Replay strategy through May -- Sep 2013 | Tests false-positive rate: credit spreads widened but equities recovered; did signal whipsaw? | Same as above | Medium | Standard institutional practice |
| 25 | **Historical Stress Testing (2022 Rate Shock)** | Replay through Jan -- Oct 2022 | Tests performance during a rates-driven rather than credit-driven selloff | Same as above | Medium | Standard institutional practice |
| 26 | **Monte Carlo Simulation** | Generates thousands of synthetic return paths by reshuffling or bootstrapping actual returns | Answers "how likely is this drawdown by chance?" and "what is the distribution of possible outcomes?" | `numpy.random`, custom bootstrap loops, `arch` for parametric simulation | High | Glasserman, *Monte Carlo Methods in Financial Engineering* (2003) |
| 27 | **Conditional Drawdown at Risk (CDaR)** | Average of the worst X% of drawdown episodes | Goes beyond max drawdown to characterize the typical "bad stretch," not just the worst one | `riskfolio-lib`, custom implementation | Medium | Chekhlov, Uryasev & Zabarankin (2005) |

---

## 3. Long-Favoured Strategy Variants

| # | Approach | What It Does / Question It Answers | Why It Matters for Credit-Spread Strategies | Python Package / Implementation | Complexity | Key Reference |
|---|----------|-------------------------------------|---------------------------------------------|--------------------------------|------------|---------------|
| 28 | **Long / Cash (Baseline)** | Binary: 100% SPY when signal is favorable, 100% cash (T-bills) otherwise | Current baseline; simple but wastes information about signal strength | Current implementation | Low | N/A |
| 29 | **Signal-Strength Position Sizing** | Continuous: allocate % to SPY proportional to signal confidence (e.g., z-score of spread deviation) | Exploits the full information content of credit spreads instead of binary thresholding | Manual: `weight = f(z_score)`, vectorized with numpy | Medium | Grinold & Kahn, *Active Portfolio Management* |
| 30 | **Volatility-Targeted Long** | Scale position size inversely to realized or implied volatility to target constant portfolio vol (e.g., 10% annualized) | Prevents position sizing from inadvertently being large during high-vol regimes when credit signals are also firing | `arch` for vol forecasting, then `target_vol / realized_vol` scaling | Medium | Moreira & Muir (2017), "Volatility-Managed Portfolios" |
| 31 | **Drawdown Control Overlay** | Reduce exposure when current drawdown exceeds a threshold (e.g., halve at -5%, exit at -10%) | Provides a hard risk floor independent of the credit signal, acting as a circuit breaker | Manual: track running drawdown, adjust weights | Medium | Grossman & Zhou (1993) |
| 32 | **Dollar-Cost Averaging with Signal Acceleration** | Regular fixed investment into SPY, with additional lump-sum deployment when credit signal is strongly favorable | Combines the behavioral discipline of DCA with opportunistic signal-based overweighting | Manual loop with conditional sizing, `pandas` | Medium | Various DCA backtests (see Medium articles) |
| 33 | **Kelly Criterion Sizing** | Optimal position size based on estimated edge and variance: `f* = (mu - rf) / sigma^2` | Theoretically optimal growth; useful as an upper bound for how much to bet on the credit signal | Manual: estimate mu and sigma from rolling window | Medium | Kelly (1956); Thorp (2006) |
| 34 | **Risk-Parity Weighting** | Allocate so each "state" (risk-on vs. risk-off) contributes equally to portfolio risk | Balances the risk contribution across regimes rather than letting one regime dominate | `riskfolio-lib`, `scipy.optimize` | High | Qian (2005) |

---

## 4. Short-Favoured / Hedging Strategies

| # | Approach | What It Does / Question It Answers | Why It Matters for Credit-Spread Strategies | Python Package / Implementation | Complexity | Key Reference |
|---|----------|-------------------------------------|---------------------------------------------|--------------------------------|------------|---------------|
| 35 | **Long / Short Switching** | Long SPY when signal favorable, short SPY when unfavorable | Tests the full symmetric value of the signal -- can credit spreads predict both rallies and declines? | Simple sign-flip on returns; vectorized | Low | Standard practice |
| 36 | **Short Overlay During Stress** | Maintain long position but add short ETF exposure (e.g., SH, SPXU) when credit stress exceeds threshold | Partial hedge instead of full exit; preserves some upside while reducing downside | Manual: add short leg when signal crosses upper threshold | Medium | Standard practice |
| 37 | **Put Protection with Signal Timing** | Buy SPX puts when credit signal indicates stress, let them expire otherwise | Tests whether credit signals can time protective put purchases better than fixed-calendar approaches | `numpy` for payoff calculations; options pricing via `py_vollib` or `QuantLib` | High | Hull, *Options, Futures, and Other Derivatives* |
| 38 | **Pairs: Long SPY / Short HYG** | Long equity, short high-yield bond ETF when credit-equity divergence detected | Exploits the credit-equity relationship directly; isolates the informational content of spread movements | Compute spread between SPY and HYG returns, trade on z-score | Medium | Gatev, Goetzmann & Rouwenhorst (2006) |
| 39 | **Pairs: Long HYG / Short SPY** | Inverse of above -- bet on credit when equity overreacts to stress | Tests whether credit market pricing is more accurate than equity pricing during dislocations | Same framework, reversed direction | Medium | Standard pairs trading |
| 40 | **Tail Hedging with VIX Derivatives** | Buy VIX calls or UVXY when credit signal indicates approaching tail event | Credit spreads may lead VIX by days or weeks; tests whether this lead time is exploitable for cheap tail hedges | VIX futures term structure data, `numpy` for payoff simulation | High | Bhansali (2014), *Tail Risk Hedging* |
| 41 | **Dynamic Hedge Ratio** | Continuously adjust hedge ratio between equity and credit instruments based on rolling correlation/beta | Accounts for time-varying relationship between credit spreads and equity returns | `statsmodels` rolling OLS, `arch` DCC-GARCH | High | Engle (2002), DCC-GARCH |

---

## 5. Validation Frameworks

| # | Approach | What It Does / Question It Answers | Why It Matters for Credit-Spread Strategies | Python Package / Implementation | Complexity | Key Reference |
|---|----------|-------------------------------------|---------------------------------------------|--------------------------------|------------|---------------|
| 42 | **Walk-Forward Optimization (WFO)** | Train on rolling in-sample window, test on subsequent out-of-sample window, roll forward | Answers "does the optimal credit-spread threshold remain stable, or does it shift across regimes?" | `sklearn.model_selection.TimeSeriesSplit`, manual loop | Medium | Pardo, *The Evaluation and Optimization of Trading Strategies* (2008) |
| 43 | **Expanding Window Validation** | Same as WFO but in-sample window grows (never drops old data) | More appropriate when the full history is informative (structural credit relationships persist over decades) | `pandas` expanding window loop | Medium | Standard time-series practice |
| 44 | **Rolling Window Validation** | Fixed-size in-sample window rolls forward, dropping oldest data | Appropriate if credit-equity relationship evolves and old data becomes less relevant | Same as WFO | Medium | Standard time-series practice |
| 45 | **K-Fold Time-Series CV** | Partition data into K sequential folds; train on earlier folds, test on later | Provides K estimates of out-of-sample performance; reduces variance of performance estimates | `sklearn.model_selection.TimeSeriesSplit(n_splits=K)` | Medium | Arlot & Celisse (2010) |
| 46 | **Combinatorial Purged Cross-Validation (CPCV)** | Generates all possible train/test combinations with purging (remove leaking observations) and embargo (add buffer) | Gold standard for preventing overfitting in financial ML; generates a distribution of OOS Sharpe ratios, not a point estimate | `mlfinlab` (Hudson & Thames), or manual implementation per de Prado | High | Lopez de Prado, *Advances in Financial Machine Learning* (2018) |
| 47 | **In-Sample vs. Out-of-Sample Comparison** | Split data at a fixed date; compare IS and OOS metrics | Simplest validity check: if OOS Sharpe is >50% below IS Sharpe, the strategy is likely overfit | Manual split, compute same metrics on both halves | Low | Standard practice |
| 48 | **Bootstrap Resampling for Significance** | Resample returns with replacement (or shuffle trades) to build null distribution of performance metrics | Answers "could this Sharpe ratio arise by chance?" -- critical for a single-signal strategy | `numpy.random.choice`, custom loop, 10,000+ iterations | Medium | Efron & Tibshirani (1993) |
| 49 | **White's Reality Check** | Tests whether the best strategy from a set of candidates is significantly better than a benchmark, correcting for data snooping | If multiple credit-spread thresholds or lookback windows were tested, WRC controls the familywise error rate | Custom implementation following White (2000); `arch` package has bootstrap tools | High | White (2000), Econometrica |
| 50 | **Hansen's SPA Test** | Improved version of White's RC; less conservative, more powerful against poor alternatives | More appropriate when the strategy universe includes many weak variants alongside the best credit-signal specification | Custom implementation following Hansen (2005) | High | Hansen (2005), "A Test for Superior Predictive Ability" |
| 51 | **Deflated Sharpe Ratio (DSR)** | Adjusts the Sharpe ratio for the number of trials, skewness, and kurtosis | Directly answers "is this Sharpe ratio statistically significant given how many variations I tested?" | Manual: formula from Bailey & Lopez de Prado (2014) | Medium | Bailey & Lopez de Prado (2014) |
| 52 | **Probability of Backtest Overfitting (PBO)** | Estimates the probability that the IS-optimal strategy will underperform OOS using CPCV | Provides a single number (0 to 1) summarizing overfitting risk -- essential reporting metric | `mlfinlab`, or manual CPCV-based computation | High | Bailey et al. (2017) |

---

## 6. Practical Considerations

| # | Approach | What It Does / Question It Answers | Why It Matters for Credit-Spread Strategies | Python Package / Implementation | Complexity | Key Reference |
|---|----------|-------------------------------------|---------------------------------------------|--------------------------------|------------|---------------|
| 53 | **Transaction Cost Modeling (Flat)** | Applies fixed cost per trade (e.g., 5 bps round-trip for SPY) | Baseline realism check; even low-frequency credit-signal strategies incur costs when switching | Subtract cost from returns at each trade; `vectorbt` supports `fees` parameter | Low | Standard practice |
| 54 | **Transaction Cost Modeling (Nonlinear / Market Impact)** | Models cost as increasing function of trade size and decreasing function of liquidity | Relevant if the strategy is deployed at scale: large SPY trades are fine, but HYG or VIX products have thinner books | Square-root market impact model: `cost = sigma * sqrt(Q/V)` | Medium | Almgren & Chriss (2001) |
| 55 | **Slippage Modeling** | Simulates execution at worse-than-mid prices due to bid-ask spread and latency | Credit-signal trades are typically end-of-day, so slippage is modest but nonzero; important for honest reporting | Add half-spread to each trade; `backtrader` has `SlippagePercentage` | Low | Standard practice |
| 56 | **Regime Duration Analysis** | Measures how long the strategy stays in each state (long vs. cash) and the distribution of holding periods | Answers "is this strategy practical?" -- 50 trades/year is very different from 2 trades/year for tax and cost implications | `pandas` groupby on signal changes, compute duration statistics | Low | Standard practice |
| 57 | **Signal Frequency & Turnover** | Counts number of signal transitions per year and the implied portfolio turnover | High turnover erodes returns through costs and taxes; credit signals should be low-frequency by nature (credit cycles are slow) | Count sign changes in signal series; annualize | Low | Standard practice |
| 58 | **Capacity Analysis** | Estimates how much AUM the strategy can absorb before market impact degrades returns | Important if publishing as a fund strategy: SPY is highly liquid, but HYG or credit derivative instruments are not | Model impact as function of AUM, average daily volume, and spread | Medium | Standard institutional practice |
| 59 | **Tax Efficiency Analysis** | Compares pre-tax and after-tax returns; analyzes short-term vs. long-term capital gains distribution | Credit-signal strategies with frequent switching generate short-term gains taxed at higher rates | Track holding periods per trade, apply tax rates | Medium | Standard practice |
| 60 | **Breakeven Analysis** | Determines the maximum transaction cost / minimum Sharpe degradation at which the strategy still outperforms passive | Answers "how robust is the credit-signal edge to real-world frictions?" -- if edge disappears at 10 bps, the strategy is fragile | Sweep cost parameter from 0 to X bps, find crossover | Low | Standard practice |
| 61 | **Execution Timing Sensitivity** | Tests whether using close vs. open vs. next-day prices materially changes results | Credit data is typically published with a lag; answers "can I actually trade on this signal in real time?" | Re-run backtest with different price assumptions (close, next open, T+1 close) | Low | Standard practice |
| 62 | **Signal Decay Analysis** | Measures how strategy performance degrades as execution is delayed by 1, 2, ... N days | If the credit signal decays quickly, real-world implementation may not capture the backtested returns | Loop over lag values, plot Sharpe vs. lag | Medium | Standard practice |

---

## Summary Statistics

| Category | Count | Complexity Distribution |
|----------|-------|------------------------|
| Return-Oriented | 12 | 8 Low, 3 Medium, 1 High |
| Risk-Oriented | 15 | 6 Low, 7 Medium, 2 High |
| Long-Favoured Variants | 7 | 1 Low, 5 Medium, 1 High |
| Short / Hedging | 7 | 1 Low, 2 Medium, 4 High |
| Validation Frameworks | 11 | 1 Low, 5 Medium, 5 High |
| Practical Considerations | 10 | 6 Low, 3 Medium, 1 High |
| **Total** | **62** | **23 Low, 25 Medium, 14 High** |

---

## Recommended Implementation Priority

### Phase 1: Quick wins (Low complexity, high impact)
1. Full metrics suite: Sharpe, Sortino, Calmar, max drawdown, CAGR (#1-5, #13-15)
2. In-sample vs. out-of-sample split (#47)
3. Transaction cost modeling (flat) (#53)
4. Regime duration and turnover analysis (#56-57)
5. Long/short switching (#35)

### Phase 2: Core risk analytics (Medium complexity)
6. VaR and CVaR (#16-17)
7. Rolling performance windows (#8)
8. Historical stress tests -- GFC, COVID, Taper Tantrum, 2022 (#22-25)
9. Walk-forward optimization (#42)
10. Signal-strength position sizing (#29)
11. Volatility targeting (#30)
12. Bootstrap significance testing (#48)

### Phase 3: Advanced validation (High complexity)
13. Monte Carlo simulation (#26)
14. Combinatorial purged cross-validation (#46)
15. Deflated Sharpe ratio and PBO (#51-52)
16. White's Reality Check / Hansen's SPA (#49-50)
17. Kelly criterion sizing (#33)

### Phase 4: Alternative strategies (Medium-High complexity)
18. Put protection with signal timing (#37)
19. Pairs trading: SPY/HYG (#38-39)
20. Tail hedging with VIX derivatives (#40)
21. Dynamic hedge ratio (#41)

---

## Key Python Libraries Summary

| Library | Primary Use | Install |
|---------|------------|---------|
| `quantstats` | Comprehensive metrics & tearsheets (Sharpe, Sortino, Calmar, VaR, CVaR, Omega, Ulcer, drawdown) | `pip install quantstats` |
| `empyrical` | Core financial metrics (used by pyfolio/zipline) | `pip install empyrical` |
| `vectorbt` | High-performance vectorized backtesting with fees, slippage | `pip install vectorbt` |
| `backtrader` | Event-driven backtesting with analyzers for drawdown, Sharpe, etc. | `pip install backtrader` |
| `riskfolio-lib` | Portfolio optimization, CDaR, CVaR, 24 risk measures | `pip install riskfolio-lib` |
| `pyfolio` | Tear-sheet generation, performance attribution | `pip install pyfolio` |
| `arch` | GARCH volatility, unit root tests, bootstrap tools | `pip install arch` |
| `statsmodels` | Regression, rolling OLS, time-series econometrics | `pip install statsmodels` |
| `mlfinlab` | CPCV, de Prado methods, financial ML tools (Hudson & Thames) | Commercial license |
| `scipy` | Statistical tests, optimization, distributions | `pip install scipy` |
| `sklearn` | TimeSeriesSplit, cross-validation infrastructure | `pip install scikit-learn` |
| `py_vollib` | Options pricing (Black-Scholes, Greeks) for put/hedge strategies | `pip install py_vollib` |

---

## Sources

- [Advanced Trading Metrics: Sharpe, Sortino, Calmar, SQN & K-Ratio](https://algostrategyanalyzer.com/en/blog/advanced-trading-metrics/)
- [QuantStats GitHub](https://github.com/ranaroussi/quantstats)
- [VectorBT Backtesting Skills](https://github.com/marketcalls/vectorbt-backtesting-skills)
- [Backtrader Analyzers Reference](https://www.backtrader.com/docu/analyzers-reference/)
- [Combinatorial Purged Cross-Validation](https://towardsai.net/p/l/the-combinatorial-purged-cross-validation-method)
- [Walk-Forward Optimization](https://blog.quantinsti.com/walk-forward-optimization-introduction/)
- [Cross Validation in Finance: Purging, Embargoing, Combinatorial](https://blog.quantinsti.com/cross-validation-embargo-purging-combinatorial/)
- [White (2000), "A Reality Check for Data Snooping"](https://www.econometricsociety.org/publications/econometrica/2000/09/01/reality-check-data-snooping)
- [Hansen (2005), SPA Test via Hsu & Kuan](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=685361)
- [Monte Carlo Simulation for Trading](https://www.quantifiedstrategies.com/how-to-do-a-monte-carlo-simulation-using-python/)
- [Backtesting Multi-Asset Portfolios: CDaR with Riskfolio-Lib & VectorBT](https://www.pyquantnews.com/free-python-resources/backtesting-multi-asset-portfolios-for-true-resilience-cdar-optimization-with-riskfolio-lib-vectorbt)
- [Transaction Costs in Backtesting (Hudson & Thames)](https://github.com/hudson-and-thames/backtest_tutorial/blob/main/Intro_Transaction_Costs.ipynb)
- [Slippage: Nonlinear Modeling](https://quantjourney.substack.com/p/slippage-a-comprehensive-analysis)
- [Riskfolio-Lib](https://github.com/dcajasn/Riskfolio-Lib)
- [Pyfolio](https://github.com/quantopian/pyfolio)
- [VIX Tail Risk Hedging (Stanford)](http://stanford.edu/class/msande448/2021/Final_reports/gr7.pdf)
- [Hedging HY Bonds with Credit VIX](https://www.sciencedirect.com/science/article/abs/pii/S0165176524001137)
- [Stress Testing Financial Portfolios (Python)](https://thepythonlab.medium.com/building-a-python-framework-for-stress-testing-financial-portfolios-38d013f2af41)
- [Dollar Cost Averaging Backtesting](https://medium.com/@mburakbedir/dollar-cost-averaging-dca-strategy-and-backtesting-with-python-b19570c2299d)
- [Expanding vs Rolling Window Forecasting](https://medium.com/@philippetousignant/forecasting-with-python-expanding-and-rolling-window-fa0be5545940)
- [QuantStart: Backtesting Considerations](https://www.quantstart.com/articles/backtesting-systematic-trading-strategies-in-python-considerations-and-open-source-frameworks/)
- [Backtesting.py](https://kernc.github.io/backtesting.py/)
- [Volatility Trading Strategies (Quantified Strategies)](https://www.quantifiedstrategies.com/volatility-trading-strategies/)
- [Position Sizing Methods](https://www.luxalgo.com/blog/5-position-sizing-methods-for-high-volatility-trades/)

---
*Generated: 2026-02-28 | Source: Web research across quant finance literature, backtesting framework docs, and institutional research*
*Status: Reference catalog — approaches selected per analysis based on strategy type and validation needs*
