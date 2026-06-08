export type DocumentStatus = "processing" | "completed" | "failed";

export interface DocumentListItem {
  id: number;
  original_filename: string;
  file_type: string;
  status: DocumentStatus;
  summary: string | null;
  created_at: string;
  updated_at: string;
}

export interface DocumentDetail extends DocumentListItem {
  extracted_text: string | null;
}

export interface UploadResponse {
  id: number;
  status: DocumentStatus;
  original_filename: string;
}

export interface SourceSnippet {
  text: string;
  score: number | null;
}

export interface ChatResponse {
  answer: string;
  sources: SourceSnippet[];
}

export interface SearchResult {
  document_id: number;
  filename: string;
  snippet: string;
  score: number | null;
}
