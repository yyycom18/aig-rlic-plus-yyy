"""
Stage 3 — Combinatorial Tournament Backtest
HY-IG Credit Spread vs S&P 500 Returns

Author: Evan (Econometrics Agent)
Date: 2026-02-28
"""

import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

# ── Load Data ────────────────────────────────────────────────────────────────
df = pd.read_parquet('/workspaces/aig-rlic-plus/data/hy_ig_spy_daily_20000101_20251231.parquet')
df['spy_ret'] = df['spy'].pct_change()

# Load model outputs from Stage 2
CORE = '/workspaces/aig-rlic-plus/results/core_models_20260228'

# HMM states
try:
    hmm2 = pd.read_parquet(f'{CORE}/hmm_states_2state.parquet')
    df['hmm_2state'] = hmm2['hmm_state']
    df['hmm_2state_prob_stress'] = hmm2['prob_state_0']  # state 0 = high VIX = stress
except:
    df['hmm_2state'] = np.nan
    df['hmm_2state_prob_stress'] = np.nan

try:
    hmm3 = pd.read_parquet(f'{CORE}/hmm_states_3state.parquet')
    df['hmm_3state'] = hmm3['hmm_state']
except:
    df['hmm_3state'] = np.nan

# Markov-Switching regime probabilities
try:
    ms2 = pd.read_parquet(f'{CORE}/markov_regime_probs_2state.parquet')
    df['ms_2state_stress_prob'] = ms2['regime_1_prob']  # regime 1 = high variance = stress
except:
    df['ms_2state_stress_prob'] = np.nan

try:
    ms3 = pd.read_parquet(f'{CORE}/markov_regime_probs_3state.parquet')
    # For 3-state, find the highest-variance regime
    df['ms_3state_stress_prob'] = ms3.iloc[:, -1]  # last regime typically high var
except:
    df['ms_3state_stress_prob'] = np.nan

# RF probabilities
try:
    rf_probs = pd.read_csv(f'{CORE}/rf_probabilities.csv', index_col=0, parse_dates=True)
    df['rf_prob'] = rf_probs.iloc[:, 0]
except:
    df['rf_prob'] = np.nan

# Composite signal: equal weight of z-score and VIX term structure (both normalized)
zscore_norm = (df['hy_ig_zscore_252d'] - df['hy_ig_zscore_252d'].mean()) / df['hy_ig_zscore_252d'].std()
vts_norm = -(df['vix_term_structure'] - df['vix_term_structure'].mean()) / df['vix_term_structure'].std()
df['composite_zscore_vts'] = 0.5 * zscore_norm + 0.5 * vts_norm

# ── Define Signals ───────────────────────────────────────────────────────────
signals_config = {
    'S1':  {'col': 'hy_ig_spread', 'thresholds': ['T1', 'T2', 'T3']},
    'S2a': {'col': 'hy_ig_zscore_252d', 'thresholds': ['T1', 'T2', 'T3']},
    'S2b': {'col': 'hy_ig_zscore_504d', 'thresholds': ['T1', 'T2', 'T3']},
    'S3a': {'col': 'hy_ig_pctrank_504d', 'thresholds': ['T1', 'T2', 'T3']},
    'S3b': {'col': 'hy_ig_pctrank_1260d', 'thresholds': ['T1', 'T2', 'T3']},
    'S4a': {'col': 'hy_ig_roc_21d', 'thresholds': ['T1', 'T2', 'T3']},
    'S4b': {'col': 'hy_ig_roc_63d', 'thresholds': ['T1', 'T2', 'T3']},
    'S4c': {'col': 'hy_ig_roc_126d', 'thresholds': ['T1', 'T2', 'T3']},
    'S5':  {'col': 'ccc_bb_spread', 'thresholds': ['T1', 'T2', 'T3']},
    'S6':  {'col': 'hmm_2state_prob_stress', 'thresholds': ['T4']},
    'S7':  {'col': 'ms_2state_stress_prob', 'thresholds': ['T5']},
    'S8':  {'col': 'composite_zscore_vts', 'thresholds': ['T1', 'T2', 'T3']},
    'S9':  {'col': 'rf_prob', 'thresholds': ['T_RF']},
    'S10': {'col': 'hy_ig_mom_21d', 'thresholds': ['T1', 'T2', 'T3']},
    'S11': {'col': 'hy_ig_mom_63d', 'thresholds': ['T1', 'T2', 'T3']},
    'S12': {'col': 'hy_ig_mom_252d', 'thresholds': ['T1', 'T2', 'T3']},
    'S13': {'col': 'hy_ig_acceleration', 'thresholds': ['T1', 'T2', 'T3']},
}

lead_times = [0, 1, 5, 10, 21, 63]

