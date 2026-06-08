from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import SessionLocal, get_db
from app.models.document import ChatMessage, Document
from app.schemas.document import (
    ChatRequest,
    ChatResponse,
    DocumentDetail,
    DocumentListItem,
    SearchResult,
    SourceSnippet,
    SummaryResponse,
    UploadResponse,
)
from app.services.ollama import OllamaClient
from app.services.processing import process_document
from app.services.vector_store import VectorStore

router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_TYPES = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "image/png": "png",
    "image/jpeg": "jpg",
}


@router.post("/upload", response_model=UploadResponse, status_code=201)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    settings = get_settings()
    file_type = ALLOWED_TYPES.get(file.content_type or "")
    if file_type is None:
        raise HTTPException(status_code=400, detail="Only PDF, DOCX, PNG, JPG, and JPEG files are allowed.")

    content = await file.read()
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail="File is too large.")

    safe_filename = f"{uuid4().hex}.{file_type}"
    file_path = settings.upload_dir / safe_filename
    file_path.write_bytes(content)

    document = Document(
        filename=safe_filename,
        original_filename=Path(file.filename or "document").name,
        file_type=file_type,
        file_path=str(file_path),
        status="processing",
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    background_tasks.add_task(process_document, document.id, SessionLocal)
    return UploadResponse(
        id=document.id,
        status=document.status,
        original_filename=document.original_filename,
    )


@router.get("", response_model=list[DocumentListItem])
def list_documents(db: Session = Depends(get_db)):
    statement = select(Document).order_by(Document.created_at.desc())
    return db.scalars(statement).all()


@router.get("/search", response_model=list[SearchResult])
def search_documents(
    q: str = Query(..., min_length=2),
    db: Session = Depends(get_db),
):
    rows = VectorStore().search(q, limit=10)
    document_ids = [row["metadata"]["document_id"] for row in rows]
    documents = {
        doc.id: doc
        for doc in db.scalars(
            select(Document).where(
                Document.id.in_(document_ids),
                Document.status == "completed",
            )
        ).all()
    }

    results: list[SearchResult] = []
    for row in rows:
        document_id = row["metadata"]["document_id"]
        document = documents.get(document_id)
        if document is None:
            continue
        results.append(
            SearchResult(
                document_id=document_id,
                filename=document.original_filename,
                snippet=row["text"],
                score=row["score"],
            )
        )
    return results


@router.get("/{document_id}", response_model=DocumentDetail)
def get_document(document_id: int, db: Session = Depends(get_db)):
    document = db.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    return document


@router.delete("/{document_id}", status_code=204)
def delete_document(document_id: int, db: Session = Depends(get_db)):
    document = db.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")

    VectorStore().delete_document(document.id)
    Path(document.file_path).unlink(missing_ok=True)
    db.delete(document)
    db.commit()


@router.get("/{document_id}/summary", response_model=SummaryResponse)
def get_summary(document_id: int, db: Session = Depends(get_db)):
    document = db.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    return SummaryResponse(document_id=document.id, summary=document.summary)


@router.post("/{document_id}/chat", response_model=ChatResponse)
async def chat_with_document(
    document_id: int,
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    document = db.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    if document.status != "completed":
        raise HTTPException(status_code=409, detail="Document is not ready yet.")

    matches = VectorStore().search(request.message, document_id=document_id, limit=4)
    context = "\n\n---\n\n".join(match["text"] for match in matches)
    if not context:
        answer = "I could not find this information in the document."
    else:
        answer = await OllamaClient().answer(request.message, context)

    db.add(ChatMessage(document_id=document.id, role="user", content=request.message))
    db.add(ChatMessage(document_id=document.id, role="assistant", content=answer))
    db.commit()

    return ChatResponse(
        answer=answer,
        sources=[SourceSnippet(text=match["text"], score=match["score"]) for match in matches],
    )
