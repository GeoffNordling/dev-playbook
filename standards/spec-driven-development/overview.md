# Spec-Driven Development

The key words `SHALL`, `SHALL NOT`, `SHOULD`, `SHOULD NOT`, and `MAY` in this
document are to be interpreted as described in RFC 2119, following the vocabulary
conventions in [writing.md](writing.md).

---

Spec-driven development is a project-level commitment. The human decides whether a project uses this workflow. When this document is referenced by a project, all of its rules apply.

---

## Core Principles

**Spec-as-source.** The spec is the only artifact the human authors. The human never edits code directly — all code is generated from the spec. The human writes and maintains the spec; agents derive tasks, write tests, and implement code from it.

**The spec `SHALL` explicitly state what NOT to build.** Scope exclusions are as important as requirements. Without them, the agent makes reasonable assumptions that turn out wrong. An explicit out-of-scope section prevents the agent from building things you didn't ask for.

**The spec `SHALL` always describe reality, not intent.** When implementation diverges from the spec, the spec `SHALL` be updated to reflect what was actually built. Changes to behavior `SHOULD` include a corresponding spec update in the same commit or pull request. A stale spec is a maintenance failure.

**Functional requirements are about behavior; non-functional requirements are about system qualities.** Non-functional requirements — performance, security, scalability, reliability — constrain how well the system does what it does. They are valid spec items that follow the same format. This workspace consciously omits them because personal projects rarely have meaningful non-functional constraints.

## References

- RFC 2119 — Key Words for Use in RFCs to Indicate Requirement Levels (Bradner, 1997)
- OpenFastTrace user guide — https://github.com/itsallcode/openfasttrace/blob/main/doc/user_guide.md
- Joel on Software — Painless Functional Specifications, Parts 1–4 (Spolsky, Oct 2000)
- Design Docs at Google — Industrial Empathy (Ubl)
- Engineering Practices for LLM Application Development — ThoughtWorks (Tan & Wang, Feb 2024)
