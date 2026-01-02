from __future__ import annotations

import pandas as pd
import yfinance as yf


def load_prices(tickers: dict[str, str], start: str = "2010-01-01") -> pd.DataFrame:
    """
    Download adjusted close prices for a dict of {name: ticker}.
    Returns DataFrame indexed by date with columns as names.
    """
    series = []
    for name, tkr in tickers.items():
        df = yf.download(tkr, start=start, auto_adjust=True, progress=False)

        # yfinance may return MultiIndex columns
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df.columns = [c.lower() for c in df.columns]

        if "close" not in df.columns:
            raise ValueError(f"Expected 'close' column for {tkr}, got {list(df.columns)}")

        series.append(df["close"].rename(name))

    prices = pd.concat(series, axis=1).dropna()
    prices.index = pd.to_datetime(prices.index)
    return prices
