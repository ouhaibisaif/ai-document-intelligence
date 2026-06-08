import { ChangeEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { UploadCloud } from "lucide-react";
import { uploadDocument } from "../services/api";

export function UploadPage() {
  const navigate = useNavigate();
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState("");

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    setFile(event.target.files?.[0] ?? null);
    setError("");
  }

  async function handleSubmit() {
    if (!file) {
      setError("Choose a file first.");
      return;
    }
    setIsUploading(true);
    try {
      const result = await uploadDocument(file);
      navigate(`/documents/${result.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed.");
    } finally {
      setIsUploading(false);
    }
  }

  return (
    <section className="page narrow">
      <div className="page-header">
        <div>
          <p className="eyebrow">New document</p>
          <h1>Upload document</h1>
        </div>
      </div>

      <div className="upload-zone">
        <UploadCloud size={36} />
        <input
          type="file"
          accept=".pdf,.docx,.png,.jpg,.jpeg"
          onChange={handleFileChange}
        />
        <p>{file ? file.name : "PDF, DOCX, PNG, JPG, or JPEG up to the configured size limit."}</p>
      </div>

      {error && <p className="alert">{error}</p>}
      <button className="button primary" onClick={handleSubmit} disabled={isUploading}>
        {isUploading ? "Uploading..." : "Start processing"}
      </button>
    </section>
  );
}
