"""Fraud risk classification demo: synthetic events only, no customer data."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, precision_score, recall_score, f1_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
FEATURES = ["amount", "hour", "previous_tx_count", "channel"]

def generate_events(n: int = 6000, seed: int = 13) -> pd.DataFrame:
    """Deterministic synthetic labeled event stream; simulate low base-rate positives."""
    if n < 200:
        raise ValueError("Need >=200 transactions for a meaningful train/validation/test smoke run")
    rng = np.random.default_rng(seed)
    account = rng.integers(0, 450, n)
    amount = rng.lognormal(4.0, 1.1, n).round(2)
    hour = rng.integers(0, 24, n)
    channel = rng.choice(["app","ussd","web"], n, p=[0.55,0.30,0.15])
    frame = pd.DataFrame({"event_step":np.arange(n),"account_id":account,
                          "amount":amount,"hour":hour,"channel":channel})
    # cumcount is past transaction count for same account, excluding this event.
    frame["previous_tx_count"] = frame.groupby("account_id").cumcount()
    logits = -4.6 + 0.7*(amount > 180) + 1.0*(amount > 650) + 0.8*(hour < 5) + 0.55*(channel == "web")
    p = 1 / (1 + np.exp(-logits))
    frame["is_fraud"] = rng.binomial(1, p)
    return frame

def chronological_splits(frame: pd.DataFrame):
    frame = frame.sort_values("event_step").reset_index(drop=True)
    a,b = int(len(frame)*0.7), int(len(frame)*0.85)
    train,val,test = frame.iloc[:a],frame.iloc[a:b],frame.iloc[b:]
    if any(x["is_fraud"].nunique() < 2 for x in (train,val,test)):
        raise ValueError("All splits must contain fraud and non-fraud examples")
    return train,val,test

def model_pipeline():
    return Pipeline([
        ("preprocessor", ColumnTransformer([
            ("numbers", Pipeline([("fill",SimpleImputer(strategy="median")),("scale",StandardScaler())]),
             ["amount","hour","previous_tx_count"]),
            ("channel",OneHotEncoder(handle_unknown="ignore"),["channel"])
        ])),
        ("classifier",LogisticRegression(max_iter=1000,class_weight="balanced",random_state=42))
    ])

def fit_evaluate(frame: pd.DataFrame):
    train,val,test = chronological_splits(frame)
    model = model_pipeline().fit(train[FEATURES],train["is_fraud"])
    validation_probability = model.predict_proba(val[FEATURES])[:,1]
    thresholds = np.arange(0.1,0.91,0.05)
    threshold = float(max(thresholds,key=lambda t:f1_score(val["is_fraud"],validation_probability>=t,zero_division=0)))
    probability = model.predict_proba(test[FEATURES])[:,1]
    predicted = probability>=threshold
    metrics = {
        "data_type":"synthetic_demo", "test_rows":int(len(test)),
        "fraud_prevalence_test":float(test.is_fraud.mean()),
        "selected_threshold_on_validation":threshold,
        "test_pr_auc":float(average_precision_score(test.is_fraud,probability)),
        "test_precision":float(precision_score(test.is_fraud,predicted,zero_division=0)),
        "test_recall":float(recall_score(test.is_fraud,predicted,zero_division=0)),
        "test_f1":float(f1_score(test.is_fraud,predicted,zero_division=0)),
        "baseline_pr_auc":float(test.is_fraud.mean()),
        "no_future_balance_fields":True,
        "split":"ordered by synthetic event_step; 70/15/15"
    }
    return model,metrics

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--rows",type=int,default=6000)
    args=parser.parse_args()
    model,metrics=fit_evaluate(generate_events(args.rows))
    output=ROOT/"artifacts";output.mkdir(parents=True,exist_ok=True)
    joblib.dump(model,output/"fraud_baseline.joblib")
    (output/"metrics.json").write_text(json.dumps(metrics,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(metrics,indent=2))

if __name__=="__main__":
    main()
