// The tree: every tracked markdown file in the two groups the File Roles guide
// names — the concept documents the index.md hierarchy arranges, with the ones
// no index reaches under a red row of their own, and the harness-owned files as
// a flat list. It is the page's only way in — clicking a file row opens that
// file's panel — so total accounting matters here: a file an index lists but
// the checkout does not carry still gets a row, marked.

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
  harness: FileNode[];
}

// Expansion is held per row under the row's identity. A directory identity
// always ends in a slash, or is the empty string for the root, so none of these
// three names can ever be one.
const CONCEPTS = "concepts";
const HARNESS = "harness";
const UNINDEXED = "unindexed";

const INDENT_PX = 14;

export function IndexTree({ view, viewer }: RendererProps) {
  // The view validated against index-tree.schema.json before it reached the
  // store, so the payload is this shape and the page does not check again.
  const payload = view.payload as unknown as IndexTreePayload;
  // Both groups and the hierarchy open on arrival; the unindexed list stays
  // shut, because it is a defect list and an empty screen is the good case.
  const [expanded, setExpanded] = useState<ReadonlySet<string>>(
    () => new Set([CONCEPTS, HARNESS, payload.root.identity]),
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
      <Row
        depth={0}
        open={expanded.has(CONCEPTS)}
        group
        title="Concept documents"
        description={null}
        onClick={() => {
          toggle(CONCEPTS);
        }}
      />
      {expanded.has(CONCEPTS) ? (
        <>
          <Directory
            node={payload.root}
            depth={1}
            expanded={expanded}
            toggle={toggle}
            viewer={viewer}
          />
          <Unindexed
            nodes={payload.unindexed}
            open={expanded.has(UNINDEXED)}
            toggle={toggle}
            viewer={viewer}
          />
        </>
      ) : null}
      <Row
        depth={0}
        open={expanded.has(HARNESS)}
        group
        title="Harness-owned files"
        description={null}
        count={`${payload.harness.length} files`}
        onClick={() => {
          toggle(HARNESS);
        }}
      />
      {expanded.has(HARNESS)
        ? payload.harness.map((node) => (
            <File key={node.identity} node={node} depth={1} viewer={viewer} />
          ))
        : null}
    </div>
  );
}

/**
 * The concept documents no index reaches, under a red row that names the defect.
 *
 * Nothing at all when the list is empty: okf-lint reports an unindexed document
 * as a defect, and a row saying there are none would put a permanent fixture on
 * screen for the case where there is nothing to see.
 */
function Unindexed({
  nodes,
  open,
  toggle,
  viewer,
}: {
  nodes: FileNode[];
  open: boolean;
  toggle: (identity: string) => void;
  viewer: Viewer;
}) {
  if (nodes.length === 0) {
    return null;
  }
  return (
    <>
      <Row
        depth={1}
        open={open}
        bad
        title="Not indexed"
        description={null}
        count={`${nodes.length} files`}
        onClick={() => {
          toggle(UNINDEXED);
        }}
      />
      {open
        ? nodes.map((node) => (
            <File key={node.identity} node={node} depth={2} viewer={viewer} />
          ))
        : null}
    </>
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
  group = false,
  bad = false,
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
  /** True on one of the two group headers. */
  group?: boolean;
  /** True on a row that names a defect, drawn in the bad color. */
  bad?: boolean;
  missing?: boolean;
  onClick: () => void;
}) {
  const classes = ["tree-row"];
  if (group) {
    classes.push("tree-group");
  }
  if (bad) {
    classes.push("tree-row-bad");
  }
  if (missing) {
    classes.push("tree-row-missing");
  }
  return (
    <button
      type="button"
      className={classes.join(" ")}
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
