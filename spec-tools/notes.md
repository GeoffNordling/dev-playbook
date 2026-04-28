# Notes

Forward-looking ideas not yet promoted to specs. Track for issue #16.

## Coverage views

Standard views from the requirements-traceability literature
(DOORS, Jama, OpenFastTrace). All are cheap to compute once specs
are parsed into an in-memory graph keyed by id with bidirectional
coverage edges:

- **Matrix** — sparse 2D table of items × items with cells marked
  where coverage exists. The canonical view; the others are
  derivable from it.
- **Slice** — pick one item; show its coverage subgraph downstream
  (what it covers) and upstream (what covers it).
- **Aggregate** — value counts by artifact type and coverage state
  (e.g., "5 reqs covered by dsns, 3 uncovered") — analogous to
  pandas' `value_counts`. For scanning a large project at a
  glance.
- **Gap report** — list specifically which items lack coverage
  declared by their `Needs:` — the punch list, not just counts.
- **Impact analysis** — reverse slice from a chosen item: "if I
  change this dsn, what reqs and tests does it affect?" The
  workhorse view when planning a refactor.

Deferred (need version awareness, so not v1):

- **Diff** — coverage changes between two revisions or branches.
- **Suspect links** — flag downstream coverage as suspect when an
  upstream item changes; clear on human re-review.

### No tree view

A tree is single-parent by definition. The moment one node has
two parents — one dsn covers two reqs, one utest covers two dsns
— the tree breaks. The repair options are both bad: duplicate
the node under each parent (loses identity, easy to miss), or
annotate "also under X" (no longer really a tree, the eye can't
see the cross-cuts at a glance). Any project that allows
cross-cutting gets no use from tree, so it isn't worth building.
