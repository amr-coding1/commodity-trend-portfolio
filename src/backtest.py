from __future__ import annotations

import json
from dataclasses import asdict, dataclass
import numpy as np
import pandas as pd


@dataclass
class Metrics:
    start: str
    end: str
    train_start: str
    train_end: str
    test_start: str
    test_end: str
    instruments: list[str]
    fast: int
    slow: int
    vol_target_daily: float
    cost_bps: float
    final_eq_strategy_test: float
    final_eq_benchmark_test: float
    sharpe_strategy_net_test: float
    max_drawdown_strategy_test: float
    avg_turnover_test: float


def sharpe(daily_ret: pd.Series) -> float:
    if daily_ret.std() == 0:
        return float("nan")
    return float(np.sqrt(252) * daily_ret.mean() / daily_ret.std())


def max_drawdown(equity: pd.Series) -> tuple[float, pd.Series]:
    peak = equity.cummax()
    dd = equity / peak - 1.0
    return float(dd.min()), dd


def equal_weight_benchmark(rets: pd.DataFrame) -> pd.Series:
    """
    Equal-weight buy & hold benchmark over the same instruments.
    """
    bh = rets.mean(axis=1)
    return (1 + bh).cumprod()


def run_backtest(rets: pd.DataFrame, weights: pd.DataFrame, cost_bps: float = 10.0) -> pd.DataFrame:
    """
    Cost-aware backtest:
    - gross return: sum(w_{t-1} * r_t)
    - turnover: sum(|w_t - w_{t-1}|)
    - net return: gross - turnover * cost
    """
    cost = cost_bps / 10000.0

    w_lag = weights.shift(1).fillna(0.0)
    strat_gross = (w_lag * rets).sum(axis=1)

    turnover = weights.diff().abs().sum(axis=1).fillna(0.0)
    strat_net = strat_gross - turnover * cost

    equity = (1 + strat_net).cumprod()

    return pd.DataFrame(
        {
            "strat_ret_gross": strat_gross,
            "turnover": turnover,
            "strat_ret_net": strat_net,
            "equity": equity,
        }
    )


def save_metrics(path: str, metrics: Metrics) -> None:
    with open(path, "w") as f:
        json.dump(asdict(metrics), f, indent=2)
