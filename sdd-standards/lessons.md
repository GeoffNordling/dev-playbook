# Lessons

Observations about the workspace spec standard surfaced through use.
Each entry names the friction; resolutions (if any) belong in the
standard itself or in its ADRs.

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

## 6. Open question: should `Interface:` move out of `dsn`?

Pinning the public surface of a simple requirement still requires
creating a `dsn`, even when the dsn carries no design content
beyond restating the req and naming the function. The pattern
works mechanically but feels misshapen — the load-bearing content
is the `Interface:`, and the rest of the dsn is scaffolding around
it. Finding 6 justifies the cost; this finding flags the smell.

A possible alternative is a dedicated primitive — call it
`skeleton`, `stub`, or similar — whose job is to pin code shape
(signatures, module placement, type names) rather than design
decisions. `dsn` would then be reserved for items that genuinely
narrow the implementation space, and the red TDD agent would have
a separate single-purpose handle for "what to scaffold."

If we go that route, the chain attachment is itself an open
question: a new primitive still has to tie back to the
requirements it scaffolds. The `Covers:` / `Needs:` mechanism is
type-agnostic and would admit a new artifact type without
structural change, but where the new node sits relative to `dsn`
— parallel to it, replacing it on trivial reqs, or something
else — is a separate decision.

Not deciding here. Park until enough trivial-Interface dsns
accumulate to tell whether the discomfort is recurring or one bad
case.

## 7. Authoring phases need a closing review pass, like implementation's

An ad-hoc audit of spec-tools' specs against its tests surfaced
three categories of substantive findings — tests pinning unstated
contracts, both spec and test silent on real boundary cases, and
standard-mandated rules left to implicit enforcement — across
functional requirements and design. None required deep insight;
each was visible by reading the spec alongside the test that
covers it. They slipped through because no authoring phase held
its output up against a rubric before signing off.

`sdd-implementation` already models the pattern in its
"whole-chunk refactor pass" — once slices are green, look back
across every module the chunk touched for refactor candidates
that were not visible inside any single slice. Requirements and
design lack the parallel.

The friction lives in the skills, not the standard:
`sdd-requirements` and `sdd-design` end on "iterate with the user
until the draft is approved," with no structured self-check
between draft and approval. A closing review pass — fixed
checklist, run by the agent before signaling completion — is the
natural addition. What goes on each phase's checklist is itself a
design problem (e.g., for design: every `Interface:` matched by a
behavioral commitment in `Description:`, every standard rule the
design leans on named explicitly, every `Needs:` reachable
downstream). Agents are unreliable at improvisational
self-critique and reliable at running a rubric, so the pass
should be structured, not freeform.
