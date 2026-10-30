"""Synthetic retail demand prototype; run locally with python pipeline.py."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error

ROOT = Path(__file__).resolve().parent

def make_data(seed=42):
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2024-01-01", periods=500, freq="D")
    rows = []
    for store in range(3):
        for sku in range(4):
            season = 8 * np.sin(np.arange(len(dates)) * 2 * np.pi / 7)
            trend = np.arange(len(dates)) * 0.01
            demand = np.maximum(0, np.round(30 + 4*store + 3*sku + season + trend + rng.normal(0, 5, len(dates))))
            rows.extend(zip(dates, [store]*len(dates), [sku]*len(dates), demand))
    return pd.DataFrame(rows, columns=["date", "store", "sku", "units"])

def features(df):
    df = df.sort_values(["store", "sku", "date"]).copy()
    group = df.groupby(["store", "sku"])["units"]
    df["lag_1"] = group.shift(1)
    df["lag_7"] = group.shift(7)
    df["avg_7"] = df.groupby(["store", "sku"])["lag_1"].transform(lambda x: x.rolling(7, min_periods=7).mean())
    df["dow"] = df["date"].dt.dayofweek
    return df.dropna().reset_index(drop=True)

def run():
    frame = features(make_data())
    cutoff = frame["date"].max() - pd.Timedelta(days=60)
    train, test = frame[frame.date <= cutoff], frame[frame.date > cutoff].copy()
    cols = ["store", "sku", "lag_1", "lag_7", "avg_7", "dow"]
    model = HistGradientBoostingRegressor(random_state=42)
    model.fit(train[cols], train.units)
    test["predicted_units"] = np.maximum(0, model.predict(test[cols]))
    test["baseline_units"] = test["lag_7"]
    test["stock_on_hand"] = 40
    test["stockout_risk"] = test.predicted_units > test.stock_on_hand
    test["suggested_replenishment"] = np.maximum(0, np.ceil(test.predicted_units * 1.2 - test.stock_on_hand)).astype(int)
    out = ROOT / "outputs"
    out.mkdir(exist_ok=True)
    test[["date","store","sku","units","predicted_units","baseline_units","stockout_risk","suggested_replenishment"]].to_csv(out / "forecasts.csv", index=False)
    metrics = {"model_mae": float(mean_absolute_error(test.units, test.predicted_units)),
               "seasonal_naive_mae": float(mean_absolute_error(test.units, test.baseline_units)),
               "test_rows": len(test), "data_kind": "synthetic_demo"}
    (out / "metrics.json").write_text(json.dumps(metrics, indent=2))
    print(metrics)

if __name__ == "__main__":
    run()
