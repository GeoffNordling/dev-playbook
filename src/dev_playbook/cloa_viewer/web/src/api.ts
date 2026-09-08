// The server's whole surface, as one typed function per route plus the event
// stream. Nothing else in the page calls fetch or opens an EventSource, so the
// shapes below are the only place the page's idea of the contract lives.

/** One checkout the server was started with, as /api/checkouts reports it. */
export interface Checkout {
  dir: string;
  path: string;
  repo: string;
  branch: string;
  head: string;
}

/** One registered kind, which tells a missing renderer from a typo. */
export interface KindInfo {
  name: string;
  version: number;
  per_subject: boolean;
}

/** Which commit a view file describes, and what produced it. */
export interface Stamp {
  commit: string;
  generated_at: string;
  generator: string;
}

/** One view file: the seven envelope fields the contract fixes. */
export interface View {
  envelope: number;
  kind: string;
  kind_version: number;
  title: string;
  subject: string | null;
  stamp: Stamp;
  payload: Record<string, unknown>;
}

/** What one kind's generator did in the last refresh. */
export interface GeneratorOutcome {
  kind: string;
  status: "ok" | "failed";
  count: number;
  error: string | null;
}

/** The record of the last refresh of one checkout. */
export interface RefreshRecord {
  started: string;
  finished: string;
  commit: string;
  generators: GeneratorOutcome[];
}

/** A message from the event stream. The push is one-way, server to page. */
export type ServerEvent =
  | { event: "connected" }
  | { event: "refreshed"; checkout: string }
  | { event: "changed"; checkout: string; path: string }
  | { event: "removed"; checkout: string; path: string };

/**
 * Whether the event stream is up.
 *
 * A page that has not opened the stream yet is connecting, not disconnected:
 * the banner means a connection that was there and is lost, so it must not
 * flash on every load.
 */
export type Connection = "connecting" | "connected" | "disconnected";

async function getJson<T>(url: string): Promise<T> {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`${url}: ${response.status} ${response.statusText}`);
  }
  return (await response.json()) as T;
}

function checkoutUrl(dir: string): string {
  return `/api/checkouts/${encodeURIComponent(dir)}`;
}

export function fetchKinds(): Promise<KindInfo[]> {
  return getJson<KindInfo[]>("/api/kinds");
}

export function fetchSchema(name: string): Promise<Record<string, unknown>> {
  return getJson<Record<string, unknown>>(
    `/api/schemas/${encodeURIComponent(name)}`,
  );
}

export function fetchCheckouts(): Promise<Checkout[]> {
  return getJson<Checkout[]>("/api/checkouts");
}

export function fetchFiles(dir: string): Promise<string[]> {
  return getJson<string[]>(`${checkoutUrl(dir)}/files`);
}

export function fetchView(dir: string, path: string): Promise<unknown> {
  // The route takes the relative path whole, so the separators stay and only
  // the segments are escaped.
  const escaped = path.split("/").map(encodeURIComponent).join("/");
  return getJson<unknown>(`${checkoutUrl(dir)}/view/${escaped}`);
}

export function fetchRefresh(dir: string): Promise<RefreshRecord> {
  return getJson<RefreshRecord>(`${checkoutUrl(dir)}/refresh`);
}

/** Force a refresh of one checkout, and answer with the record it wrote. */
export async function postRefresh(dir: string): Promise<RefreshRecord> {
  const url = `${checkoutUrl(dir)}/refresh`;
  const response = await fetch(url, { method: "POST" });
  if (!response.ok) {
    throw new Error(`${url}: ${response.status} ${response.statusText}`);
  }
  return (await response.json()) as RefreshRecord;
}

/**
 * Listen on the event stream until the returned function is called.
 *
 * EventSource reconnects a dropped stream on its own, so onStateChange reports
 * the loss and then the return, and the page has nothing to retry.
 */
export function subscribe(
  onMessage: (message: ServerEvent) => void,
  onStateChange: (connection: Connection) => void,
): () => void {
  const source = new EventSource("/api/events");
  source.onopen = () => {
    onStateChange("connected");
  };
  source.onerror = () => {
    onStateChange("disconnected");
  };
  source.onmessage = (event: MessageEvent<string>) => {
    onMessage(JSON.parse(event.data) as ServerEvent);
  };
  return () => {
    source.close();
  };
}
