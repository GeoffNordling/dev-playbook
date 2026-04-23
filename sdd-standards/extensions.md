# Workspace Extensions and Constraints

This file is the single home for every choice this workspace makes about how
to use the external standards ([rfc2119.md](rfc2119.md),
[ears.md](ears.md), [oft-format.md](oft-format.md)). It covers three kinds
of decisions:

| Kind | Meaning |
|---|---|
| **Subset** | We adopt only part of the standard's optional vocabulary or features. |
| **Extension** | We add capability the standard does not define (e.g., new keywords). |
| **Constraint** | We forbid or tighten something the standard allows, with a reason given. |

The external standards describe what is *allowed*. This file describes what
is *required, added, or forbidden* when writing specs in this workspace.

Whenever a rule in this file uses an obligation verb, the verb is to be
interpreted per [rfc2119.md](rfc2119.md).

## Obligation vocabulary — subset + constraint

The full RFC 2119 vocabulary includes several synonyms. In this workspace we
use the `SHALL` family of synonyms and omit the `MUST` family, to give a
single consistent voice across specs.

| Verb | Meaning | Agent treatment | Mandatory | RFC 2119 synonyms not used here |
|---|---|---|---|---|
| `SHALL` | Absolute requirement | Blocking acceptance criterion | Yes | `MUST`, `REQUIRED` |
| `SHALL NOT` | Absolute prohibition | Blocking acceptance criterion | Yes | `MUST NOT` |
| `SHOULD` | Strong preference; deviation requires justification | Quality target | No | `RECOMMENDED` |
| `SHOULD NOT` | Strong preference against | Quality target | No | `NOT RECOMMENDED` |
| `MAY` | Truly optional | Nice to have | No | `OPTIONAL` |

### Backticking

All uppercase obligation verbs `SHALL` be wrapped in backticks wherever they
appear — in requirements, prose, and section introductions. This is a
universal formatting rule with no exceptions.

Reason: RFC 8174 clarifies that only uppercase occurrences carry normative
force. Backticking makes each load-bearing verb visually distinct from
ordinary prose use, and the pattern is trivially grep-able.

### One obligation level per item

A requirement `SHALL NOT` mix obligation levels (absolute, preference,
optional). A requirement that contains both `SHALL` and `SHOULD` is mixing
an absolute obligation with a preference, and the `SHOULD` behavior `SHALL`
be split into its own spec item with its own ID.

Using both `SHALL` and `SHALL NOT` within a single requirement is
permitted — they are the same obligation level.

Reason: downstream artifacts (tests, review agents, traceability reports)
treat each level differently. Items that mix levels cannot be unambiguously
graded as blocking or preference.

## Sentence templates — adoption

Requirements `SHALL` be written using the EARS sentence templates defined in
[ears.md](ears.md). The modal-verb slot is filled with an obligation verb
from the vocabulary above.

No subsetting: all five EARS patterns (Ubiquitous, Event-driven,
State-driven, Optional feature, Unwanted behavior) are in use. Complex
multi-clause requirements `SHOULD` be decomposed into simpler items when
practical.

## OFT artifact types — subset

