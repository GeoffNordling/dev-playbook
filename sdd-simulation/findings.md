# Findings

Observations about the workspace spec standard surfaced while running the
simulation. Each entry names the friction; resolutions (if any) belong in
the standard itself or in its ADRs.

## 1. Cross-module behavioral properties: re-frame to find ownership

Round-trip preservation factually spans serialize + deserialize. First
parked on `feat~serialize~0` (`req~serialize.round-trip~0`); felt
arbitrary. Resolved by re-phrasing from the model's facet: "the model
`SHALL` survive round-trip serialization." Moved to
`req~model.round-trip~0`.

The technique: cross-module properties often have one module that
holds the *natural ownership stake* (here, the model — its design
determines whether closure is achievable). Re-framing the prose
toward that owner attaches the req cleanly. The chain stays
hierarchical even though the test (`itest`) still spans modules.

This works when an owner exists. When no module has a clearly
stronger stake, the property fits better in a dedicated cross-module
spec file (e.g., `specs/integration.md`) than shoe-horned into a
module that doesn't quite fit. Reqs in such a file `MAY` call for
`itest` rather than `utest`. The standard accommodates this
mechanically — `itest` is a defined artifact type — but offers no
convention for the file layout of cross-cutting concerns.

## 2. Consolidate coupled commitments into a single spec item

When two commitments overlap factually but address different design
dimensions (e.g., Data shape and API-Shape), keep them in one spec
item. `dsn~model.spec-item~0` carries both a Data-dimension field
list (`Description:`) and an API-Shape constructor signature
(`Interface:`); they overlap factually but stay aligned because they
are reviewed together at every edit.

Splitting factually-coupled commitments across separate spec items
introduces drift risk — items can change independently, and no
validator catches the divergence. Best practice: consolidate
tightly-coupled commitments; only split when items genuinely change
at independent rates or for independent reasons.

## 3. Each module mapped 1:1 to a feat

In this simulation, every module has exactly one feat. The standard
doesn't require this and it isn't universal — but for small focused
libraries it appears to be the natural shape, because feat
decomposition and module decomposition both follow "one cohesive
capability per unit."

# Spec-tools feature ideas

Tool ideas surfaced while running the simulation. Track for issue
#16 when real spec-tools development begins.

## Tree structure visualizer

A CLI that loads all specs in a project and renders a digestible
tree of feats → reqs → dsns → tests, with each node annotated by
coverage state (covered / uncovered / cross-file).

Two modes:

- **Detail** — every leaf shown by id and title (matches the ASCII
  trees we drew during the simulation).
- **Aggregate** — value counts by category, e.g., "5 reqs covered
  by dsns, 3 uncovered; 2 cross-file dsn coverages" — analogous to
  pandas' `value_counts`. Useful for scanning a large project's
  coverage state at a glance without reading every item.
