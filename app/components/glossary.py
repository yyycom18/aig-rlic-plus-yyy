"""Glossary definitions extracted from portal_narrative_hy_ig_spy_20260228.md."""

GLOSSARY: dict[str, str] = {
    "Basis point (bp)": (
        "One hundredth of a percentage point (0.01%). "
        "100 basis points = 1%. Used to measure small changes in yields and spreads."
    ),
    "Buy-and-hold": (
        "An investment strategy where you purchase an asset and hold it regardless of "
        "market conditions. The simplest benchmark for comparing active strategies."
    ),
    "Credit rating": (
        "A grade assigned to a company's debt by rating agencies (S&P, Moody's, Fitch). "
        "Investment grade (AAA to BBB-) means lower default risk; high yield (BB+ and below) "
        "means higher default risk."
    ),
    "Credit spread": (
        "The difference in yield between a risky bond and a risk-free benchmark. "
        "Wider spreads indicate more perceived risk."
    ),
    "Drawdown": (
        "The peak-to-trough decline in the value of a portfolio or index. "
        "Maximum drawdown is the largest such decline in a given period."
    ),
    "Excess bond premium (EBP)": (
        "The component of credit spreads that cannot be explained by expected default risk. "
        "Captures investor sentiment and risk appetite. Proposed by Gilchrist & Zakrajsek (2012)."
    ),
    "Forward return": (
        "The return over a future period. A '21-day forward return' is the percentage change "
        "in price over the next 21 trading days (~1 month)."
    ),
    "Granger causality": (
        "A statistical test that determines whether one time series helps predict another. "
        "'X Granger-causes Y' means past values of X improve forecasts of Y. "
        "It does not prove true causation."
    ),
    "Hidden Markov Model (HMM)": (
        "A statistical model that assumes the system is in one of several unobservable "
        "('hidden') states, each with different statistical properties. The model estimates "
        "which state the market is in at any given time."
    ),
    "High-yield bonds (junk bonds)": (
        "Bonds from companies with credit ratings below investment grade (BB+ or lower). "
        "They offer higher yields to compensate for higher default risk."
    ),
    "HY-IG spread": (
        "The difference between the option-adjusted spread on high-yield bonds and the "
        "option-adjusted spread on investment-grade bonds. Our primary signal variable."
    ),
    "Impulse response": (
        "A measure of how one variable responds over time to a one-time shock in another "
        "variable. Shows whether effects are immediate, delayed, or persistent."
    ),
    "In-sample / Out-of-sample": (
        "In-sample data is used to build and fit models. Out-of-sample data is held back "
        "and used to test whether the model works on data it has never seen."
    ),
    "Investment-grade bonds": (
        "Bonds from companies with credit ratings of BBB- or above. Considered safer, "
        "with lower yields."
    ),
    "Local projection": (
        "A method for estimating impulse responses that does not require specifying a full "
        "multivariate model. More robust than traditional VAR methods. Developed by Jorda (2005)."
    ),
    "Markov-switching model": (
        "A model where the underlying regime (e.g., bull vs. bear market) can change randomly "
        "according to a Markov process. Each regime has its own set of parameters. "
        "Developed by Hamilton (1989)."
    ),
    "NFCI": (
        "National Financial Conditions Index, published weekly by the Chicago Federal Reserve. "
        "Measures overall conditions in U.S. financial markets. Positive values indicate "
        "tighter-than-average conditions."
    ),
    "Option-adjusted spread (OAS)": (
        "A credit spread that accounts for any embedded options (like call provisions) in the bond. "
        "Provides a cleaner measure of pure credit risk than raw yield spreads."
    ),
    "Quantile regression": (
        "A statistical method that estimates the effect of a variable on different parts "
        "of the outcome distribution (not just the average). Useful for understanding tail risks."
    ),
    "Regime": (
        "A distinct state of the market characterized by its own statistical properties "
        "(mean returns, volatility, correlations). Markets switch between regimes over time."
    ),
    "Sharpe ratio": (
        "A measure of risk-adjusted return: (return - risk-free rate) / volatility. "
        "Higher is better. A Sharpe of 1.0 is generally considered good."
    ),
    "Transfer entropy": (
        "An information-theoretic measure of directed information flow between time series. "
        "Unlike Granger causality, it captures nonlinear relationships."
    ),
    "VIX": (
        "The CBOE Volatility Index, often called the 'fear gauge.' Measures the market's "
        "expectation of 30-day volatility in the S&P 500, derived from option prices."
    ),
    "VIX term structure": (
        "The difference between longer-dated (VIX3M, 3-month) and shorter-dated (VIX, 1-month) "
        "implied volatility. When VIX3M > VIX (contango), markets are calm. When VIX > VIX3M "
        "(backwardation), markets are stressed."
    ),
    "Walk-forward validation": (
        "A backtesting method that simulates real-time trading by training the model on past "
        "data and testing on subsequent data, then rolling the window forward. Prevents "
        "lookahead bias."
    ),
    "Yield curve slope": (
        "The difference between long-term and short-term interest rates (e.g., 10-year minus "
        "3-month Treasury yields). An inverted yield curve (negative slope) has historically "
        "preceded recessions."
    ),
    "Z-score": (
        "A statistical measure of how many standard deviations a value is from its mean. "
        "A z-score of 2 means the value is 2 standard deviations above average -- an unusual reading."
    ),
}
