import importlib.util
from pathlib import Path

spec=importlib.util.spec_from_file_location("lakehouse",Path(__file__).resolve().parents[1]/"src"/"pipeline.py")
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def test_ingestion_quality_counts():
    bronze=mod.generate_events(100)
    silver,report=mod.curate(bronze)
    assert report["invalid_rows"]==1
    assert report["valid_duplicate_rows"]==10
    assert len(silver)==100
    assert silver.transaction_id.is_unique

def test_duplicate_replay_is_idempotent():
    bronze=mod.generate_events(150)
    first,_=mod.curate(bronze)
    replay,_=mod.curate(__import__("pandas").concat([bronze,bronze],ignore_index=True))
    assert first.equals(replay)

def test_gold_only_settled():
    silver,_=mod.curate(mod.generate_events(200))
    gold=mod.aggregate(silver)
    assert gold.transaction_count.sum()==(silver.status=="settled").sum()
