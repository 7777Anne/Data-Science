# Multi-Series Revenue Forecasting — Public Template

Standalone **synthetic demo**, inspired by general forecasting workflows. No confidential customer data, credentials, or client-specific SQL. The repo does **not** substantiate proprietary production results.

## Run
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r projects/revenue-forecasting/requirements.txt
python projects/revenue-forecasting/pipeline.py
```
Generates 26 synthetic monthly series, tests ARIMA versus seasonal-naive and 3-month mean using rolling-origin validation, and forecasts three future months. The very short demo history is for smoke testing, not a reliable accuracy claim.
