# ADR-006: Per-standard documents in sdd-standards/

**Date:** 2026-04-23
**Status:** Accepted

## Context

[ADR-001](001-adopt-openfasttrace.md) bundled two separate decisions under a
single "we adopt OpenFastTrace" framing:

1. Adopting OFT's **format** — Requirement-Enhanced Markdown, the
   `type~name~revision` ID convention, the `Needs:`/`Covers:` linking
   model, the keyword vocabulary.
2. Adopting OFT's **reference implementation** — the Java JAR that parses
   the format and walks the coverage graph.

ADR-001's "Alternatives Considered" section treated "reimplementing
tracing in pure Python" as an all-or-nothing alternative to OFT as a
whole. It did not consider the middle path: adopting the format while
owning the implementation in Python. Over time, as the workspace grew,
this bundling blurred the distinction between what we are *obligated to*
(the external standard) and what we *chose to do* (use the reference
tool).

The imprecision propagated into the documentation. `sdd-standards/writing.md`
grew to cover three distinct things in a single file:

- External standards we adopt (RFC 2119, EARS, OFT Requirement-Enhanced
  Markdown).
- Workspace-specific choices (subsets, constraints, extensions like
  `Interface:` and `AgentReview:`).
- Tool-behavior details leaking in through the discussion of how each
  rule is enforced.

Three concrete pain points surfaced:

**Verifiability against primary sources.** A deep-research agent (or
human reviewer) cannot check "is our restatement of EARS correct?"
without first sifting workspace-specific choices out of the text that
mixes the two.

**The "do we keep the JAR?" decision is now live.** A future workstream
will weigh reimplementing OFT's trace semantics in Python against keeping
the JAR. That decision is only tractable if the format and the
implementation are understood as separate commitments. ADR-001's framing
made them indistinguishable.

**Workspace rules scattered.** The `Interface:` keyword, `AgentReview:`
keyword, dimension section organization, layer-chain choice, revision
policy, forwarding prohibition, fenced-code-blocks prohibition, and
naming convention were spread across `writing.md`, `overview.md`, and
`design-layer.md` with no consistent placement relative to the standard
they modify.

