import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getDocuments } from "../services/api";
import { DocumentListItem } from "../types/api";
import { StatusBadge } from "../components/StatusBadge";

export function Dashboard() {
  const [documents, setDocuments] = useState<DocumentListItem[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    getDocuments().then(setDocuments).catch((err) => setError(err.message));
  }, []);

  const completed = documents.filter((doc) => doc.status === "completed").length;

  return (
    <section className="page">
      <div className="page-header">
        <div>
          <p className="eyebrow">Local AI workspace</p>
          <h1>DocuLens</h1>
        </div>
        <Link className="button primary" to="/upload">Upload document</Link>
      </div>

      {error && <p className="alert">{error}</p>}

      <div className="stats-grid">
        <div className="stat">
          <span>Total documents</span>
          <strong>{documents.length}</strong>
        </div>
        <div className="stat">
          <span>Ready for chat</span>
          <strong>{completed}</strong>
        </div>
        <div className="stat">
          <span>Processing</span>
          <strong>{documents.filter((doc) => doc.status === "processing").length}</strong>
        </div>
      </div>

      <div className="section-header">
        <h2>Recent documents</h2>
        <Link to="/documents">View all</Link>
      </div>
      <div className="list">
        {documents.slice(0, 5).map((doc) => (
          <Link className="row" to={`/documents/${doc.id}`} key={doc.id}>
            <span>{doc.original_filename}</span>
            <StatusBadge status={doc.status} />
          </Link>
        ))}
        {documents.length === 0 && <p className="empty">Upload your first PDF, DOCX, or image.</p>}
      </div>
    </section>
  );
}
