# Multi-Series Revenue Forecasting — Reproducible Synthetic Prototype

**Implemented:** 26 synthetic monthly series; ARIMA(1,1,0), seasonal-naive, trailing-three-month baselines; four one-step rolling origins; per-series MAE; three-month predictions; CSV outputs.

**Not implemented:** Prophet comparison, true rolling three-month backtesting, verified forecast coverage or 95% prediction intervals, production reconciliation, client credentials, regional hierarchical forecasts. This public code **does not reproduce confidential client forecasting results**.

## Run
```bash
pip install -r projects/revenue-forecasting/requirements.txt
python projects/revenue-forecasting/pipeline.py
pytest -q projects/revenue-forecasting/tests
python projects/revenue-forecasting/plot_results.py
```

Outputs: `outputs/backtest.csv`, `outputs/forecasts.csv`, `outputs/metadata.json`, and a synthetic `outputs/revenue_forecast_example.png`.

This short synthetic demonstration tests architecture, not accuracy. MAE values are **currency-unit errors**, while MAPE and sMAPE are percentage-based. Use complete data and horizon-matched tests before publishing comparison charts or accuracy claims.
