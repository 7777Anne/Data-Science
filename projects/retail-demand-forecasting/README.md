# Retail Unit Demand Forecasting and Replenishment — Runnable Demo

**Status:** end-to-end synthetic demonstration (not a verified real-retail inventory system).

## Business outputs
1. `outputs/one_step_backtest.csv` — actual vs prediction from a 60-day **one-step-ahead** evaluation; each prediction uses only observations that preceded its target date.
2. `outputs/next_day_forecast.csv` — genuinely future next-day store-SKU unit forecasts, illustrative stockout flags and order suggestions.
3. `outputs/retail_forecast_example.png` — generated actual-vs-prediction plot from synthetic backtest (run `python projects/retail-demand-forecasting/plot_results.py`).
4. `outputs/metrics.json` — MAE and seasonal-naive MAE over the same rows.

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


## Omni-channel stock-turnover and inventory extension (independent portfolio work)

**Status:** reproducible **synthetic** multi-channel engineering demo, not a deployed client system or validated retail inventory optimizer. This extension intentionally uses no confidential Landmark or Subex data.

### What was added
- Store, SKU, day and channel-level input validation with duplicate-grain rejection; channel revenue is computed before aggregation to avoid incorrect price averaging.
- Vectorized aggregation from store/online sales to store-SKU-day demand observations.
- 7-day **recursive** demand forecasting, with all future lags generated from earlier predictions rather than future observed sales.
- Two rolling-origin 7-day backtests with MAE and WAPE calculations; **no measured accuracy is claimed until the code is executed**.
- Illustrative safety stock, reorder-point and order-up-to decisions from forecast daily units, assumed lead times and stock levels.
- Controlled log-linear price-demand **association** using price, promotion, weekday and trend. This must **not** be presented as identified causal elasticity.
- Unit tests for schema contracts, leakage resistance, forecasting horizons, inventory arithmetic and parameter validation.

### Run locally (Python 3.12)
```bash
python -m pip install -r projects/retail-demand-forecasting/requirements.txt
python projects/retail-demand-forecasting/run_omnichannel.py
python -m pytest -q projects/retail-demand-forecasting/tests
```

Outputs appear under `projects/retail-demand-forecasting/outputs/omnichannel_demo/`:
`synthetic_channel_sales.csv`, `recursive_backtest.csv`, `seven_day_forecast.csv`, `inventory_recommendations.csv`, `price_associations_not_causal.csv`, `metrics.json`.

### Engineering and business limitations
1. This artificial dataset has **observed sales**, not true uncensored demand. It omits actual stock levels; zero sales cannot be interpreted as zero demand.
2. Inventory values, review intervals, lead time, error standard deviation and service factor are assumed, not calibrated. The 7-day forecast is used as an estimate of average daily rate; it is **not** a validated lead-time simulation.
3. The price coefficient is observational and potentially confounded by promotions, availability and time effects. Do not claim causal pricing recommendations.
4. No production AWS/Azure/GCP system, external API, PySpark job or deployment is implemented in this extension. These are separate future milestones.
5. Next phases: integrate an appropriately licensed M5 or other real retail dataset, channel-specific inventory availability, calibrated probabilistic forecasts, cost-aware replenishment simulation, PySpark ETL, Docker and CI reports.
