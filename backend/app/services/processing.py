from pathlib import Path

import anyio
from sqlalchemy.orm import Session

from app.models.document import Document
from app.services.extraction import extract_text
from app.services.ollama import OllamaClient
from app.services.vector_store import VectorStore
from app.utils.text import split_text


async def process_document(document_id: int, db_factory) -> None:
    db: Session = db_factory()
    try:
        document = db.get(Document, document_id)
        if document is None:
            return

        text = await anyio.to_thread.run_sync(
            extract_text, Path(document.file_path), document.file_type
        )
        if not text:
            raise ValueError("No text could be extracted from this file.")

        chunks = split_text(text)
        await anyio.to_thread.run_sync(
            VectorStore().upsert_document_chunks, document.id, chunks
        )
        summary = await OllamaClient().summarize(text)

        document.extracted_text = text
        document.summary = summary
        document.status = "completed"
        db.commit()
    except Exception as exc:
        document = db.get(Document, document_id)
        if document is not None:
            await anyio.to_thread.run_sync(VectorStore().delete_document, document.id)
            document.status = "failed"
            document.summary = f"Processing failed: {exc}"
            db.commit()
    finally:
        db.close()
