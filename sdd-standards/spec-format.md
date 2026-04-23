# Spec File Format — Integration Walkthrough

Specs in this workspace stack three external standards. Each standards
file restates its external standard and then, in a trailing Extensions
section, documents the workspace subset, constraints, and additions for
that standard. This file shows how the pieces combine in a single spec
file.

## The stack

| Concern | Standard + workspace extensions |
|---|---|
| Obligation strength | [rfc2119.md](rfc2119.md) |
| Sentence structure | [ears.md](ears.md) |
| Item identity, linking, traceability, workspace keywords (`Interface:`, `AgentReview:`) | [oft-format.md](oft-format.md) |

A valid spec file conforms to all three. A spec-phase agent grades obligations with RFC 2119 vocabulary, writes prose
following EARS, and embeds
the prose in OFT specification items — each subject to the workspace
Extensions section of its respective standards file.

Design-phase semantics (what a commitment is; the four decision
dimensions) are covered in [design-layer.md](design-layer.md).

## Reading order

A new author or agent encountering the workspace for the first time
`SHOULD` read the files in this order:

1. [rfc2119.md](rfc2119.md) — obligation vocabulary and workspace subset.
2. [ears.md](ears.md) — sentence templates.
3. [oft-format.md](oft-format.md) — item identity, keywords, linking,
   coverage, plus workspace keywords and constraints.
4. [design-layer.md](design-layer.md) — only when working on `dsn` items.

## Anatomy of a complete spec item

The following is a complete, conformant spec item. Annotations below point
to the standard that governs each piece.

    ### Login Credential Validation
    `req~auth.login-validation~1`
    Status: approved

    When the user submits credentials, the system `SHALL` verify the
    provided username and password against the credential store before
    granting session access.

    Rationale:
    Unauthenticated access to any session-bearing endpoint is a critical
    security vulnerability.

    Comment:
    The credential store interface is defined in dsn~credential-store~1.

    Covers:
    - feat~user-authentication~1

    Needs: dsn, utest

Where each piece comes from:

| Piece | Source |
|---|---|
| The Markdown heading `### Login Credential Validation` | OFT item structure; any standard Markdown heading names the item. |
| The ID `` `req~auth.login-validation~1` `` | OFT ID format; the `req` type is part of [our subset](oft-format.md#artifact-types--subset); the dotted name follows the [naming convention](oft-format.md#naming-convention--extension). |
| `Status: approved` | OFT keyword. |
| Sentence `When the user submits credentials, the system SHALL verify …` | EARS Event-driven template; `SHALL` is the RFC 2119 obligation verb, [backticked per the workspace rule](rfc2119.md#backticking--constraint). |
| `Rationale:` and `Comment:` | OFT keywords. |
| `Covers:` (bullet list) | OFT linking model. |
| `Needs: dsn, utest` | OFT linking model; the chain shape (`req → dsn → utest`) is the [workspace coverage chain](oft-format.md#coverage-chain--constraint). |

## Anatomy of a `dsn` item with workspace extensions

A `dsn` may use workspace extension keywords that OFT does not define:

    ### Session Parser
    `dsn~parser.session~1`
    Status: approved
    Dimension: API Shape

    The session parser reads a log file and returns a `Session` populated
    with its events. Errors are raised as `ParseError`.

    Covers:
    - req~parse.session-discovery~1

    Needs: utest
    Interface: parser.parse_session(path: pathlib.Path) -> parser.Session
    AgentReview: Log output follows the human-readable format specified in
                 docs/log-format.md.

Where each workspace-specific piece comes from:

| Piece | Source |
|---|---|
| `Dimension: API Shape` | [`Dimension:` workspace extension keyword](oft-format.md#extension-keyword-dimension). Classifies the commitment; enables per-dimension projection. |
| `Interface: …` | [`Interface:` workspace extension keyword](oft-format.md#extension-keyword-interface). The signature is machine-validated against the code. |
| `AgentReview: …` | [`AgentReview:` workspace extension keyword](oft-format.md#extension-keyword-agentreview). Verified by the review skill on invocation. |
| Combining `Needs:`, `Interface:`, and `AgentReview:` on one item | [Verification coverage rule](oft-format.md#verification-coverage--extension). |

## What a valid file looks like as a whole

A spec file `SHALL`:

- Live under the project's `specs/` directory
  ([file organization](oft-format.md#file-organization--extension)).
- Use only [workspace artifact types](oft-format.md#artifact-types--subset)
  (`feat`, `req`, `dsn`, `utest`, `itest`).
- Use no [fenced code blocks](oft-format.md#fenced-code-blocks--constraint-forbidden).
- Use no [OFT forwarding syntax](oft-format.md#forwarding--constraint-forbidden).
- For `dsn` items, carry a
  [`Dimension:` field](oft-format.md#extension-keyword-dimension) naming
  one or more of the four design dimensions. Section headers within a
  `dsn` file are free-form — authors may group by dimension, feature,
  subsystem, or any other axis.

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

Tool behavior is documented separately in
[tooling.md](tooling.md); nothing about how the tools enforce these rules
changes what the rules themselves say.
