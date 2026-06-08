# Architecture

DocuLens is split into a FastAPI backend, a React frontend, PostgreSQL for document metadata, ChromaDB for document chunks, and Ollama for local Qwen inference.

## Processing Flow

1. The frontend uploads a PDF, DOCX, or image through `POST /documents/upload`.
2. The backend validates MIME type and size, then saves the file with a generated filename.
3. A background task extracts text with PyMuPDF, python-docx, or Tesseract OCR.
4. Cleaned text is split into overlapping chunks.
5. Chunks are indexed in ChromaDB with document metadata.
6. Ollama runs `qwen2.5:7b` to generate a short summary.
7. The document status changes from `processing` to `completed`.

## Chat Flow

For document chat, the backend retrieves the most relevant chunks from ChromaDB and sends only those chunks to Ollama with a strict document-only system prompt. Answers include the source snippets used by the model. If no relevant context is available, the API returns a clear "not found in the document" answer.

## Storage

PostgreSQL stores document metadata, extracted text, summaries, and chat history. Uploaded files stay in `backend/uploads/`, which is ignored by Git except for a placeholder file. ChromaDB stores chunk text and vectors for search and retrieval.
