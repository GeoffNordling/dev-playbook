// The top bar: which checkout is on screen, the button that forces a refresh,
// and the last refresh's outcome. Refresh is automatic; the button is for the
// times the user wants to be sure.

import type { GeneratorOutcome, RefreshRecord } from "../api";
import type { Viewer } from "../store";

const RECORD_PATH = "refresh.json";

export function TopBar({ viewer }: { viewer: Viewer }) {
  const { checkout, record } = viewer;
  return (
    <div className="topbar">
      <span className="topbar-checkout">
        {checkout === null
          ? "no checkout"
          : `${checkout.repo} · ${checkout.branch}`}
      </span>
      <button
        type="button"
        className="button"
        onClick={viewer.refreshNow}
        disabled={checkout === null}
      >
        Refresh
      </button>
      <Status record={record} openError={viewer.openError} />
    </div>
  );
}

function Status({
  record,
  openError,
}: {
  record: RefreshRecord | null;
  openError: (path: string, error: string) => void;
}) {
  if (record === null) {
    return <span className="topbar-status">No refresh yet</span>;
  }
  const summary = `Refreshed ${record.finished} at ${record.commit.slice(0, 7)}`;
  const failed = record.generators.filter(
    (generator) => generator.status === "failed",
  );
  if (failed.length === 0) {
    return <span className="topbar-status">{summary}</span>;
  }
  // The error text is one click away rather than in the bar, because a
  // traceback is a panel's worth of text.
  return (
    <button
      type="button"
      className="topbar-status topbar-status-failed"
      onClick={() => {
        openError(RECORD_PATH, errorText(failed));
      }}
    >
      {summary} — {failed.length} failed
    </button>
  );
}

function errorText(failed: GeneratorOutcome[]): string {
  return failed
    .map((generator) => `${generator.kind}\n${generator.error ?? ""}`)
    .join("\n\n");
}
