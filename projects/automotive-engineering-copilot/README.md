# Automotive Engineering Intelligence Copilot

**Status: PROJECT SCAFFOLD — not implemented or benchmarked.**

## Dataset
NHTSA public recalls and complaints APIs and data dictionaries: https://www.nhtsa.gov/nhtsa-datasets-and-apis

## Planned end-to-end use case
Grounded retrieval on vehicle safety records, source citations, Recall@K, MRR, refusals and API.

## Evidence and limitations
Consumer complaints are allegations, not verified defects; no proprietary Mercedes documents.

## Proposed steps
1. Verify access, terms, columns, and dataset grain.
2. Build tiny reproducible fixture and data audit.
3. Establish chronological or data-quality validation as appropriate.
4. Implement the smallest working baseline/pipeline and tests.
5. Compare alternatives, log actual metrics and hardware.
6. Add an API/dashboard only if it serves a concrete stakeholder need.

## Structure
`data/raw`, `data/interim`, `data/processed` are ignored and hold local datasets. Source code belongs in `src`; tests in `tests`; notebooks in `notebooks`; settings in `configs`; research and source cards in `docs`; untracked outputs in `artifacts`.

Read [data register](../../docs/DATASET_REGISTER.md) and [roadmap](../../docs/IMPLEMENTATION_ROADMAP.md).
