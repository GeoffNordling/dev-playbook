# Spec-Driven Development Standards

Spec-driven development (SDD) is a project-level commitment. The human
decides whether a project uses this workflow. When a project adopts SDD,
all rules in this directory apply.

This directory defines every standard a spec file in this workspace
conforms to: three external standards (each colocating its workspace
extensions), an integration walkthrough, and a design-layer companion.

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

**Types of requirements.** Functional requirements are
about behavior; design requirements are about organization and methods; technical requirements are about system qualities —
performance, security, scalability, reliability. Technical requirements
are valid spec items in the same format but are consciously omitted in
this workspace, since our personal projects do not have meaningful technical
constraints.

## Composed from external standards

The workspace spec format is built from three external standards, each
contributing one layer:

- **RFC 2119** — defines the obligation vocabulary (`MUST` / `SHALL` /
  `SHOULD` / `MAY`) that grades how strong each requirement is.
- **EARS** — defines sentence templates (*When / If / While / Where*)
  that structure each requirement around its triggering condition.
- **OFT Requirement-Enhanced Markdown** — defines a Markdown item
  format with stable IDs and `Needs:` / `Covers:` links, turning a pile
  of requirement prose into a traceable graph.

We adopt each as-is, then subset, constrain, and extend it for the
workspace. Each of the three primary files below restates its external
standard and then, in a trailing Extensions section, documents the
workspace decisions layered on top. Two companion files show how the
three combine into a single spec file ([spec-format.md](spec-format.md))
and what extra semantics apply to design items
([design-layer.md](design-layer.md)).

## Files

Read in this order:

| File | Purpose |
|---|---|
| [rfc2119.md](rfc2119.md) | RFC 2119 / RFC 8174 (BCP 14) obligation vocabulary, plus the workspace subset, backticking rule, and one-obligation-per-item rule. |
| [ears.md](ears.md) | EARS sentence templates, plus the workspace adoption statement. |
| [oft.md](oft.md) | OpenFastTrace Requirement-Enhanced Markdown: item structure, IDs, keywords, linking, coverage, plus the workspace artifact-type subset, coverage chain, revision policy, verification coverage rule, `Interface:` / `AgentReview:` / `Dimension:` keywords, fenced-code-block constraint, naming convention, and file organization. |
| [spec-format.md](spec-format.md) | Integration walkthrough showing how the three standards combine in a single spec file, plus the illustrative-examples authoring convention. |
| [design-layer.md](design-layer.md) | Design-phase semantics: commitment framing, the decision dimensions, and the per-`dsn` `Dimension:` classification rule. |

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
