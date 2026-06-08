import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";
import { Search } from "lucide-react";
import { searchDocuments } from "../services/api";
import { SearchResult } from "../types/api";

export function SearchPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [error, setError] = useState("");
  const [isSearching, setIsSearching] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (query.trim().length < 2) return;

    setIsSearching(true);
    setError("");
    try {
      setResults(await searchDocuments(query.trim()));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Search failed.");
    } finally {
      setIsSearching(false);
    }
  }

  return (
    <section className="page">
      <div className="page-header">
        <div>
          <p className="eyebrow">Semantic search</p>
          <h1>Search documents</h1>
        </div>
      </div>

      <form className="search-form" onSubmit={handleSubmit}>
        <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search uploaded documents..." />
        <button className="icon-button primary" disabled={isSearching} title="Search">
          <Search size={18} />
        </button>
      </form>

      {error && <p className="alert">{error}</p>}
      <div className="search-results">
        {results.map((result, index) => (
          <Link className="result" to={`/documents/${result.document_id}`} key={`${result.document_id}-${index}`}>
            <strong>{result.filename}</strong>
            <p>{result.snippet}</p>
          </Link>
        ))}
        {results.length === 0 && <p className="empty">Results will appear here.</p>}
      </div>
    </section>
  );
}
