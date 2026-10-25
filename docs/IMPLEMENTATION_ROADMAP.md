# Execution roadmap: four flagships

## First local setup
1. `git fetch origin` then `git switch portfolio/four-flagship-projects` (or `git switch -c portfolio/four-flagship-projects --track origin/portfolio/four-flagship-projects`).
2. Read each project `README.md`, `docs/DATA_CARD.md` and `docs/RESEARCH_REVIEW.md`.
3. Create a venv **inside the project you're working on**, use its eventual pinned requirements, and validate one tiny fixture before scaling.
4. Do not place raw datasets, credentials, large model weights, or proprietary client files in Git.

## Priorities and acceptance criteria

### P1 Automotive GenAI — MBRDI
MVP: download NHTSA recall records, normalize identifiers/metadata, build BM25 retrieval baseline, semantic retrieval comparison, grounded citation response, evaluation set and tests. API + simple UI follow. Verify factual citations and refuse when no evidence.

### P2 Retail Forecasting
MVP: ingest official M5 train/calendar files, reshape to a manageable store/category subset, sanity-check calendar and prices, implement seasonal-naive 28-day forecast, rolling backtest, metrics and plots. Then expand to a global lag-feature model and interval backtests. Guard against future known/unknown covariate confusion.

### P3 Fraud ML
MVP: documented public/synthetic transaction dataset, leakage audit, imbalance-aware logistic baseline, time-based split, PR-AUC + expected-cost threshold, gradient boosted comparison, tests. SHAP, API, drift simulation next.

### P4 PySpark Lakehouse
MVP: deterministic synthetic generator + data contract, bronze ingestion, silver quality/dedup, gold aggregates, idempotent reruns, assertions and Spark explain plan evidence. Streaming and benchmark profiling after reliable batch pipeline.

### Existing booking cancellation repo
Continue separate draft PR #2. Its development status is independent of these scaffolds. Use the actual uploaded CSV for reproducible metric checks; verify CI before merge.

## Definition of done (each project)
- Reproducible small fixture and documented real data source/access
- Clear prediction/use-case boundary, schema and leakage checks
- Executable end-to-end path with deterministic tests and passing CI
- Compared baseline and candidate or justified single-method scope
- Actual run logs, honest metrics, machine specifications and limitations
- Working documented API/demo **when applicable**, secured inputs and no exposed secrets
- README demo commands re-run successfully
- Interview design decisions, failure modes and cost/performance trade-offs

**Scaffold exists ≠ implementation completed.** Never convert checkboxes to completed without a passing test or inspectable evidence.
