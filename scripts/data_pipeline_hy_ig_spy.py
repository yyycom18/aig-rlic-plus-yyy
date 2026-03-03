#!/usr/bin/env python3
"""
Data Pipeline: HY-IG Credit Spread vs SPY Analysis
====================================================
Sources 23 raw series (FRED + Yahoo Finance), aligns to a common daily
business-day calendar, computes 20 derived series and 6 forward SPY return
horizons, runs stationarity tests, and generates quality reports.

Author: Dana (Data Agent)
Date: 2026-02-28
"""

import os
import sys
import warnings
from datetime import datetime

import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore", category=FutureWarning)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
START_DATE = "2000-01-01"
END_DATE = "2025-12-31"
OUTPUT_DIR = "/workspaces/aig-rlic-plus/data"
RESULTS_DIR = "/workspaces/aig-rlic-plus/results"
FFILL_LIMIT = 5  # max business days to forward-fill

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# 1. Source Raw Series
# ---------------------------------------------------------------------------

def source_fred_series():
    """Source all FRED series. Try fredapi first, fall back to pandas-datareader."""
    fred_series = {
        "BAMLH0A0HYM2": "hy_oas",
        "BAMLC0A0CM": "ig_oas",
        "BAMLH0A1HYBB": "bb_hy_oas",
        "BAMLH0A3HYC": "ccc_hy_oas",
        "DGS10": "dgs10",
        "DTB3": "dtb3",
        "DGS2": "dgs2",
        "NFCI": "nfci",
        "DFF": "fed_funds_rate",
        "BAMLC0A4CBBB": "bbb_oas",
        "STLFSI4": "fsi",  # STLFSI2 discontinued; STLFSI4 is the current version
        "ICSA": "initial_claims",
        "SOFR": "sofr",
    }

    api_key = os.environ.get("FRED_API_KEY", "952aa4d0c4b2057609fbf3ecc6954e58")
    fred_data = {}

    # Try fredapi
    try:
        from fredapi import Fred
        if api_key:
            fred = Fred(api_key=api_key)
        else:
            # Try without key (will likely fail but worth trying)
            fred = Fred(api_key="DEMO_KEY")

        for series_id, col_name in fred_series.items():
            try:
                s = fred.get_series(series_id, observation_start=START_DATE, observation_end=END_DATE)
                s.name = col_name
                s.index = pd.to_datetime(s.index)
                fred_data[col_name] = s.astype(float)
                print(f"  [FRED] {series_id} -> {col_name}: {len(s)} obs, {s.index.min().date()} to {s.index.max().date()}")
            except Exception as e:
                print(f"  [FRED] {series_id} -> {col_name}: FAILED ({e})")
    except Exception as e:
        print(f"  [FRED] fredapi failed: {e}")

    # Fallback: pandas-datareader
    if len(fred_data) < len(fred_series):
        missing = {k: v for k, v in fred_series.items() if v not in fred_data}
        try:
            import pandas_datareader.data as web
            for series_id, col_name in missing.items():
                try:
                    s = web.DataReader(series_id, "fred", START_DATE, END_DATE)
                    s = s.iloc[:, 0]
                    s.name = col_name
                    s.index = pd.to_datetime(s.index)
                    fred_data[col_name] = s.astype(float)
                    print(f"  [PDR]  {series_id} -> {col_name}: {len(s)} obs, {s.index.min().date()} to {s.index.max().date()}")
                except Exception as e:
                    print(f"  [PDR]  {series_id} -> {col_name}: FAILED ({e})")
        except ImportError:
            print("  [PDR] pandas-datareader not available")

    # Final fallback: direct FRED CSV download
    if len(fred_data) < len(fred_series):
        missing = {k: v for k, v in fred_series.items() if v not in fred_data}
        import urllib.request
        for series_id, col_name in missing.items():
            try:
                url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}&cosd={START_DATE}&coed={END_DATE}"
                local_path = f"/tmp/fred_{series_id}.csv"
                urllib.request.urlretrieve(url, local_path)
                s = pd.read_csv(local_path, index_col=0, parse_dates=True).iloc[:, 0]
                # FRED uses '.' for missing
                s = pd.to_numeric(s, errors="coerce")
                s.name = col_name
                fred_data[col_name] = s
                print(f"  [CSV]  {series_id} -> {col_name}: {len(s)} obs, {s.index.min().date()} to {s.index.max().date()}")
            except Exception as e:
                print(f"  [CSV]  {series_id} -> {col_name}: FAILED ({e})")

    return fred_data


def source_yahoo_series():
    """Source all Yahoo Finance series."""
    import yfinance as yf

    yahoo_tickers = {
        "SPY": "spy",
        "^VIX": "vix",
        "^VIX3M": "vix3m",
        "KBE": "kbe",
        "IWM": "iwm",
        "^MOVE": "move_index",
        "GC=F": "gold",
        "HG=F": "copper",
        "DX-Y.NYB": "dxy",
        "HYG": "hyg",
    }

    yahoo_data = {}
    unavailable = []

    for ticker, col_name in yahoo_tickers.items():
        try:
            df = yf.download(ticker, start=START_DATE, end=END_DATE, progress=False, auto_adjust=True)
            if df.empty:
                raise ValueError("Empty dataframe returned")
            # Handle multi-level columns from yfinance
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            # Use Close (which is Adj Close when auto_adjust=True)
            s = df["Close"].copy()
            s.name = col_name
            s.index = pd.to_datetime(s.index)
            # Remove timezone info if present
            if s.index.tz is not None:
                s.index = s.index.tz_localize(None)
            yahoo_data[col_name] = s.astype(float)
            print(f"  [YF]   {ticker} -> {col_name}: {len(s)} obs, {s.index.min().date()} to {s.index.max().date()}")
        except Exception as e:
            unavailable.append((ticker, col_name, str(e)))
            print(f"  [YF]   {ticker} -> {col_name}: UNAVAILABLE ({e})")

    return yahoo_data, unavailable


