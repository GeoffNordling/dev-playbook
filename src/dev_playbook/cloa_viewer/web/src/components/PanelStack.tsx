// The center region: the open panels, newest first. One panel is one view
// file, drawn by its kind's renderer. The stack decides nothing about a kind
// beyond which renderer to call.

import { RENDERERS } from "../kinds";
import type { Viewer } from "../store";
import type { Validated } from "../validate";
import { ErrorPanel } from "./ErrorPanel";

export function PanelStack({ viewer }: { viewer: Viewer }) {
  return (
    <div className="panels">
      {viewer.open.map((path) => (
        <Panel key={path} path={path} viewer={viewer} />
      ))}
    </div>
  );
}

function Panel({ path, viewer }: { path: string; viewer: Viewer }) {
  const entry = viewer.views.get(path);
  const title = entry !== undefined && entry.ok ? entry.view.title : path;
  return (
    <section className="panel">
      <header className="panel-head">
        <h2 className="panel-title">{title}</h2>
        <button
          type="button"
          className="button"
          onClick={() => {
            viewer.closePanel(path);
          }}
        >
          Close
        </button>
      </header>
      <div className="panel-body">
        <PanelBody path={path} entry={entry} viewer={viewer} />
      </div>
    </section>
  );
}

function PanelBody({
  path,
  entry,
  viewer,
}: {
  path: string;
  entry: Validated | undefined;
  viewer: Viewer;
}) {
  if (entry === undefined) {
    return <ErrorPanel path={path} error="no view file" />;
  }
  if (!entry.ok) {
    return <ErrorPanel path={path} error={entry.error} />;
  }
  const Renderer = RENDERERS.get(entry.view.kind);
  if (Renderer === undefined) {
    return (
      <ErrorPanel
        path={path}
        error={`no renderer for kind ${entry.view.kind}`}
      />
    );
  }
  return <Renderer view={entry.view} viewer={viewer} />;
}
