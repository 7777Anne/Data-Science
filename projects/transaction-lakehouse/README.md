# Transaction Lakehouse

**Track:** Data platform  
**Stage:** scoped / not yet implemented. No model scores, performance benchmarks, UI demo, or deployments are claimed.

## Problem
Reconstruct consistent transaction analytics from late, duplicated and malformed synthetic events.

## Dataset
Deterministic locally generated transaction streams; optional separate UCI Online Retail II demonstration.
See [dataset card](docs/DATA_CARD.md), [research review](docs/RESEARCH_REVIEW.md), and the [shared data register](../../docs/DATASET_REGISTER.md).

## Proposed architecture
`data/raw -> schema and quality checks -> clean/curated table -> baseline -> validation/evaluation -> artifacts -> optional serving/UI`

## Technology candidates
PySpark, Spark SQL, Parquet/Delta (compatibility checked), optional Airflow, pytest, Docker.. Final decisions depend on baseline evidence and laptop/cloud resource constraints.

## Planned evaluation
Idempotency, quality rejection counts, end-to-end throughput and cost per workload on specified hardware.

## Next implementation
Implement raw generator, bronze/silver/gold, schema contracts, idempotency, incremental updates.

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
