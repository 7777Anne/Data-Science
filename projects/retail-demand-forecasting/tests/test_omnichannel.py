"""Unit and integration tests for the synthetic omnichannel extension."""
import numpy as np
import pandas as pd
import pytest

from omnichannel import (
    InventoryPolicy, aggregate_store_sku, forecast_at_origin,
    make_synthetic_sales, price_elasticity_association,
    recommend_inventory, rolling_origin_backtest, validate_sales,
)

@pytest.fixture(scope="module")
def retail():
    sales = validate_sales(make_synthetic_sales(days=105))
    return sales, aggregate_store_sku(sales)

def test_channels_sum_without_double_counting(retail):
    sales, daily = retail
    assert daily.units.sum() == sales.units.sum()
    assert np.isclose(daily.revenue.sum(), (sales.units * sales.unit_price).sum())
    assert not daily.duplicated(["date", "store", "sku"]).any()

def test_duplicate_grain_rejected(retail):
    sales, _ = retail
    with pytest.raises(ValueError, match="Duplicate"):
        validate_sales(pd.concat([sales, sales.iloc[[0]]]))

def test_negative_units_rejected(retail):
    sales, _ = retail
    bad = sales.copy()
    bad.loc[0, "units"] = -1
    with pytest.raises(ValueError, match="nonnegative"):
        validate_sales(bad)

def test_recursive_seven_day_forecast(retail):
    _, daily = retail
    result = forecast_at_origin(daily, 7)
    assert len(result) == 2 * 3 * 7
    assert set(result.horizon_day) == set(range(1, 8))
    assert (result.predicted_units >= 0).all()
    assert result.date.min() > daily.date.max()

def test_future_actuals_do_not_leak(retail):
    _, daily = retail
    origin = daily.date.max() - pd.Timedelta(days=7)
    a = forecast_at_origin(daily[daily.date <= origin], 7)
    modified = daily.copy()
    modified.loc[modified.date > origin, "units"] = 99999
    b = forecast_at_origin(modified[modified.date <= origin], 7)
    pd.testing.assert_frame_equal(a, b)

def test_rolling_origin_actuals_and_metrics(retail):
    _, daily = retail
    origin = daily.date.max() - pd.Timedelta(days=7)
    rows, metrics = rolling_origin_backtest(daily, [origin], 7)
    assert rows.date.min() > origin
    assert metrics["n_forecasts"] == len(rows)
    assert metrics["mae"] >= 0

def test_reorder_math_and_trigger():
    forecast = pd.DataFrame({"store": ["A"], "sku": ["X"], "predicted_units": [10.]})
    inventory = pd.DataFrame({"store": ["A"], "sku": ["X"],
                              "on_hand": [50], "on_order": [0], "backorders": [0]})
    recommendation = recommend_inventory(forecast, inventory, InventoryPolicy(7, 7, 0), 0)
    assert recommendation.iloc[0].reorder_point == 70
    assert recommendation.iloc[0].suggested_order_units == 90
    inventory["on_hand"] = 100
    assert recommend_inventory(forecast, inventory, InventoryPolicy(7, 7, 0), 0).iloc[0].suggested_order_units == 0

def test_association_is_reported_without_causal_claim(retail):
    sales, _ = retail
    estimates = price_elasticity_association(sales)
    assert not estimates.empty
    assert estimates.log_price_coefficient.notna().all()

def test_invalid_policy():
    with pytest.raises(ValueError):
        InventoryPolicy(lead_time_days=0)
