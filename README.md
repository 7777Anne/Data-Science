# Applied ML, Data Engineering, Forecasting and AI — Project Portfolio

A curated set of **distinct problem-domain projects**, with runnable examples, evidence boundaries and separate setup instructions. All example transaction and factory data here is synthetic/fictional. Nothing in these repositories implies access to or redistribution of employer/customer data.

## Working demos — select a project

| Domain | Project | Demonstrates | Status |
| --- | --- | --- | --- |
| Machine Learning | [Fraud Risk Intelligence](projects/fraud-risk-intelligence/README.md) | low-prevalence classification, time-aware holdout, threshold selection, PR-AUC | Synthetic demo + tests |
| Retail Analytics | [Retail Demand Forecasting](projects/retail-demand-forecasting/README.md) | unit-demand, safe lags, one-step backtest, next-day forecast, replenishment example | Synthetic demo + tests |
| Financial Forecasting | [Multi-Series Revenue Forecasting](projects/revenue-forecasting/README.md) | ARIMA + baselines, rolling-origin errors across 26 synthetic series | Synthetic demo + tests |
| Data Engineering | [Transaction Lakehouse](projects/transaction-lakehouse/README.md) | bronze/silver/gold quality validation, deduplication, analytics; optional Spark SQL | Pandas demo + tests; Spark optional |
| GenAI / Retrieval | [Industrial Knowledge Assistant](projects/industrial-knowledge-assistant/README.md) | citation-aware TF-IDF document QA; optional FAISS / local Ollama | Runnable offline baseline + tests |
| Applied ML | [Hotel Booking Cancellation](https://github.com/7777Anne/hotel-booking-cancellation-ml) | booking-time classification and serving | Separate repo; feature branches under review |

## Research / earlier work

- [Automotive Engineering Copilot](projects/automotive-engineering-copilot/README.md): NHTSA evidence-backed research scaffold, **not a working automotive model**.
- [EV Sustainability Analysis](projects/ev-sustainability-analysis/README.md): historical resume topic, evidence and reproducible source still required.
- [Precision Medicine Dashboard](projects/precision-medicine-dashboard/README.md): historical resume topic, source and medical-data review still required.

## Fast start: run one project at a time

```bash
git clone https://github.com/7777Anne/Data-Science.git
cd Data-Science
python3 -m venv .venv
source .venv/bin/activate
pip install -r projects/retail-demand-forecasting/requirements.txt
python projects/retail-demand-forecasting/pipeline.py
pytest -q projects/retail-demand-forecasting/tests
```

Other project commands are in each project's own README. CI on the curated branch runs offline unit tests and demo jobs. See [audit and quality checklist](docs/PORTFOLIO_AUDIT.md) and [resume evidence matrix](docs/RESUME_EVIDENCE_MATRIX.md).

**Status policy:** "Runnable synthetic demo" does not mean "production-ready", deployed, accurate on real data, or demonstrated at commercial scale. Data licenses, event-time semantics, privacy, resource benchmarks and model reliability must be independently reviewed before public or commercial use.
