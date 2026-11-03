"""Run the independent, synthetic omni-channel forecasting demonstration."""
from pathlib import Path
import json
import pandas as pd
from omnichannel import (
    make_synthetic_sales, validate_sales, aggregate_store_sku,
    rolling_origin_backtest, forecast_at_origin,
    recommend_inventory, price_elasticity_association,
)

ROOT = Path(__file__).resolve().parent

def main():
    sales = validate_sales(make_synthetic_sales())
    daily = aggregate_store_sku(sales)
    end = daily.date.max()
    origins = [end - pd.Timedelta(days=28), end - pd.Timedelta(days=14)]
    backtest, metrics = rolling_origin_backtest(daily, origins, horizon=7)
    future = forecast_at_origin(daily, horizon=7)
    inventory = future[["store", "sku"]].drop_duplicates().copy()
    inventory["on_hand"] = 50
    inventory["on_order"] = 0
    inventory["backorders"] = 0
    decisions = recommend_inventory(future, inventory, daily_error_sd=4.)
    price_associations = price_elasticity_association(sales)
    outputs = ROOT / "outputs" / "omnichannel_demo"
    outputs.mkdir(parents=True, exist_ok=True)
    sales.to_csv(outputs / "synthetic_channel_sales.csv", index=False)
    backtest.to_csv(outputs / "recursive_backtest.csv", index=False)
    future.to_csv(outputs / "seven_day_forecast.csv", index=False)
    decisions.to_csv(outputs / "inventory_recommendations.csv", index=False)
    price_associations.to_csv(outputs / "price_associations_not_causal.csv", index=False)
    metrics.update({
        "data_source": "synthetic; not real retail",
        "inventory_assumptions": "50 units on hand, 7-day lead/review time, 4 units daily error sd",
        "pricing_assumptions": "observational log-price coefficient, not causal elasticity"
    })
    (outputs / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n")
    print(json.dumps(metrics, indent=2))

if __name__ == "__main__":
    main()
