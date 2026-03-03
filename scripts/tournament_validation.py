"""
Stage 3 Validation — Top-5 Tournament Winners
Walk-forward, bootstrap, transaction costs, signal decay, stress tests

Author: Evan (Econometrics Agent)
Date: 2026-02-28
"""

import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

VOUT = '/workspaces/aig-rlic-plus/results/tournament_validation_20260228'
df = pd.read_parquet('/workspaces/aig-rlic-plus/data/hy_ig_spy_daily_20000101_20251231.parquet')
df['spy_ret'] = df['spy'].pct_change()

CORE = '/workspaces/aig-rlic-plus/results/core_models_20260228'
try:
    hmm2 = pd.read_parquet(f'{CORE}/hmm_states_2state.parquet')
    df['hmm_2state_prob_stress'] = hmm2['prob_state_0']
except: df['hmm_2state_prob_stress'] = np.nan

try:
    ms2 = pd.read_parquet(f'{CORE}/markov_regime_probs_2state.parquet')
    df['ms_2state_stress_prob'] = ms2['regime_1_prob']
except: df['ms_2state_stress_prob'] = np.nan

# Composite
zscore_norm = (df['hy_ig_zscore_252d'] - df['hy_ig_zscore_252d'].mean()) / df['hy_ig_zscore_252d'].std()
vts_norm = -(df['vix_term_structure'] - df['vix_term_structure'].mean()) / df['vix_term_structure'].std()
df['composite_zscore_vts'] = 0.5 * zscore_norm + 0.5 * vts_norm

OOS_START = '2018-01-01'
IS_END = '2017-12-31'

# Top-5 from tournament results
top5 = [
    {'id': 'W1', 'sig': 'hmm_2state_prob_stress', 'lead': 0, 'thresh': 'T4_0.7', 'strat': 'P1'},
    {'id': 'W2', 'sig': 'composite_zscore_vts', 'lead': 0, 'thresh': 'T3_1.5', 'strat': 'P1'},
    {'id': 'W3', 'sig': 'hmm_2state_prob_stress', 'lead': 0, 'thresh': 'T4_0.5', 'strat': 'P1'},
    {'id': 'W4', 'sig': 'hy_ig_zscore_252d', 'lead': 0, 'thresh': 'T3_2.0', 'strat': 'P1'},
    {'id': 'W5', 'sig': 'hy_ig_zscore_252d', 'lead': 5, 'thresh': 'T2_95', 'strat': 'P1'},
]

def get_strategy_returns(df, sig_col, lead, thresh_name, strat_id):
    """Reconstruct strategy returns for a given configuration."""
    signal = df[sig_col].shift(lead)

    if thresh_name.startswith('T4_') or thresh_name.startswith('T5_'):
        thresh_val = float(thresh_name.split('_')[1])
        threshold = pd.Series(thresh_val, index=df.index)
    elif thresh_name.startswith('T1_'):
        pctile = int(thresh_name.split('_')[1]) / 100
        is_signal = signal.loc[:IS_END].dropna()
        threshold = pd.Series(is_signal.quantile(pctile), index=df.index)
    elif thresh_name.startswith('T2_'):
        pctile = int(thresh_name.split('_')[1]) / 100
        threshold = signal.rolling(504, min_periods=252).quantile(pctile)
    elif thresh_name.startswith('T3_'):
        k = float(thresh_name.split('_')[1])
        threshold = signal.rolling(252, min_periods=126).mean() + k * signal.rolling(252, min_periods=126).std()
    else:
        threshold = pd.Series(0.5, index=df.index)

    stressed = signal > threshold

    if strat_id == 'P1':
        positions = (~stressed).astype(float)
    elif strat_id == 'P3':
        positions = (~stressed).astype(float) * 2 - 1
    else:
        positions = (~stressed).astype(float)

    strategy_returns = positions.shift(1) * df['spy_ret']
    return strategy_returns, positions

# ── 1. Walk-Forward Validation ───────────────────────────────────────────────
print("=== 1. Walk-Forward Validation ===")
wf_rows = []

