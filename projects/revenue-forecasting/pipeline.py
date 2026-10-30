"""Synthetic 26-series forecasting demonstration, no enterprise data."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

ROOT = Path(__file__).resolve().parent

def demo_series(seed=11):
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2023-01-01", periods=42, freq="MS")
    rows = []
    for product in range(26):
        seasonal = 60 * np.sin(2 * np.pi * np.arange(len(dates)) / 12)
        vals = np.maximum(1, 500 + product*30 + np.arange(len(dates))*3 + seasonal + rng.normal(0, 15, len(dates)))
        rows.extend(zip(dates, [f"series_{product:02d}"]*len(dates), vals))
    return pd.DataFrame(rows, columns=["month","series","revenue"])

def predict(history, horizon, method):
    x = np.asarray(history, dtype=float)
    if method == "seasonal_naive":
        return np.array([x[-12 + (i % 12)] if len(x) >= 12 else x[-1] for i in range(horizon)])
    if method == "moving_average":
        return np.repeat(np.mean(x[-3:]), horizon)
    if method == "arima":
        try:
            return np.asarray(ARIMA(x, order=(1,1,0)).fit().forecast(steps=horizon))
        except (ValueError, np.linalg.LinAlgError):
            return predict(x, horizon, "moving_average")
    raise ValueError(method)

def run():
    data = demo_series()
    forecasts, scores = [], []
    for name, group in data.groupby("series"):
        y = group.sort_values("month").revenue.to_numpy()
        methods = ["seasonal_naive", "moving_average", "arima"]
        for method in methods:
            errors = []
            for origin in range(len(y)-4, len(y)):
                errors.append(abs(y[origin] - predict(y[:origin], 1, method)[0]))
            scores.append({"series":name, "method":method, "mae":float(np.mean(errors))})
        best = min([row for row in scores if row["series"] == name], key=lambda r:r["mae"])["method"]
        predictions = predict(y, 3, best)
        for dt, value in zip(pd.date_range(group.month.max() + pd.offsets.MonthBegin(), periods=3, freq="MS"), predictions):
            forecasts.append({"series":name, "month":dt, "forecast":max(0,float(value)), "selected_model":best})
    output = ROOT / "outputs"
    output.mkdir(exist_ok=True)
    pd.DataFrame(scores).to_csv(output / "backtest.csv", index=False)
    pd.DataFrame(forecasts).to_csv(output / "forecasts.csv", index=False)
    (output / "metadata.json").write_text(json.dumps({"dataset":"synthetic_demo","rolling_origins":4,"horizon_months":3}, indent=2))
    print("Saved", len(forecasts), "forecast rows")

if __name__ == "__main__":
    run()
