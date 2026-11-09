import math

from app.services.vector_store import VectorStore, _hash_embedding


def test_hash_embedding_is_deterministic_and_normalized():
    a = _hash_embedding("Invoice total due")
    assert a == _hash_embedding("invoice TOTAL due")
    assert len(a) == 384
    assert math.isclose(sum(v * v for v in a), 1.0)


def test_search_finds_the_matching_chunk(tmp_path, monkeypatch):
    monkeypatch.setenv("CHROMA_PERSIST_DIR", str(tmp_path / "chroma"))
    monkeypatch.setenv("UPLOAD_DIR", str(tmp_path / "uploads"))
    from app.core.config import get_settings
    get_settings.cache_clear()

    store = VectorStore()
    store.upsert_document_chunks(1, ["The invoice total is 420 EUR", "The weather is sunny"])
    store.upsert_document_chunks(2, ["Unrelated notes about football"])

    hits = store.search("invoice total", document_id=1, limit=1)
    assert hits and "invoice total" in hits[0]["text"].lower()
