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
  /** The open panels, newest first. */
  open: readonly string[];
  /** What broke while talking to the server, cleared when a checkout reloads. */
  failure: string | null;
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
  const [open, setOpen] = useState<readonly string[]>([]);
  const [failure, setFailure] = useState<string | null>(null);

  const report = useCallback((cause: unknown) => {
    setFailure(String(cause));
  }, []);

  const dir = checkout === null ? null : checkout.dir;

  // The checkouts, once. The first is the one on screen; the toggle that picks
  // another is a later task.
  useEffect(() => {
    let live = true;
    void fetchCheckouts()
      .then((found) => {
        if (live) {
          setCheckouts(found);
          setCheckout(found[0] ?? null);
        }
      })
      .catch(report);
    return () => {
      live = false;
    };
  }, [report]);

  // Every view file of the selected checkout, validated, plus its refresh
  // record. Switching checkouts empties the room first: no panel of the
  // checkout being left stays open over the one arriving.
  useEffect(() => {
    if (dir === null) {
      return undefined;
    }
    let live = true;
    setViews(new Map());
    setLoaded(false);
    setOpen([]);
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
      if (message.event === "connected" || message.checkout !== dir) {
        return;
      }
      if (message.event === "refreshed") {
        void fetchRefresh(dir).then(setRecord).catch(report);
        return;
      }
      if (message.event === "removed") {
        setViews((current) => dropping(current, message.path));
        setOpen((current) => current.filter((path) => path !== message.path));
        return;
      }
      void readView(dir, message.path)
        .then((entry) => {
          setViews((current) => replacing(current, message.path, entry));
        })
        .catch(report);
    }, setConnection);
  }, [dir, report]);

  const openPanel = useCallback((path: string) => {
    // Already open comes to the top of the stack rather than opening twice.
    setOpen((current) => [path, ...current.filter((each) => each !== path)]);
  }, []);

  const openError = useCallback(
    (path: string, error: string) => {
      setViews((current) => replacing(current, path, { ok: false, error }));
      openPanel(path);
    },
    [openPanel],
  );

  const closePanel = useCallback((path: string) => {
    setOpen((current) => current.filter((each) => each !== path));
  }, []);

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