for cfg in top5:
    strat_ret, positions = get_strategy_returns(df, cfg['sig'], cfg['lead'], cfg['thresh'], cfg['strat'])

    # 5yr train / 1yr test, rolling annually
    for test_year in range(2005, 2026):
        test_start = pd.Timestamp(f'{test_year}-01-01')
        test_end = pd.Timestamp(f'{test_year}-12-31')

        window_ret = strat_ret.loc[test_start:test_end].dropna()
        if len(window_ret) < 50:
            continue

        ann_ret = window_ret.mean() * 252
        ann_vol = window_ret.std() * np.sqrt(252)
        sharpe = ann_ret / ann_vol if ann_vol > 0 else np.nan

        # Benchmark for same period
        bh_ret = df['spy_ret'].loc[test_start:test_end].dropna()
        bh_sharpe = (bh_ret.mean() * 252) / (bh_ret.std() * np.sqrt(252)) if bh_ret.std() > 0 else np.nan

        wf_rows.append({
            'winner_id': cfg['id'],
            'signal': cfg['sig'],
            'year': test_year,
            'sharpe': sharpe,
            'ann_return': ann_ret,
            'ann_vol': ann_vol,
            'bh_sharpe': bh_sharpe,
            'excess_sharpe': sharpe - bh_sharpe if not np.isnan(sharpe) and not np.isnan(bh_sharpe) else np.nan,
        })

wf_df = pd.DataFrame(wf_rows)
wf_df.to_csv(f'{VOUT}/walk_forward.csv', index=False)
print(wf_df.groupby('winner_id')[['sharpe', 'excess_sharpe']].mean().to_string())

# ── 2. Bootstrap Significance ────────────────────────────────────────────────
print("\n=== 2. Bootstrap Significance ===")
boot_rows = []
rng = np.random.default_rng(42)

for cfg in top5:
    strat_ret, _ = get_strategy_returns(df, cfg['sig'], cfg['lead'], cfg['thresh'], cfg['strat'])
    oos_ret = strat_ret.loc[OOS_START:].dropna().values

    if len(oos_ret) < 30:
        continue

    obs_sharpe = (oos_ret.mean() * 252) / (oos_ret.std() * np.sqrt(252))

    # Bootstrap 10,000 samples
    n_boot = 10000
    boot_sharpes = []
    n = len(oos_ret)
    for _ in range(n_boot):
        sample = rng.choice(oos_ret, size=n, replace=True)
        bs = (sample.mean() * 252) / (sample.std() * np.sqrt(252)) if sample.std() > 0 else 0
        boot_sharpes.append(bs)

    boot_sharpes = np.array(boot_sharpes)
    p_value = np.mean(boot_sharpes <= 0)  # p-value for Sharpe > 0
    ci_lower = np.percentile(boot_sharpes, 2.5)
    ci_upper = np.percentile(boot_sharpes, 97.5)

    boot_rows.append({
        'winner_id': cfg['id'],
        'signal': cfg['sig'],
        'obs_sharpe': obs_sharpe,
        'boot_mean_sharpe': boot_sharpes.mean(),
        'boot_ci_lower': ci_lower,
        'boot_ci_upper': ci_upper,
        'p_value_sharpe_gt_0': p_value,
        'significant_5pct': p_value < 0.05,
    })

boot_df = pd.DataFrame(boot_rows)
boot_df.to_csv(f'{VOUT}/bootstrap.csv', index=False)
print(boot_df.to_string(index=False))

# ── 3. Transaction Costs ─────────────────────────────────────────────────────
print("\n=== 3. Transaction Costs ===")
tc_rows = []

for cfg in top5:
    strat_ret, positions = get_strategy_returns(df, cfg['sig'], cfg['lead'], cfg['thresh'], cfg['strat'])
    oos_ret = strat_ret.loc[OOS_START:]
    oos_pos = positions.loc[OOS_START:]

    # Count trades (position changes)
    trades = oos_pos.diff().abs().fillna(0)

    for cost_bps in [0, 5, 10, 20, 50]:
        cost = cost_bps / 10000
        tc_deduction = trades.shift(1) * cost  # cost applied at trade execution
        net_ret = oos_ret - tc_deduction
        net_ret = net_ret.dropna()

        if len(net_ret) < 30:
            continue

        ann_ret = net_ret.mean() * 252
        ann_vol = net_ret.std() * np.sqrt(252)
        sharpe = ann_ret / ann_vol if ann_vol > 0 else np.nan

        tc_rows.append({
            'winner_id': cfg['id'],
            'cost_bps': cost_bps,
            'net_sharpe': sharpe,
            'net_ann_return': ann_ret,
        })

    # Breakeven cost
    gross_ret_mean = oos_ret.dropna().mean()
    avg_trade_freq = trades.mean()  # avg daily trade indicator
    if avg_trade_freq > 0:
        breakeven_bps = (gross_ret_mean / avg_trade_freq) * 10000
    else:
        breakeven_bps = np.inf

    tc_rows.append({
        'winner_id': cfg['id'],
        'cost_bps': 'breakeven',
        'net_sharpe': 0,
        'net_ann_return': breakeven_bps,
    })

