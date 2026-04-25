# Spec Standard

## 1. Inspiration

This document defines how specification items are written in this workspace.
Three external works inspire the form:

- **BCP 14** (RFC 2119 + RFC 8174) — the obligation vocabulary
  (`SHALL` / `SHOULD` / `MAY`).
- **EARS** (Mavin et al.) — sentence templates that structure a
  requirement around its triggering condition.
- **OpenFastTrace Requirement-Enhanced Markdown** — the Markdown item
  format with stable IDs and `Needs:` / `Covers:` links.

The rules below are the workspace standard stated directly. Familiarity
with the sources is helpful but not required.

## 2. Anatomy of a spec item

A single `dsn` item using every keyword defined by this standard. Most
real items use a subset — the table below names what applies where.

    ### Topic Classifier
    `dsn~classifier.topic~1`

    Description:
    When an inbound message is submitted, the classifier `SHALL` return
    a `TopicLabel` drawn from the fixed taxonomy. When the message
    falls outside the taxonomy, the classifier `SHALL` return
    `TopicLabel.OTHER` rather than its best guess.

    Rationale:
    A closed-taxonomy return type lets downstream routing be
    exhaustive; free-form guesses break the routing contract.

    Comment:
    The `TopicLabel` enum lives in dsn~classifier.taxonomy~1.

    Covers:
    - req~classifier.label-fidelity~1

    Depends:
    - dsn~classifier.taxonomy~1

    Tags: classifier, llm

    Needs:
    - utest

    Interface: classifier.classify(message: str) -> classifier.TopicLabel
    AgentReview: The system prompt at src/prompts/classifier.md
                 instructs the model to return `OTHER` when the message
                 is outside the taxonomy, rather than picking its
                 closest guess.

| Field | Scope | Required |
|---|---|---|
| Markdown heading | any item | **required** |
| ID `` `type~name~rev` `` | any item | **required** |
| `Description:` | any item | **required** |
| `Rationale:` | any item | optional |
| `Comment:` | any item | optional |
| `Covers:` | any item | required unless the item is a root |
| `Depends:` | any item | optional |
| `Tags:` | any item | optional |
| `Needs:` | any item | optional mechanically — required for chain termination (§5.4) |
| `Interface:` | `dsn` only | optional |
| `AgentReview:` | `feat`, `req`, `dsn` | optional |

Each piece has a dedicated section below: §3 IDs, §4 artifact types,
§5 how items chain, §6 keyword formats, §7 prose inside the description.

## 3. IDs

### 3.1 Shape

Every item is identified by a tilde-separated triple, wrapped in
backticks on the ID line:

    `type~name~revision`

### 3.2 `name`

Start with a letter. Subsequent characters `MAY` be letters, digits,
hyphens (`-`), underscores (`_`), or dots (`.`). No whitespace. No
consecutive dots.

Dots are a convention for readable hierarchy — `auth.login.validation`
reads as three grouping levels. They carry no structural meaning.

### 3.3 `revision`

A non-negative integer starting at `0`. Incremented when the item's
meaning changes in a way downstream items need to re-evaluate.

- **Bump** on semantic change: the requirement now means something
  different than it did before.
- **Do not bump** on cosmetic edits: typos, rewording that does not
  alter meaning, formatting.

