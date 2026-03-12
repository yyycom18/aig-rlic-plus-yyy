from typing import Dict, List, Tuple, Optional, Any
import streamlit as st
import plotly.graph_objects as go


def _safe_float(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default


def compute_strategy_survival_scores(
    strategy_data: Optional[Dict],
    benchmark_key: str = "spy",
) -> Tuple[List[float], List[Dict[str, Any]], float]:
    """
    Compute 5-axis strategy survival scores and metadata.
    Returns (scores_list [0-5], metadata_list per axis, average_score)
    Axes: Return Advantage, Sharpe Advantage, Drawdown Control, Consistency (win rate), Deployability (trades/year)
    """
    # Defaults
    scores: List[float] = []
    metadata: List[Dict[str, Any]] = []

    perf = (strategy_data or {}).get("performance_metrics") or {}
    strat = perf.get("strategy") or {}
    bench = perf.get(benchmark_key) or perf.get("spy") or {}
    out = (perf.get("outperformance") or {}) if perf else {}

    # 1) Return Advantage: strategy_return / benchmark_return
    s_ret = _safe_float(strat.get("annualized_return"), 0.0)
    b_ret = _safe_float(bench.get("annualized_return"), 0.0)
    # avoid divide by zero: if benchmark 0, use difference scaling
    if abs(b_ret) < 1e-6:
        ret_ratio = s_ret  # absolute
    else:
        ret_ratio = s_ret / b_ret
    # normalize: ratio 1.0 => 3 (mid), scale to 0-5: simple linear with cap
    ret_score = max(0.0, min(5.0, (ret_ratio * 1.5) + 2.0))
    scores.append(round(ret_score, 2))
    metadata.append(
        {
            "axis": "Return Advantage",
            "metric": "annualized_return",
            "strategy": s_ret,
            "benchmark": b_ret,
            "raw_ratio": ret_ratio,
            "note": "Higher ratio => higher score",
        }
    )

    # 2) Sharpe Advantage: strategy_sharpe / benchmark_sharpe
    s_sh = _safe_float(strat.get("sharpe"), 0.0)
    b_sh = _safe_float(bench.get("sharpe"), 0.0)
    if abs(b_sh) < 1e-6:
        sh_ratio = s_sh
    else:
        sh_ratio = s_sh / b_sh
    sh_score = max(0.0, min(5.0, (sh_ratio * 1.5) + 2.0))
    scores.append(round(sh_score, 2))
    metadata.append(
        {
            "axis": "Sharpe Advantage",
            "metric": "sharpe",
            "strategy": s_sh,
            "benchmark": b_sh,
            "raw_ratio": sh_ratio,
        }
    )

    # 3) Drawdown Control: benchmark_dd / strategy_dd (higher is better)
    s_dd = _safe_float(strat.get("max_drawdown"), 0.0)
    b_dd = _safe_float(bench.get("max_drawdown"), 0.0)
    # make positive magnitudes
    s_dd_abs = abs(s_dd) if s_dd != 0 else 1e-6
    b_dd_abs = abs(b_dd) if b_dd != 0 else 1e-6
    dd_ratio = b_dd_abs / s_dd_abs
    dd_score = max(0.0, min(5.0, (dd_ratio * 1.5) + 2.0))
    scores.append(round(dd_score, 2))
    metadata.append(
        {
            "axis": "Drawdown Control",
            "metric": "max_drawdown",
            "strategy": s_dd,
            "benchmark": b_dd,
            "raw_ratio": dd_ratio,
        }
    )

    # 4) Consistency: win_rate (0-1) -> scale 0-5
    win = _safe_float(strat.get("win_rate"), strat.get("winrate") or 0.5)
    win_score = max(0.0, min(5.0, win * 5.0))
    scores.append(round(win_score, 2))
    metadata.append(
        {
            "axis": "Consistency",
            "metric": "win_rate",
            "strategy": win,
        }
    )

    # 5) Deployability: trades_per_year optimal 4-20 -> score peak in that band
    trades = _safe_float(perf.get("trades_per_year") or strat.get("trades_per_year") or 0.0)
    # scoring: 4-20 -> full score 5; outside reduces linearly
    if trades <= 0:
        dep_score = 0.0
    elif 4 <= trades <= 20:
        dep_score = 5.0
    elif trades < 4:
        dep_score = max(0.0, (trades / 4.0) * 5.0)
    else:
        # penalty for overtrading: scaled down as trades increase beyond 20 up to 100
        dep_score = max(0.0, 5.0 * max(0.0, 1.0 - ((trades - 20.0) / 80.0)))
    scores.append(round(dep_score, 2))
    metadata.append(
        {
            "axis": "Deployability",
            "metric": "trades_per_year",
            "strategy": trades,
            "note": "Optimal 4–20 trades/year",
        }
    )

    avg = sum(scores) / len(scores) if scores else 0.0
    return scores, metadata, round(avg, 3)


def _radar_figure(scores: List[float], axes: List[str], title: str = "Strategy Survival") -> go.Figure:
    # ensure closure
    r = scores + [scores[0]]
    theta = axes + [axes[0]]
    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=r,
            theta=theta,
            fill="toself",
            fillcolor="rgba(255, 99, 71, 0.25)",
            line=dict(color="#ff6347", width=2),
        )
    )
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 5], tickvals=[1, 2, 3, 4, 5])
        ),
        showlegend=False,
        height=420,
    )
    fig.update_layout(title=title)
    return fig


