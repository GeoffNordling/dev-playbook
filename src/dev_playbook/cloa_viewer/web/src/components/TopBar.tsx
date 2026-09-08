// The top bar: which checkout is on screen, the button that forces a refresh,
// and the last refresh's outcome. Refresh is automatic; the button is for the
// times the user wants to be sure.

import type { Checkout, GeneratorOutcome, RefreshRecord } from "../api";
import type { Viewer } from "../store";

const RECORD_PATH = "refresh.json";

export function TopBar({ viewer }: { viewer: Viewer }) {
  const { checkout, record } = viewer;
  return (
    <div className="topbar">
      <Toggle
        checkouts={viewer.checkouts}
        checkout={checkout}
        select={viewer.selectCheckout}
      />
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

/**
 * The checkout toggle: every checkout the server found, grouped by repo.
 *
 * A repo's working copies sit together under its name and each option is its
 * branch, so a main checkout and its worktrees are told apart by the only
 * thing that differs between them. The full path is the option's tooltip, for
 * two worktrees on the same branch name in different repos.
 */
function Toggle({
  checkouts,
  checkout,
  select,
}: {
  checkouts: Checkout[];
  checkout: Checkout | null;
  select: (dir: string) => void;
}) {
  if (checkout === null) {
    return <span className="topbar-none">no checkout</span>;
  }
  return (
    <select
      className="topbar-checkout"
      value={checkout.dir}
      onChange={(event) => {
        select(event.target.value);
      }}
    >
      {byRepo(checkouts).map(([repo, listed]) => (
        <optgroup key={repo} label={repo}>
          {listed.map((each) => (
            <option key={each.dir} value={each.dir} title={each.path}>
              {each.branch}
            </option>
          ))}
        </optgroup>
      ))}
    </select>
  );
}

/** The checkouts as one entry per repo, both repos and checkouts in list order. */
function byRepo(checkouts: Checkout[]): [string, Checkout[]][] {
  const groups = new Map<string, Checkout[]>();
  for (const each of checkouts) {
    const listed = groups.get(each.repo);
    if (listed === undefined) {
      groups.set(each.repo, [each]);
    } else {
      listed.push(each);
    }
  }
  return [...groups];
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
