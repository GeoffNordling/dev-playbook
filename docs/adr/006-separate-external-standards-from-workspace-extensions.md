# ADR-006: Separate External Standards from Workspace Extensions

**Date:** 2026-04-23
**Status:** Accepted

## Context

[ADR-001](001-adopt-openfasttrace.md) bundled two separate decisions under a
single "we adopt OpenFastTrace" framing:

1. Adopting OFT's **format** — Requirement-Enhanced Markdown, the `type~name~revision`
   ID convention, the `Needs:`/`Covers:` linking model, the keyword
   vocabulary.
2. Adopting OFT's **reference implementation** — the Java JAR that parses the
   format and walks the coverage graph.

ADR-001's "Alternatives Considered" section treated "reimplementing tracing in
pure Python" as an all-or-nothing alternative to OFT as a whole. It did not
consider the middle path: adopting the format while owning the implementation
in Python. Over time, as the workspace grew, this bundling blurred the
distinction between what we are *obligated to* (the external standard) and
what we *chose to do* (use the reference tool).

The imprecision propagated into the documentation. `sdd-standards/writing.md`
grew to cover three distinct things in a single file:

- External standards we adopt (RFC 2119, EARS, OFT Requirement-Enhanced Markdown).
- Workspace-specific choices (subsets, constraints, extensions like
  `Interface:` and `AgentReview:`).
- Tool-behavior details leaking in through the discussion of how each rule is
  enforced.

Three concrete pain points surfaced:

**Verifiability against primary sources.** A deep-research agent (or human
reviewer) cannot check "is our restatement of EARS correct?" without first
sifting workspace-specific choices out of the text that mixes the two.

**The "do we keep the JAR?" decision is now live.** A future workstream will
weigh reimplementing OFT's trace semantics in Python against keeping the
JAR. That decision is only tractable if the format and the implementation
are understood as separate commitments. ADR-001's framing made them
indistinguishable.

**Workspace rules scattered.** The `Interface:` keyword, `AgentReview:`
keyword, dimension section organization, layer-chain choice, revision
policy, forwarding prohibition, fenced-code-blocks prohibition, and naming
convention were spread across `writing.md`, `overview.md`, and
`design-layer.md` with no single place to see "what does this workspace
require on top of the external standards?"