# ---------------------------------------------------------------------------
# 2. Align to Common Calendar
# ---------------------------------------------------------------------------

def align_to_bday_calendar(all_series, weekly_cols):
    """Reindex all series to a common business-day calendar.

    Weekly series (NFCI, FSI, ICSA) are released on non-business days
    (Fridays/Saturdays). We first reindex to all calendar days, forward-fill,
    then select business days only.
    """
    bdays = pd.bdate_range(START_DATE, END_DATE)
    all_days = pd.date_range(START_DATE, END_DATE, freq="D")
    master = pd.DataFrame(index=bdays)
    master.index.name = "date"

    for col_name, s in all_series.items():
        if col_name in weekly_cols:
            # Weekly series: reindex to ALL calendar days first (to capture
            # weekend release dates), forward-fill fully, then select bdays
            s_all = s.reindex(all_days)
            s_all = s_all.ffill()
            master[col_name] = s_all.reindex(bdays)
        else:
            # Daily series: reindex directly to bdays, ffill up to limit
            s_reindexed = s.reindex(bdays)
            s_reindexed = s_reindexed.ffill(limit=FFILL_LIMIT)
            master[col_name] = s_reindexed

    return master


# ---------------------------------------------------------------------------
# 3. Compute Derived Series
# ---------------------------------------------------------------------------

def compute_derived(df):
    """Compute 20 derived series."""
    # D1: HY-IG spread
    df["hy_ig_spread"] = df["hy_oas"] - df["ig_oas"]
    spread = df["hy_ig_spread"]

    # D2: Z-score 252d
    rm252 = spread.rolling(252, min_periods=200)
    df["hy_ig_zscore_252d"] = (spread - rm252.mean()) / rm252.std()

    # D3: Z-score 504d
    rm504 = spread.rolling(504, min_periods=400)
    df["hy_ig_zscore_504d"] = (spread - rm504.mean()) / rm504.std()

    # D4: Percentile rank 504d
    df["hy_ig_pctrank_504d"] = spread.rolling(504, min_periods=400).apply(
        lambda x: stats.rankdata(x)[-1] / len(x), raw=True
    )

    # D5: Percentile rank 1260d
    df["hy_ig_pctrank_1260d"] = spread.rolling(1260, min_periods=1000).apply(
        lambda x: stats.rankdata(x)[-1] / len(x), raw=True
    )

    # D6-D8: Rate of change
    df["hy_ig_roc_21d"] = (spread / spread.shift(21) - 1) * 100
    df["hy_ig_roc_63d"] = (spread / spread.shift(63) - 1) * 100
    df["hy_ig_roc_126d"] = (spread / spread.shift(126) - 1) * 100

    # D9-D11: Momentum (absolute change)
    df["hy_ig_mom_21d"] = spread - spread.shift(21)
    df["hy_ig_mom_63d"] = spread - spread.shift(63)
    df["hy_ig_mom_252d"] = spread - spread.shift(252)

    # D12: Acceleration (diff of 21d RoC)
    df["hy_ig_acceleration"] = df["hy_ig_roc_21d"] - df["hy_ig_roc_21d"].shift(21)

    # D13: CCC-BB quality spread
    df["ccc_bb_spread"] = df["ccc_hy_oas"] - df["bb_hy_oas"]

    # D14: Realized vol of spread (rolling std of daily diff)
    df["hy_ig_realized_vol_21d"] = spread.diff().rolling(21, min_periods=15).std()

    # D15: VIX term structure
    if "vix3m" in df.columns and "vix" in df.columns:
        df["vix_term_structure"] = df["vix3m"] - df["vix"]
    else:
        df["vix_term_structure"] = np.nan

    # D16-D17: Yield curve spreads
    df["yield_spread_10y3m"] = df["dgs10"] - df["dtb3"]
    df["yield_spread_10y2y"] = df["dgs10"] - df["dgs2"]

    # D18: Bank/small-cap ratio
    if "kbe" in df.columns and "iwm" in df.columns:
        df["bank_smallcap_ratio"] = df["kbe"] / df["iwm"]
    else:
        df["bank_smallcap_ratio"] = np.nan

    # D19: NFCI momentum (65 bdays ~ 13 weeks)
    if "nfci" in df.columns:
        df["nfci_momentum_13w"] = df["nfci"] - df["nfci"].shift(65)
    else:
        df["nfci_momentum_13w"] = np.nan

    # D20: BBB-IG spread
    df["bbb_ig_spread"] = df["bbb_oas"] - df["ig_oas"]

    return df


# ---------------------------------------------------------------------------
# 4. Compute Forward SPY Returns
# ---------------------------------------------------------------------------

def compute_forward_returns(df):
    """Compute forward SPY returns at multiple horizons."""
    spy = df["spy"]
    df["spy_fwd_1d"] = spy.pct_change(1).shift(-1)
    df["spy_fwd_5d"] = spy.shift(-5) / spy - 1
    df["spy_fwd_21d"] = spy.shift(-21) / spy - 1
    df["spy_fwd_63d"] = spy.shift(-63) / spy - 1
    df["spy_fwd_126d"] = spy.shift(-126) / spy - 1
    df["spy_fwd_252d"] = spy.shift(-252) / spy - 1
    return df


# ---------------------------------------------------------------------------
# 5. Stationarity Tests
# ---------------------------------------------------------------------------

