# Spec File Format — Integration Walkthrough

This file is the integration walkthrough: concrete examples of how the
three standards ([rfc2119.md](rfc2119.md), [ears.md](ears.md),
[oft.md](oft.md)) combine in a single spec file. Design-phase semantics
(what a commitment is; the decision dimensions) are covered in
[design-layer.md](design-layer.md).

## Anatomy of a spec item

A single `dsn` item using every OFT keyword and every workspace
extension keyword. Most items use a subset — the table below names
which pieces are required and which are optional, and which apply only
to `dsn` items.

    ### Session Parser
    `dsn~parser.session~1`
    Status: approved
    Dimension: API Shape

    Description:
    When the parser is invoked, it `SHALL` return a `Session` populated
    with every event from the log file. While the file is malformed,
    the parser `SHALL` raise `ParseError` rather than return a partial
    session.

    Rationale:
    Separating success and failure channels lets callers treat a return
    value as unambiguous — a `Session` is complete, or nothing is.

    Comment:
    The `ParserConfig` type lives in dsn~parser.config~1.

    Covers:
    - req~parse.session-discovery~1

    Depends:
    - dsn~parser.config~1

    Tags: parser, io

    Needs: utest
    Interface: parser.parse_session(path: pathlib.Path) -> parser.Session
    AgentReview: Log output follows the human-readable format specified in
                 docs/log-format.md.

Every piece, by source and applicability:

| Piece | Source | Presence |
|---|---|---|
| Heading `### Session Parser` | OFT item structure — any Markdown heading names the item. | Optional — an item `MAY` begin with just its ID line. Conventional for every item to carry a heading. |
| ID `` `dsn~parser.session~1` `` | [OFT ID format](oft.md#specification-item-id); `dsn` is in the [workspace artifact subset](oft.md#artifact-types--subset); the dotted name follows the [naming convention](oft.md#naming-convention--extension). | Required on every item. |
| `Status:` | [OFT keyword](oft.md#keyword-fields). | Required (workspace). Value is one of `draft` / `proposed` / `approved`. |
| `Dimension:` | Workspace [extension keyword](oft.md#extension-keyword-dimension). Classifies the commitment; enables per-dimension projection. | Required on `dsn` items; invalid on other types. Comma-separated list of one or more dimensions. |
| `Description:` | [OFT keyword](oft.md#keyword-fields). | Optional. When absent, non-keyword prose after the heading is the description automatically. `MUST` precede `Rationale:` and `Comment:`. |
| Description prose — `When the parser is invoked, … SHALL return …` / `While the file is malformed, … SHALL raise …` | Content, not a keyword. Sentences are graded with [RFC 2119](rfc2119.md) obligation verbs ([backticked per the workspace rule](rfc2119.md#backticking--constraint)) and structured per [EARS](ears.md) templates (here, Event-driven and State-driven). | Required content of the item body. Style is conventional: `req` items typically use EARS sentences end-to-end; `dsn` items are more often descriptive prose with obligations for error semantics and behavior. |
| `Rationale:` | [OFT keyword](oft.md#keyword-fields). | Optional; at most one per item by convention. |
| `Comment:` | [OFT keyword](oft.md#keyword-fields). | Optional; at most one per item by convention. |
| `Covers:` | [OFT linking model](oft.md#linking-model). Bullet list of upstream IDs. | Required when the item covers upstream items; root `feat` items omit it. |
| `Depends:` | [OFT keyword](oft.md#keyword-fields). Ordering hint; does not affect coverage. | Optional. |
| `Tags:` | [OFT keyword](oft.md#keyword-fields). Comma-separated labels. | Optional. |
| `Needs:` | [OFT linking model](oft.md#linking-model); chain shape per [workspace coverage chain](oft.md#coverage-chain--constraint). | Optional; absence terminates the chain at this item. |
| `Interface:` | Workspace [extension keyword](oft.md#extension-keyword-interface). Signature is machine-validated against the code. | Optional; `dsn`-only. |
| `AgentReview:` | Workspace [extension keyword](oft.md#extension-keyword-agentreview). Verified by the review skill on invocation. | Optional; `dsn`-only. |

Every `dsn` additionally `SHALL` carry at least one of `Needs:` /
`Interface:` / `AgentReview:` — the
[verification coverage rule](oft.md#verification-coverage--extension).

## What a valid file looks like as a whole

A spec file `SHALL`:

- Live under the project's `specs/` directory
  ([file organization](oft.md#file-organization--extension)).
- Use only [workspace artifact types](oft.md#artifact-types--subset)
  (`feat`, `req`, `dsn`, `utest`, `itest`).
- Use no [fenced code blocks](oft.md#fenced-code-blocks--constraint-forbidden).
- Use no [OFT forwarding syntax](oft.md#forwarding--constraint-forbidden).
- For `dsn` items, carry a
  [`Dimension:` field](oft.md#extension-keyword-dimension) naming
  one or more design dimensions. Section headers within a `dsn` file
  are free-form — authors may group by dimension, feature, subsystem,
  or any other axis.

Prose that is not part of any item is ignored by OFT and `MAY` be used
freely for context, headings, or notes.

## Illustrative examples in prose

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

## When things go wrong

Two classes of problems surface at different points:

- **Structural errors** (malformed ID, unknown keyword, missing required
  keyword, obligation verb not backticked): caught by workspace lint
  tooling against this format.
- **Coverage errors** (uncovered `Needs:`, unresolved `Covers:`, revision
  mismatch, orphan): caught by OFT's trace check.

Tool behavior is documented separately from the format; nothing about
how the tools enforce these rules changes what the rules themselves say.
