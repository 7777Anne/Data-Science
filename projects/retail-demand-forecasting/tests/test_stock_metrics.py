import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import pytest
from omnichannel import make_synthetic_sales
from stock_metrics import make_assumed_stock_and_costs, stock_turnover_metrics

def test_stock_turnover_matches_cogs_divided_by_inventory():
    sales = pd.DataFrame({
        "date": ["2025-01-01", "2025-01-02"], "store": ["A", "A"],
        "sku": ["X", "X"], "channel": ["store", "store"],
        "units": [10, 20], "unit_price": [20., 20.], "promotion": [0, 0]})
    snapshots = pd.DataFrame({
        "date": ["2025-01-01", "2025-01-02"], "store": ["A", "A"],
        "sku": ["X", "X"], "on_hand": [100, 200]})
    costs = pd.DataFrame({"store": ["A"], "sku": ["X"], "unit_cost": [10.]})
    result = stock_turnover_metrics(sales, snapshots, costs).iloc[0]
    assert result.cost_of_goods_sold == 300
    assert result.average_inventory_at_cost == 1500
    assert result.inventory_turnover_period == pytest.approx(.2)
    assert result.sales_velocity_units_per_day == 15

def test_missing_inventory_snapshots_are_not_silently_assumed():
    sales = pd.DataFrame({
        "date": ["2025-01-01", "2025-01-02"], "store": ["A", "A"],
        "sku": ["X", "X"], "channel": ["store", "store"],
        "units": [10, 20], "unit_price": [20., 20.], "promotion": [0, 0]})
    stock = pd.DataFrame({"date": ["2025-01-01"], "store": ["A"],
                          "sku": ["X"], "on_hand": [100]})
    costs = pd.DataFrame({"store": ["A"], "sku": ["X"], "unit_cost": [10.]})
    with pytest.raises(ValueError, match="Snapshot"):
        stock_turnover_metrics(sales, stock, costs)

def test_assumed_inventory_generator_is_explicit():
    sales = make_synthetic_sales(days=90)
    stock, costs = make_assumed_stock_and_costs(sales)
    result = stock_turnover_metrics(sales, stock, costs)
    assert len(result) == 6
    assert np.isfinite(result.inventory_turnover_period).all()
