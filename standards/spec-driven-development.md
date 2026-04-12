# Spec-Driven Development

The key words `SHALL`, `SHALL NOT`, `SHOULD`, `SHOULD NOT`, and `MAY` in this
document are to be interpreted as described in RFC 2119, following the vocabulary
conventions in the [spec format reference](spec-format.md).

---

Spec-driven development is a project-level commitment. The human decides whether a project uses this workflow. When this document is referenced by a project, all of its rules apply.

---

## Core Principles

**Spec-as-source.** The spec is the only artifact the human authors. The human never edits code directly — all code is generated from the spec. The human writes and maintains the spec; agents derive tasks, write tests, and implement code from it.

**The spec `SHALL` explicitly state what NOT to build.** Scope exclusions are as important as requirements. Without them, the agent makes reasonable assumptions that turn out wrong. An explicit out-of-scope section prevents the agent from building things you didn't ask for.

**The spec `SHALL` always describe reality, not intent.** When implementation diverges from the spec, the spec `SHALL` be updated to reflect what was actually built. Changes to behavior `SHOULD` include a corresponding spec update in the same commit or pull request. A stale spec is a maintenance failure.

**Functional requirements are about behavior; non-functional requirements are about system qualities.** Non-functional requirements — performance, security, scalability, reliability — constrain how well the system does what it does. They are valid spec items that follow the same format. This workspace consciously omits them because personal projects rarely have meaningful non-functional constraints.

**Functional before design.** Decide what the system does before deciding how it's structured. A functional spec is always written first. A design spec is written after behavior is settled.

**The design layer's primary role is to name the interfaces that tests target.** Each design item connects a functional requirement to the specific code (module, class, function) that fulfills it. The red agent writes tests against that interface; the green agent implements it. Without this layer, the red agent has no target — the functional requirement says what the system does, but not where the code lives or what the public API looks like.

The design layer's secondary role is to document design decisions — algorithm choice, data structure, component boundary, error handling strategy — when those decisions exist. Most design items do both; some only do one.

**Every design item `SHALL` earn its place.** A design item earns its place by doing one or both of:

- **Naming an interface** — connecting a functional requirement to the specific code that fulfills it. This is the essential bridge between behavioral requirements and testable code.
- **Making a concrete design decision** — something the functional requirement deliberately left open, where options were weighed and a choice was made.

A design item `SHALL NOT` merely restate the functional requirement's behavior without naming an interface or making a decision. Every design item must do at least one of the above. Most functional requirements will have a corresponding design item, because the red agent needs a target even when there is no hard design decision. Cases where a functional requirement skips the design layer entirely are rare.

For how to write and format spec items — IDs, keywords, coverage chains, EARS templates, RFC 2119 obligations, and file structure — see the [spec format reference](spec-format.md).

---

## References

- RFC 2119 — Key Words for Use in RFCs to Indicate Requirement Levels (Bradner, 1997)
- OpenFastTrace user guide — https://github.com/itsallcode/openfasttrace/blob/main/doc/user_guide.md
- Joel on Software — Painless Functional Specifications, Parts 1–4 (Spolsky, Oct 2000)
- Design Docs at Google — Industrial Empathy (Ubl)
- Engineering Practices for LLM Application Development — ThoughtWorks (Tan & Wang, Feb 2024)
