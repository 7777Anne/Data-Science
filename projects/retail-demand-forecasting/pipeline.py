"""Retail unit-demand demonstration with one-step evaluation and next-day inference.

Synthetic data and fixed illustrative inventory are not real store forecasts.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error

ROOT = Path(__file__).resolve().parent
FEATURES = ["store", "sku", "lag_1", "lag_7", "avg_7", "dow"]

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
    return pd.DataFrame(rows, columns=["date","store","sku","units"])

def features(df):
    df = df.sort_values(["store","sku","date"]).copy()
    group = df.groupby(["store","sku"])["units"]
    df["lag_1"] = group.shift(1)
    df["lag_7"] = group.shift(7)
    df["avg_7"] = df.groupby(["store","sku"])["lag_1"].transform(
        lambda x: x.rolling(7,min_periods=7).mean())
    df["dow"] = df["date"].dt.dayofweek
    return df.dropna(subset=["lag_1","lag_7","avg_7"]).reset_index(drop=True)

def next_day_features(history):
    rows=[]
    for (store,sku),group in history.groupby(["store","sku"]):
        group=group.sort_values("date")
        if len(group)<7:
            raise ValueError("At least seven days of history required per store-SKU")
        tomorrow=group.date.iloc[-1]+pd.Timedelta(days=1)
        rows.append({"date":tomorrow,"store":store,"sku":sku,
                     "lag_1":float(group.units.iloc[-1]),
                     "lag_7":float(group.units.iloc[-7]),
                     "avg_7":float(group.units.iloc[-7:].mean()),
                     "dow":tomorrow.dayofweek})
    return pd.DataFrame(rows)

def run():
    history=make_data()
    frame=features(history)
    cutoff=frame.date.max()-pd.Timedelta(days=60)
    train=frame.loc[frame.date<=cutoff]
    test=frame.loc[frame.date>cutoff].copy()
    model=HistGradientBoostingRegressor(random_state=42)
    model.fit(train[FEATURES],train.units)
    # Historical one-step predictions, using actual observations available before each date.
    test["predicted_units"]=np.maximum(0,model.predict(test[FEATURES]))
    test["seasonal_naive_units"]=test.lag_7
    backtest=test[["date","store","sku","units","predicted_units","seasonal_naive_units"]]
    # Refit using all historical observations for true next-day inference.
    final_model=HistGradientBoostingRegressor(random_state=42)
    final_model.fit(frame[FEATURES],frame.units)
    future=next_day_features(history)
    future["predicted_units"]=np.maximum(0,final_model.predict(future[FEATURES]))
    future["assumed_stock_on_hand"]=40
    future["stockout_risk"]=future.predicted_units>future.assumed_stock_on_hand
    future["suggested_units_to_order"]=np.maximum(
        0,np.ceil(future.predicted_units*1.2-future.assumed_stock_on_hand)).astype(int)
    out=ROOT/"outputs";out.mkdir(exist_ok=True)
    backtest.to_csv(out/"one_step_backtest.csv",index=False)
    future[["date","store","sku","predicted_units","assumed_stock_on_hand",
            "stockout_risk","suggested_units_to_order"]].to_csv(out/"next_day_forecast.csv",index=False)
    metrics={"model_mae":float(mean_absolute_error(test.units,test.predicted_units)),
             "seasonal_naive_mae":float(mean_absolute_error(test.units,test.seasonal_naive_units)),
             "test_rows":len(test),"data_kind":"synthetic_demo",
             "evaluation":"60-day test period with one-step-ahead observed lag features",
             "deployment_horizon":"one day; no recursive 60-day claim"}
    (out/"metrics.json").write_text(json.dumps(metrics,indent=2)+"\n")
    print(json.dumps(metrics,indent=2))
    return metrics

if __name__=="__main__":
    run()
