# standards/ — index

The catalog: every standard has a card here (`type: Standard-Card`), and
each card's cells point at the files that define, audit, enforce, and
adopt it. See [Standards and Standard Cards](/standards/standard/format.md).
Ordering: README, then the cards — meta-standard first, the rest
alphabetical — then the contract documents not listed by a child index,
alphabetical; directories last.

- [Standards](/standards/README.md) — Cross-project engineering standards that apply to every repository in the workspace
- [Meta-Standard](/standards/standard.md) — Governs how the workspace's standards themselves are declared, found, and kept honest — the card format, the catalog, and drift
- [Build](/standards/build.md) — Governs how a repository is laid out, built, and checked — layers, skeleton, Make, canonical artifacts, distribution, CI, and enforcement
- [Decision Records](/standards/decisions.md) — Governs how hard-to-reverse or surprising decisions are recorded — the Decision Record's warrant, template, numbering, immutability, and status vocabulary
- [Harness Files](/standards/harness.md) — Governs how the files an agent harness loads — context, configuration, instructions — are distinguished from ordinary files and what each contains
- [Instruments](/standards/instrument.md) — Governs how purpose-built devices — artifact formats with tooling — are specified and kept conformant
- [Knowledge Organization](/standards/knowledge-organization.md) — Governs how knowledge is organized in markdown — file roles, document types, indexes, cross-references, and working documentation sets
- [Module Design](/standards/modules.md) — Governs how modules are designed — interfaces, depth, and seams
- [Prose](/standards/prose.md) — Governs how prose is written in every workspace document — voice, structure, and brevity
- [Python](/standards/python.md) — Governs how Python source code is written — language conventions and the anti-pattern catalog
- [Python Testing](/standards/testing.md) — Governs how Python tests are written — structure, behavioral focus, test doubles, fixtures, and humble objects
- [Semantic Validation](/standards/semantic-validation.md) — Governs how claims only language can check — accuracy, honesty, scope — are validated and kept from drifting as the underlying files change
- [Shell](/standards/shell.md) — Governs how shell is written — the glue-only boundary, strict mode, declared bash, and shellcheck-clean
- [Software Factory](/standards/software-factory.md) — Governs how an idea becomes a merged pull request — the state graph, the node contracts, review, and the user's checkpoints
- [Tracking](/standards/tracking.md) — Governs how work is tracked — candidates, issue authoring, factory labels, tracker operations, and repository settings
- [Adopting a Repo-Scoped Standard](/standards/standard/consuming.md) — The consumer-repo recipe for a first repo-scoped standard — grow the standards/ tree, write and publish a conforming detector, mirror it, and gate it
- [Decision Record Conventions](/standards/decisions/records.md) — When to write a Decision Record, its template, sequential numbering, immutability, status vocabulary, scope, and the hard-to-reverse-or-surprising bar that justifies one
- [Instruments and Instrument Specs](/standards/instrument/format.md) — What an instrument is and the Instrument Spec contract every instrument carries
- [Python Style](/standards/python/style.md) — Default Python language conventions and anti-pattern catalog — fail-loud, docstrings, module layout, helper extraction
- [Shell Conventions](/standards/shell/conventions.md) — How shell is written — glue-only boundary, strict mode, declared bash, shellcheck-clean
- [Standards and Standard Cards](/standards/standard/format.md) — What a standard is and the standard-card format — four pointer cells that catalog every standard for one-hop lookup
- [Testing Conventions](/standards/testing/conventions.md) — Default pytest conventions — structure, behavioral focus, test doubles, fixtures, and humble objects

## Directories

- [build/](/standards/build/index.md) — The layered repo standard, one concern per document — layers, skeleton, the Python project, Make, canonical artifacts, distribution, thin CI, enforcement, bootstrap
- [harness/](/standards/harness/index.md) — The harness-files standard, one concern per document — the member registry, CLAUDE.md content, the instruction grammar, runbook conventions
- [knowledge-organization/](/standards/knowledge-organization/index.md) — The documentation-content standard, one concern per document — the OKF bundle, the document-type registry, per-file content docs, indexes, cross-references, working documentation sets
- [prose/](/standards/prose/index.md) — The prose standard's contract, one concern per document — conventions and the slop-tics catalog
- [references/](/standards/references/index.md) — Verbatim mirrors of external documents, vendored for network-free reading
- [semantic-validation/](/standards/semantic-validation/index.md) — The judgments standard, one concern per document — declarations, the cache gate, consuming from another repo
- [tracking/](/standards/tracking/index.md) — The tracking standard's contract, one concern per document — candidate conventions, issue authoring, repository settings, tracker operations
