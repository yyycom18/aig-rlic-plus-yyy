"""
Stage 2 — Core Models
HY-IG Credit Spread vs S&P 500 Returns

Author: Evan (Econometrics Agent)
Date: 2026-02-28
"""

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
from statsmodels.tsa.api import VAR
from statsmodels.tsa.stattools import grangercausalitytests
from statsmodels.tsa.vector_ar.vecm import coint_johansen
import pickle
import warnings
warnings.filterwarnings('ignore')

OUT = '/workspaces/aig-rlic-plus/results/core_models_20260228'
df = pd.read_parquet('/workspaces/aig-rlic-plus/data/hy_ig_spy_daily_20000101_20251231.parquet')
df['spy_ret'] = df['spy'].pct_change()
df['hy_ig_spread_chg'] = df['hy_ig_spread'].diff()
df['log_spy'] = np.log(df['spy'])

# Quartile regime
df['spread_quartile'] = pd.qcut(df['hy_ig_spread'], 4, labels=['Q1', 'Q2', 'Q3', 'Q4'])
df['stress'] = (df['spread_quartile'] == 'Q4').astype(int)

diagnostics_rows = []

def add_diag(model_name, test_name, stat, pval, interp):
    diagnostics_rows.append({
        'model': model_name, 'test': test_name,
        'statistic': stat, 'p_value': pval, 'interpretation': interp
    })

# ══════════════════════════════════════════════════════════════════════════════
# 1. TODA-YAMAMOTO GRANGER CAUSALITY
# ══════════════════════════════════════════════════════════════════════════════
print("=== 1. Toda-Yamamoto Granger Causality ===")

granger_rows = []
pair_data = df[['hy_ig_spread_chg', 'spy_ret']].dropna()

d_max = 1  # augmentation order

for regime_label, regime_mask in [
    ('full_sample', pd.Series(True, index=pair_data.index)),
    ('stress', df.loc[pair_data.index, 'stress'] == 1),
    ('calm', df.loc[pair_data.index, 'stress'] == 0),
]:
    sub = pair_data.loc[regime_mask].copy()
    if len(sub) < 100:
        continue

    for lag_k in [1, 5, 10, 21]:
        total_lags = lag_k + d_max
        if len(sub) < total_lags + 50:
            continue
        try:
            model = VAR(sub.values)
            result = model.fit(total_lags)

            for direction, col_idx, cause_idx in [
                ('Credit->Equity', 1, 0),  # test if spread_chg Granger-causes spy_ret
                ('Equity->Credit', 0, 1),  # test if spy_ret Granger-causes spread_chg
            ]:
                # Test restriction: coefficients on cause variable at lags 1..k are zero
                # Build restriction matrix
                n_vars = 2
                n_params = total_lags * n_vars + 1  # +1 for const
                R = np.zeros((lag_k, n_params))
                for i in range(lag_k):
                    # Position of cause variable at lag i+1
                    param_pos = i * n_vars + cause_idx + 1  # +1 for const
                    R[i, param_pos] = 1

                # Get params and vcov for the equation of the response variable
                params = result.params[:, col_idx]
                # Flatten params: const, y1_L1, y2_L1, y1_L2, y2_L2, ...
                # statsmodels VAR stores as [const, L1, L2, ...] where each L has n_vars params
                p_flat = np.concatenate([[params[0]], params[1:].flatten()])

                # Use Wald test from the VAR result
                test_result = result.test_causality(
                    caused=sub.columns[col_idx] if hasattr(sub, 'columns') else col_idx,
                    causing=[cause_idx],
                    kind='wald'
                )
                test_stat = test_result.test_statistic
                p_value = test_result.pvalue

                conclusion = 'Reject H0 (causal)' if p_value < 0.05 else 'Fail to reject H0'
                granger_rows.append({
                    'direction': direction,
                    'lag_order': lag_k,
                    'd_max': d_max,
                    'total_lags': total_lags,
                    'regime': regime_label,
                    'n_obs': len(sub),
                    'test_stat': test_stat,
                    'p_value': p_value,
                    'conclusion': conclusion,
                })
        except Exception as e:
            granger_rows.append({
                'direction': 'both', 'lag_order': lag_k, 'd_max': d_max,
                'total_lags': total_lags, 'regime': regime_label,
                'n_obs': len(sub), 'test_stat': np.nan, 'p_value': np.nan,
                'conclusion': f'Error: {str(e)[:80]}'
            })

