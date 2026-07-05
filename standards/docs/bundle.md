---
type: Standard
title: The OKF Bundle
description: The documentation bundle — its purpose, principles, the concept/harness boundary, and the per-file map
---

# The OKF Bundle

Every documentation file in a workspace repository has a defined content
scope, so any human or agent can open a repo cold and immediately orient —
what it is, how to operate it, and where to find the rest. Which files must
exist is declared once, in the build standard's
[file skeleton](/standards/build/skeleton.md); the documents in this
directory govern what goes inside them.

A repo's agent-navigated documentation is one
[Open Knowledge Format (OKF)](https://github.com/GoogleCloudPlatform/knowledge-catalog)
bundle, per the [OKF SPEC](/standards/references/okf-spec.md). The bundle is
the whole repository: an agent triages a document by its frontmatter and
navigates between documents by the per-directory `index.md` listings
([indexes.md](/standards/docs/indexes.md)), loading full bodies only when a
document is relevant.

## Concept documents and harness-owned files

Not every file in the repo is a concept document. The bundle divides in two:

- **Concept documents** — prose knowledge a reader loads to *understand*
  something: standards, guides, surveys, ADRs, READMEs, the domain
  vocabulary. Each carries OKF frontmatter (`type` + `title` +
  `description`, per [document-types.md](/standards/docs/document-types.md)) and
  is subject to the type-lint.
- **Harness-owned files** — files a tool *consumes as configuration or runs
  as code*, not prose a reader loads to learn: `CLAUDE.md`, skill `SKILL.md`
  and their `references/`, `rules/`, `settings*.json`, `hooks/`, `.js`
  workflows, and checked-in code. These carry no OKF frontmatter and are not
  type-linted. They keep whatever format their consumer requires — a
  `SKILL.md` keeps its Claude Code frontmatter (`name`, `model`, …), not OKF
  frontmatter.

The test is *how the file is used*, not where it sits: everything is in the
repo, hence in the bundle; harness-owned files are simply in-bundle
non-concept-documents. `CLAUDE.md` is the worked example — it is prose a
human could read, but an agent's harness loads it as operating
configuration, so it is harness-owned and carries no OKF frontmatter.

## Principles

**Scope is standardized; depth is not.** Every file has a defined scope
(what goes in it), but depth varies by project. A CLI tool's README may be
10 lines. A simulation's may be 100. Both are conformant if the content
stays within scope.

**Presence is the status signal.** There are no explicit status fields. The
presence or absence of optional files signals the project's stage. A missing
`CONTEXT.md` means no domain terms have needed pinning yet; a populated
`specs/` directory means the project is complex enough to warrant formal
requirements.

**No duplication across files.** Each piece of information has exactly one
home. Files reference each other rather than repeating content.

**Voice and structure are standardized.** Every doc in this hierarchy
follows [doc-conventions.md](/standards/doc-conventions.md) — declarative
present tense, one rule per section, current-state only.

## Audience

Who is expected to read a file. These are intended audiences, not access
restrictions — a human may read CLAUDE.md; an agent may read a
human-audience file.

## Files

| File | Type | Audience | Scope |
|---|---|---|---|
| `CLAUDE.md` | Harness-owned | Agent | How to operate in this repo: build/run/test commands, rules, pointers to other docs. `SHALL NOT` contain what the project is, why it exists, or developer profile information. Content: [claude-content.md](/standards/docs/claude-content.md). |
| `README.md` | `README` | Human + Agent | What the project does, prerequisites, how to run it. `SHALL NOT` contain agent instructions or architecture decisions. Content: [readme-content.md](/standards/docs/readme-content.md). |
| `index.md` | — (typeless) | Human + Agent | Per-directory navigational listing: the directory's README, its concept documents (each with its `description`), and links to child indexes. Carries no OKF frontmatter. See [indexes.md](/standards/docs/indexes.md). |
| `specs/` | — (SDD) | Human + Agent | Functional requirements and optionally system design, as flat files or hierarchical folders. Governed by the SDD standards, not this OKF profile. See the [SDD standards index](~/workspace/spec-tools/sdd-standards/README.md) for content conventions and [spec-standard.md — File organization](~/workspace/spec-tools/sdd-standards/spec-standard.md#4-file-organization) for file layout and splitting rules. |
| `docs/` | Concept docs | Human + Agent | Supplementary documentation that does not belong in README, specs, or CLAUDE.md — guides, surveys, and the ADR subdirectory. Each file is a concept document with its own `type`. |
| `docs/adr/` | `ADR` | Human + Agent | Architectural decision records. One per file, immutable once written, listed by `docs/adr/index.md`. See [adr-conventions.md](/standards/adr-conventions.md) for numbering, template, and offer-gate. |
| `CONTEXT.md` | `Vocabulary` | Human + Agent | Domain glossary at the repo root: canonical terms, their relationships, and illustrative scenarios. Created lazily as terminology ambiguity surfaces; do not pre-populate. See [context-content.md](/standards/docs/context-content.md) for the structure. |
| `<dir>/CLAUDE.md` | Harness-owned | Agent | Nested rules for a directory whose operating conventions diverge from the repo root. See [claude-content.md — Hierarchy](/standards/docs/claude-content.md#hierarchy). |