threshold_methods = {
    'T1_75': lambda s: s.quantile(0.75),
    'T1_85': lambda s: s.quantile(0.85),
    'T1_95': lambda s: s.quantile(0.95),
    'T2_75': lambda s: s.rolling(504, min_periods=252).quantile(0.75),
    'T2_85': lambda s: s.rolling(504, min_periods=252).quantile(0.85),
    'T2_95': lambda s: s.rolling(504, min_periods=252).quantile(0.95),
    'T3_1.5': lambda s: s.rolling(252, min_periods=126).mean() + 1.5 * s.rolling(252, min_periods=126).std(),
    'T3_2.0': lambda s: s.rolling(252, min_periods=126).mean() + 2.0 * s.rolling(252, min_periods=126).std(),
    'T3_2.5': lambda s: s.rolling(252, min_periods=126).mean() + 2.5 * s.rolling(252, min_periods=126).std(),
    'T4_0.5': lambda s: pd.Series(0.5, index=s.index),  # HMM prob threshold
    'T4_0.7': lambda s: pd.Series(0.7, index=s.index),
    'T5_0.5': lambda s: pd.Series(0.5, index=s.index),  # MS prob threshold
    'T5_0.7': lambda s: pd.Series(0.7, index=s.index),
    'T_RF_0.5': lambda s: pd.Series(0.5, index=s.index),
    'T_RF_0.6': lambda s: pd.Series(0.6, index=s.index),
    'T_RF_0.7': lambda s: pd.Series(0.7, index=s.index),
}

# Map signal threshold types to threshold methods
threshold_map = {
    'T1': ['T1_75', 'T1_85', 'T1_95'],
    'T2': ['T2_75', 'T2_85', 'T2_95'],
    'T3': ['T3_1.5', 'T3_2.0', 'T3_2.5'],
    'T4': ['T4_0.5', 'T4_0.7'],
    'T5': ['T5_0.5', 'T5_0.7'],
    'T_RF': ['T_RF_0.5', 'T_RF_0.6', 'T_RF_0.7'],
}

strategies = {
    'P1': 'Long/Cash',
    'P2': 'Signal-Strength',
    'P3': 'Long/Short',
}

IS_END = '2017-12-31'
OOS_START = '2018-01-01'

# ── Metrics ──────────────────────────────────────────────────────────────────
def compute_metrics(returns, label=''):
    """Compute strategy performance metrics on a returns series."""
    r = returns.dropna()
    if len(r) < 30:
        return {}
    ann_ret = r.mean() * 252
    ann_vol = r.std() * np.sqrt(252)
    sharpe = ann_ret / ann_vol if ann_vol > 0 else np.nan
    downside = r[r < 0].std() * np.sqrt(252) if (r < 0).sum() > 10 else np.nan
    sortino = ann_ret / downside if downside and downside > 0 else np.nan
    # Max drawdown
    cum = (1 + r).cumprod()
    peak = cum.cummax()
    dd = (cum - peak) / peak
    max_dd = dd.min()
    calmar = ann_ret / abs(max_dd) if max_dd != 0 else np.nan
    avg_dd = dd[dd < 0].mean() if (dd < 0).any() else 0
    win_rate = (r > 0).mean()
    n_days = len(r)

    return {
        'ann_return': ann_ret,
        'ann_vol': ann_vol,
        'sharpe': sharpe,
        'sortino': sortino,
        'calmar': calmar,
        'max_drawdown': max_dd,
        'avg_drawdown': avg_dd,
        'win_rate': win_rate,
        'n_days': n_days,
    }

# ── Tournament Loop ──────────────────────────────────────────────────────────
print("=== Starting Tournament ===")
results = []
n_combos = 0

spy_daily_ret = df['spy_ret']