def run_stationarity_tests(df):
    """Run ADF and KPSS on all level (raw) series."""
    from arch.unitroot import ADF, KPSS

    raw_cols = [
        "hy_oas", "ig_oas", "bb_hy_oas", "ccc_hy_oas",
        "dgs10", "dtb3", "dgs2", "nfci", "fed_funds_rate",
        "bbb_oas", "fsi", "initial_claims", "sofr",
        "spy", "vix", "vix3m", "kbe", "iwm", "move_index",
        "gold", "copper", "dxy", "hyg",
    ]

    results = []
    for col in raw_cols:
        if col not in df.columns:
            continue
        s = df[col].dropna()
        if len(s) < 100:
            results.append({
                "variable": col, "test": "ADF", "statistic": np.nan,
                "p_value": np.nan, "lags": np.nan,
                "conclusion": f"Insufficient data ({len(s)} obs)"
            })
            continue

        # ADF test
        try:
            adf = ADF(s, max_lags=20)
            results.append({
                "variable": col, "test": "ADF",
                "statistic": round(adf.stat, 4),
                "p_value": round(adf.pvalue, 4),
                "lags": adf.lags,
                "conclusion": "Stationary at 5%" if adf.pvalue < 0.05 else "Non-stationary at 5%"
            })
        except Exception as e:
            results.append({
                "variable": col, "test": "ADF",
                "statistic": np.nan, "p_value": np.nan, "lags": np.nan,
                "conclusion": f"Error: {e}"
            })

        # KPSS test
        try:
            kpss = KPSS(s)
            results.append({
                "variable": col, "test": "KPSS",
                "statistic": round(kpss.stat, 4),
                "p_value": round(kpss.pvalue, 4),
                "lags": kpss.lags,
                "conclusion": "Stationary (fail to reject)" if kpss.pvalue > 0.05 else "Non-stationary (reject null)"
            })
        except Exception as e:
            results.append({
                "variable": col, "test": "KPSS",
                "statistic": np.nan, "p_value": np.nan, "lags": np.nan,
                "conclusion": f"Error: {e}"
            })

    return pd.DataFrame(results)


# ---------------------------------------------------------------------------
# 6. Quality Reports
# ---------------------------------------------------------------------------

def generate_missing_report(df, unavailable_yahoo):
    """Generate missing value report as markdown."""
    lines = [
        "# Missing Value Report",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Dataset shape:** {df.shape[0]} rows x {df.shape[1]} columns",
        f"**Date range:** {df.index.min().date()} to {df.index.max().date()}",
        "",
        "## Unavailable Series",
        "",
    ]

    if unavailable_yahoo:
        for ticker, col, reason in unavailable_yahoo:
            lines.append(f"- **{ticker}** ({col}): {reason}")
    else:
        lines.append("- None")

    lines += [
        "",
        "## Missing Values by Column",
        "",
        "| Column | Total Obs | Missing | Missing % | First Available | Last Available | Max Gap (days) |",
        "|--------|-----------|---------|-----------|-----------------|----------------|----------------|",
    ]

    for col in sorted(df.columns):
        total = len(df)
        missing = df[col].isna().sum()
        pct = missing / total * 100
        valid = df[col].dropna()
        first_date = valid.index.min().date() if len(valid) > 0 else "N/A"
        last_date = valid.index.max().date() if len(valid) > 0 else "N/A"

        # Max gap
        if len(valid) > 1:
            gaps = pd.Series(valid.index).diff().dt.days
            max_gap = int(gaps.max()) if not gaps.empty else 0
        else:
            max_gap = 0

        lines.append(f"| {col} | {total} | {missing} | {pct:.1f}% | {first_date} | {last_date} | {max_gap} |")

    lines += [
        "",
        "## Outlier Flags (|z-score| > 4)",
        "",
    ]

    outlier_count = 0
    for col in sorted(df.select_dtypes(include=[np.number]).columns):
        s = df[col].dropna()
        if len(s) < 30:
            continue
        z = np.abs((s - s.mean()) / s.std())
        outliers = z[z > 4]
        if len(outliers) > 0:
            outlier_count += len(outliers)
            lines.append(f"- **{col}**: {len(outliers)} observations with |z| > 4")
            # Show top 5
            for idx in outliers.nlargest(5).index:
                lines.append(f"  - {idx.date()}: value={df.loc[idx, col]:.4f}, z={z.loc[idx]:.2f}")

    if outlier_count == 0:
        lines.append("- No outliers detected with |z-score| > 4")

    lines += [
        "",
        "## Forward-Fill Documentation",
        "",
        f"- Maximum forward-fill: {FFILL_LIMIT} business days for daily series",
        "- Weekly series (NFCI, FSI, ICSA): fully forward-filled to daily after reindexing",
        "- Gaps beyond 5 business days left as NaN for daily series",
        "",
        "## Econometric Implications",
        "",
        "- Forward-filling weekly series to daily induces artificial autocorrelation at the daily frequency. "
        "Consider using weekly-frequency data for regressions involving NFCI, FSI, or ICSA as regressors.",
        "- SOFR series starts ~2018; any analysis using SOFR is limited to post-2018 sample.",
        "- VIX3M may start later than VIX; VIX term structure (D15) has a later start date accordingly.",
        "- KBE (bank ETF) starts ~2005; bank/small-cap ratio (D18) is unavailable before then.",
    ]

    return "\n".join(lines)


