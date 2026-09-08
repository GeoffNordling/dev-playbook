// The tree: every tracked markdown file arranged by the index.md hierarchy,
// and the unindexed list last. It is the page's only way in — clicking a file
// row opens that file's panel — so total accounting matters here: a file an
// index lists but the checkout does not carry still gets a row, marked.

import { useCallback, useState } from "react";

import type { Viewer } from "../../store";
import type { RendererProps } from "../index";

/** One directory row: the facts its index.md carries, and what it lists. */
export interface DirectoryNode {
  identity: string;
  title: string;
  description: string | null;
  children: TreeNode[];
}

/** One file row: its frontmatter facts. */
export interface FileNode {
  identity: string;
  type: string | null;
  title: string | null;
  description: string | null;
  exists: boolean;
}

export type TreeNode = DirectoryNode | FileNode;

/** The index-tree payload, as its schema fixes it. */
export interface IndexTreePayload {
  root: DirectoryNode;
  unindexed: FileNode[];
}

// Expansion is held per row under the row's identity. A directory identity
// always ends in a slash, or is the empty string for the root, so this name
// can never be one.
const UNINDEXED = "unindexed";

const INDENT_PX = 14;

export function IndexTree({ view, viewer }: RendererProps) {
  // The view validated against index-tree.schema.json before it reached the
  // store, so the payload is this shape and the page does not check again.
  const payload = view.payload as unknown as IndexTreePayload;
  const [expanded, setExpanded] = useState<ReadonlySet<string>>(
    () => new Set([payload.root.identity]),
  );
  const toggle = useCallback((identity: string) => {
    setExpanded((current) => {
      const next = new Set(current);
      if (!next.delete(identity)) {
        next.add(identity);
      }
      return next;
    });
  }, []);
  return (
    <div className="tree-rows">
      <Directory
        node={payload.root}
        depth={0}
        expanded={expanded}
        toggle={toggle}
        viewer={viewer}
      />
      <Row
        depth={0}
        open={expanded.has(UNINDEXED)}
        title="Unindexed"
        description={null}
        count={`${payload.unindexed.length} files`}
        onClick={() => {
          toggle(UNINDEXED);
        }}
      />
      {expanded.has(UNINDEXED)
        ? payload.unindexed.map((node) => (
            <File key={node.identity} node={node} depth={1} viewer={viewer} />
          ))
        : null}
    </div>
  );
}

function Directory({
  node,
  depth,
  expanded,
  toggle,
  viewer,
}: {
  node: DirectoryNode;
  depth: number;
  expanded: ReadonlySet<string>;
  toggle: (identity: string) => void;
  viewer: Viewer;
}) {
  const open = expanded.has(node.identity);
  return (
    <>
      <Row
        depth={depth}
        open={open}
        title={node.title}
        description={node.description}
        onClick={() => {
          toggle(node.identity);
        }}
      />
      {open
        ? node.children.map((child) =>
            isDirectory(child) ? (
              <Directory
                key={child.identity}
                node={child}
                depth={depth + 1}
                expanded={expanded}
                toggle={toggle}
                viewer={viewer}
              />
            ) : (
              <File
                key={child.identity}
                node={child}
                depth={depth + 1}
                viewer={viewer}
              />
            ),
          )
        : null}
    </>
  );
}

function File({
  node,
  depth,
  viewer,
}: {
  node: FileNode;
  depth: number;
  viewer: Viewer;
}) {
  return (
    <Row
      depth={depth}
      open={null}
      title={node.title ?? node.identity}
      description={node.description}
      missing={!node.exists}
      onClick={() => {
        openFile(viewer, node.identity);
      }}
    />
  );
}

/**
 * Open a file's markdown-file panel, or say why there is none.
 *
 * The tree names a file by its identity and the contract fixes the path from
 * it, so the page resolves nothing. A file with no view file is an index
 * listing something the checkout does not carry: an error panel, not a
 * silently dead row.
 */
function openFile(viewer: Viewer, identity: string): void {
  const path = `markdown-file/${identity}.json`;
  if (viewer.views.has(path)) {
    viewer.openPanel(path);
    return;
  }
  viewer.openError(path, `no view file for ${identity}`);
}

function Row({
  depth,
  open,
  title,
  description,
  count,
  missing = false,
  onClick,
}: {
  depth: number;
  /** Whether the disclosure triangle points down, or null on a file row. */
  open: boolean | null;
  title: string;
  description: string | null;
  /** The trailing figure, on the rows that have one to show. */
  count?: string;
  missing?: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      className={missing ? "tree-row tree-row-missing" : "tree-row"}
      style={{ paddingLeft: `${depth * INDENT_PX}px` }}
      onClick={onClick}
    >
      <span className="tree-twist">{twist(open)}</span>
      <span className="tree-text">
        <span className="tree-title">
          {title}
          {missing ? <span className="tree-missing">missing</span> : null}
        </span>
        {description === null ? null : (
          <span className="tree-description">{description}</span>
        )}
      </span>
      {count === undefined ? null : <span className="tree-count">{count}</span>}
    </button>
  );
}

/** The disclosure triangle: down when open, right when shut, none on a file. */
function twist(open: boolean | null): string {
  if (open === null) {
    return "";
  }
  return open ? "▾" : "▸";
}

function isDirectory(node: TreeNode): node is DirectoryNode {
  return "children" in node;
}