A revision bump voids every downstream `Covers:` link pinned to the
previous revision. Each downstream author `SHALL` re-evaluate and
update the `Covers:` line to the new revision (noting "no change
needed" in `Comment:` if that is the outcome).

## 4. Artifact types

The workspace uses five types:

| Type | Purpose |
|---|---|
| `feat` | High-level feature or capability. |
| `req` | User or functional requirement. |
| `dsn` | Design commitment. |
| `utest` | Unit test. |
| `itest` | Integration test. |

No others are defined. The list may expand in the future; additions
come through this document, not per-project.

`feat`, `req`, and `dsn` are written as Markdown items in spec files.
`utest` and `itest` are realized by pytest tests that carry an
`@pytest.mark.req("req~...")` marker linking back to the item they
cover — they are not themselves Markdown items. Spec-item keywords
(below) apply to the three Markdown types.

## 5. Coverage chain

### 5.1 Shape

    feat  →  req  →  dsn  →  utest / itest

Each arrow is realized by a `Needs:` / `Covers:` pair. Keyword formats
live in §6.

### 5.2 Chain mechanism

The chain is a directed graph built from two declarations per item:
`Needs:` (downstream artifact types that must cover this item) and
`Covers:` (upstream IDs this item satisfies). The graph is well-formed
when:

- An item without a `Covers:` line is a **root** — it sits at the top
  of its chain. Every non-root item `SHALL` declare `Covers:`.
- For every type named in an upstream item's `Needs:`, at least one
  downstream item of that type `SHALL` declare `Covers:` pointing at
  the upstream.
- An item with no `Needs:` declaration terminates the chain below
  itself.

That is the full system rule for well-formedness. It says nothing about
which types go where — it admits any arrangement the author writes.

### 5.3 Typical arrangement

The five types usually chain as `feat → req → dsn → utest/itest`, with
`feat` at the root. Authors may deviate when the situation genuinely
calls for it — a `req` with neither a design decision nor an ownership
assignment may declare tests directly, skipping `dsn`. Conventional
usage is a writing norm, not a system rule.

### 5.4 Verification termination

A chain terminates in verification when its terminal items are one of:

- a `utest` (pytest test covering a `req` or `dsn`),
- an `itest` (pytest integration test covering a `req` or `dsn`), or
- a `feat`, `req`, or `dsn` carrying `AgentReview:`.

A chain `SHOULD` terminate in verification. A commitment that nothing
ever checks is a quality gap worth flagging, but partial chains — e.g.,
a `feat` written before its downstream items, or an aspirational `feat`
that never grounds cleanly — are a normal intermediate state. Whether
to ground each chain is a project-level judgment, not a grammar
requirement. Tooling `SHALL` clearly report chains that do not
terminate in verification so authors can decide what to do about them.

`feat` and `req` typically delegate verification downstream by
declaring `Needs:`, but `MAY` instead carry `AgentReview:` directly
when the commitment is best checked by a review (e.g., an aspirational
`feat` evaluated through observation rather than tests). `dsn`
verifies via `Needs:` or `AgentReview:`.

`Interface:` does **not** count as verification. It is a design-phase
structural commitment (§6.8) — deterministically validated against the
Python code, but it pins *structure*, not *behavior*. A requirement
ties off only when its behavior is checked by a test or an agent
review.

## 6. Keyword reference

Each keyword is a case-sensitive label followed by a colon at the start
of a line. Content may begin on the same line or on the line following,
as shown in each subsection.

### 6.1 `Description:`

Required. An explicit marker that opens the item body. Prose rules
(obligation verbs, sentence templates) are in §7.

    Description:
    When the user submits credentials, the system `SHALL` verify them
    against the credential store.

### 6.2 `Rationale:`

Optional. Why the requirement exists. At most one per item.

### 6.3 `Comment:`

Optional. Caveats, implementation notes, or anything that fits neither
description nor rationale. At most one per item.

### 6.4 `Covers:`

Bullet list. Each entry names a full upstream ID *including revision*:

    Covers:
    - feat~user-auth~0
    - feat~session~1

Required except on root items (see §5.2).

### 6.5 `Depends:`

Bullet list. Ordering hints between items; carries no coverage effect.
Optional.

### 6.6 `Needs:`

Bullet list, even for a single entry. Names the downstream artifact
types required to cover this item:

    Needs:
    - dsn

    Needs:
    - utest
    - itest

Chain semantics are in §5.

### 6.7 `Tags:`

Comma-separated labels on a single line. Optional. Used by tooling for
filtering.

    Tags: classifier, llm

### 6.8 `Interface:`

Optional. Valid only on `dsn` items. A design-phase structural
commitment: the human pins code shape so downstream agents implement
against a fixed target.

Each `Interface:` entry is a single line declaring one signature. A
`dsn` `MAY` declare multiple entries.

    Interface: parser.parse_session(path: pathlib.Path) -> parser.Session
    Interface: parser.SessionParser.__init__(self, config: parser.ParserConfig) -> None
    Interface: parser.SessionParser.parse(self, path: pathlib.Path) -> parser.Session

Each signature contains the fully-qualified symbol path
(`module.ClassName.method`), the parameter list with annotations, and
the return annotation. Parameter kinds use standard Python syntax
(`/` for positional-only, `*` for keyword-only, `*args`, `**kwargs`).
Instance methods include `self`; classmethods include `cls`;
staticmethods omit both.

Annotations follow a single modern idiom, matching what ruff's `UP`
rules produce:

| Annotation form | Use | Do not use |
|---|---|---|
| Non-stdlib classes | `pathlib.Path`, `myapp.session.Session` | bare `Path`, bare `Session` |
| Built-in generics | `list[int]`, `dict[str, Event]` | `typing.List[int]`, `typing.Dict[str, Event]` |
| Unions with `None` | `Event \| None` | `Optional[Event]`, `Union[Event, None]` |
| Primitives | `int`, `str`, `float`, `bool`, `bytes` | — |

Complex types `SHALL` be named through a single import and referenced
by name rather than inlined as sprawling generic expressions.

`Interface:` is deterministically validated by parsing the spec and
matching against the Python code. **It is not a chain terminator** —
verification of behavior still comes from a test or `AgentReview:`
(§5.4).

### 6.9 `AgentReview:`

Optional. Valid on any Markdown spec item — `feat`, `req`, or `dsn`.
Prose describing what a review agent must check. The non-test arm of
verification (§5.4).

Each `AgentReview:` entry is a single declaration describing one thing
to check. An item `MAY` declare multiple entries.

    AgentReview: The agent's system prompt at src/prompts/agent.md
                 contains a directive discouraging filler or polite
                 conversation.

File paths named in the prose let the review agent locate what to
compare against.

Use `AgentReview:` when a commitment cannot be deterministically
tested:

- Behavioral requirements for LLM agents (e.g., "`SHALL NOT` attempt
  polite conversation for no reason").
- Output-format requirements where a prompt-inclusion test would
  degenerate into test-theater.
- Cross-cutting conventions too contextual for a unit assertion.
- Aspirational `feat` or `req` items that are evaluated through
  observation rather than tests.

If a commitment can be tested deterministically, prefer
`Needs: utest` or `Needs: itest` — tests are faster and more reliable
than a review skill.

### Keyword ordering

- `Description:` before `Rationale:` before `Comment:`.
- Relationship lists (`Covers:`, `Depends:`, `Needs:`, `Tags:`) and
  extension keywords (`Interface:`, `AgentReview:`) appear after the
  body.

## 7. Prose within a spec item

### 7.1 Obligation vocabulary

Five verbs, defined:

- `SHALL` / `SHALL NOT` — absolute requirement / prohibition.
- `SHOULD` / `SHOULD NOT` — strong preference; deviation is allowed
  only with a justified reason.
- `MAY` — truly optional.

Rules:

- Uppercase only; lowercase occurrences are ordinary English and carry
  no normative force.
- Always wrapped in backticks wherever they appear (in `Description:`,
  in prose, in section introductions).
- One obligation level per item. An item `SHALL NOT` mix `SHALL` with
  `SHOULD` — split into separate items, each with its own ID. `SHALL`
  and `SHALL NOT` within one item are fine — they are the same level.

### 7.2 Sentence templates

Five patterns structure the `Description:` body. Keyword markers are
written in sentence case in the actual requirement.

| Pattern | Template | Use when |
|---|---|---|
| Ubiquitous | `The <system> SHALL <response>.` | The requirement always holds. |
| Event-driven | `When <trigger>, the <system> SHALL <response>.` | A discrete event fires the requirement. |
| State-driven | `While <state>, the <system> SHALL <response>.` | The requirement holds during a continuous state. `During` is a sanctioned alternative. |
| Optional feature | `Where <feature-is-included>, the <system> SHALL <response>.` | The requirement applies only in configurations where a feature is present. |
| Unwanted behavior | `If <optional preconditions> <trigger>, then the <system> SHALL <response>.` | Response to an error or undesired condition. |

### 7.3 Complex requirements

A single behavior may combine more than one trigger, state, or
condition. Chain pattern-introducer clauses before the subject-verb
body:

    While <state>, when <trigger>, the <system> SHALL <response>.

## 8. File organization

- All spec files live under `/specs/` at the repository root, versioned
  alongside the code they describe.
- A simple spec is a single file (`design.md`,
  `functional_requirements.md`). A complex spec is a folder of files
  (`design/`, `functional_requirements/`) organized by feature or
  capability area. **The choice between single file and folder is the
  human's, not the agent's.**
- A folder-form spec `SHALL` contain an `index.md` — a structured
  table listing every file with a one-line scope description, so an
  agent can decide which files to load without reading all of them.
- Spec files `SHALL NOT` use fenced code blocks (triple-backtick or
  `~~~`). Use 4-space indented code blocks.

## 9. Illustrative examples (convention)

A section that introduces non-trivial domain vocabulary `SHOULD`
include a short illustrative example before the formal requirements.
The example grounds the vocabulary in concrete terms so that
requirements can reference it without re-explaining.

- One scenario per section. If a second example is needed, the
  section's vocabulary may be too overloaded and `SHOULD` be split.
- The example `SHALL` appear after the section's prose introduction
  and before the formal spec items.
- Examples `SHALL` use indented code blocks (4-space indent) or a
  structured form that mirrors what the system actually produces or
  consumes.

## 10. References

- Bradner, S. *Key words for use in RFCs to Indicate Requirement
  Levels.* RFC 2119 / BCP 14. IETF, March 1997.
  https://www.rfc-editor.org/rfc/rfc2119
- Leiba, B. *Ambiguity of Uppercase vs Lowercase in RFC 2119 Key
  Words.* RFC 8174. IETF, May 2017.
  https://www.rfc-editor.org/rfc/rfc8174
- Mavin, A., Wilkinson, P., Harwood, A., and Novak, M. *Easy Approach
  to Requirements Syntax (EARS).* 17th IEEE International Requirements
  Engineering Conference (RE'09), 2009. DOI: 10.1109/RE.2009.9
- OpenFastTrace user guide.
  https://github.com/itsallcode/openfasttrace