granger_df = pd.DataFrame(granger_rows)
granger_df.to_csv(f'{OUT}/granger_causality.csv', index=False)
print(f"Granger causality: {len(granger_df)} tests saved")
print(granger_df[['direction', 'lag_order', 'regime', 'p_value', 'conclusion']].to_string(index=False))

# ══════════════════════════════════════════════════════════════════════════════
# 2. TRANSFER ENTROPY (Binning approach)
# ══════════════════════════════════════════════════════════════════════════════
print("\n=== 2. Transfer Entropy ===")

def transfer_entropy_binned(x, y, lag=1, n_bins=5):
    """Compute TE(X->Y) using binning approach."""
    x_lag = pd.Series(x[:-lag]).values
    y_curr = pd.Series(y[lag:]).values
    y_lag = pd.Series(y[:-lag]).values
    # Discretize
    x_d = pd.qcut(x_lag, n_bins, labels=False, duplicates='drop')
    y_d = pd.qcut(y_curr, n_bins, labels=False, duplicates='drop')
    yl_d = pd.qcut(y_lag, n_bins, labels=False, duplicates='drop')

    # Joint distribution p(y_t, y_{t-1}, x_{t-1})
    df_te = pd.DataFrame({'y': y_d, 'yl': yl_d, 'x': x_d}).dropna()
    n = len(df_te)
    if n < 100:
        return np.nan

    # TE = sum p(y,yl,x) * log[ p(y|yl,x) / p(y|yl) ]
    # = sum p(y,yl,x) * log[ p(y,yl,x)*p(yl) / (p(yl,x)*p(y,yl)) ]
    joint_yylx = df_te.groupby(['y', 'yl', 'x']).size() / n
    joint_yyl = df_te.groupby(['y', 'yl']).size() / n
    joint_ylx = df_te.groupby(['yl', 'x']).size() / n
    marg_yl = df_te.groupby('yl').size() / n

    te = 0.0
    for (y_v, yl_v, x_v), p_yylx in joint_yylx.items():
        p_yyl = joint_yyl.get((y_v, yl_v), 0)
        p_ylx = joint_ylx.get((yl_v, x_v), 0)
        p_yl = marg_yl.get(yl_v, 0)
        if p_yyl > 0 and p_ylx > 0 and p_yl > 0:
            te += p_yylx * np.log(p_yylx * p_yl / (p_ylx * p_yyl))
    return te

te_rows = []
pair_clean = pair_data.dropna()
x_spread = pair_clean['hy_ig_spread_chg'].values
y_spy = pair_clean['spy_ret'].values

for lag in [1, 5]:
    te_c2e = transfer_entropy_binned(x_spread, y_spy, lag=lag)
    te_e2c = transfer_entropy_binned(y_spy, x_spread, lag=lag)

    # Bootstrap significance (1000 shuffles)
    n_boot = 1000
    te_c2e_null = []
    te_e2c_null = []
    rng = np.random.default_rng(42)
    for _ in range(n_boot):
        x_shuf = rng.permutation(x_spread)
        te_c2e_null.append(transfer_entropy_binned(x_shuf, y_spy, lag=lag))
        y_shuf = rng.permutation(y_spy)
        te_e2c_null.append(transfer_entropy_binned(y_shuf, x_spread, lag=lag))

    p_c2e = np.mean([t >= te_c2e for t in te_c2e_null if not np.isnan(t)])
    p_e2c = np.mean([t >= te_e2c for t in te_e2c_null if not np.isnan(t)])

    te_rows.append({'direction': 'Credit->Equity', 'lag': lag, 'transfer_entropy': te_c2e,
                    'bootstrap_p': p_c2e, 'significant': p_c2e < 0.05})
    te_rows.append({'direction': 'Equity->Credit', 'lag': lag, 'transfer_entropy': te_e2c,
                    'bootstrap_p': p_e2c, 'significant': p_e2c < 0.05})

