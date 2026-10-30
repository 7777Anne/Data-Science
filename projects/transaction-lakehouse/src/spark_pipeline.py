"""Optional Spark SQL equivalent of silver/gold stage. Requires pip install pyspark."""
from __future__ import annotations
from pyspark.sql import SparkSession, functions as F, Window

def curate_spark(df):
    required={"transaction_id","event_time","ingest_time","amount","currency","status"}
    missing=required-set(df.columns)
    if missing: raise ValueError(f"Missing columns: {sorted(missing)}")
    valid=df.where(
        F.col("transaction_id").isNotNull() &
        F.col("event_time").isNotNull() &
        F.col("ingest_time").isNotNull() &
        (F.col("amount")>=0) &
        F.col("currency").isin("USD","INR","EUR") &
        F.col("status").isin("settled","pending"))
    # Assumes identical timestamp ties represent the same event; upstream needs a source sequence for true CDC.
    window=Window.partitionBy("transaction_id").orderBy(F.col("ingest_time").desc(),
                                                        F.col("event_time").desc())
    return valid.withColumn("_rank",F.row_number().over(window)).where(F.col("_rank")==1).drop("_rank")

def aggregate_spark(silver):
    return (silver.where(F.col("status")=="settled")
            .groupBy(F.to_date("event_time").alias("date"),"currency")
            .agg(F.count("*").alias("transaction_count"),
                 F.sum("amount").alias("transaction_value")))

if __name__=="__main__":
    spark=SparkSession.builder.appName("portfolio-transaction-lakehouse").master("local[*]").getOrCreate()
    df=spark.read.option("header",True).option("inferSchema",True).csv("projects/transaction-lakehouse/artifacts/bronze.csv")
    clean=curate_spark(df)
    aggregate_spark(clean).show(20,truncate=False)
    spark.stop()
