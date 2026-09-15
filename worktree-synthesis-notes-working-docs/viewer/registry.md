---
type: General-Sheet
title: Registry
description: The registered kinds — what an entry consists of, the two kinds built, the CLOA views to come, and the kinds deferred
---

# Registry

The registry is the list of kinds the tool can show. A kind outside the
registry has no way onto the screen, by the known kinds only principle
([CLOA Viewer](/worktree-synthesis-notes-working-docs/viewer/ROOT.md#principles)).
Every kind is a view of the checkout's
[fact base](/worktree-synthesis-notes-working-docs/fact-base/fact-base.md#views-are-selections):
a selection of its nodes and edges and a renderer. Every view file a
kind produces obeys the
[Contract](/worktree-synthesis-notes-working-docs/viewer/contract.md). What a
payload holds is stated here in words; the schemas come with the build.

## An entry

A registry entry holds, under one lowercase kebab-case name:

- a selection, the nodes and edges the kind keeps from the fact base,
  and the payload schema that is the shape of that selection;
- a renderer, a component from a validated payload to a panel;
- a doc page, the concept document that defines what the kind shows; for
  a view over a CLOA object that is its doc-type's contract-shape page
  under `doc-types/`.

A kind is per checkout, one view file, or per subject, one view file per
node it describes. The server and the page each hold a list of kinds,
and a name present on one side and absent on the other is an error
shown on screen.

## index-tree

Per checkout. The containment tree, restricted to tracked markdown.
Every tracked markdown file, in the two groups the
[File Roles](/standards/knowledge-organization/file-roles.md) guide
names: **concept documents**, arranged by the `index.md` hierarchy
([Indexes](/standards/knowledge-organization/indexes.md)), and
**harness-owned files**, a flat list. Tracked means what
[gitrepo.py](/src/dev_playbook/gitrepo.py) lists; the group is what
`classify()` in [md.py](/src/dev_playbook/md.py) answers, the one
encoding of the boundary, so the tree and okf-lint can never disagree. A
file that function calls excluded, the `PLAN.md` and `PROGRESS.md` pair,
has no row and no view file of any kind. A concept document that no
index reaches is listed under the hierarchy as not indexed and drawn as a
defect, because okf-lint reports it as one. Each entry carries its
identity, its title, and its description. There is no word count: how
big or how complex a document is will be a kind of its own, designed on
its own, and a summed count is not it.

## markdown-file

Per subject, one per tracked markdown file that `classify()` does not
exclude. The interface card of one file: its frontmatter attributes,
its headings, its `links-to` edges out with whether each resolves, its
`links-to` edges in, and the source itself as markdown for the page to
render. It is the detail behind a CLOA panel, reached by a button, and
the default panel only for a file with no CLOA kind.

A link out carries its identity when it names something in the checkout,
so the page opens the target without resolving a path itself. A
Citation of this repo
([Cross-References](/standards/knowledge-organization/cross-references.md#workspace-path-for-a-stable-location))
resolves into the checkout like a root-absolute link. A Citation of
another repo is reported as a citation and not checked: an extractor
reads one checkout, and ref-lint already verifies those targets. A link
out of a numbered decision record whose target is gone is reported as
`decision-record`, not broken: records are immutable
([Decision Records](/standards/decisions/records.md)), ref-lint exempts
them as sources for that reason, and the status names the object as it
is rather than inventing a word. The predicate that says which files are
records is shared with ref-lint, never copied.

## CLOA views

Per subject, one per document of a doc-type. The interface card of one
CLOA object is the document's node and every edge its doc-type extractor
yielded: for a runbook, the root with its name, type, and node data, the
signature, and the chain edges with operation, target, condition, and
annotation
([Reference Chain](/doc-types/runbook/contract-shape.md),
[Reference Chain Encoding](/doc-types/runbook/encoding.md)); for a
Standard, its population and its rules with their conditions
([Population and Rules Encoding](/doc-types/standard/encoding.md));
for a loop, its acts, checks, and yields, read from the Mermaid block
([Acts, Checks, and Yields](/doc-types/loop/contract-shape.md),
[encoding](/doc-types/loop/encoding.md)). A
runbook also has a control flow view, the same edges with order and
condition kept.

How these panels draw is not settled, and the kind names are not
chosen. The renderer ideas for the runbook are in
[Design](/worktree-synthesis-notes-working-docs/viewer/design.md), and the
drawing rules land here when the design session settles them.

## Deferred

Kinds and writers outside v1, in the likely order of arrival:

- **The other views** — the dependency graph, the data flow, the
  catalog, and the cross-reference matrix over the whole checkout
  ([Views are selections](/worktree-synthesis-notes-working-docs/fact-base/fact-base.md#views-are-selections)).
  Which arrive first is decided by the use cases the fact base
  simulations enumerate.
- **mermaid** — a diagram rendered from mermaid source.
- **The agent as a second writer** — view files an agent authors, and a
  flag that opens a panel without a click. The state directory already
  admits another writer; v1 has none.
- **Code extractors** — bedrock extractors over code, each wrapping a
  tool the candidates list already names under
  [Code legibility](/CANDIDATES.md#code-legibility): the import graph,
  the call graph, the rendered API surface, the complexity report, the
  sequence diagram, and the import contract, itself a CLOA object the
  user authors. Their rows land in the same fact base and the same
  views; non-markdown files join the tree with them.
- **Documentation report kinds** — the markdown complexity and
  duplication reports under
  [Documentation quality](/CANDIDATES.md#documentation-quality), which
  are code's static analyzers applied to prose.
- **Others named in design** — a diff against main, a free dashboard
  layout, and generation on request rather than up front.

## Acronyms

API — Application Programming Interface.
