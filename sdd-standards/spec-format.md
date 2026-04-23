# Spec File Format — Integration Walkthrough

Specs in this workspace stack three external standards with a set of
workspace extensions. This file shows how the pieces combine in a single
spec file; each per-standard file carries the authoritative detail.

## The stack

| Concern | Standard | File |
|---|---|---|
| Obligation strength | RFC 2119 | [rfc2119.md](rfc2119.md) |
| Sentence structure | EARS | [ears.md](ears.md) |
| Item identity, linking, traceability | OFT Requirement-Enhanced Markdown | [oft-format.md](oft-format.md) |
| Subsets, constraints, and added keywords | Workspace | [extensions.md](extensions.md) |

A valid spec file conforms to all four. A spec-phase agent writes prose
following EARS, grades obligations with RFC 2119 vocabulary, embeds the
prose in OFT specification items, and respects every workspace-level
constraint and extension from `extensions.md`.

Design-phase semantics (what a commitment is; the four decision dimensions)
are covered in [design-layer.md](design-layer.md).

## Reading order

A new author or agent encountering the workspace for the first time
`SHOULD` read the files in this order:

1. [rfc2119.md](rfc2119.md) — obligation vocabulary.
2. [ears.md](ears.md) — sentence templates.
3. [oft-format.md](oft-format.md) — item identity, keywords, linking,
   coverage.
4. [extensions.md](extensions.md) — workspace subsets, extensions, and
   constraints. Many rules here override the defaults of the external
   standards, so this file is load-bearing for practical authoring.
5. [design-layer.md](design-layer.md) — only when working on `dsn` items.

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
| The ID `` `req~auth.login-validation~1` `` | OFT ID format; the `req` type is part of our subset (extensions.md); the dotted name follows the workspace naming convention (extensions.md). |
| `Status: approved` | OFT keyword. |
| Sentence `When the user submits credentials, the system SHALL verify …` | EARS Event-driven template; `SHALL` is the RFC 2119 obligation verb, backticked per extensions.md. |
| `Rationale:` and `Comment:` | OFT keywords. |
| `Covers:` (bullet list) | OFT linking model. |
| `Needs: dsn, utest` | OFT linking model; the chain shape (`req → dsn → utest`) is the workspace coverage chain in extensions.md. |

## Anatomy of a `dsn` item with workspace extensions

A `dsn` may use workspace extension keywords that OFT does not define:

    ## API Shape

    ### Session Parser
    `dsn~parser.session~1`
    Status: approved

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
| The `## API Shape` section header | Dimension section organization (extensions.md). |
| `Interface: …` | Workspace extension keyword (extensions.md). The signature is machine-validated against the code. |
| `AgentReview: …` | Workspace extension keyword (extensions.md). Verified by the review skill on invocation. |
| Combining `Needs:`, `Interface:`, and `AgentReview:` on one item | Verification coverage rule (extensions.md). |

## What a valid file looks like as a whole

A spec file `SHALL`:

- Live under the project's `specs/` directory
  ([extensions.md](extensions.md#file-organization--extension)).
- Use only [workspace artifact types](extensions.md#oft-artifact-types--subset)
  (`feat`, `req`, `dsn`, `utest`, `itest`).
- Use no fenced code blocks
  ([extensions.md](extensions.md#fenced-code-blocks--constraint-forbidden)).
- Use no OFT forwarding syntax
  ([extensions.md](extensions.md#forwarding--constraint-forbidden)).
- For `dsn` files only, carry the four dimension `##` headers in canonical
  order ([extensions.md](extensions.md#dimension-section-organization--extension)).

Prose that is not part of any item is ignored by OFT and `MAY` be used
freely for context, headings, or notes.

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
