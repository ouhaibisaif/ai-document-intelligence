import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Trash2 } from "lucide-react";
import { deleteDocument, getDocuments } from "../services/api";
import { DocumentListItem } from "../types/api";
import { StatusBadge } from "../components/StatusBadge";

export function DocumentsPage() {
  const [documents, setDocuments] = useState<DocumentListItem[]>([]);
  const [error, setError] = useState("");

  async function loadDocuments() {
    try {
      setDocuments(await getDocuments());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load documents.");
    }
  }

  useEffect(() => {
    loadDocuments();
  }, []);

  async function handleDelete(id: number) {
    await deleteDocument(id);
    setDocuments((current) => current.filter((doc) => doc.id !== id));
  }

  return (
    <section className="page">
      <div className="page-header">
        <div>
          <p className="eyebrow">Library</p>
          <h1>Documents</h1>
        </div>
        <Link className="button primary" to="/upload">Upload</Link>
      </div>

      {error && <p className="alert">{error}</p>}
      <div className="table">
        {documents.map((doc) => (
          <div className="table-row" key={doc.id}>
            <Link to={`/documents/${doc.id}`}>
              <strong>{doc.original_filename}</strong>
              <small>{doc.file_type.toUpperCase()}</small>
            </Link>
            <StatusBadge status={doc.status} />
            <button className="icon-button" onClick={() => handleDelete(doc.id)} title="Delete document">
              <Trash2 size={18} />
            </button>
          </div>
        ))}
        {documents.length === 0 && <p className="empty">No documents yet.</p>}
      </div>
    </section>
  );
}