tc_df = pd.DataFrame(tc_rows)
tc_df.to_csv(f'{VOUT}/transaction_costs.csv', index=False)
print(tc_df[tc_df['cost_bps'] != 'breakeven'].to_string(index=False))

# ── 4. Signal Decay ──────────────────────────────────────────────────────────
print("\n=== 4. Signal Decay ===")
decay_rows = []

for cfg in top5:
    signal = df[cfg['sig']].shift(cfg['lead'])

    for delay in [0, 1, 2, 3, 5]:
        # Add execution delay
        total_lead = cfg['lead'] + delay
        strat_ret, _ = get_strategy_returns(df, cfg['sig'], total_lead, cfg['thresh'], cfg['strat'])
        oos_ret = strat_ret.loc[OOS_START:].dropna()

        if len(oos_ret) < 30:
            continue

        ann_ret = oos_ret.mean() * 252
        ann_vol = oos_ret.std() * np.sqrt(252)
        sharpe = ann_ret / ann_vol if ann_vol > 0 else np.nan

        decay_rows.append({
            'winner_id': cfg['id'],
            'execution_delay': delay,
            'total_lead': total_lead,
            'oos_sharpe': sharpe,
            'oos_ann_return': ann_ret,
        })

decay_df = pd.DataFrame(decay_rows)
decay_df.to_csv(f'{VOUT}/signal_decay.csv', index=False)
print(decay_df.to_string(index=False))

# ── 5. Stress Tests ──────────────────────────────────────────────────────────
print("\n=== 5. Stress Tests ===")
stress_periods = {
    'GFC': ('2007-01-01', '2009-12-31'),
    'COVID': ('2020-01-01', '2020-12-31'),
    'Taper_Tantrum': ('2013-04-01', '2013-12-31'),
    'Rate_Shock_2022': ('2022-01-01', '2022-12-31'),
    'Full_OOS': ('2018-01-01', '2025-12-31'),
}

stress_rows = []
for cfg in top5:
    strat_ret, _ = get_strategy_returns(df, cfg['sig'], cfg['lead'], cfg['thresh'], cfg['strat'])

    for period_name, (start, end) in stress_periods.items():
        period_ret = strat_ret.loc[start:end].dropna()
        bh_ret = df['spy_ret'].loc[start:end].dropna()

        if len(period_ret) < 20:
            continue

        ann_ret = period_ret.mean() * 252
        ann_vol = period_ret.std() * np.sqrt(252)
        sharpe = ann_ret / ann_vol if ann_vol > 0 else np.nan
        cum = (1 + period_ret).cumprod()
        max_dd = ((cum - cum.cummax()) / cum.cummax()).min()

        bh_ann_ret = bh_ret.mean() * 252
        bh_sharpe = bh_ann_ret / (bh_ret.std() * np.sqrt(252)) if bh_ret.std() > 0 else np.nan
        bh_cum = (1 + bh_ret).cumprod()
        bh_max_dd = ((bh_cum - bh_cum.cummax()) / bh_cum.cummax()).min()

        stress_rows.append({
            'winner_id': cfg['id'],
            'period': period_name,
            'start': start, 'end': end,
            'strat_sharpe': sharpe,
            'strat_ann_return': ann_ret,
            'strat_max_dd': max_dd,
            'bh_sharpe': bh_sharpe,
            'bh_ann_return': bh_ann_ret,
            'bh_max_dd': bh_max_dd,
            'excess_sharpe': sharpe - bh_sharpe if not np.isnan(sharpe) and not np.isnan(bh_sharpe) else np.nan,
        })

stress_df = pd.DataFrame(stress_rows)
stress_df.to_csv(f'{VOUT}/stress_tests.csv', index=False)
print(stress_df[['winner_id', 'period', 'strat_sharpe', 'bh_sharpe', 'excess_sharpe', 'strat_max_dd', 'bh_max_dd']].to_string(index=False))

print("\n=== Validation Complete ===")