The three standards we adopt come from three sources: RFC 2119 (IETF), EARS
(Mavin et al., RE'09), and OFT's format spec (openfasttrace project). Each
source is verifiable independently. Our documentation should reflect that
separability.

## Decision

### Per-standard documentation

`sdd-standards/` is restructured into one file per external standard, one
file for workspace extensions and constraints, and targeted companion
documents:

| File | Scope |
|---|---|
| `rfc2119.md` | RFC 2119 obligation vocabulary as the standard defines it, including synonyms this workspace does not use. |
| `ears.md` | EARS sentence templates as the standard defines them. |
| `oft-format.md` | OFT Requirement-Enhanced Markdown as the standard defines it, including features (forwarding, additional artifact types) this workspace does not use. |
| `extensions.md` | Workspace subsets, constraints, and extensions. The single home for choices on top of the external standards. |
| `design-layer.md` | Design-phase semantics: commitment framing and the four decision dimensions. Trimmed of mechanical rules that moved to `extensions.md`. |
| `spec-format.md` | Integration walkthrough showing how the four standards combine in a single spec file. |
| `README.md` | Directory index and core SDD philosophy (spec-anchored, SDD triangle, technical-requirements-omission). |
| `tooling.md` | Tool behavior — unchanged in content; cross-references retargeted at the new doc anchors. |

`writing.md` and `overview.md` are deleted.

### External-standards files restate the standard as-is

Each external-standards file describes its standard **as the standard
defines it**, including features this workspace does not use. Optional
features are named and flagged ("allowed by the standard, not required") —
not omitted. This makes each file verifiable against its primary source
without the reviewer having to mentally subtract workspace-specific
decisions.

Our subset choices (which RFC 2119 verbs we use, which OFT artifact types
we use, etc.) live exclusively in `extensions.md`.

### Taxonomy of workspace choices

`extensions.md` classifies each workspace choice into one of three kinds:

| Kind | Meaning |
|---|---|
| **Subset** | We adopt only part of the standard's optional vocabulary or features. |
| **Extension** | We add capability the standard does not define (e.g., new keywords). |
| **Constraint** | We forbid or tighten something the standard allows, with a reason given. |

Each entry in `extensions.md` flags its kind, so the distinction between
"we chose not to use X" and "we forbid X" is explicit. Extensions and
constraints name a reason; subsets name the unused portion of the
vocabulary.

### Format adoption and implementation choice are separable

This ADR makes explicit what ADR-001 left implicit: adopting OFT's format
and using OFT's reference JAR are two separate commitments. The workspace
continues to use both today, but future decisions about either are
independent:

- The format is committed via `oft-format.md`. Changing format means
  revising this document and propagating changes across all specs.
- The implementation is described in `tooling.md`. The JAR can be
  replaced with an alternative implementation without changing any
  `.md` file in `sdd-standards/`, as long as the replacement enforces
  the same format.

This ADR does **not** decide whether to replace the JAR. That remains a
future workstream. The decision space is now clean: format stays, tooling
is re-evaluated on its own merits.

## Alternatives Considered

| Alternative | Why rejected |
|---|---|
| Keep `writing.md` as a single integrated document | Muddles "the standard we adopt" with "our choices on top of it." Verifiability against primary sources requires a pre-separation pass every time. |
| Split by concern (prose rules / structural rules / linking rules) rather than by source of authority | Verifiability is a per-source property: "is our EARS correct?" and "is our RFC 2119 correct?" are distinct questions. Splitting by concern merges them. |
| Drop restatement of external standards entirely; link out to primary sources | Having our own restatement lets us mark optional features the workspace does not use, explain our subset, and keep the full stack visible in one place. Pure linking shifts that burden to every reader. |
| Merge `design-layer.md` into `extensions.md` | Design-phase semantics (what a commitment is, what the four dimensions mean) is a different kind of content from mechanical layout rules. Merging them loses the distinction. |
| One combined standards document covering all three external standards plus extensions | Defeats the per-source verifiability goal. Each external standard has a separate primary source and should be reviewed independently. |
| Decide the JAR-vs-Python implementation question in this ADR | Out of scope. This ADR makes the decision separable; the actual choice belongs to a dedicated workstream with its own analysis. |

## Consequences

- `sdd-standards/writing.md` and `sdd-standards/overview.md` are deleted;
  seven standards documents live in the directory.
- `sdd-standards/design-layer.md` is trimmed to design semantics only;
  mechanical rules (dimension section organization, verification fields)
  move to `extensions.md`.
- `extensions.md` is the single home for workspace-specific choices on top
  of the external standards.
- `spec-format.md` is the new front door for authors and agents learning
  how the standards combine in practice.
- Cross-references are retargeted across `sdd-standards/tooling.md`, the
  SDD skills (`sdd-func-reqs`, `sdd-red`, `sdd-review`), and `standards/*.md`
  files. `ref-check` reports no broken links.
- The SDD skills are cached at session start; a running Claude Code session
  will not see the updated SKILL.md content until restart.
- ADR-001 is partially superseded. Its adoption of the OFT format stands;
  the implicit bundling of the format with the reference JAR is dissolved.
  A future ADR may revisit the implementation choice on its own merits.
- The three external-standards files (`rfc2119.md`, `ears.md`,
  `oft-format.md`) are written from conversation-level knowledge and are
  being verified against primary sources by a deep-research pass.
  Corrections from that pass will land as a follow-up edit, not a new ADR.
- Future tool work (strict Python deserializer, JAR-vs-Python decision,
  validator re-architecture) now has a clean foundation: the format is
  precisely documented, workspace-specific rules are enumerated in one
  file, and every rule carries an anchor a tool can link to.
