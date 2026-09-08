// The registry, on the page's side: one renderer per registered kind. Adding a
// view to the viewer is adding an entry here and nothing else. A kind with no
// entry is not a crash — its panel says so.

import type { ComponentType } from "react";

import type { View } from "../api";
import type { Viewer } from "../store";
import { IndexTree } from "./index-tree/IndexTree";
import { MarkdownFile } from "./markdown-file/MarkdownFile";

/** What a renderer is given: its own view file, and the room it sits in. */
export interface RendererProps {
  view: View;
  viewer: Viewer;
}

export const RENDERERS = new Map<string, ComponentType<RendererProps>>([
  ["index-tree", IndexTree],
  ["markdown-file", MarkdownFile],
]);
