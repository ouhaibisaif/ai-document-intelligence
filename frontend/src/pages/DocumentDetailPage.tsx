import { FormEvent, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { Send } from "lucide-react";
import { chatWithDocument, getDocument } from "../services/api";
import { DocumentDetail, SourceSnippet } from "../types/api";
import { StatusBadge } from "../components/StatusBadge";

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: SourceSnippet[];
}

export function DocumentDetailPage() {
  const { id } = useParams();
  const documentId = Number(id);
  const [document, setDocument] = useState<DocumentDetail | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [isSending, setIsSending] = useState(false);

  useEffect(() => {
    let isMounted = true;

    async function loadDocument() {
      try {
        const nextDocument = await getDocument(documentId);
        if (isMounted) {
          setDocument(nextDocument);
        }
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : "Could not load document.");
        }
      }
    }

    loadDocument();
    const timer = window.setInterval(() => {
      if (document?.status === "processing") {
        loadDocument();
      }
    }, 2500);

    return () => {
      isMounted = false;
      window.clearInterval(timer);
    };
  }, [documentId, document?.status]);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!message.trim()) return;

    const userMessage = message.trim();
    setMessages((current) => [...current, { role: "user", content: userMessage }]);
    setMessage("");
    setIsSending(true);
    setError("");

    try {
      const response = await chatWithDocument(documentId, userMessage);
      setMessages((current) => [
        ...current,
        { role: "assistant", content: response.answer, sources: response.sources }
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Chat failed.");
    } finally {
      setIsSending(false);
    }
  }

  if (!document) {
    return <section className="page"><p className="empty">Loading document...</p></section>;
  }

  return (
    <section className="page">
      <div className="page-header">
        <div>
          <p className="eyebrow">Document</p>
          <h1>{document.original_filename}</h1>
        </div>
        <StatusBadge status={document.status} />
      </div>

      {error && <p className="alert">{error}</p>}

      <div className="detail-grid">
        <section>
          <div className="section-header">
            <h2>Summary</h2>
            <Link to="/search">Search library</Link>
          </div>
          <p className="summary">{document.summary ?? "Summary will appear after processing."}</p>
          <h2>Extracted text</h2>
          <pre className="text-preview">{document.extracted_text ?? "Text will appear after processing."}</pre>
        </section>

        <section className="chat-panel">
          <h2>Chat</h2>
          <div className="messages">
            {messages.map((item, index) => (
              <div className={`message ${item.role}`} key={`${item.role}-${index}`}>
                <p>{item.content}</p>
                {item.sources && item.sources.length > 0 && (
                  <details>
                    <summary>Sources</summary>
                    {item.sources.map((source, sourceIndex) => (
                      <blockquote key={sourceIndex}>{source.text}</blockquote>
                    ))}
                  </details>
                )}
              </div>
            ))}
            {messages.length === 0 && <p className="empty">Ask a question about this document.</p>}
          </div>
          <form className="chat-form" onSubmit={handleSubmit}>
            <input
              value={message}
              onChange={(event) => setMessage(event.target.value)}
              placeholder="Ask from this document..."
              disabled={document.status !== "completed"}
            />
            <button className="icon-button primary" disabled={isSending || document.status !== "completed"} title="Send">
              <Send size={18} />
            </button>
          </form>
        </section>
      </div>
    </section>
  );
}
