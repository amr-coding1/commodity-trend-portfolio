# Commodity Trend-Following Portfolio

A rule-based trend-following strategy applied to a small commodity portfolio, inspired by systematic CTA-style approaches.  
The project focuses on mechanical signal generation, risk management, and realistic backtesting rather than prediction.

---

## Overview

This project tests whether simple, transparent trend signals can generate risk-adjusted returns across commodity markets when combined into a portfolio.

The strategy is intentionally:
- Rule-based and mechanical
- Interpretable (no black-box models)
- Evaluated strictly out-of-sample
- Transaction-cost-aware

The goal is not to optimise performance, but to understand where and why trend-following works — and where it fails.

---

## Instruments

Liquid ETF proxies are used to represent commodity exposure:

- **WTI Crude Oil** — `USO`
- **Brent Crude Oil** — `BNO`
- **Gold** — `GLD`

These instruments provide sufficient liquidity for systematic testing while keeping the universe focused.

---

## Strategy Logic

- **Trend signal:** Fast / slow moving-average crossover
- **Positioning:** Long or flat (no leverage, no shorting)
- **Risk targeting:** Volatility-scaled position sizing
- **Portfolio construction:** Equal-weight across active signals
- **Transaction costs:** 10 basis points per trade (round-turn approximation)

Positions are adjusted daily based on updated signals and volatility estimates.

---

## Backtesting Framework

- Strict time-ordered train / test split
- No lookahead bias
- Signals computed using past information only
- Portfolio-level aggregation of individual instruments
- Performance measured net of transaction costs

### Metrics evaluated
- Cumulative PnL
- Sharpe ratio
- Maximum drawdown
- Turnover

---

## Results (Out-of-Sample)

Over the test period, the trend-following portfolio outperformed an equal-weight buy-and-hold benchmark, with:

- Higher cumulative return
- Improved risk-adjusted performance
- Controlled drawdowns during trending regimes

Performance deteriorates during range-bound or rapidly mean-reverting markets, consistent with known trend-following behaviour.

All results are saved to the `results/` directory.

---

## Reproducibility

Run the full research pipeline end-to-end:

```bash
python -m src.main
```

This will generate:
- `results/equity_curve.csv` — daily portfolio and benchmark equity
- `results/equity_curve.png` — equity curve comparison
- `results/metrics.json` — summary performance statistics

---

## Project Structure

```
commodity-trend-portfolio/
├── src/
│   ├── data.py        # Data loading and preprocessing
│   ├── features.py    # Trend and volatility features
│   ├── strategy.py    # Signal generation and position logic
│   ├── backtest.py    # Portfolio backtesting engine
│   └── main.py        # End-to-end execution
├── results/
│   ├── equity_curve.csv
│   ├── equity_curve.png
│   └── metrics.json
├── notebooks/
│   └── 01_research_trend_portfolio.ipynb
├── requirements.txt
└── README.md
```

The core logic is implemented in modular Python files to ensure clarity and reproducibility.  
The notebook is intentionally minimal and reserved for optional exploratory analysis.

---

## Notes

This project is a research and learning exercise, not a production trading system.  
Results are sensitive to parameter choices, market regime, and transaction cost assumptions.

The emphasis is on:
- disciplined research structure
- realistic evaluation
- understanding failure modes

rather than maximising backtested performance.
