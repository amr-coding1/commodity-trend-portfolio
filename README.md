# Commodity Trend-Following Portfolio (Rule-Based)

Rule-based, reproducible backtest of a simple trend-following strategy across a small commodity-focused basket using ETF proxies:
- USO (WTI proxy)
- BNO (Brent proxy)
- GLD (Gold)

## Strategy (high level)
- Signal: long when fast SMA > slow SMA, else flat
- Position sizing: inverse-vol scaling + portfolio gross constraint
- Execution: next-day (weights are lagged by 1 day)
- Costs: 10 bps per trade, applied on turnover

## Reproducibility
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.main
