from app.components.strategy_radar import compute_strategy_survival_scores


def test_compute_strategy_survival_scores_basic():
    # Minimal synthetic strategy data
    strategy_data = {
        "performance_metrics": {
            "strategy": {
                "annualized_return": 0.12,
                "sharpe": 1.2,
                "max_drawdown": -0.10,
                "win_rate": 0.55,
            },
            "spy": {
                "annualized_return": 0.08,
                "sharpe": 0.8,
                "max_drawdown": -0.20,
            },
            "trades_per_year": 10,
        }
    }
    scores, metadata, avg = compute_strategy_survival_scores(strategy_data)
    assert isinstance(scores, list) and len(scores) == 5
    assert 0.0 <= avg <= 5.0
    # Return advantage should be > 3 given 0.12/0.08 ratio
    assert scores[0] > 3.0

