# Retail Demand, Stockout Risk & Replenishment

Runnable **demonstration** project using generated synthetic store-SKU demand. It does not claim actual commercial deployment or verified pricing elasticity.

## Quickstart
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r projects/retail-demand-forecasting/requirements.txt
python projects/retail-demand-forecasting/pipeline.py
pytest projects/retail-demand-forecasting/tests -q
```
Output: `projects/retail-demand-forecasting/outputs/forecasts.csv` and `metrics.json`. Replace synthetic data with authorized real transactions for real evaluation. A baseline is included before more advanced models.
