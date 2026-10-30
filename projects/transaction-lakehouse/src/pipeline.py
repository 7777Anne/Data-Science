"""Deterministic bronze/silver/gold transaction ETL with data quality checks."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
CURRENCIES={"USD","INR","EUR"}

def generate_events(n=1000,seed=23):
    if n<10: raise ValueError("Use at least 10 transactions")
    rng=np.random.default_rng(seed)
    ts=pd.Timestamp("2026-01-01",tz="UTC")+pd.to_timedelta(rng.integers(0,86400*7,n),unit="s")
    data=pd.DataFrame({
        "transaction_id":[f"tx_{i:08d}" for i in range(n)],
        "event_time":ts,
        "ingest_time":ts+pd.to_timedelta(rng.integers(0,3600,n),unit="s"),
        "account_id_hash":[f"demo_{i%100:04d}" for i in range(n)],
        "amount":rng.uniform(1,1500,n).round(2),
        "currency":rng.choice(sorted(CURRENCIES),n),
        "status":rng.choice(["settled","pending"],n,p=[0.9,0.1])})
    duplicates=data.iloc[:10].copy()
    duplicates["ingest_time"]+=pd.Timedelta(hours=3)
    invalid=data.iloc[[10]].copy()
    invalid["transaction_id"]="bad_currency"
    invalid["currency"]="INVALID"
    invalid["ingest_time"]+=pd.Timedelta(hours=4)
    return pd.concat([data,duplicates,invalid],ignore_index=True)

def curate(bronze):
    required={"transaction_id","event_time","ingest_time","amount","currency","status"}
    missing=required-set(bronze.columns)
    if missing: raise ValueError(f"Missing columns: {sorted(missing)}")
    events=bronze.copy()
    events["event_time"]=pd.to_datetime(events["event_time"],utc=True,errors="coerce")
    events["ingest_time"]=pd.to_datetime(events["ingest_time"],utc=True,errors="coerce")
    events["amount"]=pd.to_numeric(events["amount"],errors="coerce")
    valid=(events.transaction_id.notna() & events.event_time.notna() &
           events.ingest_time.notna() & events.amount.ge(0) &
           events.currency.isin(CURRENCIES) &
           events.status.isin(["settled","pending"]))
    clean=events.loc[valid].sort_values(["ingest_time","transaction_id"],kind="stable")
    # Latest valid record wins; deterministic for identical ingestion timestamps.
    silver=clean.drop_duplicates("transaction_id",keep="last").sort_values("transaction_id").reset_index(drop=True)
    report={"bronze_rows":int(len(bronze)),"invalid_rows":int((~valid).sum()),
            "valid_duplicate_rows":int(len(clean)-len(silver)),
            "silver_rows":int(len(silver))}
    return silver,report

def aggregate(silver):
    settled=silver.loc[silver.status=="settled"].copy()
    settled["date"]=settled.event_time.dt.strftime("%Y-%m-%d")
    return settled.groupby(["date","currency"],as_index=False).agg(
        transaction_count=("transaction_id","size"),
        transaction_value=("amount","sum")).sort_values(["date","currency"])

def run(n=1000):
    bronze=generate_events(n)
    silver,report=curate(bronze)
    gold=aggregate(silver)
    out=ROOT/"artifacts";out.mkdir(parents=True,exist_ok=True)
    bronze.to_csv(out/"bronze.csv",index=False)
    silver.to_csv(out/"silver.csv",index=False)
    gold.to_csv(out/"gold_daily.csv",index=False)
    (out/"quality.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--rows",type=int,default=1000)
    run(p.parse_args().rows)
