---
type: General-Sheet
title: Viewer
description: The page in the browser — its fixed regions, the tree, panels and the arrangement, everything about one file, the checkout toggle, refresh, and how failure shows
---

# Viewer

The viewer is one page at a localhost address. It reads view files and
never a checkout, and it behaves like an IDE: the user navigates with
mouse and keyboard, and nothing opens on its own. The files it reads
obey the [Contract](/worktree-cloa-viewer-tool-working-docs/contract.md);
the panels it can draw are the
[Registry](/worktree-cloa-viewer-tool-working-docs/registry.md).

## Layout

Three fixed regions, none movable in v1:

- **Top bar** — the checkout toggle, the refresh button, and the status:
  connection, last refresh time and commit, and failed generators.
- **Left** — the tree.
- **Center** — a vertical stack of open panels. Each panel has its title,
  its stale badge when stale, a pin, and a close.

## The tree

The tree renders the `index-tree` view file in its two groups, headed
`Concept documents` and `Harness-owned files`. Under the first,
directories expand and collapse, and each level is told from the next by
eye, not by hunting for the triangle: a guide line runs down each level,
and an index row is set heavier than a file row. Each entry shows its
title and its description, nothing else. A concept document no index
reaches sits at the end of the first group under a red `Not indexed`
row, the tree's way of showing the defect okf-lint reports. The second
group is a flat list by identity. Clicking a file
opens its CLOA panel: the Reference chain for a runbook, the rules for a
Standard, the cells for a card. A file with no CLOA kind opens its
`markdown-file` panel. A panel already open comes to the top of the
stack instead.

## Panels and the arrangement

A newly opened panel goes to the top of the stack. Close removes it.
Pinned panels survive "close others"; that is the whole meaning of the
pin. The open panels, their order, their pins, and the expanded
directories are saved as the arrangement after every change and
restored when the page opens on that checkout.

## Everything about one file

Every panel about a file lists the other view files with the same
subject, as buttons. A CLOA panel offers the file's details, its
`markdown-file` panel, as the exception for when the CLOA object is not
enough; the details panel offers the CLOA panel back. A link in the
rendered source, or in the links-in and links-out lists, that points
inside the checkout opens the target the way the tree does. This is the
single identity scheme at work; the viewer needs no other
cross-reference.

## The checkout toggle

The toggle lists every checkout the server discovered
([Server and Stack](/worktree-cloa-viewer-tool-working-docs/server-and-stack.md#the-command)),
grouped by repo and labelled by branch, so a main checkout and its
worktrees sit together. Switching swaps the tree, the panels, and the
arrangement to that checkout's directory, with nothing to restart. The
page keeps the choice in its address, so a reload returns to the same
checkout. The list is discovered again each time the page asks for it,
which it does on load and after every refresh, so a worktree created or
removed while the server runs appears or disappears on its own, and a
branch change shows in the label. Until the arrangement is saved, the
page keeps each checkout's open panels for its own lifetime, so
switching away and back finds the room as it was left. View files of a
checkout the server was not given this run stay on disk and off screen.

## Refresh

Refresh is automatic: the server refreshes a checkout when a tracked
file in it changes. The button forces one. The status shows the last
refresh's time and commit and turns red when the refresh record has a
failed generator; clicking it shows the error text.

## Failure on screen

The failure rules in the Contract look like this on screen: a red panel
in the place of a view file that failed validation, naming the file and
the field; a banner across the top while the connection is lost; a badge
on a panel whose commit is behind the checkout's HEAD, showing both; a
red refresh status for a failed generator; and a red `Not indexed` row
in the tree. A link badge reading `decision-record` is not a failure and
is not red: it says the source is immutable and its target has moved on.

## Acronyms

None.
