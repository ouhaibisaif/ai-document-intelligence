import { DocumentStatus } from "../types/api";

export function StatusBadge({ status }: { status: DocumentStatus }) {
  return <span className={`status status-${status}`}>{status}</span>;
}
