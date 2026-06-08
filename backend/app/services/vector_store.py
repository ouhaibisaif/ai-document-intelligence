import hashlib
import math

import chromadb
from chromadb.api.types import EmbeddingFunction

from app.core.config import get_settings


class HashEmbeddingFunction(EmbeddingFunction):
    def __call__(self, input: list[str]) -> list[list[float]]:
        return [_hash_embedding(text) for text in input]


def _hash_embedding(text: str, dimensions: int = 384) -> list[float]:
    vector = [0.0] * dimensions
    words = text.lower().split()
    for word in words:
        digest = hashlib.sha256(word.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "big") % dimensions
        vector[index] += 1.0

    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [value / norm for value in vector]


class VectorStore:
    def __init__(self) -> None:
        settings = get_settings()
        if settings.chroma_host:
            self.client = chromadb.HttpClient(
                host=settings.chroma_host, port=settings.chroma_port
            )
        else:
            self.client = chromadb.PersistentClient(path=str(settings.chroma_persist_dir))

        self.collection = self.client.get_or_create_collection(
            name="document_chunks",
            embedding_function=HashEmbeddingFunction(),
        )

    def upsert_document_chunks(self, document_id: int, chunks: list[str]) -> None:
        self.delete_document(document_id)
        if not chunks:
            return

        ids = [f"{document_id}:{index}" for index in range(len(chunks))]
        metadatas = [{"document_id": document_id, "chunk_index": index} for index in range(len(chunks))]
        self.collection.add(ids=ids, documents=chunks, metadatas=metadatas)

    def search(self, query: str, document_id: int | None = None, limit: int = 5) -> list[dict]:
        where = {"document_id": document_id} if document_id is not None else None
        results = self.collection.query(
            query_texts=[query],
            n_results=limit,
            where=where,
            include=["documents", "distances", "metadatas"],
        )

        rows: list[dict] = []
        documents = results.get("documents", [[]])[0]
        distances = results.get("distances", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        for text, distance, metadata in zip(documents, distances, metadatas, strict=False):
            rows.append({"text": text, "score": distance, "metadata": metadata})
        return rows

    def delete_document(self, document_id: int) -> None:
        self.collection.delete(where={"document_id": document_id})
