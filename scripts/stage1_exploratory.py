"""
Stage 1 — Exploratory Analysis
HY-IG Credit Spread vs S&P 500 Returns

Author: Evan (Econometrics Agent)
Date: 2026-02-28
"""

import numpy as np
import pandas as pd
from scipy import stats
from scipy.spatial.distance import pdist, squareform
import warnings
warnings.filterwarnings('ignore')

# ── Load data ────────────────────────────────────────────────────────────────
df = pd.read_parquet('/workspaces/aig-rlic-plus/data/hy_ig_spy_daily_20000101_20251231.parquet')
print(f"Dataset: {df.shape[0]} rows x {df.shape[1]} columns")
print(f"Date range: {df.index.min()} to {df.index.max()}")

OUT = '/workspaces/aig-rlic-plus/results/exploratory_20260228'

# Compute daily SPY returns
df['spy_ret'] = df['spy'].pct_change()
# Compute HY-IG spread daily change
df['hy_ig_spread_chg'] = df['hy_ig_spread'].diff()

# ── 1. Correlation Suite ─────────────────────────────────────────────────────
print("\n=== 1. Correlation Suite ===")

# Signals to correlate
spread_signals = {
    'hy_ig_spread': 'HY-IG Spread Level',
    'hy_ig_spread_chg': 'HY-IG Spread Change',
    'hy_ig_zscore_252d': 'HY-IG Z-Score 252d',
    'hy_ig_zscore_504d': 'HY-IG Z-Score 504d',
    'hy_ig_pctrank_504d': 'HY-IG Pctrank 504d',
    'hy_ig_pctrank_1260d': 'HY-IG Pctrank 1260d',
    'hy_ig_roc_21d': 'HY-IG RoC 21d',
    'hy_ig_roc_63d': 'HY-IG RoC 63d',
    'hy_ig_roc_126d': 'HY-IG RoC 126d',
    'hy_ig_mom_21d': 'HY-IG MoM 21d',
    'hy_ig_mom_63d': 'HY-IG MoM 63d',
    'hy_ig_mom_252d': 'HY-IG MoM 252d',
    'hy_ig_acceleration': 'Spread Acceleration',
    'ccc_bb_spread': 'CCC-BB Spread',
}

fwd_cols = ['spy_fwd_1d', 'spy_fwd_5d', 'spy_fwd_21d', 'spy_fwd_63d', 'spy_fwd_126d', 'spy_fwd_252d']

corr_rows = []
for sig_col, sig_name in spread_signals.items():
    for fwd in fwd_cols:
        mask = df[sig_col].notna() & df[fwd].notna()
        x, y = df.loc[mask, sig_col], df.loc[mask, fwd]
        if len(x) < 100:
            continue
        pr, pr_p = stats.pearsonr(x, y)
        sr, sr_p = stats.spearmanr(x, y)
        kr, kr_p = stats.kendalltau(x, y)
        corr_rows.append({
            'signal': sig_name,
            'signal_col': sig_col,
            'forward_return': fwd,
            'n_obs': len(x),
            'pearson_r': pr, 'pearson_p': pr_p,
            'spearman_r': sr, 'spearman_p': sr_p,
            'kendall_tau': kr, 'kendall_p': kr_p,
        })

corr_df = pd.DataFrame(corr_rows)

# Rolling 252d Pearson correlation: HY-IG spread change vs SPY daily return
roll_corr = df[['hy_ig_spread_chg', 'spy_ret']].dropna().rolling(252).corr()
# Extract just the cross-correlation
idx = roll_corr.index.get_level_values(1)
rolling_pearson = roll_corr.loc[idx == 'hy_ig_spread_chg', 'spy_ret'].droplevel(1)
rolling_pearson.name = 'rolling_252d_pearson'

# Distance correlation (dcor) — full sample and rolling would be expensive, do full sample
def distance_correlation(x, y):
    n = len(x)
    a = squareform(pdist(x.values.reshape(-1, 1), 'euclidean'))
    b = squareform(pdist(y.values.reshape(-1, 1), 'euclidean'))
    A = a - a.mean(axis=0) - a.mean(axis=1, keepdims=True) + a.mean()
    B = b - b.mean(axis=0) - b.mean(axis=1, keepdims=True) + b.mean()
    dcov2 = (A * B).mean()
    dvar_x = (A * A).mean()
    dvar_y = (B * B).mean()
    if dvar_x * dvar_y == 0:
        return 0.0
    return np.sqrt(dcov2 / np.sqrt(dvar_x * dvar_y))

# Subsample for distance correlation (expensive O(n^2))
np.random.seed(42)
mask_dcor = df[['hy_ig_spread_chg', 'spy_ret']].dropna().index
sample_idx = np.random.choice(len(mask_dcor), min(3000, len(mask_dcor)), replace=False)
sample_idx.sort()
dcor_sub = df.loc[mask_dcor[sample_idx]]
dcor_val = distance_correlation(dcor_sub['hy_ig_spread_chg'], dcor_sub['spy_ret'])
print(f"Distance correlation (HY-IG chg vs SPY ret, n={len(sample_idx)}): {dcor_val:.4f}")

# Add distance correlation as a note row
corr_rows.append({
    'signal': 'HY-IG Spread Change (dcor)',
    'signal_col': 'hy_ig_spread_chg',
    'forward_return': 'spy_ret (same day)',
    'n_obs': len(sample_idx),
    'pearson_r': dcor_val, 'pearson_p': np.nan,
    'spearman_r': np.nan, 'spearman_p': np.nan,
    'kendall_tau': np.nan, 'kendall_p': np.nan,
})
corr_df = pd.DataFrame(corr_rows)
corr_df.to_csv(f'{OUT}/correlations.csv', index=False)

