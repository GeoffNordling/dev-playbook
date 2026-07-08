# standards/ — index

The catalog: every standard has a card here (`type: Standard Card`), and
each card's cells point at the files that define, audit, enforce, and adopt
it. See [Standards and Standard Cards](/standards/standard/format.md).
Ordered by level of abstraction — meta first — then alphabetically within
a level.

> **Temporary:** most entries below predate the card format and have no
> standard card yet; cataloging them is tracked in
> [issue #133](https://github.com/GeoffNordling/dev-playbook/issues/133).

- [Standards](/standards/README.md) — Cross-project engineering standards that apply to every repository in the workspace
- [Meta-Standard](/standards/standard.md) — Card for the meta-standard — how standards are declared as cards, cataloged, and kept honest
- [Standards and Standard Cards](/standards/standard/format.md) — What a standard is and the standard-card format — four pointer cells that catalog every standard for one-hop lookup
- [Build](/standards/build.md) — Card for the build standard — how a repository is laid out, built, and checked
- [Claude Code Harness Files](/standards/claude-code.md) — Card for the Claude Code harness-files standard — which repo files the harness consumes and what each contains
- [ADR Conventions](/standards/adr-conventions.md) — When to write an ADR, its template, sequential numbering, and the hard-to-reverse-or-surprising bar that justifies one
- [Agentic Box](/standards/agentic-box.md) — The delegation boundary for autonomous agent work — walls, charter, checks, and emissions around a sealed black box
- [Doc Conventions](/standards/doc-conventions.md) — How Markdown docs are written — voice, structure, brevity, current-state-only, one concern per document
- [Issue Conventions](/standards/issue-conventions.md) — GitHub issue body format — the body as agent brief, vertical-slice decomposition, blocked-by and sub-issue relationships
- [Module Design](/standards/module-design.md) — How to design modules with good interfaces — deep modules, the deletion test, designing for testability
- [Python Style](/standards/python-style.md) — Default Python language conventions and anti-pattern catalog — fail-loud, docstrings, module layout, helper extraction
- [Repository Settings](/standards/repo-settings.md) — GitHub repository settings every repo should have — squash-only merges, PR message format, auto-deleted merged branches
- [Skill Conventions](/standards/skill-conventions.md) — Skill-bundle format — frontmatter fields, SKILL.md structure, and directory organization
- [Skill Management](/standards/skill-management.md) — Where skills live, how third-party skills are installed, and the mirror rule between authored and installed
- [Testing Conventions](/standards/testing-conventions.md) — Default pytest conventions — structure, behavioral focus, test doubles, fixtures, and humble objects

## Directories

- [agentic-box/templates/greenfield-cli/](/standards/agentic-box/templates/greenfield-cli/index.md) — The worked greenfield-CLI box template
- [build/](/standards/build/index.md) — The layered repo standard, one concern per document — layers, skeleton, the Python project, Make, canonical artifacts, distribution, thin CI, enforcement
- [claude-code/](/standards/claude-code/index.md) — The Claude Code harness-files standard — the member registry and the CLAUDE.md content standard
- [docs/](/standards/docs/index.md) — The documentation-content standard, one concern per document — the OKF bundle, the document-type registry, per-file content docs, indexes, cross-references
- [judgments/](/standards/judgments/index.md) — The judgments standard, one concern per document — declarations, the cache gate, consuming from another repo
- [references/](/standards/references/index.md) — Verbatim mirrors of external documents, vendored for network-free reading
