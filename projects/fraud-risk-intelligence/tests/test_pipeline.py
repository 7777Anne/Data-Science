import importlib.util
from pathlib import Path
import numpy as np
import pytest

path=Path(__file__).resolve().parents[1]/"src"/"pipeline.py"
spec=importlib.util.spec_from_file_location("fraud_demo",path)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

def test_synthetic_data_deterministic():
    a,b=module.generate_events(500),module.generate_events(500)
    assert a.equals(b)
    assert a["is_fraud"].isin([0,1]).all()

def test_features_are_prediction_time_safe():
    data=module.generate_events(500)
    assert "newbalanceOrig" not in module.FEATURES
    assert "is_fraud" not in module.FEATURES
    assert data["previous_tx_count"].ge(0).all()

def test_splits_are_ordered_and_disjoint():
    a,b,c=module.chronological_splits(module.generate_events())
    assert a.event_step.max()<b.event_step.min()<c.event_step.min()

def test_model_metrics_finite():
    _,score=module.fit_evaluate(module.generate_events())
    assert 0<=score["test_pr_auc"]<=1
    assert np.isfinite([score[k] for k in ["test_pr_auc","test_precision","test_recall"]]).all()
