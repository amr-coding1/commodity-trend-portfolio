from __future__ import annotations

import numpy as np
import pandas as pd


def trend_signal(sma_fast: pd.DataFrame, sma_slow: pd.DataFrame) -> pd.DataFrame:
    """
    Long/flat signal:
    1 when fast MA > slow MA, else 0.
    """
    return (sma_fast > sma_slow).astype(int)


def vol_target_weights(
    signal: pd.DataFrame,
    vol: pd.DataFrame,
    vol_target_daily: float = 0.006,
    max_leverage_per_asset: float = 1.0,
    max_gross: float = 1.0,
) -> pd.DataFrame:
    """
    Risk-aware weights:
    - inverse-vol scaling (target vol per asset)
    - apply signal (long/flat)
    - normalise to portfolio gross <= max_gross
    """
    vol_safe = vol.replace(0, np.nan)

    raw = (vol_target_daily / vol_safe).clip(upper=max_leverage_per_asset)
    w = raw * signal

    gross = w.abs().sum(axis=1).replace(0, np.nan)
    w = w.div(gross, axis=0).fillna(0.0)

    return w * max_gross
