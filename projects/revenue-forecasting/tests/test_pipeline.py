import importlib.util
from pathlib import Path
import numpy as np
spec=importlib.util.spec_from_file_location(
    "revenue_demo",Path(__file__).resolve().parents[1]/"pipeline.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def test_deterministic_series():
    a=m.demo_series()
    assert len(a)==26*42
    assert a.equals(m.demo_series())
    assert a.revenue.gt(0).all()

def test_moving_average_is_history_only():
    values=np.arange(1,21,dtype=float)
    pred=m.predict(values,3,"moving_average")
    assert np.allclose(pred,np.mean(values[-3:]))

def test_seasonal_naive_forecast():
    x=np.arange(1,25,dtype=float)
    assert np.array_equal(m.predict(x,3,"seasonal_naive"),x[-12:-9])
