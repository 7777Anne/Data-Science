# Code review, debugging decisions and next actions

Reviewed: 2026-10-30. Scope: available GitHub branches and resume variants; remote CI should verify the resulting code. Full local Mac execution with real licensed datasets remains pending.

## Findings and applied fixes

| Priority | Finding | Resolution or action |
| --- | --- | --- |
| P0 | Main lacked project navigation; several open PRs had overlapping work | Created a curated PR with explicit project domains. Avoid blindly merging earlier PRs on top |
| P0 | Retail test predictions used actual preceding test observations, yet could appear to be a multi-day forward forecast | Relabeled as **one-step historical backtest** and separated actual next-day inference |
| P0 | Existing hotel PR #3 had random holdout and static risk bands | Prefer older chronological baseline PR #2 with validation-selected threshold; reconcile in hotel repo |
| P0 | Incomplete/NaN labels might evade original cancellation-label validation | Prefer strict target checks in hotel baseline branch |
| P1 | Multiple portfolio scaffolds were empty | Reused existing RAG source and implemented synthetic fraud classification and transaction ETL rather than more empty directories |
| P1 | No centralized tests for forecasting and data ETL | Added a project CI workflow, unit tests and reproducible outputs |
| P1 | Forecast code missing Prophet, calibrated intervals and regional decomposition | Documented as **not yet implemented** rather than asserting they exist |
| P1 | Transaction Spark path not locally verified | Kept Spark optional and documented runtime dependencies and semantics |

## Verification levels

- Static code review: source inspection for problem definition, leakage, metrics, testing and deployability.
- Automated smoke test: CI installs dependencies, runs unit tests and demo scripts with synthetic data.
- Real-dataset validity: **NOT established** by this PR; requires source provenance, EDA, split design and independently recorded metrics.
- Production-readiness: **NOT established** by this PR; requires security review, CI/CD, observability, artifact provenance, data contracts, automated rollback and operations runbook.

## Debug locally (same sequence a senior reviewer follows)

```bash
python -m pip install -r projects/retail-demand-forecasting/requirements.txt
pytest -q -x projects/retail-demand-forecasting/tests
python projects/retail-demand-forecasting/pipeline.py
cat projects/retail-demand-forecasting/outputs/metrics.json

python -m pip install -r projects/fraud-risk-intelligence/requirements.txt
pytest -q -x projects/fraud-risk-intelligence/tests
python projects/fraud-risk-intelligence/src/pipeline.py

python -m pip install -r projects/transaction-lakehouse/requirements.txt
pytest -q -x projects/transaction-lakehouse/tests
python projects/transaction-lakehouse/src/pipeline.py
```

- `-x` stops on first failure, preserving the first root-cause traceback.
- Check input schema -> prediction-time feature availability -> split boundaries -> baseline -> model -> output invariants.
- Re-run with same random seed; inspect reproducibility before optimizing model scores.
- Run CI on each PR, review failed job logs and avoid merging until tests pass.

## What a portfolio-grade project still needs

1. Sourced, permitted dataset with data card, precise target and prediction-time contract.
2. Honest baseline and proper time-aware validation / held-out test.
3. Actual metrics, confidence intervals where appropriate, error segmentation and failure analysis.
4. Typed modules, modular configuration, test coverage, deterministic dependencies, explicit resource assumptions.
5. One useful output: report/dashboard/API endpoint plus architecture screenshot *from actual execution*.
6. Security controls, privacy review, monitoring/observability and incremental/deployment strategy where relevant.
7. README screenshots based on actual generated results, not fabricated metrics or UI mockups.

Never publish production data, internal IP, client names/tables, credentials or unverifiable performance results.
