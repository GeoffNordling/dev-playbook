# standards/ — index

The catalog: every standard is one directory here, holding its card
(`type: Standard-Card`) and the Standards the card's Define cell points
at, and each row below carries the card's question sentence. See
[Card Cells](/doc-types/standard-card/contract-shape.md). One directory,
`references/`, is no standard: it holds the upstream specifications the
Standards cite.
Ordering: README, then the directories — meta-standard first, the rest
alphabetical.

- [Standards](/standards/README.md) — Cross-project engineering standards that apply to every repository in the workspace

## Directories

- [standard/](/standards/standard/index.md) — Governs how the workspace's standards themselves are declared, found, and kept honest — the card, the catalog, the detectors, and the gates
- [build/](/standards/build/index.md) — Governs how a repository is laid out, built, and checked — the file skeleton, the canonical artifacts, and the Python project
- [decisions/](/standards/decisions/index.md) — Governs how hard-to-reverse or surprising decisions are recorded — the Decision Record's warrant, template, numbering, immutability, and status vocabulary
- [distribution/](/standards/distribution/index.md) — Governs how dev-playbook's checks reach the governed repos — the published hook, the roster, dogfooding, and the pinned rev
- [harness/](/standards/harness/index.md) — Governs how the files Claude Code loads are written — a CLAUDE.md's content and a runbook's format
- [knowledge-organization/](/standards/knowledge-organization/index.md) — Governs how knowledge is organized in markdown — document types, indexes, the README and CONTEXT.md, cross-references, and documentation sets
- [modules/](/standards/modules/index.md) — Governs how modules are designed — interfaces, depth, and seams
- [prose/](/standards/prose/index.md) — Governs how prose is written in every workspace document — voice, structure, and brevity
- [python/](/standards/python/index.md) — Governs how Python source is written — fail-loud code, docstrings, module layout, helpers, formatting, and type annotations
- [references/](/standards/references/index.md) — Verbatim mirrors of external documents, vendored for network-free reading
- [shell/](/standards/shell/index.md) — Governs how shell is written — the glue-only boundary, strict mode, declared bash, and the shellcheck and shfmt bars every file clears
- [testing/](/standards/testing/index.md) — Governs how Python tests are written — the pytest framework, mirror layout, test structure, behavioral focus, doubles, and fixtures
- [tracking/](/standards/tracking/index.md) — Governs how work is tracked — candidates, issue shapes, the label scheme, and repository settings
