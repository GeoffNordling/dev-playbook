// Everything the page knows, in one hook. The store fetches, validates, and
// listens; the components below it only read and call. The user owns the room,
// so nothing here opens a panel on its own.

import { useCallback, useEffect, useState } from "react";

import {
  fetchCheckouts,
  fetchFiles,
  fetchRefresh,
  fetchView,
  postRefresh,
  subscribe,
  type Checkout,
  type Connection,
  type RefreshRecord,
} from "./api";
import { loadSchemas, validateView, type Validated } from "./validate";

/**
 * The open panels of a checkout nothing has opened a panel on yet.
 *
 * One shared value rather than a fresh array each time, so a component that
 * reads ``open`` sees the same list until a panel actually opens.
 */
const NO_PANELS: readonly string[] = [];

/** The page's whole state, and everything a component may do to it. */
export interface Viewer {
  checkouts: Checkout[];
  checkout: Checkout | null;
  /** Every view file of the selected checkout, by its path under that checkout. */
  views: ReadonlyMap<string, Validated>;
  /**
   * Whether that map has arrived.
   *
   * An empty map is the checkout's first moment, not an empty checkout, and
   * the tree must not call a view file missing before the fetch answers.
   */
  loaded: boolean;
  record: RefreshRecord | null;
  connection: Connection;
  /**
   * The selected checkout's open panels, newest first.
   *
   * Every checkout keeps its own list for the page's lifetime, so switching
   * away and back finds the room as it was left.
   */
  open: readonly string[];
  /** What broke while talking to the server, cleared when a checkout reloads. */
  failure: string | null;
  /** Show the checkout with this dir, and put it in the page's address. */
  selectCheckout: (dir: string) => void;
  openPanel: (path: string) => void;
  /** Open a panel that has no view file behind it, carrying this error. */
  openError: (path: string, error: string) => void;
  closePanel: (path: string) => void;
  refreshNow: () => void;
}