te_df = pd.DataFrame(te_rows)
te_df.to_csv(f'{OUT}/transfer_entropy.csv', index=False)
print(te_df.to_string(index=False))

# ══════════════════════════════════════════════════════════════════════════════
# 3. JOHANSEN COINTEGRATION + VECM
# ══════════════════════════════════════════════════════════════════════════════
print("\n=== 3. Johansen Cointegration ===")

coint_data = df[['log_spy', 'hy_ig_spread']].dropna()

# Johansen test
joh_result = coint_johansen(coint_data.values, det_order=0, k_ar_diff=5)

coint_rows = []
for i in range(2):
    coint_rows.append({
        'null_hypothesis': f'r <= {i}',
        'trace_stat': joh_result.lr1[i],
        'trace_cv_5pct': joh_result.cvt[i, 1],
        'trace_reject': joh_result.lr1[i] > joh_result.cvt[i, 1],
        'max_eigen_stat': joh_result.lr2[i],
        'max_eigen_cv_5pct': joh_result.cvm[i, 1],
        'max_eigen_reject': joh_result.lr2[i] > joh_result.cvm[i, 1],
    })

coint_df = pd.DataFrame(coint_rows)
coint_df.to_csv(f'{OUT}/cointegration.csv', index=False)
print(coint_df.to_string(index=False))

coint_found = coint_df.iloc[0]['trace_reject']
if coint_found:
    print("Cointegration FOUND — fitting VECM")
    from statsmodels.tsa.vector_ar.vecm import VECM
    vecm = VECM(coint_data.values, k_ar_diff=5, coint_rank=1, deterministic='co')
    vecm_fit = vecm.fit()
    print("VECM alpha (adjustment coefficients):", vecm_fit.alpha.flatten())
    # Save VECM
    vecm_summary = {
        'alpha_log_spy': vecm_fit.alpha[0, 0],
        'alpha_hy_ig_spread': vecm_fit.alpha[1, 0],
        'beta_log_spy': vecm_fit.beta[0, 0],
        'beta_hy_ig_spread': vecm_fit.beta[1, 0],
    }
    pd.DataFrame([vecm_summary]).to_csv(f'{OUT}/vecm_coefficients.csv', index=False)
else:
    print("No cointegration found — proceed with VAR in differences")

add_diag('Johansen Cointegration', 'Trace (r=0)', joh_result.lr1[0], np.nan,
         'Reject' if coint_df.iloc[0]['trace_reject'] else 'Fail to reject')

# ══════════════════════════════════════════════════════════════════════════════
# 4. MARKOV-SWITCHING REGRESSION
# ══════════════════════════════════════════════════════════════════════════════
print("\n=== 4. Markov-Switching Regression ===")
from statsmodels.tsa.regime_switching.markov_regression import MarkovRegression

ms_data = df[['spy_ret', 'hy_ig_spread_chg']].dropna()

for k_regimes in [2, 3]:
    try:
        ms_model = MarkovRegression(
            ms_data['spy_ret'],
            k_regimes=k_regimes,
            exog=sm.add_constant(ms_data['hy_ig_spread_chg']),
            switching_variance=True,
        )
        ms_fit = ms_model.fit(maxiter=500, em_iter=100)

        # Save coefficients
        ms_params = pd.DataFrame({
            'parameter': ms_fit.params.index,
            'value': ms_fit.params.values,
        })
        ms_params.to_csv(f'{OUT}/markov_switching_{k_regimes}state.csv', index=False)

        # Save regime probabilities
        regime_probs = pd.DataFrame(
            ms_fit.smoothed_marginal_probabilities,
            index=ms_data.index,
            columns=[f'regime_{i}_prob' for i in range(k_regimes)]
        )
        regime_probs.to_parquet(f'{OUT}/markov_regime_probs_{k_regimes}state.parquet')

        print(f"\n{k_regimes}-State Markov-Switching:")
        print(ms_params.to_string(index=False))
        print(f"Log-likelihood: {ms_fit.llf:.2f}, AIC: {ms_fit.aic:.2f}")

        add_diag(f'Markov-Switching {k_regimes}S', 'AIC', ms_fit.aic, np.nan,
                 f'{k_regimes}-state model AIC')

        # Pickle
        with open(f'{OUT}/markov_switching_{k_regimes}state.pkl', 'wb') as f:
            pickle.dump(ms_fit, f)

    except Exception as e:
        print(f"{k_regimes}-State MS failed: {e}")
        pd.DataFrame([{'error': str(e)}]).to_csv(
            f'{OUT}/markov_switching_{k_regimes}state.csv', index=False)