def generate_data_dictionary():
    """Generate data dictionary as a list of dicts for CSV output."""
    entries = [
        # Raw FRED series
        {"Column Name": "hy_oas", "Display Name": "HY OAS (bps)", "Display Note": "High-yield corporate bond risk premium over Treasuries", "Description": "ICE BofA US High Yield Index Option-Adjusted Spread", "Source": "FRED", "Series ID": "BAMLH0A0HYM2", "Unit": "bps", "Transformation": "Level", "Seasonal Adj": "NSA", "Known Quirks": "Index composition changes over time; pre-2000 methodology differs", "Refresh Freq": "Daily", "Refresh Source": "fred MCP"},
        {"Column Name": "ig_oas", "Display Name": "IG OAS (bps)", "Display Note": "Investment-grade corporate bond risk premium", "Description": "ICE BofA US Corporate Index Option-Adjusted Spread", "Source": "FRED", "Series ID": "BAMLC0A0CM", "Unit": "bps", "Transformation": "Level", "Seasonal Adj": "NSA", "Known Quirks": "Includes all IG-rated bonds; composition shifts with ratings migration", "Refresh Freq": "Daily", "Refresh Source": "fred MCP"},
        {"Column Name": "bb_hy_oas", "Display Name": "BB HY OAS (bps)", "Display Note": "BB-rated high-yield bond risk premium", "Description": "ICE BofA BB US High Yield Index OAS", "Source": "FRED", "Series ID": "BAMLH0A1HYBB", "Unit": "bps", "Transformation": "Level", "Seasonal Adj": "NSA", "Known Quirks": "BB is the highest quality HY tier; composition changes with fallen angels", "Refresh Freq": "Daily", "Refresh Source": "fred MCP"},
        {"Column Name": "ccc_hy_oas", "Display Name": "CCC HY OAS (bps)", "Display Note": "CCC-rated (riskiest) high-yield bond risk premium", "Description": "ICE BofA CCC & Lower US High Yield Index OAS", "Source": "FRED", "Series ID": "BAMLH0A3HYC", "Unit": "bps", "Transformation": "Level", "Seasonal Adj": "NSA", "Known Quirks": "Most volatile OAS series; spikes during stress; thin market segments", "Refresh Freq": "Daily", "Refresh Source": "fred MCP"},
        {"Column Name": "dgs10", "Display Name": "10Y Treasury Yield (%)", "Display Note": "US 10-year government bond interest rate", "Description": "10-Year Treasury Constant Maturity Rate", "Source": "FRED", "Series ID": "DGS10", "Unit": "%", "Transformation": "Level", "Seasonal Adj": "NSA", "Known Quirks": "Market holidays cause gaps; constant maturity interpolation", "Refresh Freq": "Daily", "Refresh Source": "fred MCP"},
        {"Column Name": "dtb3", "Display Name": "3M Treasury Yield (%)", "Display Note": "US 3-month government bond interest rate", "Description": "3-Month Treasury Bill Secondary Market Rate", "Source": "FRED", "Series ID": "DTB3", "Unit": "%", "Transformation": "Level", "Seasonal Adj": "NSA", "Known Quirks": "Can go negative during extreme flight-to-quality", "Refresh Freq": "Daily", "Refresh Source": "fred MCP"},
        {"Column Name": "dgs2", "Display Name": "2Y Treasury Yield (%)", "Display Note": "US 2-year government bond interest rate", "Description": "2-Year Treasury Constant Maturity Rate", "Source": "FRED", "Series ID": "DGS2", "Unit": "%", "Transformation": "Level", "Seasonal Adj": "NSA", "Known Quirks": "Highly sensitive to Fed rate expectations", "Refresh Freq": "Daily", "Refresh Source": "fred MCP"},
        {"Column Name": "nfci", "Display Name": "NFCI", "Display Note": "Chicago Fed measure of US financial conditions (negative = loose, positive = tight)", "Description": "Chicago Fed National Financial Conditions Index", "Source": "FRED", "Series ID": "NFCI", "Unit": "Index", "Transformation": "Level, ffill weekly->daily", "Seasonal Adj": "NSA", "Known Quirks": "Weekly release; forward-filled to daily — induces autocorrelation", "Refresh Freq": "Weekly", "Refresh Source": "fred MCP"},
        {"Column Name": "fed_funds_rate", "Display Name": "Fed Funds Rate (%)", "Display Note": "The interest rate banks charge each other for overnight loans", "Description": "Effective Federal Funds Rate", "Source": "FRED", "Series ID": "DFF", "Unit": "%", "Transformation": "Level", "Seasonal Adj": "NSA", "Known Quirks": "Near-zero 2008-2015 and 2020-2022", "Refresh Freq": "Daily", "Refresh Source": "fred MCP"},
        {"Column Name": "bbb_oas", "Display Name": "BBB OAS (bps)", "Display Note": "BBB-rated (lowest investment-grade) bond risk premium", "Description": "ICE BofA BBB US Corporate Index OAS", "Source": "FRED", "Series ID": "BAMLC0A4CBBB", "Unit": "bps", "Transformation": "Level", "Seasonal Adj": "NSA", "Known Quirks": "BBB is the cliff-edge rating tier; sensitive to downgrade fears", "Refresh Freq": "Daily", "Refresh Source": "fred MCP"},
        {"Column Name": "fsi", "Display Name": "St. Louis FSI", "Display Note": "Federal Reserve measure of financial market stress (higher = more stress)", "Description": "St. Louis Fed Financial Stress Index (v4)", "Source": "FRED", "Series ID": "STLFSI4", "Unit": "Index", "Transformation": "Level, ffill weekly->daily", "Seasonal Adj": "NSA", "Known Quirks": "Weekly release; STLFSI4 is the current version (STLFSI2 discontinued ~2022)", "Refresh Freq": "Weekly", "Refresh Source": "fred MCP"},
        {"Column Name": "initial_claims", "Display Name": "Initial Jobless Claims", "Display Note": "Weekly count of new unemployment benefit applications", "Description": "Initial Claims, Seasonally Adjusted", "Source": "FRED", "Series ID": "ICSA", "Unit": "Thousands", "Transformation": "Level, ffill weekly->daily", "Seasonal Adj": "SA", "Known Quirks": "Weekly release; holiday-adjusted; COVID spike to 6M+ in 2020", "Refresh Freq": "Weekly", "Refresh Source": "fred MCP"},
        {"Column Name": "sofr", "Display Name": "SOFR (%)", "Display Note": "Secured overnight financing rate — replacement for LIBOR", "Description": "Secured Overnight Financing Rate", "Source": "FRED", "Series ID": "SOFR", "Unit": "%", "Transformation": "Level", "Seasonal Adj": "NSA", "Known Quirks": "Starts ~April 2018; occasional quarter-end spikes", "Refresh Freq": "Daily", "Refresh Source": "fred MCP"},

        # Raw Yahoo series
        {"Column Name": "spy", "Display Name": "SPY Price ($)", "Display Note": "S&P 500 index fund price", "Description": "SPDR S&P 500 ETF Trust — Adjusted Close", "Source": "Yahoo Finance", "Series ID": "SPY", "Unit": "USD", "Transformation": "Level (adjusted)", "Seasonal Adj": "N/A", "Known Quirks": "Adjusted for splits and dividends", "Refresh Freq": "Daily", "Refresh Source": "yfinance"},
        {"Column Name": "vix", "Display Name": "VIX", "Display Note": "Market fear gauge — expected stock market volatility over next 30 days", "Description": "CBOE Volatility Index", "Source": "Yahoo Finance", "Series ID": "^VIX", "Unit": "Index", "Transformation": "Level", "Seasonal Adj": "N/A", "Known Quirks": "Not directly investable; mean-reverting; spikes during crises", "Refresh Freq": "Daily", "Refresh Source": "yfinance"},
        {"Column Name": "vix3m", "Display Name": "VIX3M", "Display Note": "Expected stock market volatility over next 3 months", "Description": "CBOE 3-Month Volatility Index", "Source": "Yahoo Finance", "Series ID": "^VIX3M", "Unit": "Index", "Transformation": "Level", "Seasonal Adj": "N/A", "Known Quirks": "Starts ~2007; shorter history than VIX", "Refresh Freq": "Daily", "Refresh Source": "yfinance"},
        {"Column Name": "kbe", "Display Name": "KBE Price ($)", "Display Note": "US bank stocks index fund price", "Description": "SPDR S&P Bank ETF — Adjusted Close", "Source": "Yahoo Finance", "Series ID": "KBE", "Unit": "USD", "Transformation": "Level (adjusted)", "Seasonal Adj": "N/A", "Known Quirks": "Starts ~2005; equal-weighted bank ETF", "Refresh Freq": "Daily", "Refresh Source": "yfinance"},
        {"Column Name": "iwm", "Display Name": "IWM Price ($)", "Display Note": "Small-company stocks index fund price", "Description": "iShares Russell 2000 ETF — Adjusted Close", "Source": "Yahoo Finance", "Series ID": "IWM", "Unit": "USD", "Transformation": "Level (adjusted)", "Seasonal Adj": "N/A", "Known Quirks": "Starts ~2000; small-cap benchmark", "Refresh Freq": "Daily", "Refresh Source": "yfinance"},
        {"Column Name": "move_index", "Display Name": "MOVE Index", "Display Note": "Bond market fear gauge — expected Treasury volatility", "Description": "ICE BofA MOVE Index", "Source": "Yahoo Finance", "Series ID": "^MOVE", "Unit": "Index", "Transformation": "Level", "Seasonal Adj": "N/A", "Known Quirks": "May be unavailable on Yahoo Finance; bond market equivalent of VIX", "Refresh Freq": "Daily", "Refresh Source": "yfinance"},
        {"Column Name": "gold", "Display Name": "Gold Price ($/oz)", "Display Note": "Price of gold — a traditional safe-haven asset", "Description": "Gold Futures (GC=F) — Close", "Source": "Yahoo Finance", "Series ID": "GC=F", "Unit": "USD/oz", "Transformation": "Level", "Seasonal Adj": "N/A", "Known Quirks": "Futures contract; roll dates cause minor discontinuities", "Refresh Freq": "Daily", "Refresh Source": "yfinance"},
        {"Column Name": "copper", "Display Name": "Copper Price ($/lb)", "Display Note": "Price of copper — a barometer of global economic health", "Description": "Copper Futures (HG=F) — Close", "Source": "Yahoo Finance", "Series ID": "HG=F", "Unit": "USD/lb", "Transformation": "Level", "Seasonal Adj": "N/A", "Known Quirks": "Futures contract; roll dates cause minor discontinuities", "Refresh Freq": "Daily", "Refresh Source": "yfinance"},
        {"Column Name": "dxy", "Display Name": "Dollar Index (DXY)", "Display Note": "Value of the US dollar against a basket of major currencies", "Description": "US Dollar Index — Close", "Source": "Yahoo Finance", "Series ID": "DX-Y.NYB", "Unit": "Index", "Transformation": "Level", "Seasonal Adj": "N/A", "Known Quirks": "Euro-heavy basket; may have gaps on non-US holidays", "Refresh Freq": "Daily", "Refresh Source": "yfinance"},
        {"Column Name": "hyg", "Display Name": "HYG Price ($)", "Display Note": "High-yield corporate bond fund price — tracks junk bond market", "Description": "iShares iBoxx $ High Yield Corporate Bond ETF — Adjusted Close", "Source": "Yahoo Finance", "Series ID": "HYG", "Unit": "USD", "Transformation": "Level (adjusted)", "Seasonal Adj": "N/A", "Known Quirks": "Starts ~2007; ETF discount/premium to NAV during stress", "Refresh Freq": "Daily", "Refresh Source": "yfinance"},

        # Derived series
        {"Column Name": "hy_ig_spread", "Display Name": "HY-IG Spread (bps)", "Display Note": "Difference between high-yield and investment-grade risk premiums — the core signal", "Description": "HY OAS minus IG OAS", "Source": "Derived", "Series ID": "D1", "Unit": "bps", "Transformation": "BAMLH0A0HYM2 - BAMLC0A0CM", "Seasonal Adj": "N/A", "Known Quirks": "Widens during stress, tightens during calm", "Refresh Freq": "Daily", "Refresh Source": "Computed"},
        {"Column Name": "hy_ig_zscore_252d", "Display Name": "HY-IG Z-Score (1Y)", "Display Note": "How unusual is today's spread compared to the past year (0 = normal, >2 = elevated)", "Description": "252-day rolling z-score of HY-IG spread", "Source": "Derived", "Series ID": "D2", "Unit": "Std devs", "Transformation": "(spread - rolling_mean_252) / rolling_std_252", "Seasonal Adj": "N/A", "Known Quirks": "Requires 252 obs to initialize; first ~1 year is NaN", "Refresh Freq": "Daily", "Refresh Source": "Computed"},
        {"Column Name": "hy_ig_zscore_504d", "Display Name": "HY-IG Z-Score (2Y)", "Display Note": "How unusual is today's spread compared to the past 2 years", "Description": "504-day rolling z-score of HY-IG spread", "Source": "Derived", "Series ID": "D3", "Unit": "Std devs", "Transformation": "(spread - rolling_mean_504) / rolling_std_504", "Seasonal Adj": "N/A", "Known Quirks": "Requires 504 obs to initialize; first ~2 years NaN", "Refresh Freq": "Daily", "Refresh Source": "Computed"},
        {"Column Name": "hy_ig_pctrank_504d", "Display Name": "HY-IG Percentile (2Y)", "Display Note": "Where today's spread ranks vs the past 2 years (0.5 = median, 0.95 = very high)", "Description": "504-day rolling percentile rank", "Source": "Derived", "Series ID": "D4", "Unit": "Ratio (0-1)", "Transformation": "rolling_rank / window", "Seasonal Adj": "N/A", "Known Quirks": "Bounded 0-1; requires 504 obs", "Refresh Freq": "Daily", "Refresh Source": "Computed"},
        {"Column Name": "hy_ig_pctrank_1260d", "Display Name": "HY-IG Percentile (5Y)", "Display Note": "Where today's spread ranks vs the past 5 years", "Description": "1260-day rolling percentile rank", "Source": "Derived", "Series ID": "D5", "Unit": "Ratio (0-1)", "Transformation": "rolling_rank / window", "Seasonal Adj": "N/A", "Known Quirks": "Bounded 0-1; requires 1260 obs (~5 years)", "Refresh Freq": "Daily", "Refresh Source": "Computed"},
        {"Column Name": "hy_ig_roc_21d", "Display Name": "HY-IG RoC 1M (%)", "Display Note": "How much the spread changed over the past month (%)", "Description": "21-day rate of change of HY-IG spread", "Source": "Derived", "Series ID": "D6", "Unit": "%", "Transformation": "(spread / spread.shift(21) - 1) * 100", "Seasonal Adj": "N/A", "Known Quirks": "Percentage change; can be extreme from low base", "Refresh Freq": "Daily", "Refresh Source": "Computed"},
        {"Column Name": "hy_ig_roc_63d", "Display Name": "HY-IG RoC 3M (%)", "Display Note": "How much the spread changed over the past quarter (%)", "Description": "63-day rate of change of HY-IG spread", "Source": "Derived", "Series ID": "D7", "Unit": "%", "Transformation": "(spread / spread.shift(63) - 1) * 100", "Seasonal Adj": "N/A", "Known Quirks": "Percentage change", "Refresh Freq": "Daily", "Refresh Source": "Computed"},
        {"Column Name": "hy_ig_roc_126d", "Display Name": "HY-IG RoC 6M (%)", "Display Note": "How much the spread changed over the past 6 months (%)", "Description": "126-day rate of change of HY-IG spread", "Source": "Derived", "Series ID": "D8", "Unit": "%", "Transformation": "(spread / spread.shift(126) - 1) * 100", "Seasonal Adj": "N/A", "Known Quirks": "Percentage change", "Refresh Freq": "Daily", "Refresh Source": "Computed"},
        {"Column Name": "hy_ig_mom_21d", "Display Name": "HY-IG Mom 1M (bps)", "Display Note": "Absolute change in spread over 1 month", "Description": "21-day momentum of HY-IG spread", "Source": "Derived", "Series ID": "D9", "Unit": "bps", "Transformation": "spread - spread.shift(21)", "Seasonal Adj": "N/A", "Known Quirks": "Absolute change, not percentage", "Refresh Freq": "Daily", "Refresh Source": "Computed"},
        {"Column Name": "hy_ig_mom_63d", "Display Name": "HY-IG Mom 3M (bps)", "Display Note": "Absolute change in spread over 3 months", "Description": "63-day momentum of HY-IG spread", "Source": "Derived", "Series ID": "D10", "Unit": "bps", "Transformation": "spread - spread.shift(63)", "Seasonal Adj": "N/A", "Known Quirks": "Absolute change", "Refresh Freq": "Daily", "Refresh Source": "Computed"},
        {"Column Name": "hy_ig_mom_252d", "Display Name": "HY-IG Mom 1Y (bps)", "Display Note": "Absolute change in spread over 1 year", "Description": "252-day momentum of HY-IG spread", "Source": "Derived", "Series ID": "D11", "Unit": "bps", "Transformation": "spread - spread.shift(252)", "Seasonal Adj": "N/A", "Known Quirks": "Absolute change", "Refresh Freq": "Daily", "Refresh Source": "Computed"},
        {"Column Name": "hy_ig_acceleration", "Display Name": "Spread Acceleration", "Display Note": "Is the spread change speeding up or slowing down?", "Description": "Change in 21d RoC over 21 days (second derivative)", "Source": "Derived", "Series ID": "D12", "Unit": "pp", "Transformation": "roc_21d - roc_21d.shift(21)", "Seasonal Adj": "N/A", "Known Quirks": "Second derivative; noisy", "Refresh Freq": "Daily", "Refresh Source": "Computed"},
        {"Column Name": "ccc_bb_spread", "Display Name": "CCC-BB Spread (bps)", "Display Note": "Risk premium difference between junkiest and least-junky high-yield bonds", "Description": "CCC OAS minus BB OAS (quality spread within HY)", "Source": "Derived", "Series ID": "D13", "Unit": "bps", "Transformation": "BAMLH0A3HYC - BAMLH0A1HYBB", "Seasonal Adj": "N/A", "Known Quirks": "Widens sharply during credit events; thin CCC market", "Refresh Freq": "Daily", "Refresh Source": "Computed"},
        {"Column Name": "hy_ig_realized_vol_21d", "Display Name": "Spread Vol (21d)", "Display Note": "How volatile the spread has been over the past month", "Description": "21-day rolling std of daily spread changes", "Source": "Derived", "Series ID": "D14", "Unit": "bps", "Transformation": "rolling_std(spread.diff(), 21)", "Seasonal Adj": "N/A", "Known Quirks": "Clusters during stress", "Refresh Freq": "Daily", "Refresh Source": "Computed"},
        {"Column Name": "vix_term_structure", "Display Name": "VIX Term Structure", "Display Note": "Difference between 3-month and 1-month fear gauges (negative = near-term panic)", "Description": "VIX3M minus VIX", "Source": "Derived", "Series ID": "D15", "Unit": "Index pts", "Transformation": "VIX3M - VIX", "Seasonal Adj": "N/A", "Known Quirks": "Negative = backwardation (near-term stress); starts when VIX3M starts", "Refresh Freq": "Daily", "Refresh Source": "Computed"},
        {"Column Name": "yield_spread_10y3m", "Display Name": "10Y-3M Spread (%)", "Display Note": "Yield curve slope — negative means recession warning", "Description": "10Y minus 3M Treasury yield spread", "Source": "Derived", "Series ID": "D16", "Unit": "%", "Transformation": "DGS10 - DTB3", "Seasonal Adj": "N/A", "Known Quirks": "Classic recession indicator; negative = inverted curve", "Refresh Freq": "Daily", "Refresh Source": "Computed"},
        {"Column Name": "yield_spread_10y2y", "Display Name": "10Y-2Y Spread (%)", "Display Note": "Another yield curve slope measure — negative = recession signal", "Description": "10Y minus 2Y Treasury yield spread", "Source": "Derived", "Series ID": "D17", "Unit": "%", "Transformation": "DGS10 - DGS2", "Seasonal Adj": "N/A", "Known Quirks": "More volatile than 10Y-3M; popular media indicator", "Refresh Freq": "Daily", "Refresh Source": "Computed"},
        {"Column Name": "bank_smallcap_ratio", "Display Name": "Bank/SmallCap Ratio", "Display Note": "Relative performance of banks vs small companies — credit health indicator", "Description": "KBE / IWM price ratio", "Source": "Derived", "Series ID": "D18", "Unit": "Ratio", "Transformation": "KBE / IWM", "Seasonal Adj": "N/A", "Known Quirks": "Starts when KBE starts (~2005)", "Refresh Freq": "Daily", "Refresh Source": "Computed"},
        {"Column Name": "nfci_momentum_13w", "Display Name": "NFCI Momentum (13w)", "Display Note": "Are financial conditions tightening or loosening over the past quarter?", "Description": "NFCI minus NFCI lagged 65 business days", "Source": "Derived", "Series ID": "D19", "Unit": "Index pts", "Transformation": "NFCI - NFCI.shift(65)", "Seasonal Adj": "N/A", "Known Quirks": "Based on weekly NFCI, forward-filled to daily", "Refresh Freq": "Daily", "Refresh Source": "Computed"},
        {"Column Name": "bbb_ig_spread", "Display Name": "BBB-IG Spread (bps)", "Display Note": "Risk premium for being at the edge of investment grade", "Description": "BBB OAS minus IG OAS", "Source": "Derived", "Series ID": "D20", "Unit": "bps", "Transformation": "BAMLC0A4CBBB - BAMLC0A0CM", "Seasonal Adj": "N/A", "Known Quirks": "Sensitive to downgrade risk at the IG/HY boundary", "Refresh Freq": "Daily", "Refresh Source": "Computed"},

        # Forward returns
        {"Column Name": "spy_fwd_1d", "Display Name": "SPY Fwd Return 1D", "Display Note": "S&P 500 return over the next trading day", "Description": "1-day forward SPY return", "Source": "Derived", "Series ID": "FWD1", "Unit": "Decimal", "Transformation": "SPY.pct_change(1).shift(-1)", "Seasonal Adj": "N/A", "Known Quirks": "Look-ahead variable — NOT for use as a predictor", "Refresh Freq": "Daily", "Refresh Source": "Computed"},
        {"Column Name": "spy_fwd_5d", "Display Name": "SPY Fwd Return 1W", "Display Note": "S&P 500 return over the next week", "Description": "5-day forward SPY return", "Source": "Derived", "Series ID": "FWD5", "Unit": "Decimal", "Transformation": "(SPY.shift(-5) / SPY - 1)", "Seasonal Adj": "N/A", "Known Quirks": "Look-ahead variable", "Refresh Freq": "Daily", "Refresh Source": "Computed"},
        {"Column Name": "spy_fwd_21d", "Display Name": "SPY Fwd Return 1M", "Display Note": "S&P 500 return over the next month", "Description": "21-day forward SPY return", "Source": "Derived", "Series ID": "FWD21", "Unit": "Decimal", "Transformation": "(SPY.shift(-21) / SPY - 1)", "Seasonal Adj": "N/A", "Known Quirks": "Look-ahead variable", "Refresh Freq": "Daily", "Refresh Source": "Computed"},
        {"Column Name": "spy_fwd_63d", "Display Name": "SPY Fwd Return 3M", "Display Note": "S&P 500 return over the next quarter", "Description": "63-day forward SPY return", "Source": "Derived", "Series ID": "FWD63", "Unit": "Decimal", "Transformation": "(SPY.shift(-63) / SPY - 1)", "Seasonal Adj": "N/A", "Known Quirks": "Look-ahead variable", "Refresh Freq": "Daily", "Refresh Source": "Computed"},
        {"Column Name": "spy_fwd_126d", "Display Name": "SPY Fwd Return 6M", "Display Note": "S&P 500 return over the next 6 months", "Description": "126-day forward SPY return", "Source": "Derived", "Series ID": "FWD126", "Unit": "Decimal", "Transformation": "(SPY.shift(-126) / SPY - 1)", "Seasonal Adj": "N/A", "Known Quirks": "Look-ahead variable", "Refresh Freq": "Daily", "Refresh Source": "Computed"},
        {"Column Name": "spy_fwd_252d", "Display Name": "SPY Fwd Return 1Y", "Display Note": "S&P 500 return over the next year", "Description": "252-day forward SPY return", "Source": "Derived", "Series ID": "FWD252", "Unit": "Decimal", "Transformation": "(SPY.shift(-252) / SPY - 1)", "Seasonal Adj": "N/A", "Known Quirks": "Look-ahead variable; last 252 obs are NaN", "Refresh Freq": "Daily", "Refresh Source": "Computed"},
    ]
    return entries


