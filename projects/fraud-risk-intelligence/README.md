# Fraud Risk Intelligence — Classification and Risk Thresholds

**Implemented:** deterministic synthetic transaction generator; prediction-time features; chronological split; imputation fitted only on training records; balanced logistic-regression baseline; validation-selected F1 threshold; held-out PR-AUC/precision/recall; unit tests and model artifacts.

**Not yet implemented:** PaySim evaluation, XGBoost/SHAP, probability calibration, production scoring, real 300M/day benchmarking. No model score is asserted without running the pipeline.

## Run (from repository root)
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r projects/fraud-risk-intelligence/requirements.txt
python projects/fraud-risk-intelligence/src/pipeline.py
pytest -q projects/fraud-risk-intelligence/tests
```
Output: `projects/fraud-risk-intelligence/artifacts/metrics.json` and a locally serialized model (ignored by Git).

**Leakage contract:** Exclude post-event account balances, investigation labels, and merchant outcomes. `previous_tx_count` is strictly prior-event count. If moving to PaySim, rewrite the source contract and feature policy; synthetic data is not interchangeable with actual telecom fraud detection. See [data card](docs/DATA_CARD.md).
