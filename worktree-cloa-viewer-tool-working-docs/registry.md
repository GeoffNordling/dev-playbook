---
type: General-Sheet
title: Registry
description: The registered kinds — what an entry consists of, the five v1 kinds and what each panel shows, and the kinds deferred
---

# Registry

The registry is the list of kinds the tool can show. v1 registers five.
A kind outside the registry has no way onto the screen, by the known
kinds only principle
([CLOA Viewer](/worktree-cloa-viewer-tool-working-docs/ROOT.md#principles)).
Every view file a kind produces obeys the
[Contract](/worktree-cloa-viewer-tool-working-docs/contract.md). What a
payload holds is stated here in words; the schemas come with the build.

## An entry

A registry entry is four things under one lowercase kebab-case name:

- a payload schema;
- a generator, a function from a checkout to the kind's view files;
- a renderer, a component from a validated payload to a panel;
- a doc page, the concept document that defines what the kind shows; for
  a CLOA kind that is its doc-type's contract-shape page under
  `doc-types/`.

A kind is per checkout, one view file, or per subject, one view file per
thing it describes. The server and the page each hold a list of kinds,
and a name present on one side and absent on the other is an error
shown on screen.

## index-tree

Per checkout. Every tracked markdown file, arranged by the `index.md`
hierarchy ([Indexes](/standards/knowledge-organization/indexes.md)),
plus every tracked markdown file no index reaches, in a flagged
unindexed list. Tracked means what
[gitrepo.py](/src/dev_playbook/gitrepo.py) lists. Each entry carries its
identity, its title and description, and its word count; a directory's
count sums what is below it.

## markdown-file

Per subject, one per tracked markdown file. What the file is and what
touches it: its frontmatter facts, its word count, its headings, its
links out with whether each resolves, its links in, and the source
itself as markdown for the page to render. It is the detail behind a
CLOA panel, reached by a button, and the default panel only for a file
with no CLOA kind.

A link out carries its identity when it names something in the checkout,
so the page opens the target without resolving a path itself. A
Citation of this repo
([Cross-References](/standards/knowledge-organization/cross-references.md#workspace-path-for-a-stable-location))
resolves into the checkout like a root-absolute link. A Citation of
another repo is reported as a citation and not checked: a generator
reads one checkout, and ref-lint already verifies those targets.

## runbook-chain

Per subject, one per runbook, an agent definition or a skill. The
Reference chain as data, the thing `chains.txt` draws as text today:
the runbook's header facts and its edges, each with its verb, its
target, its note, and its condition when it has one
([Reference Chain](/doc-types/runbook/contract-shape.md),
[Reference Chain Encoding](/doc-types/runbook/encoding.md)).

## standard

Per subject, one per Standard file. Its card, its population, and its
rules with their conditions, the rows `standards.txt` lists today
([Population and Rules Encoding](/doc-types/standard/encoding.md)).

## standard-card

Per subject, one per Standard-Card file. The four cells and the pointers
in each, the rows `cards.txt` lists today
([Card Cells](/doc-types/standard-card/contract-shape.md)).

## Deferred

Kinds and writers outside v1, in the likely order of arrival:

- **force-graph** — the checkout's link graph, for the connectivity
  questions the tree cannot answer. First to add.
- **mermaid** — a diagram rendered from mermaid source.
- **The agent as a second writer** — view files an agent authors, and a
  flag that opens a panel without a click. The state directory already
  admits another writer; v1 has none.
- **Code kinds** — each the output of a tool the candidates list already
  names under [Code legibility](/CANDIDATES.md#code-legibility): the
  import graph, the call graph, the rendered API surface, the complexity
  report, the sequence diagram, and the import contract, itself a CLOA
  object the user authors. Non-markdown files join the tree with them.
- **Documentation report kinds** — the markdown complexity and
  duplication reports under
  [Documentation quality](/CANDIDATES.md#documentation-quality), which
  are code's static analyzers applied to prose.
- **Others named in design** — a diff against main, a free dashboard
  layout, and generation on request rather than up front.

## Acronyms

None.
