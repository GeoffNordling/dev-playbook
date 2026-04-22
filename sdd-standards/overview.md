# Spec-Driven Development

Spec-driven development is a project-level commitment. The human decides whether a project uses this workflow. When this document is referenced by a project, all of its rules apply.

---

## Core Principles

**Spec-anchored.** The spec and the code are co-maintained as peers — the spec has authority, and machine-verified traceability (via OpenFastTrace) keeps them in sync. Code is primarily edited by agents rather than by hand. Term from Böckeler, *Three Schools of Spec-Driven Development Tools*; see [ADR-003](../docs/adr/003-evaluate-sdd-community-landscape.md) for the landscape evaluation that led to this position.

**SDD Triangle.** Spec, tests, and code do not stay automatically synchronized — implementation continuously surfaces gaps. Every divergence is a tracked action item; the default reconciliation is that the spec wins and code updates to match, but the human decides per-case. Term from Breunig, *The Spec-Driven Development Triangle*.

**Functional requirements are about behavior; technical requirements are about system qualities.** Technical requirements — performance, security, scalability, reliability — constrain how well the system does what it does. They are valid spec items that follow the same format. This workspace consciously omits them because personal projects rarely have meaningful technical constraints.

## Coverage Chain

OFT enforces a directed graph of coverage. Each item declares what must cover it downstream (`Needs:`), and each downstream item declares what it covers upstream (`Covers:`). OFT walks this graph and fails if any required link is absent.

The standard layers, from upstream to downstream:

```
feat  →  req  →  dsn  →  utest / itest
```

Each arrow represents a coverage relationship: the downstream layer covers the upstream layer. Every item declares which downstream types must cover it (`Needs:`) and which upstream items it satisfies (`Covers:`).

**Which layers are required depends on the project and the item:**

- **`feat`** is the root. Every project `SHALL` begin the chain with `feat` items.
- **`req`** items cover `feat`. Most `req` items declare `Needs: dsn` to carry the chain forward into the design layer.
- **`dsn`** items cover `req` and are expected for most `req` items. A `req` `MAY` skip `dsn` only when it needs neither a design decision nor an ownership assignment; in that case the `req` declares `Needs: utest` and/or `Needs: itest` directly.
- **`utest` and `itest`** cover the item directly upstream. Either a `req` or a `dsn` `MAY` declare `Needs: utest`, `Needs: itest`, or both — whichever is appropriate to verify the commitment.

An item with no `Needs:` declaration terminates the chain below itself — nothing downstream is required.

OFT fails the trace when:
- Any item's `Needs:` types are not all covered by at least one item of each required type
- A `Covers:` link references an ID that does not exist at that revision
- Any item is orphaned (has `Covers:` pointing to a nonexistent item)

**Every requirement ties off with verification.** Beyond OFT's own chain checks, this workspace requires every requirement — at every layer — to name how its commitment is verified. For `feat` and `req` items, that means a `Needs:` declaration pointing at a covering downstream type. For `dsn` items, verification may come from `Needs:` or from the design-layer fields `Interface:` and `AgentReview:` (see [design-layer.md — Verification Fields](design-layer.md#verification-fields)). A requirement with no verification mechanism is a commitment that nothing ever checks.

## Revision Policy

The revision number is a semantic version for the item's meaning.

**Increment** the revision when the semantic content changes — when the requirement means something different than it did before. This immediately breaks all downstream `Covers:` links that referenced the previous revision, forcing downstream documents to explicitly acknowledge and respond to the change.

**Do not increment** for typo fixes, rephrasing that does not change meaning, or formatting changes.

When you increment a revision, update all `Covers:` references in downstream documents to the new revision. If a downstream item's response to the change is "no change needed," update the `Covers:` link and note this in the `Comment:` field.

## Forwarding

OFT supports a forwarding syntax that lets a document layer acknowledge a requirement and pass coverage responsibility downstream without creating a full spec item:

```markdown
arch --> dsn : req~auth.login-validation~1
```

**Do not use forwarding in this workspace.** When a layer has nothing to say for a particular item, the item `SHALL` skip that layer entirely (by omitting the type from its `Needs:`) rather than creating a hollow passthrough. Forwarding is documented here so you recognize it if you encounter it in the OFT documentation.

## References

- RFC 2119 — Key Words for Use in RFCs to Indicate Requirement Levels (Bradner, 1997)
- EARS — Easy Approach to Requirements Syntax (Mavin et al.)
- OpenFastTrace user guide — https://github.com/itsallcode/openfasttrace/blob/main/doc/user_guide.md
- OpenFastTrace repository — https://github.com/itsallcode/openfasttrace
- Joel on Software — Painless Functional Specifications, Parts 1–4 (Spolsky, Oct 2000)
- Design Docs at Google — Industrial Empathy (Ubl)
- Engineering Practices for LLM Application Development — ThoughtWorks (Tan & Wang, Feb 2024)
- Exploring Gen AI: Three Schools of Spec-Driven Development Tools — martinfowler.com (Böckeler, 2026) — https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html
- The Spec-Driven Development Triangle — dbreunig.com (Breunig, March 2026) — https://www.dbreunig.com/2026/03/04/the-spec-driven-development-triangle.html
