from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
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
    s_ret = strat.get("annualized_return")
    b_ret = bench.get("annualized_return")
    try:
        s_ret_f = float(s_ret) if s_ret is not None and s_ret != "" else None
    except Exception:
        s_ret_f = None
    try:
        b_ret_f = float(b_ret) if b_ret is not None and b_ret != "" else None
    except Exception:
        b_ret_f = None
    ret_ratio = None
    if b_ret_f is None or abs(b_ret_f) < 1e-12:
        # mark as NA; cannot compute ratio
        ret_score = None
    else:
        ret_ratio = s_ret_f / b_ret_f if s_ret_f is not None else None
        if ret_ratio is None:
            ret_score = None
        else:
            # normalize: ratio -> score (heuristic)
            ret_score = max(0.0, min(5.0, (ret_ratio * 1.5) + 2.0))
    scores.append(ret_score)
    metadata.append(
        {
            "axis": "Return Advantage",
            "metric": "annualized_return",
            "strategy": s_ret_f,
            "benchmark": b_ret_f,
            "raw_ratio": ret_ratio,
            "note": "Higher ratio => higher score",
            "na": ret_score is None,
        }
    )

    # 2) Sharpe Advantage: strategy_sharpe / benchmark_sharpe
    s_sh = _safe_float(strat.get("sharpe"), 0.0)
    b_sh = _safe_float(bench.get("sharpe"), 0.0)
    if abs(b_sh) < 1e-6:
        sh_ratio = s_sh
    else:
        sh_ratio = s_sh / b_sh
    sh_score = None
    if b_sh is None or abs(b_sh) < 1e-12:
        sh_score = None
    else:
        if sh_ratio is not None:
            sh_score = max(0.0, min(5.0, (sh_ratio * 1.5) + 2.0))
    scores.append(sh_score)
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
    dd_score = None
    if s_dd_abs is None or b_dd_abs is None:
        dd_score = None
    else:
        dd_score = max(0.0, min(5.0, (dd_ratio * 1.5) + 2.0))
    scores.append(dd_score)
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
    win_score = None
    if win is not None:
        try:
            win_f = float(win)
            win_score = max(0.0, min(5.0, win_f * 5.0))
        except Exception:
            win_score = None
    scores.append(win_score)
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
    scores.append(dep_score)
    metadata.append(
        {
            "axis": "Deployability",
            "metric": "trades_per_year",
            "strategy": trades,
            "note": "Optimal 4–20 trades/year",
        }
    )

    # compute average ignoring None entries
    numeric = [s for s in scores if s is not None]
    avg = sum(numeric) / len(numeric) if numeric else 0.0
    return scores, metadata, round(avg, 3)


def _radar_figure(scores: List[Optional[float]], axes: List[str], title: str = "Strategy Survival") -> go.Figure:
    # ensure closure
    # replace None with neutral 2.5 for plotting
    plot_scores = [(s if s is not None else 2.5) for s in scores]
    r = plot_scores + [plot_scores[0]]
    theta = axes + [axes[0]]
    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=r,
            theta=theta,
            fill="toself",
            fillcolor="rgba(102, 126, 234, 0.4)",
            line=dict(color="#667eea", width=2),
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


