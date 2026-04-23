# OpenFastTrace Requirement-Enhanced Markdown

OpenFastTrace (OFT) is a requirement-tracing toolchain. It defines two
things that commonly get conflated:

- A **format**, called *Requirement-Enhanced Markdown* — a superset of
  standard Markdown that any ordinary renderer will display, and that
  OFT-aware tools can parse for structured tracing.
- A **reference implementation** — a Java application (distributed as
  `openfasttrace-x.y.z.jar`) that parses the format, walks the coverage
  graph, and reports traceability.

This file describes the **format**. It does not describe the reference
implementation or any tool. Our choices about which subset of the format we
use, and which features we deliberately avoid, live in
[extensions.md](extensions.md).

## Document model

An OFT spec file is a Markdown file containing one or more **specification
items**. An item is identified by its ID and is delimited by Markdown
structure; any prose that is not part of an item is ignored by the tracer.

An item begins with either:

- a standard Markdown heading (`#`, `##`, `###`, …) that names the item, with
  the item's ID on the line immediately following, or
- an ID line with no preceding heading (the ID itself starts the item).

An item ends at the next item's heading-or-ID, at a forwarding line (see
*Forwarding* below), or at end of file.

Between its start and end, an item may contain a description (free-form
prose) and zero or more **keyword fields**. Each keyword field begins with a
keyword followed by a colon at the start of a line.

Content inside fenced code blocks is not parsed. An ID-looking string inside
a fenced block does not begin a specification item.

## Specification item ID

Every specification item is identified by a tilde-separated triple:

    type~name~revision

IDs are conventionally wrapped in backticks in source files
(`` `req~auth.login~1` ``); every user-guide example uses this form.

| Component | Definition |
|---|---|
| `type` | A short ASCII-letter string identifying the artifact kind (e.g., `req`, `dsn`). See *Artifact types* below. |
| `name` | A unique identifier for this item within its type. Must start with a Unicode letter; subsequent characters may be Unicode letters, digits, hyphens (`-`), underscores (`_`), or dots (`.`). No whitespace. No consecutive dots. |
| `revision` | A non-negative integer. Conventionally starts at 1; starting at 0 is permitted (Tag Importer output defaults to revision 0). |

The dot character in `name` is permitted by the format but carries no
structural meaning to OFT. It is sometimes used to create readable
hierarchies in IDs (`auth.login.validation`), which the format allows but
does not require.

## Artifact types

The `type` component is not enforced by OFT. Projects are free to define
whatever types they need. The user guide ships a recommended set for
software development:

| Type | Typical role |
|---|---|
| `feat` | Feature (high-level capability) |
| `req` | User or functional requirement |
| `arch` | Architecture |
| `dsn` | Design |
| `impl` | Implementation |
| `utest` | Unit test |
| `itest` | Integration test |
| `stest` | System test |
| `uman` | User manual |
| `oman` | Operation manual |

A project adopts whichever subset it needs. The format does not require any
specific combination.

## Keyword fields

Each keyword is a case-sensitive label followed by a colon at the start of a
line. Content may begin on the same line or the following line, depending on
the keyword.

| Keyword | Content | Cardinality |
|---|---|---|
| `Status:` | Lifecycle state: `draft`, `proposed`, or `approved`. | At most one per item, appears before the description. |
| `Description:` | Explicit marker for the start of the description body. | Optional. When absent, any non-keyword prose begins the description automatically. |
| `Rationale:` | Why the requirement exists. | At most one per item. |
| `Comment:` | Caveats, implementation notes, or anything that fits neither description nor rationale. | At most one per item. |
| `Covers:` | Upstream IDs this item satisfies. | Bullet list (one ID per line, prefixed `-`, `*`, or `+`). |
| `Needs:` | Downstream artifact types that must cover this item. | Either a comma-separated one-liner (`Needs: dsn, utest`) or a bullet list. The two forms cannot be mixed within one item. |
| `Tags:` | Labels for filtering. | Comma-separated list. |
| `Depends:` | Ordering dependencies between items. | Bullet list. Does not affect coverage; affects XML output only. |

`Status:` is informational for default reports (HTML, plaintext): a `draft`
item participates in coverage checks identically to an `approved` item. The
aspec XML report is stricter — its shallow-coverage check counts only
`approved` covering items.

## Linking model

OFT builds a directed graph from two keyword fields:

- `Needs:` declares which downstream artifact types **must** cover this item.
- `Covers:` declares which upstream items this item satisfies.

A `Covers:` entry names the full upstream ID, including the revision:
`- feat~user-auth~1`.

