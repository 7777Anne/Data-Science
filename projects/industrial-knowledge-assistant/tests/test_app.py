"""Offline acceptance tests for citations, abstention and API behavior."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from fastapi.testclient import TestClient
from app import Assistant, app, load_passages

client = TestClient(app)


def test_documents_are_chunked_with_source_ids():
    passages = load_passages(Path(__file__).resolve().parents[1] / "sample_docs")
    assert len(passages) >= 3
    assert all(p.source.endswith(".md") and p.chunk_id for p in passages)


def test_reject_invalid_chunk_overlap():
    with pytest.raises(ValueError):
        load_passages(Path(__file__).resolve().parents[1] / "sample_docs", 10, 10)


def test_grounded_answer_contains_traceable_source():
    result = Assistant().ask("What should be done if the conveyor bearing exceeds 75 C?")
    assert result["grounded"] is True
    assert any(c["source"] == "conveyor-maintenance.md" for c in result["citations"])
    assert result["answer"]


def test_abstains_outside_document_scope():
    result = Assistant().ask("What is the latest cryptocurrency exchange rate?")
    assert result["grounded"] is False
    assert result["citations"] == []


def test_health_endpoint():
    assert client.get("/health").json() == {"status": "ok"}


def test_ask_endpoint_includes_citations():
    result = client.post("/ask", json={"question": "What is required before line changeover?"})
    assert result.status_code == 200
    assert result.json()["citations"]


def test_question_input_validation():
    assert client.post("/ask", json={"question": "a"}).status_code == 422
    assert client.post("/ask", json={"question": "test", "generator": "invalid"}).status_code == 422


def test_retrieval_index_cached_between_requests():
    from app import get_assistant
    assert get_assistant("tfidf") is get_assistant("tfidf")
