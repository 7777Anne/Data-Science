"""Inventory turnover KPIs using explicit inventory and product-cost inputs.

No inventory history or COGS is inferred from sales alone. The runnable
example supplies clearly labelled synthetic snapshots and assumed costs.
"""
import numpy as np
import pandas as pd

from omnichannel import validate_sales, KEYS

def stock_turnover_metrics(sales, snapshots, costs):
    """Store-SKU turnover = total COGS / mean inventory value at cost.

    Assumes one daily closing inventory snapshot per sales date and store/SKU.
    Output period is exactly the input sales date range.
    """
    transactions = validate_sales(sales)
    expected_snap = ["date", "store", "sku", "on_hand"]
    expected_cost = ["store", "sku", "unit_cost"]
    if set(expected_snap).difference(snapshots.columns):
        raise ValueError("Missing inventory snapshot fields")
    if set(expected_cost).difference(costs.columns):
        raise ValueError("Missing product cost fields")
    stock = snapshots[expected_snap].copy()
    stock["date"] = pd.to_datetime(stock.date).dt.normalize()
    products = costs[expected_cost].copy()
    if stock[expected_snap].isna().any().any() or products[expected_cost].isna().any().any():
        raise ValueError("Missing values in stock or cost records")
    if stock.duplicated(["date"] + KEYS).any() or products.duplicated(KEYS).any():
        raise ValueError("Duplicate inventory or cost grain")
    if (stock.on_hand < 0).any() or (products.unit_cost <= 0).any():
        raise ValueError("Invalid stock or cost values")
    daily = transactions.groupby(["date"] + KEYS, as_index=False).agg(units=("units", "sum"))
    matched = daily.merge(stock, on=["date"] + KEYS, how="left", validate="one_to_one")
    if matched.on_hand.isna().any() or len(stock) != len(matched):
        raise ValueError("Snapshot must cover every sales date and store/SKU exactly")
    matched = matched.merge(products, on=KEYS, how="left", validate="many_to_one")
    if matched.unit_cost.isna().any():
        raise ValueError("No product cost for some store/SKUs")
    matched["cogs"] = matched.units * matched.unit_cost
    matched["inventory_at_cost"] = matched.on_hand * matched.unit_cost
    result = matched.groupby(KEYS, as_index=False).agg(
        units_sold=("units", "sum"),
        days_observed=("date", "nunique"),
        cost_of_goods_sold=("cogs", "sum"),
        average_inventory_at_cost=("inventory_at_cost", "mean"),
        average_on_hand=("on_hand", "mean"))
    result["sales_velocity_units_per_day"] = result.units_sold / result.days_observed
    average_value = result.average_inventory_at_cost.replace(0, np.nan)
    result["inventory_turnover_period"] = result.cost_of_goods_sold / average_value
    result["days_of_supply_at_observed_velocity"] = (
        result.average_on_hand / result.sales_velocity_units_per_day.replace(0, np.nan))
    return result

def make_assumed_stock_and_costs(sales, seed=42):
    """Synthetic assumptions for demo only, never presented as measured inventory."""
    df = validate_sales(sales)
    rng = np.random.default_rng(seed)
    unique = df[["date"] + KEYS].drop_duplicates().sort_values(["date"] + KEYS).copy()
    unique["on_hand"] = rng.integers(50, 150, size=len(unique))
    costs = unique[KEYS].drop_duplicates().copy()
    costs["unit_cost"] = costs.sku.map({
        "TEE-BLK-M": 360., "SHOE-WHT-08": 1100., "BAG-CASUAL": 590.})
    if costs.unit_cost.isna().any():
        raise ValueError("Add an explicit cost assumption for new SKUs")
    return unique, costs
