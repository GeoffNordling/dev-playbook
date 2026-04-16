# Spec-Driven Development

Spec-driven development is a project-level commitment. The human decides whether a project uses this workflow. When this document is referenced by a project, all of its rules apply.

---

## Core Principles

**Spec-anchored.** The spec and the code are co-maintained as peers — the spec has authority, and machine-verified traceability (via OpenFastTrace) keeps them in sync. Code is primarily edited by agents rather than by hand. The term "spec-anchored" is taken from [Birgitta Böckeler's three-school taxonomy of SDD tools](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html); see [ADR-003](../../docs/adr/003-evaluate-sdd-community-landscape.md) for the landscape evaluation that led to this position.

**SDD Triangle.** Spec, tests, and code do not stay automatically synchronized — implementation continuously surfaces gaps. Every divergence is a tracked action item; the default reconciliation is that the spec wins and code updates to match, but the human decides per-case. Term from [Drew Breunig's "SDD Triangle" post (March 2026)](https://www.dbreunig.com/2026/03/04/the-spec-driven-development-triangle.html).

**Functional requirements are about behavior; technical requirements are about system qualities.** Technical requirements — performance, security, scalability, reliability — constrain how well the system does what it does. They are valid spec items that follow the same format. This workspace consciously omits them because personal projects rarely have meaningful technical constraints.

## References

- RFC 2119 — Key Words for Use in RFCs to Indicate Requirement Levels (Bradner, 1997)
- OpenFastTrace user guide — https://github.com/itsallcode/openfasttrace/blob/main/doc/user_guide.md
- Joel on Software — Painless Functional Specifications, Parts 1–4 (Spolsky, Oct 2000)
- Design Docs at Google — Industrial Empathy (Ubl)
- Engineering Practices for LLM Application Development — ThoughtWorks (Tan & Wang, Feb 2024)
