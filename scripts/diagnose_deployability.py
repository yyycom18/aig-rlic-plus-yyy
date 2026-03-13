#!/usr/bin/env python3
"""
Produce deployability diagnostics for HY-IG -> SPY top-20 strategies.
Outputs CSV: results/diagnostics/deployability_debug_hy_ig_spy.csv
and a short log: results/diagnostics/deployability_debug_hy_ig_spy.log
"""
import os
import csv
import math
from pathlib import Path

INPUT = Path(__file__).resolve().parents[1] / "results" / "tournament_results_20260228.csv"
OUTDIR = Path(__file__).resolve().parents[1] / "results" / "diagnostics"
OUTDIR.mkdir(parents=True, exist_ok=True)
OUTCSV = OUTDIR / "deployability_debug_hy_ig_spy.csv"
OUTLOG = OUTDIR / "deployability_debug_hy_ig_spy.log"

def map_deployability(trades):
    try:
        trades = float(trades)
    except Exception:
        return 0.0
    if trades <= 0:
        return 0.0
    if 4 <= trades <= 20:
        return 5.0
    if trades < 4:
        return max(0.0, min(5.0, (trades / 4.0) * 5.0))
    # overtrading penalty: linear down to 0 at trades=100
    score = max(0.0, 5.0 * max(0.0, 1.0 - ((trades - 20.0) / 80.0)))
    return round(score, 6)

def main():
    if not INPUT.exists():
        with open(OUTLOG, "w") as f:
            f.write(f"ERROR: input file not found: {INPUT}\n")
        print("Input CSV not found:", INPUT)
        return

    rows = []
    with open(INPUT, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r.get("signal_col") != "hy_ig_spread":
                continue
            rows.append(r)

    if not rows:
        with open(OUTLOG, "w") as f:
            f.write("No rows for hy_ig_spread found in tournament_results_20260228.csv\n")
        print("No rows found for hy_ig_spread")
        return

    # sort by oos_sharpe desc
    def safe_float(x):
        try:
            return float(x)
        except Exception:
            return -math.inf

    rows.sort(key=lambda r: safe_float(r.get("oos_sharpe")), reverse=True)
    top20 = rows[:20]

    out_rows = []
    log_lines = []
    for r in top20:
        strategy_id = r.get("strategy_id")
        signal = r.get("signal_col")
        lead = r.get("lead_time")
        threshold = r.get("threshold_method")
        # trades per year: prefer n_trades then annual_turnover or 0
        trades = r.get("n_trades") or r.get("trades_per_year") or r.get("annual_turnover") or "0"
        try:
            trades_val = float(trades)
        except Exception:
            trades_val = 0.0
        deploy_raw = trades_val
        mapped = map_deployability(deploy_raw)
        out_rows.append({
            "strategy_id": strategy_id,
            "signal": signal,
            "lead": lead,
            "threshold": threshold,
            "trades_per_year": trades_val,
            "deployability_raw_score": deploy_raw,
            "mapped_deployability_score": mapped,
            "valid": r.get("valid"),
            "oos_sharpe": r.get("oos_sharpe"),
        })
        # log suspicious filters
        if trades_val == 0.0:
            reason = []
            if r.get("valid", "").lower() in ("false", "0", "no"):
                reason.append("strategy marked invalid")
            reason.append("n_trades==0")
            log_lines.append(f"{strategy_id}: trades=0 ({';'.join(reason)})")

    # write CSV
    keys = ["strategy_id","signal","lead","threshold","trades_per_year","deployability_raw_score","mapped_deployability_score","valid","oos_sharpe"]
    with open(OUTCSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for r in out_rows:
            writer.writerow({k: r.get(k) for k in keys})

    # write log
    with open(OUTLOG, "w", encoding="utf-8") as f:
        if log_lines:
            f.write("Warnings / zero-trades entries:\n")
            for l in log_lines:
                f.write(l + "\n")
            f.write("\nMapping used: optimal range 4-20 trades/year -> score 5; <4 scaled up; >20 penalized to 0 at 100.\n")
            f.write("If trades are zero, check tournament n_trades column, strategy validity, and date windows.\n")
        else:
            f.write("No zero-trades warnings; all top-20 have trades > 0.\n")
    print("Wrote diagnostics:", OUTCSV, OUTLOG)

    # Also produce a top20_raw.csv with raw columns for quick inspection
    top20_csv = OUTDIR / "top20_raw.csv"
    top20_keys = ["strategy_id", "oos_sharpe", "oos_ann_return", "oos_max_dd", "n_trades", "oos_win_rate", "return_ratio"]
    with open(top20_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=top20_keys)
        writer.writeheader()
        for r in top20:
            # return_ratio: cannot compute benchmark from this file, set empty
            writer.writerow({
                "strategy_id": r.get("strategy_id"),
                "oos_sharpe": r.get("oos_sharpe"),
                "oos_ann_return": r.get("oos_ann_return"),
                "oos_max_dd": r.get("oos_max_dd"),
                "n_trades": r.get("n_trades"),
                "oos_win_rate": r.get("oos_win_rate"),
                "return_ratio": "",
            })
    print("Wrote top20 raw inputs:", top20_csv)
if __name__ == "__main__":
    main()

