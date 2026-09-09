// One view file on screen, in whichever region it sits: the kind's renderer
// when the file validated, and the failure named in its place when it did not.
// The tree and the panel stack both come through here, so a broken view file
// looks the same wherever it lands.

import { RENDERERS } from "../kinds";
import type { Viewer } from "../store";
import { ErrorPanel } from "./ErrorPanel";

export function ViewBody({ path, viewer }: { path: string; viewer: Viewer }) {
  const entry = viewer.views.get(path);
  if (entry === undefined) {
    return <ErrorPanel path={path} error="no view file" />;
  }
  if (!entry.ok) {
    return <ErrorPanel path={path} error={entry.error} />;
  }
  const Renderer = RENDERERS.get(entry.view.kind);
  if (Renderer === undefined) {
    return (
      <ErrorPanel path={path} error={`no renderer for kind ${entry.view.kind}`} />
    );
  }
  return <Renderer view={entry.view} viewer={viewer} />;
}