Example of the linkage between two items:

    ### User Authentication
    `feat~user-auth~1`
    Status: approved

    The system shall authenticate users before granting access.

    Needs: req

    ### Login Credential Validation
    `req~auth.login~1`
    Status: approved

    When the user submits credentials, the system shall verify them against
    the credential store.

    Covers:
    - feat~user-auth~1

    Needs: utest

The `feat` declares that at least one `req` must cover it; the `req`
declares it covers the `feat` at revision 1 and that at least one `utest`
must cover the `req` in turn.

## Coverage checks

Given a set of items, OFT classifies each outgoing link (`Covers:` entry)
and each incoming link (coverage received) against the upstream graph.
An item is a **terminating specification item** when it needs no
downstream types (empty `Needs:`); terminators are leaves and never
register as "uncovered".

### Outgoing-link statuses

| Status | Meaning |
|---|---|
| `Covers` | Link resolves cleanly to an existing upstream at the named revision. |
| `Predated` | The upstream ID exists, but the link names a revision *older* than the upstream's current revision. The covering item is stale; its author must re-evaluate. |
| `Outdated` | The upstream ID exists, but the link names a revision *newer* than any revision the upstream has ever carried. Usually a typo or stale expectation. |
| `Ambiguous` | More than one item with the named ID exists, so the link cannot resolve to a single upstream. |
| `Unwanted` | The link resolves, but the upstream's `Needs:` does not ask for a covering item of this downstream's type. |
| `Orphaned` | The link names an ID that does not exist in the trace set at all. |

### Incoming-link statuses

| Status | Meaning |
|---|---|
| `Covered Shallow` | At least one downstream item with a `Covers` status exists for every type in this item's `Needs:`. |
| `Covered Unwanted` | A downstream covers this item but declares a type not requested by this item's `Needs:`. |
| `Covered Predated` / `Covered Outdated` | A downstream covers this item, but the link it supplies is in the `Predated` or `Outdated` state for this item's current revision. |

### Other defects

| Defect | Meaning |
|---|---|
| Missing coverage | An item's `Needs:` names a type that no downstream covers cleanly. Surfaced in reports with a minus-prefix on the missing type (e.g. `(-utest)`). |
| `Duplicate` | Two or more items are defined with the same ID. |

A trace is considered clean when no defect is reported.

## Revisions

The `revision` component of an ID is a semantic version for the item's
meaning. Incrementing a revision indicates that the item's content has
changed in a way that affects downstream items. Because downstream
`Covers:` entries pin a specific upstream revision, a revision bump
voids existing coverage links — they become `Predated` defects in the
next trace run, forcing each downstream author to re-evaluate and
explicitly acknowledge the change.

Cosmetic edits (typos, formatting, wording that does not change meaning)
should not trigger a revision bump: they create churn without meaningful
re-evaluation.

OFT does not mandate when to increment; it only enforces that `Covers:`
revisions match upstream revisions at trace time.

## Forwarding

A **forward** lets an intermediate layer acknowledge an upstream item and
pass coverage responsibility to a further-downstream layer, without
creating a full specification item. The canonical form is:

    arch --> dsn : req~auth.login~1

A compact backtick-wrapped bullet form is also accepted (no spaces around
the arrow):

    - `dsn-->impl:req~bar~1`

The arrow uses two dashes to reduce the chance of parser collisions.
Forwards are allowed after a title line or within `Needs:`, `Covers:`,
`Depends:`, or `Tags:` blocks. A forward inside a description, rationale,
or comment block is ignored.

A forward line silently terminates the preceding specification item. This
is a common source of bugs when a forward is placed inside what the author
assumed was an ongoing item body.

## Excluding sections

Any content wrapped in the HTML-comment markers `<!-- oft:off -->` and
`<!-- oft:on -->` is skipped by the OFT parser:

    <!-- oft:off -->
    This section, and anything resembling an ID inside it, is ignored by
    the OFT parser:
    `req~example~1`
    <!-- oft:on -->

This is useful for example text, reference material, or documentation of
the format itself — content that would otherwise be mis-parsed as live
specification items.

## File discovery

OFT scans the paths it is given recursively, treating every file with a
`.md` or `.markdown` extension as a potential spec file. It assembles the
full coverage graph from whatever IDs and links it finds across the
discovered files. File names and folder structure do not affect tracing —
an ID defined in `a/b/c.md` is indistinguishable from the same ID in
`x.md` as far as the trace is concerned.

Projects may organize files hierarchically, by feature, or flat — all are
valid. Hierarchical organization is an allowed convenience, not a
requirement of the format.

## Reference

- OpenFastTrace repository and user guide:
  https://github.com/itsallcode/openfasttrace
- User guide (format specification):
  https://github.com/itsallcode/openfasttrace/blob/main/doc/user_guide.md
