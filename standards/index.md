# standards/ — index

The catalog: every standard has a card here (`type: Standard-Card`), and
each card's cells point at the files that define, audit, enforce, and
adopt it. See [Card Cells](/doc-types/standard-card/contract-shape.md).
Ordering: README, then the cards — meta-standard first, the rest
alphabetical — then the contract documents not listed by a child index,
alphabetical; directories last.

- [Standards](/standards/README.md) — Cross-project engineering standards that apply to every repository in the workspace
- [Meta-Standard](/standards/standard.md) — Governs how the workspace's standards themselves are declared, found, and kept honest — the card, the catalog, the detectors, and the gates
- [Build](/standards/build.md) — Governs how a repository is laid out, built, and checked — the file skeleton, the canonical artifacts, and the Python project
- [Decision Records](/standards/decisions.md) — Governs how hard-to-reverse or surprising decisions are recorded — the Decision Record's warrant, template, numbering, immutability, and status vocabulary
- [Distribution](/standards/distribution.md) — Governs how dev-playbook's checks reach the governed repos — the published hook, the roster, dogfooding, and the pinned rev
- [Harness Files](/standards/harness.md) — Governs how the files Claude Code loads are written — a CLAUDE.md's content and a runbook's format
- [Instruments](/standards/instrument.md) — Governs how purpose-built devices — artifact formats with tooling — are specified and kept conformant
- [Knowledge Organization](/standards/knowledge-organization.md) — Governs how knowledge is organized in markdown — document types, indexes, the README and CONTEXT.md, cross-references, and working documentation sets
- [Module Design](/standards/modules.md) — Governs how modules are designed — interfaces, depth, and seams
- [Prose](/standards/prose.md) — Governs how prose is written in every workspace document — voice, structure, and brevity
- [Python](/standards/python.md) — Governs how Python source is written — fail-loud code, docstrings, module layout, helpers, formatting, and type annotations
- [Python Testing](/standards/testing.md) — Governs how Python tests are written — the pytest framework, mirror layout, test structure, behavioral focus, doubles, and fixtures
- [Semantic Validation](/standards/semantic-validation.md) — Governs how claims only language can check — accuracy, honesty, scope — are validated and kept from drifting as the underlying files change
- [Shell](/standards/shell.md) — Governs how shell is written — the glue-only boundary, strict mode, declared bash, and the shellcheck and shfmt bars every file clears
- [Tracking](/standards/tracking.md) — Governs how work is tracked — candidates, issue shapes, the label scheme, and repository settings
- [Decision Record Conventions](/standards/decisions/records.md) — How a Decision Record is written, from the bar that warrants one and the directory that holds it to its scope, template, date, numbering, immutability, status vocabulary, optional sections, and the pin on an external-convention evaluation
- [Distribution Channel](/standards/distribution/channel.md) — How dev-playbook's checks reach the governed repos — the one published hook, the roster, a publisher's local block, and a consumer's pinned rev
- [Instruments and Instrument Specs](/standards/instrument/format.md) — What an instrument is and the Instrument Spec contract every instrument carries
- [Module Design Conventions](/standards/modules/design.md) — The deep-module contract — depth, the deletion test, the seam rules, and the port at a process boundary
- [Python Style](/standards/python/style.md) — How a Python file is written — empty initializers, docstrings, fail-loud values, statement order, banned future imports, helper shape, formatting, and annotations
- [Shell Conventions](/standards/shell/conventions.md) — How a shell file is written — the glue boundary, strict mode, declared bash, the shellcheck and shfmt bars, and what a sourced fragment carries
- [Testing Conventions](/standards/testing/conventions.md) — How a repo's Python test suite is written — the pytest framework, mirror layout, test structure, behavioral focus, doubles, and fixtures

## Directories

- [build/](/standards/build/index.md) — The build standard's Standards, one population each, and the guide to joining the workspace — the file skeleton, the canonical artifacts, the Python project, bootstrap
- [harness/](/standards/harness/index.md) — The Harness Files card's two Standards, one object each — a CLAUDE.md and a runbook — and the two guides beside them: the registry of what Claude Code loads and the craft of writing for an agent
- [knowledge-organization/](/standards/knowledge-organization/index.md) — The documentation-content standard, one concern per document — the OKF bundle, the document-type registry, per-file content docs, indexes, cross-references, working documentation sets
- [prose/](/standards/prose/index.md) — The prose standard's contract, one concern per document — conventions and the slop-tics catalog
- [references/](/standards/references/index.md) — Verbatim mirrors of external documents, vendored for network-free reading
- [semantic-validation/](/standards/semantic-validation/index.md) — The Semantic Validation card's one Standard, a repo's judgment declarations, and the guides to the cache gate and to consuming the tooling
- [standard/](/standards/standard/index.md) — The Meta-Standard card's three Standards, one object each (the card catalog, a gate, and a detector), and the guide to standing up a repo-scoped standard in a consumer repo
- [tracking/](/standards/tracking/index.md) — The Tracking card's four Standards, one object each — the candidate register, an issue, a repo's labels, and its GitHub settings — and the guide to linking issues on GitHub
