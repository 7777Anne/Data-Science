import importlib.util
from pathlib import Path
import pandas as pd
spec = importlib.util.spec_from_file_location(
    'retail_pipeline', Path(__file__).resolve().parents[1] / 'pipeline.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

def test_features_have_only_past_values():
    original=module.make_data()
    frame=module.features(original)
    first=frame[(frame.store==0)&(frame.sku==0)].iloc[0]
    history=original[(original.store==0)&(original.sku==0)].sort_values("date")
    lag=history.loc[history.date==first.date-pd.Timedelta(days=1),"units"].iloc[0]
    assert first.lag_1==lag
    assert frame[["lag_1","lag_7","avg_7"]].notna().all().all()

def test_next_day_forecast_features_use_recent_history():
    original=module.make_data()
    future=module.next_day_features(original)
    assert len(future)==12
    assert (future.date==original.date.max()+pd.Timedelta(days=1)).all()
    item=original.query("store == 0 and sku == 0").sort_values("date")
    tomorrow=future.query("store == 0 and sku == 0").iloc[0]
    assert tomorrow.lag_1==item.units.iloc[-1]
    assert tomorrow.lag_7==item.units.iloc[-7]
    assert tomorrow.avg_7==item.units.iloc[-7:].mean()
