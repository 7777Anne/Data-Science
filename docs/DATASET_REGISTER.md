# Dataset register and acquisition decisions

Last reviewed: 2026-10-25. Download availability, license and raw schema must be verified again when ingestion code is implemented.

## 1. Fraud Risk Intelligence
**Candidate source:** PaySim synthetic mobile-money transactions, originally designed from aggregated transaction patterns to simulate fraud. Dataset often distributed through Kaggle under "Synthetic Financial Datasets For Fraud Detection" / `PS_2017_Generated_Data.csv`.
- Typical schema to verify: step, type, amount, nameOrig, oldbalanceOrg, newbalanceOrig, nameDest, oldbalanceDest, newbalanceDest, isFraud, isFlaggedFraud.
- Prediction-time rules: **post-transaction balances can leak future/outcome state** and must be excluded for pre-authorization prediction unless justified by an exact event-time contract.
- Validate chronology of `step`, duplicated IDs, drift, positive rate, class imbalance and feature availability.
- Fallback: generate a clearly labeled synthetic transaction dataset from a documented schema, without claiming it reproduces PaySim or production fraud prevalence.
- Paper to read: López-Rojas et al., PaySim / mobile money financial simulator; verify publication and simulator assumptions from the original source.
- Never commit raw transaction-level data if provenance/permissions are uncertain.

## 2. Transaction Lakehouse
**Primary data:** deterministic **synthetic** streaming/batch transaction events generated locally, with data contract and injected defects. Fields: transaction_id, account_id_hash, event_time, ingest_time, amount, currency, merchant_category, channel, status, source_system, schema_version.
- Data quality scenarios: repeated events, null IDs, late arrivals, invalid currency, schema evolution, skewed merchant IDs.
- Goal is to benchmark throughput and shuffle behavior on stated actual compute; synthetic volume is **not evidence** of processing 300M+ events/day in production.
- Optionally import a small permitted sample of Online Retail II for separate retail analytics. Do not conflate retail invoices with bank transfers.
- Public reference: UCI Online Retail II https://archive.ics.uci.edu/dataset/502/online+retail+ii

## 3. Automotive Engineering Copilot
**Source:** public NHTSA vehicle recall and complaint datasets + field dictionaries.
- Source hub: https://www.nhtsa.gov/nhtsa-datasets-and-apis
- API examples: `https://api.nhtsa.gov/recalls/recallsByVehicle?make=acura&model=rdx&modelYear=2012` and complaint endpoints.
- Document units: recall campaign, vehicle make/model/year, affected components, summary, consequence, remedy, report date, and provenance URI where supplied.
- Build retrieval gold set with manual factual Q&A, supporting record IDs, and answerability labels. Keep official source updates and snapshots tracked.
- Cautions: complaint narratives are unverified allegations, not proof of a defect. Never represent generated recommendations as safety engineering approvals.
- No Mercedes proprietary documents or internal procedures.

## 4. Retail Demand Forecasting
**Preferred dataset:** M5 Forecasting Accuracy competition (Walmart historical **daily unit sales**, not revenue).
- Official dataset: https://www.kaggle.com/competitions/m5-forecasting-accuracy/data
- Files: `calendar.csv`, `sell_prices.csv`, `sales_train_validation.csv` (d_1..d_1913); historical labels and competition evaluation split.
- M5 is ~450 MB compressed listing; Kaggle account/rules acceptance may be required. Never rehost competition data without permission.
- Grain: item x store x date; combine optional calendar events, SNAP indicators and prices only at times legitimately known at forecasting origin.
- Forecast **unit demand** for 28 days; a separately derived revenue estimate needs contemporaneous price availability and explicit assumptions.
- Methods: seasonal naive, moving average, ETS / SARIMA for aggregated subset, gradient-boosted lag model if compute permits.
- Evaluation: rolling-origin backtests with a 28-day horizon, WAPE/MAE/sMAPE and M5-style WRMSSE where correctly implemented; report zero-demand and intermittent series.
- Reference: https://www.kaggle.com/competitions/m5-forecasting-uncertainty/data for uncertainty challenge; do not claim calibrated intervals without testing.
- Lightweight alternative for faster local experiments: UCI Online Retail II has ~1.07M invoice lines (2009–2011). It supports aggregated daily or weekly gross sales analysis, but cancellations/returns, negative quantities and incomplete stock history limit demand interpretation. Cite https://archive.ics.uci.edu/dataset/502/online+retail+ii

## Shared governance
For each dataset document source URL, license/access constraints, download date, immutable file hash, row count, time coverage, schema, missingness, duplicates, target/prediction-time definition, leakage risks, and ethical limitations in `docs/DATA_CARD.md`. No results are reported until actual ingestion and tests run.
