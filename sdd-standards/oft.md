# OpenFastTrace Requirement-Enhanced Markdown

OpenFastTrace (OFT) is a requirement-tracing toolchain. It defines two
things that commonly get conflated:

- A **format**, called *Requirement-Enhanced Markdown* — a superset of
  standard Markdown that any ordinary renderer will display, and that
  OFT-aware tools can parse for structured tracing.
- A **reference implementation** — a Java application (distributed as
  `openfasttrace-x.y.z.jar`) that parses the format, walks the coverage
  graph, and reports traceability.

This file describes the **format** and then, in a trailing
[Extensions](#extensions) section, describes the workspace subset,
added keywords, and constraints layered on top. It does not describe the
reference implementation or any tool.

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
| `revision` | A non-negative integer. Conventionally starts at 1; starting at 0 is permitted. |

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
| `Status:` | Lifecycle state: `draft`, `proposed`, or `approved`. | At most one per item. Must appear before `Description:`, `Rationale:`, and `Comment:`. |
| `Description:` | Explicit marker for the start of the description body. | Optional. When absent, any non-keyword prose begins the description automatically. Must appear before `Rationale:` and `Comment:`. |
| `Rationale:` | Why the requirement exists. | Conventionally at most one per item. |
| `Comment:` | Caveats, implementation notes, or anything that fits neither description nor rationale. | Conventionally at most one per item. |
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
An item is a **terminating specification item** when it requires coverage
in no artifact type — either because it has no `Needs:` keyword at all
(the common case) or because its `Needs:` list is empty. Terminators are
leaves and never register as "uncovered".

### Outgoing-link statuses

| Status | Meaning |
|---|---|
| `Covers` | Link resolves cleanly to an existing upstream at the named revision. |
| `Predated` | The upstream ID exists, but the link names a revision *newer* than the upstream's current revision. The link is ahead of the upstream — typically a typo or a link written against an expected-but-unlanded revision bump. |
| `Outdated` | The upstream ID exists, but the link names a revision *older* than the upstream's current revision. The upstream has advanced and the covering item is stale; its author must re-evaluate. |
| `Ambiguous` | More than one item with the named ID exists, so the link cannot resolve to a single upstream. |
| `Unwanted` | The link resolves, but the upstream's `Needs:` does not ask for a covering item of this downstream's type. |
| `Orphaned` | The link names an ID that does not exist in the trace set at all. |

### Incoming-link statuses

| Status | Meaning |
|---|---|
| `Covered Shallow` | At least one downstream item with a `Covers` status exists for every type in this item's `Needs:`. |
| `Covered Unwanted` | A downstream covers this item but declares a type not requested by this item's `Needs:`. |
| `Covered Predated` / `Covered Outdated` | A downstream covers this item, but the link it supplies is in the `Predated` or `Outdated` state for this item's current revision. |

### Other statuses and defects

| Name | Scope | Meaning |
|---|---|---|
| `Duplicate` | Link status (bidirectional) | Two or more items are defined with the same ID, so any link naming that ID cannot resolve to a single item. |
| Missing coverage | Item-level defect | An item's `Needs:` names a type that no downstream covers cleanly. Surfaced in reports with a minus-prefix on the missing type (e.g. `(-utest)`). A symmetric `+type` form (e.g. `(+itest)`) appears when coverage is received from a type the item did not request — the same condition the per-link `Covered Unwanted` status flags. |

A trace is considered clean when no defect is reported.

## Revisions

The `revision` component of an ID is a semantic version for the item's
meaning. Incrementing a revision indicates that the item's content has
changed in a way that affects downstream items. Because downstream
`Covers:` entries pin a specific upstream revision, a revision bump
voids existing coverage links — they become `Outdated` defects in the
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
Forwards are allowed after a title line, or after a `Needs:`, `Covers:`,
`Depends:`, or `Tags:` block. A forward inside a description, rationale,
or comment block is ignored.

A forward line silently terminates the preceding specification item.
Any `Needs:`, `Covers:`, or similar fields placed after the forward are
therefore silently dropped from the preceding item — a documented
footgun. The user guide recommends collecting forwards in a separate
titled section to avoid placing them mid-item.

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

## Extensions

Everything above is the external standard. This section records how this
workspace uses the format: which parts we adopt, what we add on top, and
what we forbid. The three kinds of decisions are **subset** (we adopt only
part of the standard's optional vocabulary), **extension** (we add
capability the standard does not define), and **constraint** (we forbid
or tighten something the standard allows).

Obligation verbs below follow [rfc2119.md](rfc2119.md).

### Artifact types — subset

The format's recommended set is ten types. This workspace uses five:

| Type | Purpose |
|---|---|
| `feat` | High-level feature |
| `req` | User or functional requirement |
| `dsn` | Design item |
| `utest` | Unit test |
| `itest` | Integration test |

Types not used in this workspace: `arch`, `impl`, `stest`, `uman`, `oman`.

Reason: the five chosen types are sufficient to express the workspace's
coverage chain (below). Adding more types without a specific need inflates
the vocabulary without information gain. Projects `MAY` adopt additional
types if they have a concrete need; additional types `SHALL` be documented
in the project's `specs/` directory.

### Coverage chain — constraint

The workspace chain is:

    feat  →  req  →  dsn  →  utest / itest

Each arrow is an OFT coverage relationship: the downstream layer covers
the upstream layer through `Needs:` / `Covers:` links.

Required structure:

- `feat` `SHALL` be the root. Every project `SHALL` begin the chain with
  `feat` items.
- `req` items `SHALL` cover `feat`.
- Most `req` items `SHALL` declare `Needs: dsn` to carry the chain forward
  into the design layer.
- `dsn` items `SHALL` cover `req` and are expected for most `req` items. A
  `req` `MAY` skip `dsn` only when it needs neither a design decision nor
  an ownership assignment; in that case the `req` `SHALL` declare
  `Needs: utest` and/or `Needs: itest` directly.
- `utest` and `itest` `SHALL` cover the item directly upstream. Either a
  `req` or a `dsn` `MAY` declare `Needs: utest`, `Needs: itest`, or both —
  whichever is appropriate to verify the commitment.
- An item with no `Needs:` declaration terminates the chain below itself —
  nothing downstream is required.

The chain shape is a workspace choice. OFT itself does not prescribe any
particular inter-layer relationship; it only enforces whatever coverage
each item declares.

### Forwarding — constraint (forbidden)

OFT's forwarding syntax (see [Forwarding](#forwarding)) `SHALL NOT` be used
in this workspace. When a layer has nothing to say for a particular item,
the item `SHALL` skip that layer entirely (by omitting the type from its
`Needs:`) rather than creating a hollow passthrough.

Reason: a forward is a load-bearing structural element that reads like an
item but contains no content. Skipping the layer is more honest — the
coverage chain shows exactly where decisions are made.

### Revision policy — extension

The revision number in an ID is a semantic version for the item's meaning.

**Increment** the revision when the semantic content changes — when the
requirement means something different than it did before. This voids all
downstream `Covers:` links that referenced the previous revision, forcing
downstream documents to explicitly acknowledge and respond to the change.

**Do not increment** for typo fixes, rephrasing that does not change
meaning, or formatting changes.

When you increment a revision, update all `Covers:` references in
downstream documents to the new revision. If a downstream item's response
to the change is "no change needed," update the `Covers:` link and note
this in the downstream item's `Comment:` field.

Reason: OFT's revision-match check is mechanical — it flags all downstream
links when an upstream revision bumps. This policy tells authors when that
flag is the right signal (semantic change) versus when it would be
unnecessary churn (typos).

### Verification coverage — extension

Every requirement `SHALL` tie off with a verification mechanism at its
layer.

| Layer | Verification comes from |
|---|---|
| `feat` | `Needs:` pointing at a covering downstream type. |
| `req` | `Needs:` pointing at a covering downstream type. |
| `dsn` | Any combination of `Needs:`, `Interface:`, or `AgentReview:` — at least one `SHALL` be present. |

A requirement with no verification mechanism is a commitment that nothing
ever checks. This rule applies at every layer; it is not restricted to
chain leaves.

`Interface:` and `AgentReview:` are workspace extension keywords defined
below. `dsn` items additionally carry a `Dimension:` classification
field; its rules are in the
[`Dimension:`](#extension-keyword-dimension) subsection.

### Extension keyword: `Interface:`

`Interface:` is a workspace-defined keyword, not part of OFT. It is valid
only on `dsn` items.

A `dsn` that commits to a public surface `SHALL` declare the committed
signatures in `Interface:` fields so the commitment can be machine-validated
against the code.

#### Format

Each `Interface:` entry is a single line declaring one signature. A design
item `MAY` declare multiple `Interface:` entries to commit to multiple
related signatures (e.g., a class and its public methods).

    Interface: parser.parse_session(path: pathlib.Path) -> parser.Session
    Interface: parser.SessionParser.__init__(self, config: parser.ParserConfig) -> None
    Interface: parser.SessionParser.parse(self, path: pathlib.Path) -> parser.Session

Each signature includes the fully-qualified symbol path
(`module.ClassName.method`), the parameter list with annotations, and the
return annotation. Parameter kinds use standard Python syntax (`/` for
positional-only, `*` for keyword-only, `*args`, `**kwargs`). Instance
methods include `self`; classmethods include `cls`; staticmethods omit
both.

#### Annotation convention

Interface annotations follow a single modern idiom, matching what ruff's
`UP` rules produce in the code.

| Annotation form | Modern (use) | Legacy (do not use) |
|---|---|---|
| Non-stdlib classes | `pathlib.Path`, `myapp.session.Session` | bare `Path`, bare `Session` |
| Built-in generics | `list[int]`, `dict[str, Event]` | `typing.List[int]`, `typing.Dict[str, Event]` |
| Unions with None | `Event \| None` | `Optional[Event]`, `Union[Event, None]` |
| Primitives | `int`, `str`, `float`, `bool`, `bytes` | — |

Complex types `SHALL` be named through a single import and referenced by
name rather than inlined as sprawling generic expressions.

#### Coexistence with prose

A `dsn` `MAY` contain both prose and `Interface:` entries. Prose captures
non-API decisions — schema, algorithm, error semantics — and flows through
OFT's tracing into reports. `Interface:` entries are the machine-checked
part: validators compare them against the code.

### Extension keyword: `AgentReview:`

`AgentReview:` is a workspace-defined keyword, not part of OFT. It is
valid only on `dsn` items.

A `dsn` that commits to a non-testable behavior or a review-only property
`SHALL` declare what must be checked in an `AgentReview:` field.

#### Format

Each `AgentReview:` entry is a single declaration describing one thing to
check. A `dsn` `MAY` declare multiple entries for multiple separate
checks.

    AgentReview: The agent's system prompt at src/prompts/agent.md should
                 contain a directive discouraging filler or polite
                 conversation.

File paths named inside the prose let a review agent locate what to
compare against.

#### When to use

`AgentReview:` is the mechanism for commitments that cannot be
deterministically tested. Typical cases:

- Behavioral requirements for LLM agents (e.g., "`SHALL NOT` attempt
  polite conversation for no reason").
- Output-format requirements where a prompt-inclusion test would
  degenerate into test-theater.
- Cross-cutting conventions too contextual for a unit assertion.

If a commitment can be tested deterministically, prefer `Needs: utest` or
`Needs: itest` — tests are faster and more reliable than a review skill.

#### Coexistence

A `dsn` `MAY` combine `AgentReview:` with `Needs:` and `Interface:`. One
design decision often commits several aspects simultaneously; one `dsn`
captures them all, and each field names how its respective aspect is
verified.

### Extension keyword: `Dimension:`

`Dimension:` is a workspace-defined keyword, not part of OFT. It is
valid only on `dsn` items.

Every `dsn` `SHALL` carry a `Dimension:` field naming one or more of
the design dimensions defined in
[design-layer.md](design-layer.md#decision-dimensions).

#### Format

The value is a comma-separated list of dimension names on a single line:

    Dimension: Data
    Dimension: API Shape, Algorithms

Dimension names are spelled exactly as above — two-word names
(`API Shape`) use a single space; case is preserved. A name outside the
fixed set is invalid. Empty lists and repeated names within one field
are invalid.

#### Many allowed, one typical

Most items name a single dimension. A list expresses decisions that
genuinely commit across dimensions — e.g., a schema decision that also
pins a return type commits both `Data` and `API Shape`. Items that span
three or more dimensions are candidates for splitting; one commitment
typically has one primary axis.

#### Coexistence

A `dsn` `MAY` combine `Dimension:` with `Needs:`, `Interface:`, and
`AgentReview:`. `Dimension:` classifies the commitment; the verification
fields name how it is checked.

### Fenced code blocks — constraint (forbidden)

Spec files `SHALL NOT` contain fenced code blocks (triple backticks or
`~~~`). Use indented code blocks (4-space indent) instead.

Reason: the OFT reference parser historically had edge cases around
fenced code blocks that silently affected which specification items were
picked up. Indented code blocks render identically and avoid the class of
bug entirely.

### Naming convention — extension

Item names (the middle segment of `type~name~revision`) `SHOULD` use dots
to express readable hierarchy: `auth.login-validation`,
`parser.segment.timestamp`. OFT permits dots in names; this workspace uses
them as the convention for grouping related items.

Consecutive dots are prohibited by OFT itself; no additional workspace
rule is needed.

### File organization — extension

All spec files `SHALL` live in a `/specs/` directory at the repository
root, versioned alongside the code. The
[repo-documentation standard](~/workspace/dev-playbook/standards/repo-documentation.md)
defines which files exist and their purpose.

#### Splitting large specs

Each spec file starts as a single file. When it grows large enough to
impair an agent's ability to work with it in a single context load, it
`SHOULD` be split into a folder of files organized by feature or
capability area.

**The decision to split `SHALL` be made by the human, not the agent.**

When split:

- `functional_requirements.md` → `functional_requirements/` folder.
- `design.md` → `design/` folder.
- Each folder `SHALL` contain an `index.md` — a structured Markdown table
  listing every file with a one-line scope description, so an agent can
  decide which files to load without reading all of them.

OFT natively supports hierarchical organization (see
[File discovery](#file-discovery)); file names and folder structure do
not affect tracing.

## Reference

- OpenFastTrace repository and user guide:
  https://github.com/itsallcode/openfasttrace
- User guide (format specification):
  https://github.com/itsallcode/openfasttrace/blob/main/doc/user_guide.md
