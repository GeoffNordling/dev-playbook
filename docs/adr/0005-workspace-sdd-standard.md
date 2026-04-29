# ADR-0005: Workspace SDD Standard

**Date:** 2026-04-24
**Status:** Accepted

## Context

The workspace practices spec-driven development: every feature is captured as a traced chain of `feat → req → dsn → utest/itest` items, with coverage links running between them. That practice needs a defined standard — item format, IDs, keywords, obligation vocabulary, sentence shapes, file organization — so authors, reviewers, and tools share one grammar.

Three external sources inspired the standard:

- **BCP 14** (RFC 2119 / RFC 8174) — obligation vocabulary.
- **EARS** (Mavin et al., RE'09) — sentence templates.
- **OFT Requirement-Enhanced Markdown** — item format, IDs, `Needs:`/`Covers:` linking model.

None of the three covers the workspace's full scope. BCP 14 specifies only the verbs; EARS only the sentence templates; OFT only the linking model. The workspace also needs a way to structure design-layer thinking, a non-test verification path for non-testable commitments, and design-phase structural commitments that downstream agents can implement against. The standard documents these workspace-specific choices directly and names the external sources as inspiration, not as constraints.

## Decision

### The workspace SDD standard lives in one document

`sdd-standards/spec-standard.md` is the complete standard — item anatomy, IDs, artifact types, coverage chain, keyword reference, prose rules (obligation vocabulary + sentence templates), and file organization. Design-phase semantics (commitment framing, decision dimensions) live in a companion file, `sdd-standards/design-layer.md`. `sdd-standards/README.md` is a thin index.

External standards are named as inspiration at the top of `spec-standard.md`; they are not restated. Readers familiar with RFC 2119, EARS, or OFT recognize the scaffolding; readers unfamiliar with them can still read the workspace standard in isolation.

### Artifact types

Five types: `feat`, `req`, `dsn`, `utest`, `itest`.

`feat`, `req`, and `dsn` are Markdown spec items in `/specs/`. `utest` and `itest` are pytest tests carrying `@pytest.mark.req("req~...")` markers; they are not Markdown items. The coverage graph realizes `utest`/`itest` nodes at pytest collection time.

### Coverage chain as a graph

The chain is a directed graph built from two per-item declarations — `Needs:` (downstream types required to cover this item) and `Covers:` (upstream IDs this item satisfies). Graph well-formedness rules (roots, `Covers:`/`Needs:` agreement, termination by absent `Needs:`) are the full system rule. The conventional arrangement `feat → req → dsn → utest/itest` is a writing norm, not a grammar rule; authors may deviate when the situation calls for it.

Verification termination is a `SHOULD`, not a `SHALL`. Every chain `SHOULD` terminate in verification — a `utest`, an `itest`, or a `feat`/`req`/`dsn` carrying `AgentReview:`. Partial and unverified chains are permitted; tools report them clearly so developers can decide per case.

### Four decision dimensions

Design-layer thinking is structured around four axes — `Data`, `API-Shape`, `Algorithms`, `Composition`. The framework is a writing aid walked through during `dsn` authoring to keep each item from drifting into prose-shaped narrative. It is not encoded as metadata on the item; `design-layer.md` describes each axis.

### `AgentReview:` as non-test verification

`AgentReview:` is an optional keyword on `feat`, `req`, or `dsn` items. Its value is prose describing what a review agent must check. It is the non-test arm of verification, used for commitments that cannot be deterministically tested (LLM behavior, prompt conventions, cross-cutting conventions that would degenerate into prompt-inclusion test-theater).

### `Interface:` as structural commitment, not verification

`Interface:` is an optional `dsn`-only keyword. Its value is one or more fully-qualified, annotated Python signatures. It pins code shape so downstream agents implement against a fixed target, and is deterministically validated against the code at pytest collection time.

`Interface:` does **not** terminate a chain. It commits structure; behavior still terminates through a test or an `AgentReview:`. A `dsn` carrying `Interface:` alone describes a structural target without verifying the behavior it serves.

### Obligation vocabulary

Five verbs: `SHALL`, `SHALL NOT`, `SHOULD`, `SHOULD NOT`, `MAY`. Uppercase only; always wrapped in backticks. One obligation level per item — an item `SHALL NOT` mix `SHALL` with `SHOULD`; mixed-level obligations split into separate items. `SHALL` and `SHALL NOT` within one item are the same level and fine.

### Revisions start at 0

Item IDs have the shape `type~name~revision`. Revisions are non-negative integers starting at 0. Semantic changes bump the revision; cosmetic edits leave it alone. Bumping voids every downstream `Covers:` link that pinned the previous revision.

### File organization

A simple spec is a single Markdown file. A complex spec is a directory containing an `index.md` plus individual files. The split decision belongs to the human, not the agent. Spec files do not use fenced code blocks (triple-backtick or `~~~`); they use 4-space indented code blocks.

## Alternatives Considered

| Alternative | Why rejected |
|---|---|
| Adopt an external standard unchanged (BCP 14, EARS, or OFT) | None of the three covers the workspace's full scope. A usable standard needs all three plus workspace-specific choices. |
| Restate the external standards inside the workspace document | Duplicates what the primary sources already publish. Naming them as inspiration and writing workspace rules directly keeps the document focused on decisions the workspace controls. |
| Split the workspace standard into per-source documents with workspace-specific sections appended | Readers reconcile "what the external standard says" with "what we do on top" on every lookup. A single document that states workspace rules directly is easier to read and maintain. |
| Encode dimension as item metadata (`Dimension:` keyword on every item) | Forced classification was a writing-time discipline aid, but encoding it as required metadata created redundancy with `Interface:` (which already implies API-Shape) and turned a writing heuristic into a grammar rule. The four dimensions live as a thinking framework in `design-layer.md` instead. |
| Make verification termination a hard `SHALL` | Partial and aspirational chains are normal during active spec work; a hard rule produces false-positive lint noise. `SHOULD` plus explicit tool reporting gives developers the signal without the false alarm. |
| Restrict `AgentReview:` to `dsn` only | Some non-testable commitments belong at `feat` or `req` level. Restricting `AgentReview:` to `dsn` forces a synthetic design item to exist solely to carry the review. |
| Treat `Interface:` as a chain terminator | `Interface:` commits structure; a test or `AgentReview:` commits behavior. Conflating the two lets a structural commitment pose as behavioral verification, which is what the chain is trying to prevent. |
| Start revisions at 1 | No material difference, and 0 is the common convention for this kind of versioning. |

## Consequences

### Files

- `sdd-standards/` contains three files: `README.md`, `spec-standard.md`, `design-layer.md`.
- Root `README.md`, the `standards/*.md` files (BCP 14 boilerplate), and the SDD skills (`sdd-red`, `sdd-review`) link to `spec-standard.md` anchors.

### Changes from ADR-0004

ADR-0004's "Four principles for design items" framing (single role, observable-to-tests scope, commitment by naming, design-agent ownership of structure) is reabsorbed:

- The commitment framing in `design-layer.md` replaces the four principles.
- `Interface:` is now an optional `dsn` keyword (previously required on any `dsn` naming a public surface). The machinery — strict-equality signature validation at pytest collection time, the annotation convention — is unchanged.
- `Interface:` is a structural commitment, not a verification field. Behavioral verification still terminates through a test or `AgentReview:`.

ADR-0004's other commitments (public-only testing enforcement via Ruff `SLF001` plus test-privacy AST check; the `Interface:` validator algorithm and annotation convention) stand unchanged.

### Implementation

- `sdd-tools` implements the standard: `spec-lint` enforces keyword well-formedness; `sdd-index`, `sdd-atlas`, `sdd-chain`, and `sdd-review` provide projections; `pytest-sdd` parses markers and `Interface:` declarations at collection time.
- Greenfield `spec-tools` rewrite (GH issue #16) targets this standard.
