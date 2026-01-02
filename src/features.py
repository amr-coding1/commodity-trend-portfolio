from __future__ import annotations

import numpy as np
import pandas as pd


def compute_features(
    prices: pd.DataFrame,
    fast: int,
    slow: int,
    vol_window: int = 20,
) -> dict[str, pd.DataFrame]:
    """
    Compute:
    - daily returns
    - fast/slow simple moving averages
    - realised volatility (rolling std of returns)
    """
    rets = prices.pct_change().dropna()

    sma_fast = prices.rolling(fast).mean()
    sma_slow = prices.rolling(slow).mean()
    vol = rets.rolling(vol_window).std()

    # Align all to common dates (remove NaNs from rolling windows)
    common = rets.index
    common = common.intersection(sma_fast.dropna().index)
    common = common.intersection(sma_slow.dropna().index)
    common = common.intersection(vol.dropna().index)

    return {
        "prices": prices.loc[common],
        "rets": rets.loc[common],
        "sma_fast": sma_fast.loc[common],
        "sma_slow": sma_slow.loc[common],
        "vol": vol.loc[common],
    }


def split_index(index: pd.DatetimeIndex, split_frac: float = 0.7, split_date: str | None = None):
    """
    Returns (train_idx, test_idx) as slices of the DatetimeIndex.
    - If split_date is provided, uses that boundary.
    - Else uses split_frac.
    """
    if split_date is not None:
        split_ts = pd.to_datetime(split_date)
        train = index[index < split_ts]
        test = index[index >= split_ts]
        return train, test

    n = len(index)
    cut = int(np.floor(n * split_frac))
    return index[:cut], index[cut:]
