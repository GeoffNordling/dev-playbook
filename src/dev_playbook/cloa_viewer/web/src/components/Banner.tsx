// The banner says the page is looking at a picture that has stopped being
// kept up to date. EventSource retries on its own, so it clears itself.

import type { Connection } from "../api";

export function Banner({ connection }: { connection: Connection }) {
  if (connection !== "disconnected") {
    return null;
  }
  return <div className="banner">Disconnected from cloa-viewer</div>;
}