for sig_id, sig_cfg in signals_config.items():
    col = sig_cfg['col']
    if col not in df.columns or df[col].isna().all():
        continue
    signal_raw = df[col]

    for lead in lead_times:
        lagged_signal = signal_raw.shift(lead)

        for thresh_type in sig_cfg['thresholds']:
            for thresh_name in threshold_map.get(thresh_type, []):
                thresh_func = threshold_methods[thresh_name]

                # Compute threshold
                if thresh_name.startswith('T1_'):
                    # Fixed percentile — use IS sample only
                    is_signal = lagged_signal.loc[:IS_END].dropna()
                    if len(is_signal) < 100:
                        continue
                    thresh_val = thresh_func(is_signal)
                    threshold = pd.Series(thresh_val, index=lagged_signal.index)
                elif thresh_name.startswith(('T2_', 'T3_')):
                    threshold = thresh_func(lagged_signal)
                else:
                    threshold = thresh_func(lagged_signal)

                # For RF signal, higher prob = more bullish (invert logic)
                if sig_id == 'S9':
                    # RF prob > threshold → go long
                    stressed = lagged_signal < threshold
                else:
                    stressed = lagged_signal > threshold

                for strat_id, strat_name in strategies.items():
                    if strat_id == 'P1':
                        # Long when not stressed, cash when stressed
                        positions = (~stressed).astype(float)
                    elif strat_id == 'P2':
                        # Signal-strength sizing
                        if sig_id == 'S9':
                            positions = lagged_signal.clip(0, 1)
                        else:
                            sig_min = lagged_signal.rolling(504, min_periods=252).min()
                            sig_max = lagged_signal.rolling(504, min_periods=252).max()
                            sig_range = sig_max - sig_min
                            sig_norm = (lagged_signal - sig_min) / sig_range.replace(0, np.nan)
                            positions = (1 - sig_norm).clip(0, 1)
                    elif strat_id == 'P3':
                        # Long when calm, short when stressed
                        positions = (~stressed).astype(float) * 2 - 1  # 1 or -1

                    # Apply positions (shift 1 day to avoid lookahead)
                    strategy_returns = positions.shift(1) * spy_daily_ret

                    # Compute trades / turnover
                    pos_changes = positions.diff().abs()
                    n_trades_total = (pos_changes > 0).sum()

                    # IS metrics
                    is_ret = strategy_returns.loc[:IS_END]
                    oos_ret = strategy_returns.loc[OOS_START:]

                    # Skip if too many NaNs in OOS
                    oos_valid = oos_ret.dropna()
                    if len(oos_valid) < 30:
                        continue

                    oos_nan_pct = oos_ret.isna().mean()
                    if oos_nan_pct > 0.5:
                        continue

                    is_metrics = compute_metrics(is_ret)
                    oos_metrics = compute_metrics(oos_ret)

                    if not oos_metrics:
                        continue

                    # Turnover
                    oos_trades = (pos_changes.loc[OOS_START:] > 0).sum()
                    oos_years = len(oos_valid) / 252
                    annual_turnover = oos_trades / oos_years if oos_years > 0 else np.nan

                    # Validity
                    valid = (
                        oos_metrics.get('sharpe', -1) >= 0 and
                        annual_turnover <= 24 and
                        oos_trades >= 30
                    ) if not np.isnan(annual_turnover) else False

                    results.append({
                        'signal_id': sig_id,
                        'signal_col': col,
                        'lead_time': lead,
                        'threshold_method': thresh_name,
                        'strategy_id': strat_id,
                        'strategy_name': strat_name,
                        'is_sharpe': is_metrics.get('sharpe', np.nan),
                        'is_ann_return': is_metrics.get('ann_return', np.nan),
                        'oos_sharpe': oos_metrics.get('sharpe', np.nan),
                        'oos_sortino': oos_metrics.get('sortino', np.nan),
                        'oos_calmar': oos_metrics.get('calmar', np.nan),
                        'oos_max_dd': oos_metrics.get('max_drawdown', np.nan),
                        'oos_ann_return': oos_metrics.get('ann_return', np.nan),
                        'oos_ann_vol': oos_metrics.get('ann_vol', np.nan),
                        'oos_win_rate': oos_metrics.get('win_rate', np.nan),
                        'n_trades': oos_trades,
                        'annual_turnover': annual_turnover,
                        'valid': valid,
                    })
                    n_combos += 1

    if n_combos % 100 == 0 and n_combos > 0:
        print(f"  Processed {n_combos} combinations...")

# ── Benchmark: Buy & Hold SPY ────────────────────────────────────────────────
bh_oos = spy_daily_ret.loc[OOS_START:].dropna()
bh_metrics = compute_metrics(bh_oos)
results.append({
    'signal_id': 'BH', 'signal_col': 'spy', 'lead_time': 0,
    'threshold_method': 'none', 'strategy_id': 'BH', 'strategy_name': 'Buy&Hold SPY',
    'is_sharpe': compute_metrics(spy_daily_ret.loc[:IS_END]).get('sharpe', np.nan),
    'is_ann_return': compute_metrics(spy_daily_ret.loc[:IS_END]).get('ann_return', np.nan),
    'oos_sharpe': bh_metrics.get('sharpe', np.nan),
    'oos_sortino': bh_metrics.get('sortino', np.nan),
    'oos_calmar': bh_metrics.get('calmar', np.nan),
    'oos_max_dd': bh_metrics.get('max_drawdown', np.nan),
    'oos_ann_return': bh_metrics.get('ann_return', np.nan),
    'oos_ann_vol': bh_metrics.get('ann_vol', np.nan),
    'oos_win_rate': bh_metrics.get('win_rate', np.nan),
    'n_trades': 0, 'annual_turnover': 0, 'valid': True,
})

# ── Save & Summarize ─────────────────────────────────────────────────────────
results_df = pd.DataFrame(results)
results_df.to_csv('/workspaces/aig-rlic-plus/results/tournament_results_20260228.csv', index=False)

print(f"\n=== Tournament Complete ===")
print(f"Total combinations tested: {n_combos}")
print(f"Valid combinations: {results_df['valid'].sum()}")
print(f"Buy & Hold SPY OOS Sharpe: {bh_metrics.get('sharpe', np.nan):.3f}")

# Top 10 by OOS Sharpe
valid_df = results_df[results_df['valid'] == True].sort_values('oos_sharpe', ascending=False)
print(f"\nTop 10 valid strategies by OOS Sharpe:")
top10_cols = ['signal_id', 'lead_time', 'threshold_method', 'strategy_id',
              'oos_sharpe', 'oos_sortino', 'oos_ann_return', 'oos_max_dd', 'annual_turnover']
print(valid_df[top10_cols].head(10).to_string(index=False))

print(f"\nBottom of valid (worst OOS Sharpe):")
print(valid_df[top10_cols].tail(5).to_string(index=False))
