---
type: Workstream
title: CLOA Viewer
description: The plan for cloa-viewer, a local visual IDE that shows a checkout's fact base in the browser as registered views read from files on disk
---

# CLOA Viewer

cloa-viewer is a local visual IDE for every checkout in the workspace,
and this child workstream is its plan. This workstream is speculative.

Everything the viewer draws is a selection of the fact base, which is
its own child workstream
([Fact Base Workstream](/workstreams/system/see/fact-base/WORKSTREAM.md)):
the fact base is the theory, how deterministic code produces one
precise object of what a checkout is doing, and the viewer is the
delivery, how that object reaches a browser screen. Where the two
disagree, the fact base has priority
([Standing](/workstreams/system/see/fact-base/WORKSTREAM.md#standing)).

Its files:

- [Contract](/workstreams/system/see/viewer/contract.md) — the
  state directory, view file paths, identities, the envelope, the
  arrangement, the refresh record, and the failure rules.
- [Registry](/workstreams/system/see/viewer/registry.md) — what
  a registry entry is, the kinds built, and the kinds deferred.
- [Design](/workstreams/system/see/viewer/design.md) — how a
  panel is designed, and the renderer ideas recorded for the runbook
  views.
- [Viewer](/workstreams/system/see/viewer/viewer.md) — the page
  in the browser: layout, tree, panels, toggle, refresh, and failure on
  screen.
- [Server](/workstreams/system/see/viewer/server.md) — the
  command, the server's jobs, and live update.
- [Stack](/workstreams/system/see/viewer/stack.md) — the two
  languages, the schema bridge, the package shape, and the checks.

## Terms

Fact base, view, and extractor are the repo's words
([CONTEXT.md](/CONTEXT.md)). The terms of this child workstream:

- **CLOA object** — what a doc-type's contract shape defines for one
  document, a runbook's chain, a Standard's rules
  ([Doc-Type](/doc-types/doc-type.md)). In the fact base it is
  the nodes and edges that document's doc-type extractor yields.
- **view file** — one JSON file the server writes and the viewer shows as
  one panel; every view file has one kind
  ([Contract](/workstreams/system/see/viewer/contract.md)).
- **subject** — the thing in the checkout a view file is about, named
  by its identity; a per-subject kind writes one view file per subject.
- **kind** — a registered view: a selection, a renderer, and a doc page
  under one name ([an entry](/workstreams/system/see/viewer/registry.md#an-entry)).
  The repo's word for it is view; the pages and the code keep kind
  until the rename lands
  ([Planned](/workstreams/system/see/viewer/WORKSTREAM.md#planned)).
- **registry** — the list of kinds the tool can show
  ([Registry](/workstreams/system/see/viewer/registry.md)).
  Goes with kind: registry is the doc-type registry of
  [Document Types](/standards/knowledge-organization/document-types.md),
  and this list becomes the views in the same rename.
- **panel** — one view file rendered on screen.
- **state directory** — the directory outside every repo where view files
  live
  ([the state directory](/workstreams/system/see/viewer/contract.md#the-state-directory)).
- **identity** — how a view file names a thing in a checkout
  ([identities](/workstreams/system/see/viewer/contract.md#identities)).
- **stamp** — the envelope field that says which commit a view file
  describes and what produced it
  ([the envelope](/workstreams/system/see/viewer/contract.md#the-envelope)).
- **arrangement** — what the user has open, saved per checkout
  ([the arrangement](/workstreams/system/see/viewer/contract.md#the-arrangement)).
- **refresh record** — the outcome of the last refresh for one checkout
  ([the refresh record](/workstreams/system/see/viewer/contract.md#the-refresh-record)).

## Goal

cloa-viewer puts a checkout on a browser screen at the
[correct level of abstraction](/docs/system-legibility.md#the-cloa), so
the user can understand a system that the terminal and the IDE show
only as text. Deterministic code extracts the checkout's fact base;
every panel is one registered view selected from it; and a new view is
a new registry entry and nothing else changes. No model token is spent
to put anything on screen.

The acceptance picture. The user starts the viewer once, from
`~/workspace/`, and picks this checkout from the toggle. The left side
shows the tree, every tracked markdown file in its two groups
([index-tree](/workstreams/system/see/viewer/registry.md#index-tree)),
each with its description. The user clicks
`dotfiles/dot-claude/agents/doc-repairer.md`: its chain appears,
the CLOA object itself. A button on that panel opens the file's details,
its frontmatter facts, its links in and out, and its rendered source, for
the times the chain is not enough. The user edits the file in the IDE:
the chain redraws within the second that
[Live update](/workstreams/system/see/viewer/server.md#live-update)
targets.

## Principles

- **The objects are already defined; the viewer only draws them.** A
  CLOA object is defined by its doc-type pages under `doc-types/`, the
  contract shape above all. A panel uses the object's own primitives and
  the object's own terms, and mints neither: a runbook panel says edge,
  node, bucket, condition, and never a word the
  [chain](/doc-types/runbook/contract-shape.md) does not. A
  panel that needs a primitive the shape lacks is a residual for that
  doc-type's ledger, never a term the viewer invents
  ([Fact Base](/workstreams/system/see/fact-base/fact-base.md#the-objects-are-already-defined)).
  How an object draws is the renderer's to decide, which the
  doc-type itself says
  ([Nodes and Edges Encoding](/doc-types/runbook/encoding.md)), so the
  drawing rules are stated here, in the kind's registry entry, and the
  meaning they draw is the doc-type's.
- **A view drops; it never adds or converts**
  ([View](/CONTEXT.md#fact-base)).
  When a panel needs a shape the fact base lacks, the extractor or a
  rule changes, upstream of every view. No layer converts one view into
  another.
- **Known kinds only.** The viewer shows registered kinds and nothing
  else. Adding a kind is adding a registry entry
  ([Registry](/workstreams/system/see/viewer/registry.md)).
- **Deterministic and free of model tokens.** Every view file comes from
  code. An agent spends no output tokens to put something on screen.
- **Fail loud.** A view file validates or it shows as an error panel. An
  extractor or a kind succeeds or the refresh record names its failure. Nothing is
  hidden or silently dropped.
- **The CLOA object is the default face.** Clicking a file shows its
  CLOA object when one exists. The markdown behind it, frontmatter facts,
  links, and source, is one click further. The screen is not limited to
  CLOA objects; the default is.
- **Total accounting.** Every tracked markdown file appears in the tree,
  whether an index reaches it or not.
- **The user owns the room.** The user opens, arranges, and closes
  panels. Nothing opens on its own.
- **Simple, standard, modular.** Plain JSON files, JSON Schema, one small
  server, one page. Every kind plugs into the same sockets.
- **Greenfield inside the definition.** What the definition does not
  prohibit is allowed. Stitching a chain into the chains its do-edges
  name is one such move: the contract shape describes it and no text file
  ever drew it. When it is unclear whether a move draws the object or
  changes it, the user decides.
- **Design like a visual designer.** A panel follows data visualization
  practice. Each visual channel, hue, shape, line style, position, carries
  one variable of the object and means the same thing on every panel of
  that kind. A channel that carries nothing is not used. A shape always
  has its word beside it. Red is reserved for defects. The facts a reader
  needs first, a runbook's signature and its effects, sit where the eye
  lands first.

## Constraints

- The package lives in dev-playbook at `src/dev_playbook/cloa_viewer/`,
  a subpackage, per
  [One package under src/](/standards/build/skeleton.md#one-package-under-src).
  Breaking it out into its own repo is a later choice.
- The tool runs on the user's machine at a localhost address. It is never
  an artifact or a hosted page. Whether the page stays this tool's own
  shell or becomes a VS Code extension is open. The user leans to the
  shell, because the dashboard is to be composable and flexible and VS
  Code lays panels out as tabs. The panels are HTML in either home, so
  the choice would move the shell and not the kinds.
- The canonical artifacts stay untouched
  ([Canonical Artifacts](/standards/build/canonical.md)).
- The viewer reads only the state directory.
- One checkout is on screen at a time; the toggle switches between every
  checkout the workspace holds, main checkouts and worktrees alike, from
  one server that never has to be restarted to change repo or branch.
- The viewer classifies nothing itself. Which files are concept
  documents, harness-owned, or excluded, and which link sources are
  immutable, comes from the same functions the repo's checks use, so the
  screen and the checks can never disagree.

### Working agreements

How the user and the agent design a panel together. These bind the
design sessions, not the code.

- Design happens in the terminal, as Unicode sketches. The most a turn
  adds is one static SVG, fake data and no script, that the user opens in
  the browser. A sketch is judged in the turn it appears and then dropped.
- No prototype is built inside the design loop. A detailed build, a mock
  over real data or a renderer, goes to a dedicated subagent or a loop
  and takes the time it takes.
- A panel speaks in its doc-type's terms only. A new term is approved by
  the user and written into the doc-type's pages before the viewer uses
  it.
- When it is unclear whether a move draws the object or changes it, the
  user decides.
- A design turn asks at most one or two loose questions, never a batch.
- The text files are never cited as constraints. What they drew is not
  what the screen must draw.
- As this becomes a long-lived project, the principles, constraints, and
  agreements here need firmer structure than one head file. How is open.

## Planned

In build order. The vertical slice and the room are built (see
Completed). The viewer's next kinds are selections from the fact base,
which the fact base child workstream proves by simulation and then extracts
([Planned](/workstreams/system/see/fact-base/WORKSTREAM.md#planned));
each waits on it.

- **Runbook design** — a design session for the runbook views, starting
  from the renderer ideas in
  [Design](/workstreams/system/see/viewer/design.md): the
  interface card and control flow of one runbook. Nothing there is
  settled. The session ends with the drawing rules written into the
  kind's registry entry.
- **CLOA kinds** — the registry entries for the
  [CLOA views](/workstreams/system/see/viewer/registry.md#cloa-views):
  a name, a selection from the fact base, and drawing rules for each of
  the runbook, the Standard, and the loop. A Standard-Card kind is not
  among them: the card is retired.
- **Pinning and the arrangement** — pin, close others, and the
  arrangement saved and restored per checkout.
- **Stale badge** — the badge on a panel whose commit is behind HEAD.
- **Kind becomes view** — kind and view are one thing under two
  words ([View](/CONTEXT.md#fact-base)):
  the envelope's `kind` field becomes `view`, the `kinds` package
  becomes `views`, the registry becomes the views and its page
  `views.md`, and every page of this child workstream follows, in one change
  so the pages never describe a field the code does not have.

## Completed

- **Design settled** — the decisions this workstream records, reached in one
  design session on 2026-09-08, and reconciled with the fact base on
  2026-09-14.
- **Vertical slice** — loop 1, 2026-09-08: the package and command, the
  contract module, `index-tree` and `markdown-file`, the server with
  refresh and both watchers and the event stream, the page skeleton, the
  tree and file panels, the front-end checks, and the red refresh status.
- **The room** — loop 2, 2026-09-08: the tree in the two groups with
  nested guide lines and no word counts, the `decision-record` link
  status, discovery of every checkout under a directory of repos with
  rediscovery while the server runs, the checkout toggle on the page, a
  smoke run over dev-playbook's two checkouts, and Ctrl-C stopping the
  server while a page holds the stream.

## Acronyms

- **IDE** — Integrated Development Environment.
- **RFC** — Request for Comments.
- **UTC** — Coordinated Universal Time.
- **XDG** — X Desktop Group.
