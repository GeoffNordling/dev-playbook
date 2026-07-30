# standards/ — index

The catalog: every standard has a card here (`type: Standard-Card`), and
each card's cells point at the files that define, audit, enforce, and
adopt it. See [Standards and Standard Cards](/standards/standard/format.md).
Ordering: README, then the cards — meta-standard first, the rest
alphabetical — then the contract documents not listed by a child index,
alphabetical; directories last.

- [Standards](/standards/README.md) — Cross-project engineering standards that apply to every repository in the workspace
- [Meta-Standard](/standards/standard.md) — Card for the meta-standard — how standards are declared as cards, cataloged, and kept honest
- [Build](/standards/build.md) — Card for the build standard — how a repository is laid out, built, and checked
- [Claude Code Harness Files](/standards/claude-code.md) — Card for the Claude Code harness-files standard — how harness-consumed files are distinguished from ordinary files and what each contains
- [Decision Records](/standards/decisions.md) — Card for the decision-records standard — how hard-to-reverse decisions are recorded
- [Instruments](/standards/instrument.md) — Card for the instrument standard — how purpose-built devices are specified and kept conformant
- [Knowledge Organization](/standards/knowledge-organization.md) — Card for the knowledge-organization standard — how knowledge is organized in markdown
- [Module Design](/standards/modules.md) — Card for the module-design standard — how modules are designed
- [Prose](/standards/prose.md) — Card for the prose standard — how workspace prose is written
- [Python](/standards/python.md) — Card for the Python standard — how Python source code is written
- [Python Testing](/standards/testing.md) — Card for the Python-testing standard — how Python tests are written
- [Semantic Validation](/standards/semantic-validation.md) — Card for the semantic-validation standard — how claims only language can check are validated and kept from drifting
- [Shell](/standards/shell.md) — Card for the shell standard — how shell is written
- [Software Factory](/standards/software-factory.md) — Card for the software factory standard — how an idea becomes a merged pull request
- [System Legibility](/standards/legibility.md) — Card for the system-legibility standard — how a human understands a large system they did not write and will not read directly
- [Tracking](/standards/tracking.md) — Card for the tracking standard — how committed and uncommitted work is tracked through issues, candidates, and repository settings
- [Adopting a Repo-Scoped Standard](/standards/standard/consuming.md) — The consumer-repo recipe for a first repo-scoped standard — grow the standards/ tree, write and publish a conforming detector, mirror it, and gate it
- [Decision Record Conventions](/standards/decisions/records.md) — When to write a Decision Record, its template, sequential numbering, immutability, status vocabulary, scope, and the hard-to-reverse-or-surprising bar that justifies one
- [Doc Conventions](/standards/prose/conventions.md) — How Markdown docs are written — voice, structure, brevity, current-state-only, one concern per document
- [Instruments and Instrument Specs](/standards/instrument/format.md) — What an instrument is and the Instrument Spec contract every instrument carries
- [Module Design](/standards/modules/design.md) — How to design modules with good interfaces — deep modules, the deletion test, designing for testability
- [Python Style](/standards/python/style.md) — Default Python language conventions and anti-pattern catalog — fail-loud, docstrings, module layout, helper extraction
- [Shell Conventions](/standards/shell/conventions.md) — How shell is written — glue-only boundary, strict mode, declared bash, shellcheck-clean
- [Standards and Standard Cards](/standards/standard/format.md) — What a standard is and the standard-card format — four pointer cells that catalog every standard for one-hop lookup
- [Testing Conventions](/standards/testing/conventions.md) — Default pytest conventions — structure, behavioral focus, test doubles, fixtures, and humble objects

## Directories

- [build/](/standards/build/index.md) — The layered repo standard, one concern per document — layers, skeleton, the Python project, Make, canonical artifacts, distribution, thin CI, enforcement, bootstrap
- [claude-code/](/standards/claude-code/index.md) — The Claude Code harness-files standard — the member registry, the CLAUDE.md content standard, and the skill conventions
- [docs/](/standards/docs/index.md) — The documentation-content standard, one concern per document — the OKF bundle, the document-type registry, per-file content docs, indexes, cross-references
- [judgments/](/standards/judgments/index.md) — The judgments standard, one concern per document — declarations, the cache gate, consuming from another repo
- [references/](/standards/references/index.md) — Verbatim mirrors of external documents, vendored for network-free reading
- [tracking/](/standards/tracking/index.md) — The tracking standard's contract — issue conventions and repository settings