# ---------------------------------------------------------------------------
# Main Pipeline
# ---------------------------------------------------------------------------

def main():
    print("=" * 70)
    print("HY-IG Credit Spread vs SPY — Data Pipeline")
    print(f"Sample: {START_DATE} to {END_DATE}")
    print("=" * 70)

    # Step 1: Source FRED data
    print("\n[1/8] Sourcing FRED series...")
    fred_data = source_fred_series()
    print(f"  -> {len(fred_data)} FRED series sourced")

    # Step 2: Source Yahoo data
    print("\n[2/8] Sourcing Yahoo Finance series...")
    yahoo_data, unavailable_yahoo = source_yahoo_series()
    print(f"  -> {len(yahoo_data)} Yahoo series sourced, {len(unavailable_yahoo)} unavailable")

    # Combine all series
    all_series = {**fred_data, **yahoo_data}
    print(f"\n  Total raw series: {len(all_series)}")

    # Step 3: Align to common calendar
    print("\n[3/8] Aligning to business-day calendar...")
    weekly_cols = {"nfci", "fsi", "initial_claims"}
    df = align_to_bday_calendar(all_series, weekly_cols)
    print(f"  -> Shape: {df.shape}")

    # Step 4: Compute derived series
    print("\n[4/8] Computing 20 derived series...")
    df = compute_derived(df)
    print(f"  -> Shape after derived: {df.shape}")

    # Step 5: Compute forward returns
    print("\n[5/8] Computing forward SPY returns...")
    df = compute_forward_returns(df)
    print(f"  -> Shape after forward returns: {df.shape}")

    # Step 6: Stationarity tests
    print("\n[6/8] Running stationarity tests (ADF + KPSS)...")
    stationarity_df = run_stationarity_tests(df)
    stationarity_path = os.path.join(RESULTS_DIR, "stationarity_tests_20260228.csv")
    stationarity_df.to_csv(stationarity_path, index=False)
    print(f"  -> Saved to {stationarity_path}")
    print(f"  -> {len(stationarity_df)} test results")

    # Step 7: Quality reports
    print("\n[7/8] Generating quality reports...")

    # Missing value report
    missing_report = generate_missing_report(df, unavailable_yahoo)
    missing_path = os.path.join(OUTPUT_DIR, "missing_value_report_20260228.md")
    with open(missing_path, "w") as f:
        f.write(missing_report)
    print(f"  -> Missing report: {missing_path}")

    # Summary statistics
    summary = df.describe().T
    summary["skewness"] = df.skew()
    summary["kurtosis"] = df.kurtosis()
    summary_path = os.path.join(OUTPUT_DIR, "summary_stats_20260228.csv")
    summary.to_csv(summary_path)
    print(f"  -> Summary stats: {summary_path}")

    # Data dictionary
    dict_entries = generate_data_dictionary()
    dict_df = pd.DataFrame(dict_entries)
    dict_path = os.path.join(OUTPUT_DIR, "data_dictionary_hy_ig_spy_20260228.csv")
    dict_df.to_csv(dict_path, index=False)
    print(f"  -> Data dictionary: {dict_path}")

    # Step 8: Save master dataset
    print("\n[8/8] Saving master dataset...")
    master_path = os.path.join(OUTPUT_DIR, "hy_ig_spy_daily_20000101_20251231.parquet")
    df.to_parquet(master_path, engine="pyarrow")
    print(f"  -> Master: {master_path}")

    # Latest alias (copy, not symlink — more portable)
    latest_path = os.path.join(OUTPUT_DIR, "hy_ig_spy_daily_latest.parquet")
    df.to_parquet(latest_path, engine="pyarrow")
    print(f"  -> Latest alias: {latest_path}")

    # Final summary
    print("\n" + "=" * 70)
    print("Pipeline Complete")
    print("=" * 70)
    print(f"  Rows: {df.shape[0]}")
    print(f"  Columns: {df.shape[1]}")
    print(f"  Date range: {df.index.min().date()} to {df.index.max().date()}")
    print(f"  Raw series sourced: {len(all_series)}/23")
    if unavailable_yahoo:
        print(f"  Unavailable: {[t for t, _, _ in unavailable_yahoo]}")
    print(f"  Derived series: 20")
    print(f"  Forward return horizons: 6")

    # Print column list
    print(f"\n  All columns ({len(df.columns)}):")
    for i, col in enumerate(df.columns, 1):
        missing_pct = df[col].isna().mean() * 100
        print(f"    {i:3d}. {col:<30s} ({missing_pct:.1f}% missing)")

    return df


if __name__ == "__main__":
    main()
