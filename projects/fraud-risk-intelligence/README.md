# Fraud Risk Intelligence

**Track:** ML platform  
**Stage:** scoped / not yet implemented. No model scores, performance benchmarks, UI demo, or deployments are claimed.

## Problem
Explain and classify potentially fraudulent digital transactions at scoring time.

## Dataset
PaySim synthetic mobile money (subject to access/license), with deterministic synthetic fallback.
See [dataset card](docs/DATA_CARD.md), [research review](docs/RESEARCH_REVIEW.md), and the [shared data register](../../docs/DATASET_REGISTER.md).

## Proposed architecture
`data/raw -> schema and quality checks -> clean/curated table -> baseline -> validation/evaluation -> artifacts -> optional serving/UI`

## Technology candidates
Python, pandas, scikit-learn, XGBoost (candidate), MLflow, SHAP, FastAPI, pytest.. Final decisions depend on baseline evidence and laptop/cloud resource constraints.

## Planned evaluation
Time-safe PR-AUC and precision/recall; compare monetary expected cost, calibrate probabilities, SHAP and threshold choice.

## Next implementation
Define predict-before-authorization contract; audit post-event balance leakage; baseline, validation, calibration, service.

## Folder map
- `data/raw/`: source download location (ignored)
- `data/interim/`: cleaning outputs (ignored)
- `data/processed/`: model-ready outputs (ignored)
- `notebooks/`: exploration and experiments
- `src/`: maintainable pipeline/application source
- `tests/`: unit and integration tests
- `configs/`: schema/experiment configuration
- `docs/DATA_CARD.md`: source, provenance and risks
- `docs/RESEARCH_REVIEW.md`: references, tradeoffs and decisions
- `artifacts/`: local models and plots (ignored)

## Acceptance conditions
Actual ingestion + reproducible tests + measured baseline + justified model selection + observed failures + clear run instructions. A working real-data end-to-end run must precede the label "portfolio-ready".

## Ethical and technical boundaries
Public/licensed or synthetic data only; no client or employer information; no invented benchmarks or deployment claims.
