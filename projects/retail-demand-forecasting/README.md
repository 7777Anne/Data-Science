# Retail Unit Demand Forecasting and Replenishment — Runnable Demo

**Status:** end-to-end synthetic demonstration (not a verified real-retail inventory system).

## Business outputs
1. `outputs/one_step_backtest.csv` — actual vs prediction from a 60-day **one-step-ahead** evaluation; each prediction uses only observations that preceded its target date.
2. `outputs/next_day_forecast.csv` — genuinely future next-day store-SKU unit forecasts, illustrative stockout flags and order suggestions.
3. `outputs/metrics.json` — MAE and seasonal-naive MAE over the same rows.

A 60-day *test span* is not a 60-day *forecast horizon*. No claim is made that the system performs reliable multi-step prediction or optimizes actual inventory. Assumed inventory level 40 and buffer 1.2 are demonstration parameters, not empirically calibrated business rules.

## Run
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r projects/retail-demand-forecasting/requirements.txt
python projects/retail-demand-forecasting/pipeline.py
pytest -q projects/retail-demand-forecasting/tests
```

## Next upgrade
Use documented M5 competition data, hold out 28 days per rolling origin, add multi-step recursive/direct prediction with known-at-origin features, test stockout-cost assumptions, and benchmark with WAPE/WRMSSE. See [data card](docs/DATA_CARD.md) and [dataset register](../../docs/DATASET_REGISTER.md).