def render_strategy_survival_panel(strategy_data: Optional[Dict], study: str = "hy_ig", key_prefix: str = "strategy"):
    axes = ["Return Advantage", "Sharpe Advantage", "Drawdown Control", "Consistency", "Deployability"]
    scores, metadata, avg = compute_strategy_survival_scores(strategy_data)
    st.subheader("Strategy Survival — how this indicator performs in strategies")
    st.caption("Radar summarizes how strategies built from this indicator perform vs the benchmark (SPY). Higher scores are better.")
    # Text summary for screen-readers & quick view (format N/A when score is missing)
    def fmt_score(s):
        return f"{s:.2f}/5" if s is not None else "N/A"

    st.markdown(
        "- " + ", ".join([f"**{axes[i]}:** {fmt_score(scores[i])}" for i in range(len(axes))])
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
        for idx, m in enumerate(metadata):
            # Human-readable formatting per axis
            axis = m.get("axis", "Axis")
            if axis == "Return Advantage":
                s_strat = m.get('strategy')
                s_bench = m.get('benchmark')
                r_raw = m.get('raw_ratio')
                score_val = scores[0] if len(scores) > 0 else None
                s_text = f"{s_strat:.3f}" if s_strat is not None else "N/A"
                b_text = f"{s_bench:.3f}" if s_bench is not None else "N/A"
                r_text = f"{r_raw:.3f}" if r_raw is not None else "N/A"
                st.markdown(f"- **Return Advantage:** Strategy annualized return = {s_text}, benchmark = {b_text}, ratio = {r_text} → score {fmt_score(score_val)}")
            elif axis == "Sharpe Advantage":
                s_strat = m.get('strategy')
                s_bench = m.get('benchmark')
                r_raw = m.get('raw_ratio')
                s_text = f"{s_strat:.2f}" if s_strat is not None else "N/A"
                b_text = f"{s_bench:.2f}" if s_bench is not None else "N/A"
                r_text = f"{r_raw:.2f}" if r_raw is not None else "N/A"
                score_val = scores[1] if len(scores) > 1 else None
                st.markdown(f"- **Sharpe Advantage:** Strategy Sharpe = {s_text}, benchmark Sharpe = {b_text}, ratio = {r_text} → score {fmt_score(score_val)}")
            elif axis == "Drawdown Control":
                s_strat = m.get('strategy')
                s_bench = m.get('benchmark')
                r_raw = m.get('raw_ratio')
                s_text = f"{s_strat}" if s_strat is not None else "N/A"
                b_text = f"{s_bench}" if s_bench is not None else "N/A"
                r_text = f"{r_raw:.2f}" if r_raw is not None else "N/A"
                score_val = scores[2] if len(scores) > 2 else None
                st.markdown(f"- **Drawdown Control:** Strategy max drawdown = {s_text}, benchmark max drawdown = {b_text}, ratio = {r_text} → score {fmt_score(score_val)}")
            elif axis == "Consistency":
                s_strat = m.get('strategy')
                score_val = scores[3] if len(scores) > 3 else None
                s_text = f"{s_strat:.2%}" if s_strat is not None else "N/A"
                st.markdown(f"- **Consistency:** Win rate = {s_text} → score {fmt_score(score_val)}")
            elif axis == "Deployability":
                s_strat = m.get('strategy')
                score_val = scores[4] if len(scores) > 4 else None
                s_text = f"{s_strat:.1f}" if s_strat is not None else "N/A"
                st.markdown(f"- **Deployability:** Trades/year = {s_text} (optimal 4–20/year) → score {fmt_score(score_val)}")
            else:
                st.markdown(f"- **{axis}:** {m}")
    # Viability rule warning if failed
    if avg < 2.5:
        st.warning("Average radar score < 2.5 — indicator may not be viable in strategies.")
    # --- Deployability transparency: if deployability mapped to 0, show reason and top strategies table
    try:
        dep_meta = metadata[4] if len(metadata) > 4 else {}
        trades = float(dep_meta.get("strategy") or 0.0)
        mapped_dep = scores[4] if len(scores) > 4 else 0.0
    except Exception:
        trades = 0.0
        mapped_dep = 0.0

    def _deploy_reason(tr):
        try:
            tr = float(tr)
        except Exception:
            return "no_trades"
        if tr <= 0:
            return "no_trades"
        if tr < 4:
            return "below_min"
        if tr > 100:
            return "out_of_range"
        return "ok"

    reason = _deploy_reason(trades)
    reason_map = {
        "no_trades": "No trades were generated by the strategy in the evaluation window.",
        "below_min": "Too few trades per year for deployability (<4 trades/year).",
        "out_of_range": "Trades/year are outside the acceptable range (extremely high).",
        "ok": "",
    }
    if mapped_dep == 0.0:
        st.markdown(f"**Deployability note:** {reason_map.get(reason,'Unknown reason')}")

    # mini table of top-N strategies for this indicator
    top_n = 10
    tour_path = Path(__file__).resolve().parents[1] / "results" / "tournament_results_20260228.csv"
    try:
        import csv as _csv

        rows = []
        if tour_path.exists():
            with open(tour_path, "r", encoding="utf-8") as fh:
                rdr = _csv.DictReader(fh)
                for r in rdr:
                    # match by study -> signal mapping
                    if r.get("signal_col") != (study if study != "hy_ig" else "hy_ig_spread") and r.get("signal_col") != "hy_ig_spread":
                        continue
                    rows.append(r)
        # sort by oos_sharpe desc
        def _safe(x):
            try:
                return float(x)
            except Exception:
                return -1e9

        rows.sort(key=lambda r: _safe(r.get("oos_sharpe")), reverse=True)
        top = rows[:top_n]
        # render table
        if top:
            st.markdown("**Top strategies (trades/year & deployability):**")
            st.write("|strategy_id|strategy_name|trades_per_year|deployability_score|valid|")
            st.write("|-|-:|-:|-:|-:|")
            any_trades = False
            for r in top:
                sid = r.get("strategy_id")
                name = r.get("strategy_name")
                trades_v = r.get("n_trades") or r.get("annual_turnover") or "0"
                try:
                    trades_vf = float(trades_v)
                except Exception:
                    trades_vf = 0.0
                mapped = map_deployability(trades_vf)
                if trades_vf > 0:
                    any_trades = True
                st.write(f"|{sid}|{name}|{trades_vf:.1f}|{mapped:.2f}|{r.get('valid')}|")
            st.markdown("_Deployability is computed from trades/year; 4–20 trades/yr = optimal._")
            if not any_trades:
                st.markdown("**No deployable strategies in the top set — see diagnostics.**")
    except Exception as e:
        # non-fatal: just log
        st.caption(f"Deployability diagnostics unavailable: {e}")
