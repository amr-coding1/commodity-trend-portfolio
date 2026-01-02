from __future__ import annotations

import os
import pandas as pd
import matplotlib.pyplot as plt

from src.data import load_prices
from src.features import compute_features, split_index
from src.strategy import trend_signal, vol_target_weights
from src.backtest import (
    Metrics,
    equal_weight_benchmark,
    max_drawdown,
    run_backtest,
    sharpe,
    save_metrics,
)

# ---------------- CONFIG ----------------
TICKERS = {
    "WTI_proxy_USO": "USO",
    "Brent_proxy_BNO": "BNO",
    "Gold_GLD": "GLD",
}
START = "2010-01-01"

FAST = 20
SLOW = 120
VOL_WINDOW = 20

VOL_TARGET_DAILY = 0.006
MAX_LEVERAGE_PER_ASSET = 1.0
MAX_GROSS = 1.0

COST_BPS = 10.0

SPLIT_FRAC = 0.7
SPLIT_DATE = None  # e.g. "2020-01-01" if you want a fixed boundary

RESULTS_DIR = "results"
# ----------------------------------------


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    # 1) Load prices
    prices = load_prices(TICKERS, start=START)

    # 2) Features
    feats = compute_features(prices, fast=FAST, slow=SLOW, vol_window=VOL_WINDOW)
    rets = feats["rets"]

    # 3) Signal + weights
    sig = trend_signal(feats["sma_fast"], feats["sma_slow"])
    w = vol_target_weights(
        sig,
        feats["vol"],
        vol_target_daily=VOL_TARGET_DAILY,
        max_leverage_per_asset=MAX_LEVERAGE_PER_ASSET,
        max_gross=MAX_GROSS,
    )

    # 4) Split (time-ordered)
    train_idx, test_idx = split_index(rets.index, split_frac=SPLIT_FRAC, split_date=SPLIT_DATE)

    # 5) Backtest
    bt = run_backtest(rets=rets, weights=w, cost_bps=COST_BPS)
    eq_bh = equal_weight_benchmark(rets)

    bt_test = bt.loc[test_idx]
    eq_bh_test = eq_bh.loc[test_idx]

    # 6) Metrics on TEST only (keeps it honest)
    mdd_test, dd_series_test = max_drawdown(bt_test["equity"])
    sharpe_test = sharpe(bt_test["strat_ret_net"])

    # 7) Save outputs
    equity_df = pd.DataFrame(
        {
            "strategy_equity_net": bt_test["equity"],
            "benchmark_equity": eq_bh_test,
            "strategy_ret_net": bt_test["strat_ret_net"],
            "turnover": bt_test["turnover"],
        }
    )
    equity_path = os.path.join(RESULTS_DIR, "equity_curve.csv")
    equity_df.to_csv(equity_path, index=True)

    metrics = Metrics(
        start=str(rets.index.min().date()),
        end=str(rets.index.max().date()),
        train_start=str(train_idx.min().date()) if len(train_idx) else "",
        train_end=str(train_idx.max().date()) if len(train_idx) else "",
        test_start=str(test_idx.min().date()) if len(test_idx) else "",
        test_end=str(test_idx.max().date()) if len(test_idx) else "",
        instruments=list(TICKERS.keys()),
        fast=FAST,
        slow=SLOW,
        vol_target_daily=VOL_TARGET_DAILY,
        cost_bps=COST_BPS,
        final_eq_strategy_test=float(bt_test["equity"].iloc[-1]),
        final_eq_benchmark_test=float(eq_bh_test.iloc[-1]),
        sharpe_strategy_net_test=float(sharpe_test),
        max_drawdown_strategy_test=float(mdd_test),
        avg_turnover_test=float(bt_test["turnover"].mean()),
    )
    metrics_path = os.path.join(RESULTS_DIR, "metrics.json")
    save_metrics(metrics_path, metrics)

    # 8) Plot (test period)
    plt.figure(figsize=(10, 5))
    plt.plot(eq_bh_test.index, eq_bh_test, label="Benchmark (equal-weight B&H)")
    plt.plot(bt_test.index, bt_test["equity"], label="Trend Portfolio (net)")
    plt.title("Commodity Trend-Following Portfolio (Out-of-sample test)")
    plt.legend()
    plt.tight_layout()
    fig_path = os.path.join(RESULTS_DIR, "equity_curve.png")
    plt.savefig(fig_path, dpi=200)
    plt.show()

    print(f"Saved: {equity_path}")
    print(f"Saved: {metrics_path}")
    print(f"Saved: {fig_path}")


if __name__ == "__main__":
    main()