# Save rolling correlation
rolling_pearson.to_csv(f'{OUT}/rolling_252d_correlation.csv', header=True)
print(f"Correlations saved: {len(corr_df)} rows")

# ── 2. Cross-Correlation Function (CCF) ─────────────────────────────────────
print("\n=== 2. Cross-Correlation Function ===")
from statsmodels.tsa.ar_model import AutoReg

sub = df[['hy_ig_spread_chg', 'spy_ret']].dropna()

# Pre-whiten: fit AR(5) on each series, use residuals
def prewhiten(series, lags=5):
    model = AutoReg(series.values, lags=lags, old_names=False).fit()
    return pd.Series(model.resid, index=series.index[lags:])

resid_spread = prewhiten(sub['hy_ig_spread_chg'])
resid_spy = prewhiten(sub['spy_ret'])

# Align
common = resid_spread.index.intersection(resid_spy.index)
rs = resid_spread.loc[common].values
ry = resid_spy.loc[common].values

ccf_lags = range(-20, 21)
ccf_vals = []
n = len(rs)
for lag in ccf_lags:
    if lag >= 0:
        c = np.corrcoef(rs[:n-lag] if lag > 0 else rs, ry[lag:] if lag > 0 else ry)[0, 1]
    else:
        c = np.corrcoef(rs[-lag:], ry[:n+lag])[0, 1]
    ccf_vals.append(c)

ccf_df = pd.DataFrame({
    'lag': list(ccf_lags),
    'ccf': ccf_vals,
    'se': 1 / np.sqrt(n)  # approximate SE
})
ccf_df['significant_95'] = np.abs(ccf_df['ccf']) > 1.96 / np.sqrt(n)
ccf_df.to_csv(f'{OUT}/ccf.csv', index=False)
print(f"CCF saved: lags -20 to +20, {ccf_df['significant_95'].sum()} significant at 95%")

# ── 3. Descriptive Stats by Regime ───────────────────────────────────────────
print("\n=== 3. Descriptive Stats by Regime ===")

# Quartiles of HY-IG spread
df['spread_quartile'] = pd.qcut(df['hy_ig_spread'], 4, labels=['Q1_calm', 'Q2', 'Q3', 'Q4_stress'])

regime_rows = []
for q in ['Q1_calm', 'Q2', 'Q3', 'Q4_stress']:
    mask = df['spread_quartile'] == q
    spy_ret_q = df.loc[mask, 'spy_ret'].dropna()
    n = len(spy_ret_q)
    ann_ret = spy_ret_q.mean() * 252
    ann_vol = spy_ret_q.std() * np.sqrt(252)
    sharpe = ann_ret / ann_vol if ann_vol > 0 else np.nan
    # Max drawdown
    cum = (1 + spy_ret_q).cumprod()
    peak = cum.cummax()
    dd = (cum - peak) / peak
    max_dd = dd.min()
    # Mean spread
    mean_spread = df.loc[mask, 'hy_ig_spread'].mean()

    regime_rows.append({
        'regime': q,
        'mean_spread_bps': mean_spread,
        'n_days': n,
        'ann_return': ann_ret,
        'ann_volatility': ann_vol,
        'sharpe_ratio': sharpe,
        'max_drawdown': max_dd,
        'mean_daily_ret': spy_ret_q.mean(),
        'median_daily_ret': spy_ret_q.median(),
        'skewness': spy_ret_q.skew(),
        'kurtosis': spy_ret_q.kurtosis(),
    })

regime_df = pd.DataFrame(regime_rows)
regime_df.to_csv(f'{OUT}/regime_descriptive_stats.csv', index=False)
print(regime_df.to_string(index=False))

# ── 4. KDE Regime Boundaries ─────────────────────────────────────────────────
print("\n=== 4. KDE Regime Boundaries ===")
from scipy.signal import argrelextrema

spread_vals = df['hy_ig_spread'].dropna().values
kde = stats.gaussian_kde(spread_vals, bw_method='silverman')

x_grid = np.linspace(spread_vals.min(), spread_vals.max(), 1000)
density = kde(x_grid)

# Find modes (local maxima) and antimodes (local minima)
modes_idx = argrelextrema(density, np.greater, order=20)[0]
antimodes_idx = argrelextrema(density, np.less, order=20)[0]

kde_df = pd.DataFrame({
    'x': x_grid,
    'density': density,
})

# Save mode/antimode info
boundaries = []
for idx in modes_idx:
    boundaries.append({'type': 'mode', 'spread_value': x_grid[idx], 'density': density[idx]})
for idx in antimodes_idx:
    boundaries.append({'type': 'antimode', 'spread_value': x_grid[idx], 'density': density[idx]})

boundaries_df = pd.DataFrame(boundaries)
kde_df.to_csv(f'{OUT}/kde_density.csv', index=False)
boundaries_df.to_csv(f'{OUT}/kde_boundaries.csv', index=False)
print(f"KDE modes: {len(modes_idx)}, antimodes: {len(antimodes_idx)}")
print(boundaries_df.to_string(index=False))

# ── Summary ──────────────────────────────────────────────────────────────────
print("\n=== Stage 1 Complete ===")
print(f"Files saved to {OUT}/:")
print("  - correlations.csv")
print("  - rolling_252d_correlation.csv")
print("  - ccf.csv")
print("  - regime_descriptive_stats.csv")
print("  - kde_density.csv")
print("  - kde_boundaries.csv")
