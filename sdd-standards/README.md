# Spec-Driven Development Standards

Spec-driven development (SDD) is a project-level commitment. The human
decides whether a project uses this workflow. When a project adopts SDD,
all rules in this directory apply.

This directory defines every standard a spec file in this workspace
conforms to: three external standards, a workspace extensions file, a
design-layer companion, an integration walkthrough, and a tooling overview.

## Core principles

**Spec-anchored.** The spec and the code are co-maintained as peers — the
spec has authority, and machine-verified traceability keeps them in sync.
Code is primarily edited by agents rather than by hand. Term from
Böckeler, *Three Schools of Spec-Driven Development Tools*; see
[ADR-003](../docs/adr/003-evaluate-sdd-community-landscape.md) for the
landscape evaluation that led to this position.

**SDD Triangle.** Spec, tests, and code do not stay automatically
synchronized — implementation continuously surfaces gaps. Every divergence
is a tracked action item; the default reconciliation is that the spec wins
and code updates to match, but the human decides per case. Term from
Breunig, *The Spec-Driven Development Triangle*.

**Behavioral versus technical requirements.** Functional requirements are
about behavior; technical requirements are about system qualities —
performance, security, scalability, reliability. Technical requirements
are valid spec items in the same format but are consciously omitted in
this workspace, since personal projects rarely have meaningful technical
constraints. Projects that do have them `MAY` add them following the same
rules.

## Files

| File | Purpose |
|---|---|
| [rfc2119.md](rfc2119.md) | RFC 2119 obligation vocabulary. External standard, as defined. |
| [ears.md](ears.md) | EARS sentence templates. External standard, as defined. |
| [oft-format.md](oft-format.md) | OpenFastTrace Requirement-Enhanced Markdown: item structure, IDs, keywords, linking, coverage. External standard, as defined. |
| [extensions.md](extensions.md) | Workspace subsets, constraints, and extension keywords (`Interface:`, `AgentReview:`). The load-bearing file for authoring. |
| [design-layer.md](design-layer.md) | Design-phase semantics: commitment framing and the four decision dimensions. |
| [spec-format.md](spec-format.md) | Integration walkthrough showing how the four standards combine in a single spec file. |
| [tooling.md](tooling.md) | Tool overview — `pytest-sdd`, `sdd-chain`, `sdd-index`, `sdd-atlas`, `sdd-review`. Describes what enforces the rules in the other files. |

## Where to start

A new author writing their first spec:

1. [spec-format.md](spec-format.md) — the integration walkthrough.
2. [extensions.md](extensions.md) — workspace rules that override defaults.
3. The remaining files as needed.

An agent entering an SDD phase reads the standards files relevant to its
phase; the SKILL.md for each phase names which.

## External references

- Bradner, S. *Key words for use in RFCs to Indicate Requirement Levels.*
  RFC 2119 / BCP 14. IETF, March 1997.
  https://www.rfc-editor.org/rfc/rfc2119
- Leiba, B. *Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words.*
  RFC 8174. IETF, May 2017. https://www.rfc-editor.org/rfc/rfc8174
- Mavin, A., Wilkinson, P., Harwood, A., and Novak, M. *Easy Approach to
  Requirements Syntax (EARS).* 17th IEEE International Requirements
  Engineering Conference (RE'09), 2009. DOI: 10.1109/RE.2009.9
- OpenFastTrace user guide and repository:
  https://github.com/itsallcode/openfasttrace

## Adjacent reading

- *Painless Functional Specifications*, Parts 1–4. Spolsky, October 2000.
- *Design Docs at Google.* Ubl, Industrial Empathy.
- *Engineering Practices for LLM Application Development.* Tan & Wang,
  ThoughtWorks, February 2024.
- *Exploring Gen AI: Three Schools of Spec-Driven Development Tools.*
  Böckeler, martinfowler.com, 2026.
  https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html
- *The Spec-Driven Development Triangle.* Breunig, March 2026.
  https://www.dbreunig.com/2026/03/04/the-spec-driven-development-triangle.html