def render_strategy_survival_panel(strategy_data: Optional[Dict], key_prefix: str = "strategy"):
    axes = ["Return Advantage", "Sharpe Advantage", "Drawdown Control", "Consistency", "Deployability"]
    scores, metadata, avg = compute_strategy_survival_scores(strategy_data)
    st.subheader("Strategy Survival — how this indicator performs in strategies")
    st.caption("Radar summarizes how strategies built from this indicator perform vs the benchmark (SPY). Higher scores are better.")
    # Text summary for screen-readers & quick view
    st.markdown(
        "- " + ", ".join([f"**{axes[i]}:** {scores[i]}/5" for i in range(len(axes))])
    )
    # Use blue/purple visual language consistent with behavior radar
    fig = _radar_figure(scores, axes, title="Strategy Survival")
    # adjust colors to blue/purple
    fig.data[0].update(fillcolor="rgba(102, 126, 234, 0.4)", line=dict(color="#667eea", width=2))
    st.plotly_chart(fig, use_container_width=True)
    # Always show average and viability rule
    st.markdown(f"**Average radar score:** {avg}/5. Viability rule: requires ≥ 2.5 to pass.")
    with st.expander("How these scores are calculated", expanded=False):
        st.markdown(
            "These scores are based on annualized return, Sharpe ratio, drawdown, win rate, and trades per year compared to buy-and-hold SPY. "
            "They are scaled to a 0–5 range for quick comparison."
        )
        for m in metadata:
            # Human-readable formatting per axis
            axis = m.get("axis", "Axis")
            if axis == "Return Advantage":
                st.markdown(
                    f"- **Return Advantage:** Strategy annualized return = {m.get('strategy'):.3f}, "
                    f"benchmark = {m.get('benchmark'):.3f}, ratio = {m.get('raw_ratio'):.3f} → score {scores[0]}/5"
                )
            elif axis == "Sharpe Advantage":
                st.markdown(
                    f"- **Sharpe Advantage:** Strategy Sharpe = {m.get('strategy'):.2f}, "
                    f"benchmark Sharpe = {m.get('benchmark'):.2f}, ratio = {m.get('raw_ratio'):.2f} → score {scores[1]}/5"
                )
            elif axis == "Drawdown Control":
                st.markdown(
                    f"- **Drawdown Control:** Strategy max drawdown = {m.get('strategy')}, "
                    f"benchmark max drawdown = {m.get('benchmark')}, ratio = {m.get('raw_ratio'):.2f} → score {scores[2]}/5"
                )
            elif axis == "Consistency":
                st.markdown(
                    f"- **Consistency:** Win rate = {m.get('strategy'):.2%} → score {scores[3]}/5"
                )
            elif axis == "Deployability":
                st.markdown(
                    f"- **Deployability:** Trades/year = {m.get('strategy'):.1f} (optimal 4–20/year) → score {scores[4]}/5"
                )
            else:
                st.markdown(f"- **{axis}:** {m}")
    # Viability rule warning if failed
    if avg < 2.5:
        st.warning("Average radar score < 2.5 — indicator may not be viable in strategies.")
