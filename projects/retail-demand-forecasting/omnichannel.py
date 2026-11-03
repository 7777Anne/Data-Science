"""Portfolio-only retail forecasting and inventory analytics. Synthetic data, not client data."""
from dataclasses import dataclass
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

KEYS = ["store", "sku"]
FEATURES = ["store_code", "sku_code", "lag_1", "lag_7", "mean_7", "day_of_week"]

@dataclass(frozen=True)
class InventoryPolicy:
    lead_time_days: int = 7
    review_days: int = 7
    service_z: float = 1.65

    def __post_init__(self):
        if self.lead_time_days < 1 or self.review_days < 1 or self.service_z < 0:
            raise ValueError("Invalid lead time, review interval, or service factor")

def make_synthetic_sales(days=210, seed=42):
    """Generate daily synthetic store/SKU/channel sales, NOT actual customer demand."""
    if days < 90:
        raise ValueError("At least 90 days needed")
    rng = np.random.default_rng(seed)
    rows = []
    dates = pd.date_range("2025-01-01", periods=days)
    products = {"TEE-BLK-M": (28, 799), "SHOE-WHT-08": (18, 2299), "BAG-CASUAL": (14, 1299)}
    for store in ["BLR-01", "BLR-02"]:
        for sku, (base, normal_price) in products.items():
            for channel in ["store", "online"]:
                for i, date in enumerate(dates):
                    promo = int(i % 29 in [0, 1, 2, 3])
                    price = round(normal_price * (1 - .10 * promo + rng.choice([-.03, 0, .03])), 2)
                    weekly = 1 + .16 * np.sin(2 * np.pi * i / 7)
                    channel_factor = .5 if channel == "online" else 1.
                    units = max(0, int(round(base * channel_factor * weekly *
                                           (normal_price / price) ** 1.1 + rng.normal(0, 3))))
                    rows.append((date, store, sku, channel, units, price, promo))
    return pd.DataFrame(rows, columns=["date", "store", "sku", "channel", "units", "unit_price", "promotion"])