The three standards we adopt come from three sources: RFC 2119/RFC 8174
(IETF, BCP 14), EARS (Mavin et al., RE'09), and OFT's format spec
(openfasttrace project). Each source is verifiable independently. Our
documentation should reflect that separability while still keeping each
workspace choice visible next to the standard it modifies, so that a
reader who cares about "how do we actually use RFC 2119?" sees the
answer in one place.

## Decision

### One file per external standard

`sdd-standards/` is restructured into one file per external standard, one
file per layer of workspace-specific semantic content, and targeted
companion documents:

| File | Scope |
|---|---|
| `rfc2119.md` | BCP 14 obligation vocabulary (RFC 2119 + RFC 8174), plus the workspace Extensions section below it. |
| `ears.md` | EARS sentence templates. The workspace adopts EARS unchanged, so this file has no Extensions section. |
| `oft-format.md` | OFT Requirement-Enhanced Markdown, plus the workspace Extensions section below it — artifact-type subset, coverage chain, revision policy, forwarding constraint, verification coverage rule, the `Interface:` and `AgentReview:` keywords, the fenced-code-block constraint, naming convention, and file organization. |
| `design-layer.md` | Design-phase semantics (commitment framing, the four decision dimensions) and the dimension-section-organization rule. |
| `spec-format.md` | Integration walkthrough showing how the three standards combine in a single spec file, plus the illustrative-examples authoring convention. |
| `README.md` | Directory index and core SDD philosophy (spec-anchored, SDD triangle, technical-requirements-omission). |
| `tooling.md` | Tool behavior — cross-references retargeted at the new doc anchors. |

`writing.md` and `overview.md` are deleted.

### External-standards content restates the standard as-is

The top portion of each standards file describes its standard **as the
standard defines it**, including features this workspace does not use.
Optional features are named and flagged ("allowed by the standard, not
required") — not omitted. This makes the top portion verifiable against
its primary source without the reviewer having to mentally subtract
workspace-specific decisions.

### Extensions are appended, not interleaved

Each standards file that modifies its standard carries a trailing
`## Extensions` section documenting the workspace subset, added keywords,
and constraints for that standard. The section is clearly demarcated so
a verifier doing a primary-source check can stop reading at the section
break. A standards file with no modifications (currently `ears.md`) has
no Extensions section — its absence is a deliberate signal that the
workspace adopts the standard unchanged.

This resolves the tension between two goals:

- Verifiability wants the external standard presented without workspace
  noise.
- Authorship wants the workspace rules visible next to the standard they
  modify, not in a separate file.

Append-at-bottom satisfies both. Inline integration — mixing "the
standard says X; we do Y" paragraph-by-paragraph — would re-create the
verifiability problem the whole restructure is trying to solve.

### Taxonomy of workspace choices

Each Extensions section classifies its entries into one of three kinds:

| Kind | Meaning |
|---|---|
| **Subset** | We adopt only part of the standard's optional vocabulary or features. |
| **Extension** | We add capability the standard does not define (e.g., new keywords). |
| **Constraint** | We forbid or tighten something the standard allows, with a reason given. |

Extensions and constraints name a reason; subsets name the unused
portion of the vocabulary.

### Format adoption and implementation choice are separable

This ADR makes explicit what ADR-001 left implicit: adopting OFT's format
and using OFT's reference JAR are two separate commitments. The
workspace continues to use both today, but future decisions about either
are independent:

- The format is committed via `oft-format.md` (the external-standard
  portion). Changing format means revising this document and propagating
  changes across all specs.
- The implementation is described in `tooling.md`. The JAR can be
  replaced with an alternative implementation without changing any `.md`
  file in `sdd-standards/`, as long as the replacement enforces the same
  format.

This ADR does **not** decide whether to replace the JAR. That remains a
future workstream.

## Alternatives Considered

| Alternative | Why rejected |
|---|---|
| Keep `writing.md` as a single integrated document | Muddles "the standard we adopt" with "our choices on top of it." Verifiability against primary sources requires a pre-separation pass every time. |
| Split by concern (prose rules / structural rules / linking rules) rather than by source of authority | Verifiability is a per-source property: "is our EARS correct?" and "is our RFC 2119 correct?" are distinct questions. Splitting by concern merges them. |
| Drop restatement of external standards entirely; link out to primary sources | Having our own restatement lets us mark optional features the workspace does not use, explain our subset, and keep the full stack visible in one place. Pure linking shifts that burden to every reader. |
| One combined standards document covering all three external standards plus extensions | Defeats the per-source verifiability goal. Each external standard has a separate primary source and should be reviewed independently. |
| Put workspace subsets / constraints / extensions in a separate `extensions.md` file | Added indirection without informational gain. Every rule can be cleanly assigned to the one standard it modifies; a separate file forces readers to hop between a standard and a distant file that applies to it. The single-file-per-standard model keeps adjacent information physically adjacent. |
| Interleave workspace extensions inline with the standard restatement (paragraph-by-paragraph) | Re-creates the verifiability problem the restructure is trying to solve. A deep-research agent would have to sift workspace choices out of the standard text on every check. Append-at-bottom is the mechanical separator that preserves verifiability. |
| Decide the JAR-vs-Python implementation question in this ADR | Out of scope. This ADR makes the decision separable; the actual choice belongs to a dedicated workstream with its own analysis. |

## Consequences

- `sdd-standards/writing.md` and `sdd-standards/overview.md` are deleted.
- `rfc2119.md` and `oft-format.md` carry clearly-delimited `## Extensions`
  sections below the standard restatement, containing the workspace subset,
  added keywords, and constraints for each. `ears.md` has no Extensions
  section — EARS is adopted unchanged.
- `sdd-standards/design-layer.md` carries the dimension-section-organization
  rule, because that rule is a structural consequence of the four decision
  dimensions it defines.
- `sdd-standards/spec-format.md` carries the illustrative-examples
  authoring convention, because that is general authoring guidance
  orthogonal to any one external standard.
- Cross-references are retargeted across `sdd-standards/tooling.md`, the
  SDD skills (`sdd-func-reqs`, `sdd-red`, `sdd-review`), and
  `standards/*.md` files. `ref-check` reports no broken links.
- The SDD skills are cached at session start; a running Claude Code
  session will not see the updated SKILL.md content until restart.
- ADR-001 is partially superseded. Its adoption of the OFT format stands;
  the implicit bundling of the format with the reference JAR is
  dissolved. A future ADR may revisit the implementation choice on its
  own merits.
- The three external-standards files are written from conversation-level
  knowledge and verified against primary sources by a deep-research pass.
  Corrections from that pass land as follow-up edits, not new ADRs.
- Future tool work (strict Python deserializer, JAR-vs-Python decision,
  validator re-architecture) now has a clean foundation: the format is
  precisely documented, workspace-specific rules are colocated with the
  standard they modify, and every rule carries an anchor a tool can link
  to.
