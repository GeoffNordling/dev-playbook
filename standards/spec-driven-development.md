# Spec-Driven Development

The key words `SHALL`, `SHALL NOT`, `SHOULD`, `SHOULD NOT`, and `MAY` in this
document are to be interpreted as described in RFC 2119, following the vocabulary
conventions in the [spec format reference](spec-format.md).

---

## References

- RFC 2119 — Key Words for Use in RFCs to Indicate Requirement Levels (Bradner, 1997)
- OpenFastTrace user guide — https://github.com/itsallcode/openfasttrace/blob/main/doc/user_guide.md
- Joel on Software — Painless Functional Specifications, Parts 1–4 (Spolsky, Oct 2000)
- Design Docs at Google — Industrial Empathy (Ubl)
- Engineering Practices for LLM Application Development — ThoughtWorks (Tan & Wang, Feb 2024)

---

## Core Principles

**Write the spec before writing code.** Every decision you skip in a spec gets made anyway — just later, under worse conditions, mid-build or post-ship. Front-loading decisions is always cheaper.

**Only write a spec when there are hard decisions to document.** If a spec would just be an implementation manual with no genuine choices in it, there was nothing worth writing. The spec earns its existence by capturing difficult decisions — options considered, trade-offs weighed, and the choice made. If there were no hard decisions, skip the doc.

**The spec `SHALL` explicitly state what NOT to build.** Scope exclusions are as important as requirements. Without them, the agent makes reasonable assumptions that turn out wrong. An explicit out-of-scope section prevents the agent from building things you didn't ask for.

**The spec is a living document.** It `SHALL` stay in sync with what the system actually does as development proceeds. Stale specs are a maintenance failure, not an inherent property of specs. Changes to behavior `SHOULD` include a corresponding spec update in the same commit or pull request.

**Functional before design.** Decide what the system does before deciding how it's structured. A functional spec is always written first. A design spec is written after behavior is settled, defining the components, interfaces, and data structures that the red/green agents will implement against.

**Humans `SHALL NOT` write tasks.** Deriving and managing implementation tasks is the agent's job. The human only ever edits the spec. The agent creates, tracks, and completes its own tasks from the spec. Writing tasks manually reduces the human to a project manager for the LLM and defeats the purpose of agentic development.

**Plans are ephemeral; specs are durable.** Claude Code's plan mode is a thinking tool — plans are intentionally not version controlled and are disposable once used. The spec in Git is the durable source of truth. These are distinct artifacts and `SHALL NOT` be conflated.

For how to write and format spec items — IDs, keywords, coverage chains, EARS templates, RFC 2119 obligations, and file structure — see the [spec format reference](spec-format.md).

---

## Deviations

**Deviations from the spec `SHALL` be documented before merging.** When implementation diverges from the spec, the deviation is captured and the spec is updated to reflect what was actually built. The spec always describes reality, not intent.

---

## The Three Levels of Spec-Driven Development

These levels represent a progression of maturity. Each builds on the previous.

| Level | Definition |
|---|---|
| **Spec-First** | The spec is written before any code. Implementation follows the spec. |
| **Spec-Anchored** | The spec remains alive and current throughout the project lifecycle. It is updated as the system evolves. |
| **Spec-as-Source** | The spec is the only artifact the human authors. The human never edits code directly — all code is generated from the spec. This is the most aspirational level and the target practice. |

---

## When Spec-Driven Development is Overkill

SDD is not always warranted. Apply the same hard-decisions test: if there is nothing difficult to decide and document, the overhead is not justified.

SDD is appropriate for: large refactors touching many files, migrations, features with unclear or evolving requirements.

SDD is overkill for: single-file changes, simple well-defined bug fixes, trivially small features with no real decisions to make.