export function useViewer(): Viewer {
  const [checkouts, setCheckouts] = useState<Checkout[]>([]);
  const [checkout, setCheckout] = useState<Checkout | null>(null);
  const [views, setViews] = useState<ReadonlyMap<string, Validated>>(new Map());
  const [loaded, setLoaded] = useState(false);
  const [record, setRecord] = useState<RefreshRecord | null>(null);
  const [connection, setConnection] = useState<Connection>("connecting");
  const [panels, setPanels] = useState<ReadonlyMap<string, readonly string[]>>(
    new Map(),
  );
  const [failure, setFailure] = useState<string | null>(null);

  const report = useCallback((cause: unknown) => {
    setFailure(String(cause));
  }, []);

  // A fresh answer from discovery. The selected checkout is replaced by the
  // object of the same dir, so a branch that moved shows in the toggle; a
  // selection the list no longer holds gives way to the first.
  const relist = useCallback((found: Checkout[]) => {
    setCheckouts(found);
    setCheckout((current) => byDir(found, current === null ? "" : current.dir));
  }, []);

  const dir = checkout === null ? null : checkout.dir;
  const open = dir === null ? NO_PANELS : (panels.get(dir) ?? NO_PANELS);

  // The checkouts, on load. The one the address names is the one on screen, so
  // a reload returns to the checkout the user chose.
  useEffect(() => {
    let live = true;
    void fetchCheckouts()
      .then((found) => {
        if (live) {
          setCheckouts(found);
          setCheckout(byDir(found, window.location.hash.slice(1)));
        }
      })
      .catch(report);
    return () => {
      live = false;
    };
  }, [report]);

  // Every view file of the selected checkout, validated, plus its refresh
  // record. The views are emptied first, because the map that is on screen
  // belongs to the checkout being left; the open panels are not, because each
  // checkout keeps its own list and the room returns as it was.
  useEffect(() => {
    if (dir === null) {
      return undefined;
    }
    let live = true;
    setViews(new Map());
    setLoaded(false);
    setRecord(null);
    setFailure(null);
    void (async () => {
      await loadSchemas();
      const paths = await fetchFiles(dir);
      const entries = await Promise.all(
        paths.map(async (path) => [path, await readView(dir, path)] as const),
      );
      if (live) {
        setViews(new Map(entries));
        setLoaded(true);
      }
      const found = await fetchRefresh(dir);
      if (live) {
        setRecord(found);
      }
    })().catch(report);
    return () => {
      live = false;
    };
  }, [dir, report]);

  // The stream. One message names one view file, so the page refetches that
  // file alone and a refresh that rewrote two hundred moves only what changed.
  useEffect(() => {
    if (dir === null) {
      return undefined;
    }
    return subscribe((message) => {
      if (message.event === "connected") {
        return;
      }
      if (message.event === "refreshed") {
        // A refresh of any checkout, not only the one on screen, is the moment
        // to ask again: a worktree added or removed, or a branch that moved,
        // reaches the toggle without a reload.
        void fetchCheckouts().then(relist).catch(report);
        if (message.checkout === dir) {
          void fetchRefresh(dir).then(setRecord).catch(report);
        }
        return;
      }
      if (message.checkout !== dir) {
        return;
      }
      if (message.event === "removed") {
        setViews((current) => dropping(current, message.path));
        setPanels((current) =>
          closing(current, dir, (path) => path !== message.path),
        );
        return;
      }
      void readView(dir, message.path)
        .then((entry) => {
          setViews((current) => replacing(current, message.path, entry));
        })
        .catch(report);
    }, setConnection);
  }, [dir, relist, report]);

  const selectCheckout = useCallback(
    (wanted: string) => {
      setCheckout(byDir(checkouts, wanted));
      // The address is the page's memory of the choice: a reload reads it back.
      window.location.hash = wanted;
    },
    [checkouts],
  );

  const openPanel = useCallback(
    (path: string) => {
      if (dir === null) {
        return;
      }
      setPanels((current) => opening(current, dir, path));
    },
    [dir],
  );

  const openError = useCallback(
    (path: string, error: string) => {
      setViews((current) => replacing(current, path, { ok: false, error }));
      openPanel(path);
    },
    [openPanel],
  );

  const closePanel = useCallback(
    (path: string) => {
      if (dir === null) {
        return;
      }
      setPanels((current) => closing(current, dir, (each) => each !== path));
    },
    [dir],
  );

  const refreshNow = useCallback(() => {
    if (dir === null) {
      return;
    }
    void postRefresh(dir).then(setRecord).catch(report);
  }, [dir, report]);

  return {
    checkouts,
    checkout,
    views,
    loaded,
    record,
    connection,
    open,
    failure,
    selectCheckout,
    openPanel,
    openError,
    closePanel,
    refreshNow,
  };
}

/**
 * One view file, fetched and validated.
 *
 * A fetch that fails is an error on that panel, the same as a schema failure:
 * one file the page could not read closes nothing else on screen.
 */
async function readView(dir: string, path: string): Promise<Validated> {
  try {
    return validateView(await fetchView(dir, path));
  } catch (cause) {
    return { ok: false, error: String(cause) };
  }
}

/**
 * The checkout this list holds under ``dir``, else its first, else nothing.
 *
 * A dir nothing matches is the ordinary case twice over: the address names no
 * checkout on a plain load, and a worktree that was removed while the page was
 * open is gone from the next answer. Both land on the first checkout.
 */
function byDir(found: Checkout[], dir: string): Checkout | null {
  return found.find((each) => each.dir === dir) ?? found[0] ?? null;
}

function opening(
  current: ReadonlyMap<string, readonly string[]>,
  dir: string,
  path: string,
): ReadonlyMap<string, readonly string[]> {
  const next = new Map(current);
  const listed = current.get(dir) ?? NO_PANELS;
  // Already open comes to the top of the stack rather than opening twice.
  next.set(dir, [path, ...listed.filter((each) => each !== path)]);
  return next;
}

function closing(
  current: ReadonlyMap<string, readonly string[]>,
  dir: string,
  keep: (path: string) => boolean,
): ReadonlyMap<string, readonly string[]> {
  const next = new Map(current);
  next.set(dir, (current.get(dir) ?? NO_PANELS).filter(keep));
  return next;
}

function replacing(
  current: ReadonlyMap<string, Validated>,
  path: string,
  entry: Validated,
): ReadonlyMap<string, Validated> {
  const next = new Map(current);
  next.set(path, entry);
  return next;
}

function dropping(
  current: ReadonlyMap<string, Validated>,
  path: string,
): ReadonlyMap<string, Validated> {
  const next = new Map(current);
  next.delete(path);
  return next;
}
