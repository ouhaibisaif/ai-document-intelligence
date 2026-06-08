import {
  ChatResponse,
  DocumentDetail,
  DocumentListItem,
  SearchResult,
  UploadResponse
} from "../types/api";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, options);
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.detail ?? "Something went wrong.");
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return response.json() as Promise<T>;
}

export function getDocuments() {
  return request<DocumentListItem[]>("/documents");
}

export function getDocument(id: number) {
  return request<DocumentDetail>(`/documents/${id}`);
}

export function uploadDocument(file: File) {
  const formData = new FormData();
  formData.append("file", file);
  return request<UploadResponse>("/documents/upload", {
    method: "POST",
    body: formData
  });
}

export function deleteDocument(id: number) {
  return request<void>(`/documents/${id}`, { method: "DELETE" });
}

export function chatWithDocument(id: number, message: string) {
  return request<ChatResponse>(`/documents/${id}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message })
  });
}

export function searchDocuments(query: string) {
  return request<SearchResult[]>(`/documents/search?q=${encodeURIComponent(query)}`);
}