# ══════════════════════════════════════════════════════════════════════════════
# 5. HMM REGIME DETECTION
# ══════════════════════════════════════════════════════════════════════════════
print("\n=== 5. HMM Regime Detection ===")
from hmmlearn.hmm import GaussianHMM

hmm_data = df[['hy_ig_spread_chg', 'vix']].dropna()

for n_states in [2, 3]:
    try:
        hmm = GaussianHMM(
            n_components=n_states,
            covariance_type='full',
            n_iter=500,
            random_state=42,
            tol=1e-4,
        )
        hmm.fit(hmm_data.values)
        states = hmm.predict(hmm_data.values)
        probs = hmm.predict_proba(hmm_data.values)

        # Save states
        hmm_states = pd.DataFrame({
            'date': hmm_data.index,
            'hmm_state': states,
        })
        for i in range(n_states):
            hmm_states[f'prob_state_{i}'] = probs[:, i]
        hmm_states.set_index('date', inplace=True)
        hmm_states.to_parquet(f'{OUT}/hmm_states_{n_states}state.parquet')

        # Transition matrix
        trans = pd.DataFrame(
            hmm.transmat_,
            index=[f'from_state_{i}' for i in range(n_states)],
            columns=[f'to_state_{i}' for i in range(n_states)]
        )
        trans.to_csv(f'{OUT}/hmm_transition_matrix_{n_states}state.csv')

        # Means and covariances
        for i in range(n_states):
            print(f"\n{n_states}-State HMM, State {i}: mean={hmm.means_[i]}, "
                  f"n_obs={np.sum(states==i)}")
        print(f"Transition matrix:\n{trans.to_string()}")

        with open(f'{OUT}/hmm_{n_states}state.pkl', 'wb') as f:
            pickle.dump(hmm, f)

    except Exception as e:
        print(f"{n_states}-State HMM failed: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# 6. CHANGE-POINT DETECTION (PELT)
# ══════════════════════════════════════════════════════════════════════════════
print("\n=== 6. Change-Point Detection (PELT) ===")
import ruptures

spread_series = df['hy_ig_spread'].dropna().values
algo = ruptures.Pelt(model="rbf").fit(spread_series)
bkps = algo.predict(pen=10)

cp_dates = df['hy_ig_spread'].dropna().index
cp_rows = []
for bp in bkps[:-1]:  # last breakpoint is the end
    if bp < len(cp_dates):
        cp_rows.append({
            'breakpoint_index': bp,
            'date': cp_dates[bp],
            'spread_at_break': spread_series[bp] if bp < len(spread_series) else np.nan,
        })

cp_df = pd.DataFrame(cp_rows)
cp_df.to_csv(f'{OUT}/change_points.csv', index=False)
print(f"PELT detected {len(cp_df)} change points:")
print(cp_df.to_string(index=False))

# ══════════════════════════════════════════════════════════════════════════════
# 7. GJR-GARCH
# ══════════════════════════════════════════════════════════════════════════════
print("\n=== 7. GJR-GARCH ===")
from arch import arch_model

garch_data = df[['spy_ret', 'hy_ig_spread_chg']].dropna()
spy_ret_pct = garch_data['spy_ret'] * 100  # arch expects percentage returns

am = arch_model(
    spy_ret_pct,
    x=garch_data[['hy_ig_spread_chg']],
    mean='ARX',
    lags=1,
    vol='GARCH',
    p=1, o=1, q=1,  # GJR-GARCH(1,1)
    dist='normal',
)
garch_fit = am.fit(disp='off')
print(garch_fit.summary().tables[0])
print(garch_fit.summary().tables[1])

garch_params = pd.DataFrame({
    'parameter': garch_fit.params.index,
    'value': garch_fit.params.values,
    'std_err': garch_fit.std_err.values,
    'tstat': garch_fit.tvalues.values,
    'pvalue': garch_fit.pvalues.values,
})
garch_params.to_csv(f'{OUT}/gjr_garch.csv', index=False)
print(garch_params.to_string(index=False))

add_diag('GJR-GARCH', 'Log-Likelihood', garch_fit.loglikelihood, np.nan, 'Model fit')
add_diag('GJR-GARCH', 'AIC', garch_fit.aic, np.nan, 'Model complexity')

with open(f'{OUT}/gjr_garch.pkl', 'wb') as f:
    pickle.dump(garch_fit, f)

# ══════════════════════════════════════════════════════════════════════════════
# 8. QUANTILE REGRESSION
# ══════════════════════════════════════════════════════════════════════════════
print("\n=== 8. Quantile Regression ===")
import statsmodels.formula.api as smf

qr_data = df[['spy_fwd_21d', 'hy_ig_zscore_252d']].dropna()

qr_rows = []
taus = [0.05, 0.10, 0.25, 0.50, 0.75, 0.90]
for tau in taus:
    qr_model = smf.quantreg('spy_fwd_21d ~ hy_ig_zscore_252d', data=qr_data)
    qr_fit = qr_model.fit(q=tau)
    for var in qr_fit.params.index:
        qr_rows.append({
            'quantile': tau,
            'variable': var,
            'coef': qr_fit.params[var],
            'se': qr_fit.bse[var],
            't_stat': qr_fit.tvalues[var],
            'p_value': qr_fit.pvalues[var],
            'ci_lower': qr_fit.conf_int().loc[var, 0],
            'ci_upper': qr_fit.conf_int().loc[var, 1],
        })

qr_df = pd.DataFrame(qr_rows)
qr_df.to_csv(f'{OUT}/quantile_regression.csv', index=False)
print(qr_df.to_string(index=False))

# ══════════════════════════════════════════════════════════════════════════════
# 9. RANDOM FOREST + SHAP
# ══════════════════════════════════════════════════════════════════════════════
print("\n=== 9. Random Forest + SHAP ===")
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, roc_auc_score
import shap

# Features
feature_cols = [
    'hy_ig_spread', 'hy_ig_zscore_252d', 'hy_ig_zscore_504d',
    'hy_ig_pctrank_504d', 'hy_ig_roc_21d', 'hy_ig_roc_63d',
    'hy_ig_mom_21d', 'hy_ig_mom_63d', 'hy_ig_acceleration',
    'ccc_bb_spread', 'vix', 'yield_spread_10y3m', 'nfci',
]
# Add vix_term_structure if available
if 'vix_term_structure' in df.columns:
    feature_cols.append('vix_term_structure')

target_col = 'spy_fwd_21d'
rf_data = df[feature_cols + [target_col]].dropna()
rf_data['target'] = (rf_data[target_col] > 0).astype(int)

# Walk-forward: 5yr train, 1yr test
train_years = 5
test_years = 1
start_year = rf_data.index.year.min()
end_year = rf_data.index.year.max()

wf_rows = []
all_rf_probs = pd.Series(dtype=float)
all_importances = []

for test_start_year in range(start_year + train_years, end_year + 1, test_years):
    train_end = pd.Timestamp(f'{test_start_year}-01-01')
    test_end = pd.Timestamp(f'{test_start_year + test_years}-01-01')
    train_start = pd.Timestamp(f'{test_start_year - train_years}-01-01')

    train = rf_data.loc[train_start:train_end]
    test = rf_data.loc[train_end:test_end]
    if len(train) < 500 or len(test) < 50:
        continue

    X_train, y_train = train[feature_cols], train['target']
    X_test, y_test = test[feature_cols], test['target']

    rf = RandomForestClassifier(
        n_estimators=200, max_depth=5, min_samples_leaf=20,
        random_state=42, n_jobs=-1
    )
    rf.fit(X_train, y_train)
    probs = rf.predict_proba(X_test)[:, 1]
    preds = (probs > 0.5).astype(int)

    acc = accuracy_score(y_test, preds)
    try:
        auc = roc_auc_score(y_test, probs)
    except:
        auc = np.nan

    wf_rows.append({
        'test_start': train_end.strftime('%Y-%m-%d'),
        'test_end': test_end.strftime('%Y-%m-%d'),
        'n_train': len(train), 'n_test': len(test),
        'accuracy': acc, 'auc': auc,
        'pos_rate_train': y_train.mean(), 'pos_rate_test': y_test.mean(),
    })

    all_rf_probs = pd.concat([all_rf_probs, pd.Series(probs, index=X_test.index)])
    all_importances.append(
        pd.Series(rf.feature_importances_, index=feature_cols)
    )

wf_df = pd.DataFrame(wf_rows)
wf_df.to_csv(f'{OUT}/rf_walk_forward.csv', index=False)

# Average feature importance
if all_importances:
    avg_imp = pd.DataFrame(all_importances).mean().sort_values(ascending=False)
    imp_df = pd.DataFrame({'feature': avg_imp.index, 'importance': avg_imp.values})
    imp_df.to_csv(f'{OUT}/rf_feature_importance.csv', index=False)
    print("RF Walk-Forward Results:")
    print(wf_df[['test_start', 'test_end', 'accuracy', 'auc']].to_string(index=False))
    print("\nFeature Importance (avg):")
    print(imp_df.to_string(index=False))

# Save RF probabilities for tournament
all_rf_probs.name = 'rf_prob'
all_rf_probs.to_csv(f'{OUT}/rf_probabilities.csv', header=True)

# SHAP on last model
if all_importances:
    try:
        explainer = shap.TreeExplainer(rf)
        shap_values = explainer.shap_values(X_test)
        if isinstance(shap_values, list):
            shap_vals = shap_values[1]  # class 1
        else:
            shap_vals = shap_values
        shap_imp = pd.DataFrame({
            'feature': feature_cols,
            'mean_abs_shap': np.abs(shap_vals).mean(axis=0),
        }).sort_values('mean_abs_shap', ascending=False)
        shap_imp.to_csv(f'{OUT}/rf_shap_importance.csv', index=False)
        print("\nSHAP Importance (last window):")
        print(shap_imp.to_string(index=False))
    except Exception as e:
        print(f"SHAP failed: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# 10. LOCAL PROJECTIONS (Jordà)
# ══════════════════════════════════════════════════════════════════════════════
print("\n=== 10. Local Projections ===")

lp_data = df[['spy_ret', 'hy_ig_spread_chg', 'hy_ig_zscore_252d',
              'vix', 'yield_spread_10y3m', 'stress']].dropna()

horizons = [1, 5, 10, 21, 42, 63]
lp_rows = []

for h in horizons:
    # Forward cumulative return
    fwd_ret = lp_data['spy_ret'].rolling(h).sum().shift(-h)
    lp_sub = lp_data.copy()
    lp_sub['fwd_ret'] = fwd_ret
    lp_sub = lp_sub.dropna()

    if len(lp_sub) < 100:
        continue

    T = len(lp_sub)
    nw_lags = int(0.75 * T**(1/3))

    # Base model: SPY_fwd = a + b*spread_chg + controls
    X = sm.add_constant(lp_sub[['hy_ig_spread_chg', 'vix', 'yield_spread_10y3m']])
    y = lp_sub['fwd_ret']
    ols = sm.OLS(y, X).fit(cov_type='HAC', cov_kwds={'maxlags': nw_lags})

    for var in ['hy_ig_spread_chg', 'vix', 'yield_spread_10y3m']:
        lp_rows.append({
            'horizon': h, 'specification': 'base',
            'variable': var,
            'coef': ols.params[var], 'se': ols.bse[var],
            't_stat': ols.tvalues[var], 'p_value': ols.pvalues[var],
            'ci_lower': ols.conf_int().loc[var, 0],
            'ci_upper': ols.conf_int().loc[var, 1],
            'n_obs': len(lp_sub), 'r_squared': ols.rsquared,
        })

    # State-dependent: interact spread_chg with stress dummy
    lp_sub['spread_chg_x_stress'] = lp_sub['hy_ig_spread_chg'] * lp_sub['stress']
    X2 = sm.add_constant(lp_sub[['hy_ig_spread_chg', 'spread_chg_x_stress',
                                  'stress', 'vix', 'yield_spread_10y3m']])
    ols2 = sm.OLS(y, X2).fit(cov_type='HAC', cov_kwds={'maxlags': nw_lags})

    for var in ['hy_ig_spread_chg', 'spread_chg_x_stress', 'stress']:
        lp_rows.append({
            'horizon': h, 'specification': 'state_dependent',
            'variable': var,
            'coef': ols2.params[var], 'se': ols2.bse[var],
            't_stat': ols2.tvalues[var], 'p_value': ols2.pvalues[var],
            'ci_lower': ols2.conf_int().loc[var, 0],
            'ci_upper': ols2.conf_int().loc[var, 1],
            'n_obs': len(lp_sub), 'r_squared': ols2.rsquared,
        })

lp_df = pd.DataFrame(lp_rows)
lp_df.to_csv(f'{OUT}/local_projections.csv', index=False)
print("Local Projections — HY-IG spread change coefficient by horizon:")
base_lp = lp_df[(lp_df['specification']=='base') & (lp_df['variable']=='hy_ig_spread_chg')]
print(base_lp[['horizon', 'coef', 'se', 'p_value']].to_string(index=False))

# ══════════════════════════════════════════════════════════════════════════════
# DIAGNOSTICS SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
print("\n=== Diagnostics Summary ===")

# Run Jarque-Bera, Breusch-Pagan, Breusch-Godfrey on last LP OLS
from statsmodels.stats.diagnostic import het_breuschpagan, acorr_breusch_godfrey
from statsmodels.stats.stattools import jarque_bera

# Use base LP at h=21
lp_h21 = lp_data.copy()
lp_h21['fwd_ret'] = lp_data['spy_ret'].rolling(21).sum().shift(-21)
lp_h21 = lp_h21.dropna()
X_diag = sm.add_constant(lp_h21[['hy_ig_spread_chg', 'vix', 'yield_spread_10y3m']])
y_diag = lp_h21['fwd_ret']
ols_diag = sm.OLS(y_diag, X_diag).fit()

jb_stat, jb_p, jb_skew, jb_kurt = jarque_bera(ols_diag.resid)
add_diag('LP h=21', 'Jarque-Bera', jb_stat, jb_p,
         'Non-normal' if jb_p < 0.05 else 'Normal')

bp_stat, bp_p, _, _ = het_breuschpagan(ols_diag.resid, X_diag)
add_diag('LP h=21', 'Breusch-Pagan', bp_stat, bp_p,
         'Heteroskedastic' if bp_p < 0.05 else 'Homoskedastic')

bg_stat, bg_p, _, _ = acorr_breusch_godfrey(ols_diag, nlags=10)
add_diag('LP h=21', 'Breusch-Godfrey', bg_stat, bg_p,
         'Serial correlation' if bg_p < 0.05 else 'No serial correlation')

# RESET test (manual)
y_hat = ols_diag.fittedvalues
X_reset = X_diag.copy()
X_reset['y_hat_sq'] = y_hat**2
X_reset['y_hat_cu'] = y_hat**3
ols_reset = sm.OLS(y_diag, X_reset).fit()
f_stat = ((ols_diag.ssr - ols_reset.ssr) / 2) / (ols_reset.ssr / ols_reset.df_resid)
f_p = 1 - stats.f.cdf(f_stat, 2, ols_reset.df_resid)
add_diag('LP h=21', 'RESET', f_stat, f_p,
         'Misspecified' if f_p < 0.05 else 'Correctly specified')

diag_df = pd.DataFrame(diagnostics_rows)
diag_df.to_csv(f'{OUT}/diagnostics_summary.csv', index=False)
print(diag_df.to_string(index=False))

print("\n=== Stage 2 Complete ===")
print(f"All results saved to {OUT}/")
