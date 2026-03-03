"""Interactive tournament leaderboard component."""

import pandas as pd
import streamlit as st


# Hardcoded from Evan's tournament results (top 5 + benchmark)
TOURNAMENT_DATA = [
    {
        "Rank": 1,
        "Signal": "HMM 2-state (S6)",
        "Lead": "0d",
        "Threshold": "p > 0.7",
        "Strategy": "Long/Cash",
        "OOS Sharpe": 1.17,
        "OOS Return": "11.0%",
        "Max DD": "-11.6%",
    },
    {
        "Rank": 2,
        "Signal": "Composite Z+VTS (S8)",
        "Lead": "0d",
        "Threshold": "Bollinger 1.5x",
        "Strategy": "Long/Cash",
        "OOS Sharpe": 1.17,
        "OOS Return": "16.2%",
        "Max DD": "-29.1%",
    },
    {
        "Rank": 3,
        "Signal": "HMM 2-state (S6)",
        "Lead": "0d",
        "Threshold": "p > 0.5",
        "Strategy": "Long/Cash",
        "OOS Sharpe": 1.16,
        "OOS Return": "10.7%",
        "Max DD": "-11.1%",
    },
    {
        "Rank": 4,
        "Signal": "Z-Score 252d (S2a)",
        "Lead": "0d",
        "Threshold": "Bollinger 2.0x",
        "Strategy": "Long/Cash",
        "OOS Sharpe": 1.12,
        "OOS Return": "16.3%",
        "Max DD": "-28.6%",
    },
    {
        "Rank": 5,
        "Signal": "Z-Score 252d (S2a)",
        "Lead": "5d",
        "Threshold": "Rolling 95th pctile",
        "Strategy": "Long/Cash",
        "OOS Sharpe": 1.12,
        "OOS Return": "16.8%",
        "Max DD": "-23.7%",
    },
    {
        "Rank": "-",
        "Signal": "Buy-and-Hold SPY",
        "Lead": "-",
        "Threshold": "-",
        "Strategy": "Benchmark",
        "OOS Sharpe": 0.77,
        "OOS Return": "13.8%",
        "Max DD": "-33.7%",
    },
]


def render_tournament_leaderboard():
    """Render the interactive tournament leaderboard."""
    df = pd.DataFrame(TOURNAMENT_DATA)

    st.markdown("### Tournament Leaderboard")
    st.markdown(
        f"**{2304:,} combinations tested** | "
        f"**{1149:,} valid** (OOS Sharpe >= 0, turnover <= 24x/yr, >= 30 trades) | "
        f"**All top-5 significant at p < 0.01**"
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Rank": st.column_config.TextColumn("Rank", width="small"),
            "OOS Sharpe": st.column_config.NumberColumn("OOS Sharpe", format="%.2f"),
        },
    )

    st.caption(
        "Ranked by out-of-sample Sharpe ratio (2018-2025). "
        "All strategies include 5 bps round-trip transaction costs. "
        "Bootstrap significance tested with 10,000 samples."
    )
