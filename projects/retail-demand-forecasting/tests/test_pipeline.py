import importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location('retail_pipeline', Path(__file__).resolve().parents[1] / 'pipeline.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

def test_features_no_missing():
    df = module.features(module.make_data())
    assert len(df) > 0
    assert df[['lag_1','lag_7','avg_7']].notna().all().all()

def test_lags_look_backward():
    df = module.features(module.make_data())
    first = df[(df.store == 0) & (df.sku == 0)].iloc[0]
    original = module.make_data().query('store == 0 and sku == 0').sort_values('date')
    expected = original.loc[original.date == first.date - __import__('pandas').Timedelta(days=1), 'units'].iloc[0]
    assert first.lag_1 == expected