OFT defines ten canonical artifact types (see
[oft-format.md](oft-format.md#artifact-types)). This workspace uses five:

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

## Coverage chain — constraint

The workspace chain is:

    feat  →  req  →  dsn  →  utest / itest

Each arrow is an OFT coverage relationship: the downstream layer covers the
upstream layer through `Needs:` / `Covers:` links.

Required structure:

- `feat` `SHALL` be the root. Every project `SHALL` begin the chain with
  `feat` items.
- `req` items `SHALL` cover `feat`.
- Most `req` items `SHALL` declare `Needs: dsn` to carry the chain forward
  into the design layer.
- `dsn` items `SHALL` cover `req` and are expected for most `req` items. A
  `req` `MAY` skip `dsn` only when it needs neither a design decision nor an
  ownership assignment; in that case the `req` `SHALL` declare `Needs:
  utest` and/or `Needs: itest` directly.
- `utest` and `itest` `SHALL` cover the item directly upstream. Either a
  `req` or a `dsn` `MAY` declare `Needs: utest`, `Needs: itest`, or both —
  whichever is appropriate to verify the commitment.
- An item with no `Needs:` declaration terminates the chain below itself —
  nothing downstream is required.

The chain shape is a workspace choice. OFT itself does not prescribe any
particular inter-layer relationship; it only enforces whatever coverage each
item declares.

## Forwarding — constraint (forbidden)

OFT's forwarding syntax (see
[oft-format.md](oft-format.md#forwarding)) `SHALL NOT` be used in this
workspace. When a layer has nothing to say for a particular item, the item
`SHALL` skip that layer entirely (by omitting the type from its `Needs:`)
rather than creating a hollow passthrough.

Reason: a forward is a load-bearing structural element that reads like an
item but contains no content. Skipping the layer is more honest — the
coverage chain shows exactly where decisions are made.

## Revision policy — extension

The revision number in an ID is a semantic version for the item's meaning.

**Increment** the revision when the semantic content changes — when the
requirement means something different than it did before. This immediately
breaks all downstream `Covers:` links that referenced the previous revision,
forcing downstream documents to explicitly acknowledge and respond to the
change.

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

## Verification coverage — extension

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
below.

## Extension keyword: `Interface:`

`Interface:` is a workspace-defined keyword, not part of OFT. It is valid
only on `dsn` items.

A `dsn` that commits to a public surface `SHALL` declare the committed
signatures in `Interface:` fields so the commitment can be machine-validated
against the code.

### Format

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
methods include `self`; classmethods include `cls`; staticmethods omit both.

### Annotation convention

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

### Coexistence with prose

A `dsn` `MAY` contain both prose and `Interface:` entries. Prose captures
non-API decisions — schema, algorithm, error semantics — and flows through
OFT's tracing into reports. `Interface:` entries are the machine-checked
part: validators compare them against the code.

## Extension keyword: `AgentReview:`

`AgentReview:` is a workspace-defined keyword, not part of OFT. It is valid
only on `dsn` items.

A `dsn` that commits to a non-testable behavior or a review-only property
`SHALL` declare what must be checked in an `AgentReview:` field.

### Format

Each `AgentReview:` entry is a single declaration describing one thing to
check. A `dsn` `MAY` declare multiple entries for multiple separate checks.

    AgentReview: The agent's system prompt at src/prompts/agent.md should
                 contain a directive discouraging filler or polite
                 conversation.

File paths named inside the prose let a review agent locate what to compare
against.

### When to use

`AgentReview:` is the mechanism for commitments that cannot be
deterministically tested. Typical cases:

- Behavioral requirements for LLM agents (e.g., "`SHALL NOT` attempt polite
  conversation for no reason").
- Output-format requirements where a prompt-inclusion test would degenerate
  into test-theater.
- Cross-cutting conventions too contextual for a unit assertion.

If a commitment can be tested deterministically, prefer `Needs: utest` or
`Needs: itest` — tests are faster and more reliable than a review skill.

### Coexistence

A `dsn` `MAY` combine `AgentReview:` with `Needs:` and `Interface:`. One
design decision often commits several aspects simultaneously; one `dsn`
captures them all, and each field names how its respective aspect is
verified.

## Dimension section organization — extension

Every `dsn` spec file `SHALL` organize its items under four Markdown section
headers, one per dimension, in this order:

    ## Data
    ## API Shape
    ## Algorithms
    ## Composition

Every `dsn` item `SHALL` appear under exactly one of these four headers.
Items that float above or between section headers are errors.

A file where a dimension has no commitments `SHALL` still include the
header with an empty section. The empty header is the explicit signal
"considered, nothing to commit here." A missing header is not equivalent to
an empty section; the header makes the absence deliberate.

See [design-layer.md](design-layer.md) for what each dimension means
semantically.

Reason: forcing classification at the moment of writing prevents post-hoc
inference of dimension from prose and gives downstream tools a deterministic
anchor for per-dimension projection.

## Fenced code blocks — constraint (forbidden)

Spec files `SHALL NOT` contain fenced code blocks (triple backticks or
`~~~`). Use indented code blocks (4-space indent) instead.

Reason: the OFT reference parser silently ignores specification items that
appear after a fenced code block in the same file. The failure mode is
invisible — affected items simply do not appear in the trace. Indented code
blocks render identically and are parsed correctly.

This is a workaround for the current reference implementation. It is
documented here, alongside our other choices, rather than in
[oft-format.md](oft-format.md), because it describes our response to a
parser behavior, not a property of the format itself.

## Illustrative examples — extension

A spec section that introduces non-trivial domain vocabulary `SHOULD`
include a short illustrative example before the formal requirements. The
example grounds the vocabulary in concrete terms so that requirements can
reference it without re-explaining.

- One scenario per section. If a second example is needed, the section's
  vocabulary may be too overloaded and `SHOULD` be split.
- The example `SHALL` appear after the section's prose introduction and
  before the formal spec items.
- Examples `SHALL` use indented code blocks (4-space indent) or structured
  format that mirrors what the system actually produces or consumes.

## Naming convention — extension

Item names (the middle segment of `type~name~revision`) `SHOULD` use dots
to express readable hierarchy: `auth.login-validation`,
`parser.segment.timestamp`. OFT permits dots in names; this workspace uses
them as the convention for grouping related items.

Consecutive dots are prohibited by OFT itself; no additional workspace rule
is needed.

## File organization — extension

All spec files `SHALL` live in a `/specs/` directory at the repository
root, versioned alongside the code. The
[repo-documentation standard](~/workspace/dev-playbook/standards/repo-documentation.md)
defines which files exist and their purpose.

### Splitting large specs

Each spec file starts as a single file. When it grows large enough to
impair an agent's ability to work with it in a single context load, it
`SHOULD` be split into a folder of files organized by feature or capability
area.

**The decision to split `SHALL` be made by the human, not the agent.**

When split:

- `functional_requirements.md` → `functional_requirements/` folder.
- `design.md` → `design/` folder.
- Each folder `SHALL` contain an `index.md` — a structured Markdown table
  listing every file with a one-line scope description, so an agent can
  decide which files to load without reading all of them.

OFT natively supports hierarchical organization (see
[oft-format.md](oft-format.md#file-discovery)); file names and folder
structure do not affect tracing.
