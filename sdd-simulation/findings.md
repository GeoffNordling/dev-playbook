# Findings

Observations about the workspace spec standard surfaced while running the
simulation. Each entry names the friction; resolutions (if any) belong in
the standard itself or in its ADRs.

## 1. Cross-module behavioral properties: re-frame to find ownership

A behavioral property that factually spans two modules can feel
arbitrary parked on either one. The technique: such properties
often have one module that holds the *natural ownership stake* —
its design determines whether the property is achievable.
Re-framing the prose toward that owner attaches the requirement
cleanly. The chain stays hierarchical even when the test (`itest`)
spans modules.

Example: a round-trip property between a serializer and
deserializer feels arbitrary parked on either. Re-framed onto the
underlying data model — "the model `SHALL` survive round-trip
serialization" — it lands cleanly, because the model's design is
what makes round-trip closure achievable.

This works when an owner exists. When no module has a clearly
stronger stake, the property fits better in a dedicated
cross-module spec file than shoe-horned into a module that doesn't
quite fit. Reqs in such a file `MAY` call for `itest` rather than
`utest`. The standard accommodates this mechanically — `itest` is
a defined artifact type — but offers no convention for the file
layout of cross-cutting concerns.

## 2. Consolidate coupled commitments into a single spec item

When two commitments overlap factually but address different
design dimensions (e.g., Data shape and API-Shape), keep them in
one spec item. A single dsn can carry both a Data-dimension field
list (in `Description:`) and an API-Shape constructor signature
(in `Interface:`); they overlap factually but stay aligned because
they're reviewed together at every edit.

Splitting factually-coupled commitments across separate spec items
introduces drift risk — items can change independently, and no
validator catches the divergence. Best practice: consolidate
tightly-coupled commitments; split only when items genuinely
change at independent rates or for independent reasons.

## 3. Topic-hierarchy intuitions can mislead

Two dsns can feel nested when they're structurally peers — for
example, a class type and a sub-type its Interface composes. The
sub-type *feels* like a refinement, but topical nesting isn't
structural nesting.

The standard's only hierarchy is by artifact type (feat → req →
dsn → utest). Within an artifact type, items are peers connected
by `Covers:` and `Depends:`. There's no parent-child within a
level. When two dsns share a parent req and one's Interface
references a type defined by the other, the relationship rides on
the `Depends:` edge — same parent, same level, one type-edge —
that's the full structure.

The urge to add more structure comes from a topic intuition the
standard deliberately doesn't represent. Each spec item stands
alone; relationships between peers ride on `Covers:` and
`Depends:`. The existing primitives suffice.

## 4. Don't write requirements for self-evident negatives

A comprehensive positive definition implicitly excludes everything
else. A separate `SHALL NOT` requirement earns its keep only when
the positive fails to block the wrong path — typically when the
wrong path looks like a reasonable convenience a reviewer might
approve.

Example: a dsn that says "type X `SHALL NOT` carry an additional
accessor for some field" is redundant once another dsn enumerates
X's fields exhaustively. The field list excludes additional
accessors implicitly. The negative becomes one of infinitely many
things excluded by the positive — the "`SHALL NOT` have an
attribute named monkey_brains" of the spec.

Negatives earn their keep when the positive definition genuinely
leaves the wrong path open: a tempting convenience, a deprecated
alternative someone might re-introduce, or a known prior failure
mode.

## 5. One feat per module is a natural fit for small libraries

For a small focused library, each module tends to map 1:1 to a
single feat. The standard doesn't require this and it isn't
universal, but feat decomposition and module decomposition both
follow "one cohesive capability per unit," so they often line up.

# Spec-tools feature ideas

Tool ideas surfaced while running the simulation. Track for issue
#16 when real spec-tools development begins.

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
