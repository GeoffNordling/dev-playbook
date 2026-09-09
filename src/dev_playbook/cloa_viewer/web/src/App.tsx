// The page: three fixed regions, none movable. The top bar over a left column
// for the tree and a center column for the panel stack.

import "./app.css";

import { Banner } from "./components/Banner";
import { ErrorPanel } from "./components/ErrorPanel";
import { PanelStack } from "./components/PanelStack";
import { TopBar } from "./components/TopBar";
import { ViewBody } from "./components/ViewBody";
import { useViewer } from "./store";

// The tree is one view file like any other, at the path the contract fixes
// for a per-checkout kind.
const TREE_PATH = "index-tree.json";

export function App() {
  const viewer = useViewer();
  return (
    <div className="app">
      <header className="head">
        <Banner connection={viewer.connection} />
        <TopBar viewer={viewer} />
      </header>
      <div className="regions">
        <nav className="tree">
          {viewer.loaded ? <ViewBody path={TREE_PATH} viewer={viewer} /> : null}
        </nav>
        <main className="center">
          {viewer.failure === null ? null : (
            <ErrorPanel path="cloa-viewer" error={viewer.failure} />
          )}
          <PanelStack viewer={viewer} />
        </main>
      </div>
    </div>
  );
}