def validate_sales(data):
    required = ["date", "store", "sku", "channel", "units", "unit_price", "promotion"]
    missing = set(required) - set(data.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    df = data.copy()
    df["date"] = pd.to_datetime(df["date"], errors="raise").dt.normalize()
    if df[required].isna().any().any():
        raise ValueError("Required fields contain nulls")
    if (df.units < 0).any() or (df.unit_price <= 0).any():
        raise ValueError("Units must be nonnegative and prices positive")
    if not (df.units == np.floor(df.units)).all():
        raise ValueError("Units must be integer-valued")
    if not df.promotion.isin([0, 1]).all():
        raise ValueError("Promotion must be binary")
    if df.duplicated(["date", "store", "sku", "channel"]).any():
        raise ValueError("Duplicate store/SKU/channel/day record")
    return df.sort_values(["date", "store", "sku", "channel"]).reset_index(drop=True)

def aggregate_store_sku(sales):
    df = validate_sales(sales)
    df["sales_revenue"] = df.units * df.unit_price
    return df.groupby(["date", "store", "sku"], as_index=False).agg(
        units=("units", "sum"), revenue=("sales_revenue", "sum")
    ).sort_values(["store", "sku", "date"]).reset_index(drop=True)

def _training_features(df, stores, skus):
    x = df.sort_values(KEYS + ["date"]).copy()
    x["store_code"] = pd.Categorical(x.store, categories=stores).codes
    x["sku_code"] = pd.Categorical(x.sku, categories=skus).codes
    grouped = x.groupby(KEYS, sort=False).units
    x["lag_1"] = grouped.shift(1)
    x["lag_7"] = grouped.shift(7)
    x["mean_7"] = x.groupby(KEYS, sort=False).lag_1.transform(
        lambda s: s.rolling(7, min_periods=7).mean())
    x["day_of_week"] = x.date.dt.dayofweek
    return x.dropna(subset=["lag_1", "lag_7", "mean_7"])

def forecast_at_origin(history, horizon=7):
    """Recursive forecasts: future lags use earlier predictions, not future actuals."""
    if not 1 <= horizon <= 60:
        raise ValueError("Horizon must be 1..60")
    df = history.copy()
    df["date"] = pd.to_datetime(df.date).dt.normalize()
    if df.duplicated(["date"] + KEYS).any() or df.units.isna().any() or (df.units < 0).any():
        raise ValueError("Invalid daily history")
    last_date = df.date.max()
    groups = list(df.groupby(KEYS))
    if not groups or any(len(g) < 21 or g.date.max() != last_date or
                         not g.date.sort_values().diff().dropna().eq(pd.Timedelta(days=1)).all()
                         for _, g in groups):
        raise ValueError("Each store/SKU needs 21+ contiguous days through the same origin")
    stores = sorted(df.store.unique().tolist())
    skus = sorted(df.sku.unique().tolist())
    train = _training_features(df, stores, skus)
    model = HistGradientBoostingRegressor(max_iter=80, max_leaf_nodes=15,
                                           l2_regularization=1., random_state=42)
    model.fit(train[FEATURES], train.units)
    past = {key: list(g.sort_values("date").units.astype(float)) for key, g in groups}
    rows = []
    for day in range(1, horizon + 1):
        date = last_date + pd.Timedelta(days=day)
        examples, keys = [], []
        for (store, sku), values in past.items():
            keys.append((store, sku))
            examples.append({"store_code": stores.index(store), "sku_code": skus.index(sku),
                             "lag_1": values[-1], "lag_7": values[-7],
                             "mean_7": float(np.mean(values[-7:])),
                             "day_of_week": date.dayofweek})
        predictions = np.maximum(0, model.predict(pd.DataFrame(examples)[FEATURES]))
        for (store, sku), value in zip(keys, predictions):
            past[(store, sku)].append(float(value))
            rows.append((date, store, sku, day, float(value)))
    return pd.DataFrame(rows, columns=["date", "store", "sku", "horizon_day", "predicted_units"])

def rolling_origin_backtest(daily, origins, horizon=7):
    actual = daily.copy()
    actual["date"] = pd.to_datetime(actual.date).dt.normalize()
    outputs = []
    for origin in origins:
        origin = pd.Timestamp(origin).normalize()
        predictions = forecast_at_origin(actual.loc[actual.date <= origin], horizon)
        paired = predictions.merge(actual[["date", "store", "sku", "units"]],
                                   on=["date", "store", "sku"], how="left",
                                   validate="one_to_one")
        if paired.units.isna().any():
            raise ValueError("Missing held-out actuals")
        paired["origin"] = origin
        outputs.append(paired)
    if not outputs:
        raise ValueError("Provide at least one origin")
    result = pd.concat(outputs, ignore_index=True)
    error = (result.units - result.predicted_units).abs()
    denom = result.units.sum()
    return result, {"mae": float(error.mean()),
                    "wape": float(error.sum() / denom) if denom else None,
                    "n_forecasts": int(len(result)),
                    "evaluation": f"recursive {horizon}-day rolling-origin backtest"}

def price_elasticity_association(sales, min_rows=30):
    """Observational log-price coefficient, NOT causal price elasticity."""
    df = validate_sales(sales)
    estimates = []
    for (store, sku, channel), group in df.groupby(["store", "sku", "channel"]):
        g = group.loc[group.units > 0].sort_values("date")
        if len(g) < min_rows or g.unit_price.nunique() < 3:
            continue
        weekdays = g.date.dt.dayofweek.to_numpy()
        indicators = np.column_stack([(weekdays == i).astype(float) for i in range(1, 7)])
        trend = np.arange(len(g), dtype=float) / max(1, len(g) - 1)
        X = np.column_stack([np.ones(len(g)), np.log(g.unit_price.to_numpy()),
                             g.promotion.to_numpy(), trend, indicators])
        coefficients, _, rank, _ = np.linalg.lstsq(X, np.log(g.units.to_numpy()), rcond=None)
        if rank == X.shape[1]:
            estimates.append((store, sku, channel, float(coefficients[1]), len(g)))
    return pd.DataFrame(estimates, columns=["store", "sku", "channel",
                                           "log_price_coefficient", "n_rows"])

def recommend_inventory(forecast, inventory, policy=InventoryPolicy(), daily_error_sd=4.):
    """Illustrative order-up-to policy, assuming independent daily errors."""
    if daily_error_sd < 0:
        raise ValueError("Negative error standard deviation")
    required = KEYS + ["on_hand", "on_order", "backorders"]
    if set(required) - set(inventory.columns):
        raise ValueError("Missing inventory columns")
    if inventory.duplicated(KEYS).any() or inventory[required].isna().any().any():
        raise ValueError("Duplicate inventory key or missing data")
    if (inventory[["on_hand", "on_order", "backorders"]] < 0).any().any():
        raise ValueError("Negative inventory quantities")
    means = forecast.groupby(KEYS, as_index=False).agg(
        forecast_daily_units=("predicted_units", "mean"))
    result = means.merge(inventory, on=KEYS, how="left", validate="one_to_one")
    if result[["on_hand", "on_order", "backorders"]].isna().any().any():
        raise ValueError("Missing inventory for forecasted SKU")
    result["inventory_position"] = result.on_hand + result.on_order - result.backorders
    result["safety_stock"] = policy.service_z * daily_error_sd * np.sqrt(policy.lead_time_days)
    result["reorder_point"] = np.ceil(result.forecast_daily_units *
                                      policy.lead_time_days + result.safety_stock).astype(int)
    result["order_up_to"] = np.ceil(result.forecast_daily_units *
                                    (policy.lead_time_days + policy.review_days) +
                                    result.safety_stock).astype(int)
    result["reorder_now"] = result.inventory_position <= result.reorder_point
    result["suggested_order_units"] = np.where(
        result.reorder_now, np.maximum(0, np.ceil(result.order_up_to -
                                                 result.inventory_position)), 0).astype(int)
    return result
