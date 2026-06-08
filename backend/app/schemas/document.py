from datetime import datetime

from pydantic import BaseModel


class DocumentListItem(BaseModel):
    id: int
    original_filename: str
    file_type: str
    status: str
    summary: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DocumentDetail(DocumentListItem):
    extracted_text: str | None = None


class SummaryResponse(BaseModel):
    document_id: int
    summary: str | None


class SourceSnippet(BaseModel):
    text: str
    score: float | None = None


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceSnippet]


class SearchResult(BaseModel):
    document_id: int
    filename: str
    snippet: str
    score: float | None = None


class UploadResponse(BaseModel):
    id: int
    status: str
    original_filename: str
