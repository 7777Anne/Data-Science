# Transaction Lakehouse — Data Engineering

**Runnable:** deterministic bronze (raw) -> silver (validated and deduplicated) -> gold (daily settled aggregates) demonstration using pandas. A **separate optional PySpark implementation** of silver and gold is provided but requires a local Spark/JDK setup and must be verified independently.

## Run
```bash
pip install -r projects/transaction-lakehouse/requirements.txt
python projects/transaction-lakehouse/src/pipeline.py
pytest -q projects/transaction-lakehouse/tests
```
Review `artifacts/bronze.csv`, `silver.csv`, `gold_daily.csv`, and `quality.json`.

## PySpark optional
```bash
pip install -r projects/transaction-lakehouse/requirements-spark.txt
python projects/transaction-lakehouse/src/spark_pipeline.py
```

Important: This is **not** a Delta lake, streaming system, complete CDC implementation, or measured 300M+ events/day platform. It has no persistent state or late-arrival watermark yet. Do not claim performance beyond locally measured throughput. Synthetic data has no private customer details. Design notes: [data card](docs/DATA_CARD.md).
