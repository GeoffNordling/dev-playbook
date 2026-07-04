---
type: Standard
title: Repo Documentation Standard
description: Content and scope of the documentation files — README, CLAUDE.md, index.md, CONTEXT.md, cross-references — and the OKF concept-doc/harness-owned bundle boundary
---

# Repo Documentation Standard

## Purpose

Define the content and scope of every documentation file in a workspace repository, so that any human or agent can open a repo cold and immediately orient — what it is, how to operate it, and where to find the rest. Which files must exist is declared once, in the build standard's [file skeleton](/standards/build/skeleton.md); this document governs what goes inside them.

A repo's agent-navigated documentation is one Open Knowledge Format (OKF) bundle: every concept document declares its `type`, `title`, and `description` in frontmatter, so an agent triages by frontmatter and navigates by the per-directory `index.md` listings, loading full bodies only where relevant. [The OKF bundle](#the-okf-bundle) defines the boundary; [document-types.md](/standards/document-types.md) defines the types.

## Principles

**Scope is standardized; depth is not.** Every file has a defined scope (what goes in it), but depth varies by project. A CLI tool's README may be 10 lines. A simulation's may be 100. Both are conformant if the content stays within scope.

**Presence is the status signal.** There are no explicit status fields. The presence or absence of optional files signals the project's stage. A missing `CONTEXT.md` means no domain terms have needed pinning yet; a populated `specs/` directory means the project is complex enough to warrant formal requirements.

**Triage by frontmatter.** Every concept document opens with OKF frontmatter — `type`, `title`, `description`. An agent reads the frontmatter (and the directory's `index.md`) to decide what a document is and whether to open it, before paying the context cost of the body.

**No duplication across files.** Each piece of information has exactly one home. Files reference each other rather than repeating content.

**Voice and structure are standardized.** Every doc in this hierarchy follows [doc-conventions.md](/standards/doc-conventions.md) — declarative present tense, one rule per section, current-state only.

## The OKF bundle

This repo's agent-navigated documentation is one [Open Knowledge Format (OKF)](https://github.com/GoogleCloudPlatform/knowledge-catalog) bundle, per the [OKF SPEC](/standards/references/okf-spec.md). The bundle is the whole repository: an agent triages a document by its frontmatter and navigates between documents by the per-directory `index.md` listings, loading full bodies only when a document is relevant.

Not every file in the repo is a **concept document**. The bundle divides in two:

- **Concept documents** — prose knowledge a reader loads to *understand* something: standards, guides, surveys, ADRs, READMEs, the domain vocabulary. Each carries OKF frontmatter (`type` + `title` + `description`, per [document-types.md](/standards/document-types.md)) and is subject to the type-lint.
- **Harness-owned files** — files a tool *consumes as configuration or runs as code*, not prose a reader loads to learn: `CLAUDE.md`, skill `SKILL.md` and their `references/`, `rules/`, `settings*.json`, `hooks/`, `.js` workflows, and checked-in code. These carry no OKF frontmatter and are not type-linted. They keep whatever format their consumer requires — a `SKILL.md` keeps its Claude Code frontmatter (`name`, `model`, …), not OKF frontmatter.

The test is *how the file is used*, not where it sits: everything is in the repo, hence in the bundle; harness-owned files are simply in-bundle non-concept-documents. `CLAUDE.md` is the worked example — it is prose a human could read, but an agent's harness loads it as operating configuration, so it is harness-owned and carries no OKF frontmatter.

See [document-types.md](/standards/document-types.md) for the concept-document type registry and the frontmatter field profile.

## Audience

Who is expected to read a file. These are intended audiences, not access
restrictions — a human may read CLAUDE.md; an agent may read a human-audience
file.

## Files

Presence (required vs optional) is not restated here — it lives in the
build standard's [skeleton tables](/standards/build/skeleton.md).

| File | Type | Audience | Scope |
|---|---|---|---|
| `CLAUDE.md` | Harness-owned | Agent | How to operate in this repo: build/run/test commands, rules, pointers to other docs. `SHALL NOT` contain what the project is, why it exists, or developer profile information. |
| `README.md` | `README` | Human + Agent | What the project does, prerequisites, how to run it. `SHALL NOT` contain agent instructions or architecture decisions. |
| `index.md` | — (typeless) | Human + Agent | Per-directory navigational listing: the directory's README, its concept documents (each with its `description`), and links to child indexes. Carries no OKF frontmatter. See [index.md](#indexmd). |
| `specs/` | — (SDD) | Human + Agent | Functional requirements and optionally system design, as flat files or hierarchical folders. Governed by the SDD standards, not this OKF profile. See the [SDD standards index](~/workspace/spec-tools/sdd-standards/README.md) for content conventions and [spec-standard.md — File organization](~/workspace/spec-tools/sdd-standards/spec-standard.md#4-file-organization) for file layout and splitting rules. |
| `docs/` | Concept docs | Human + Agent | Supplementary documentation that does not belong in README, specs, or CLAUDE.md — guides, surveys, and the ADR subdirectory. Each file is a concept document with its own `type`. |
| `docs/adr/` | `ADR` | Human + Agent | Architectural decision records. One per file, immutable once written, listed by `docs/adr/index.md`. See [ADR conventions](#adr-conventions) for numbering, template, and offer-gate. |
| `CONTEXT.md` | `Vocabulary` | Human + Agent | Domain glossary at the repo root: canonical terms, their relationships, and illustrative scenarios. Created lazily as terminology ambiguity surfaces; do not pre-populate. See [CONTEXT.md format](#contextmd-format) for the structure. |
| `<dir>/CLAUDE.md` | Harness-owned | Agent | Nested rules for a directory whose operating conventions diverge from the repo root. See [CLAUDE.md hierarchy](#claudemd-hierarchy). |
| `.gitignore` | Harness-owned | Tooling | Git ignore rules. See [.gitignore baseline](#gitignore-baseline). |

## index.md

An `index.md` is a navigational listing that lets an agent see what a directory contains — and read each document's one-line `description` — without opening every file. `index.md` is **typeless**: it carries no OKF `type` and is not itself a concept document.

### Content

An `index.md` lists, for its own directory:

- the directory's `README.md` (if present), then
- each concept document, as a markdown link carrying the document's frontmatter `description`.

For child directories, it links the child's own `index.md` rather than reaching into it. A subdirectory is recursed into inline **only when it has no `index.md` of its own** — otherwise the listing delegates to that child index.

The repository root `index.md` additionally declares the bundle's OKF version in frontmatter (its only frontmatter key):

```yaml
---
okf_version: "0.1"
---
```

### Authored, not generated

`index.md` files are **authored**, not produced by a committed generator. A staleness checker (a pre-commit hook, alongside `ref-check` and the type-lint) fails the commit when an index omits a concept document in its directory, lists one that no longer exists, or gives a description that no longer matches the child's frontmatter. The check keeps hand-authored indexes honest without a generator owning the file.

## README.md baseline

A README's floor is its OKF frontmatter — `type: README`, `title`,
`description`, per [document-types.md](/standards/document-types.md) —
followed by an H1 and a one-line purpose. This is the floor, not the
ceiling: depth varies by project ("Scope is standardized; depth is not"),
and a README `MAY` add prerequisites, quick-start, architecture overview,
or examples as the project earns them.

## CLAUDE.md baseline

`CLAUDE.md` is harness-owned — an agent's harness loads it as operating
configuration, not as prose to learn from — so it carries no OKF frontmatter.
Every workspace repo's `CLAUDE.md` starts from the canonical baseline,
[/standards/canonical/CLAUDE.md](/standards/canonical/CLAUDE.md).

The `## Build` section is universal — every repo has `make check` (see
[make.md](/standards/build/make.md)). Project-specific
operating rules accumulate under `## Rules` as the repo evolves.

## CLAUDE.md hierarchy

Claude Code loads `CLAUDE.md` files by walking up the directory tree from the session's cwd, stacking each file it finds. A session inside `<repo>/<dir>/` therefore receives both the nested `CLAUDE.md` and the repo-root `CLAUDE.md`.

A repository `MAY` add a nested `CLAUDE.md` in a directory whose operating conventions diverge from the repo root (e.g. `dotfiles/` in dev-playbook). The nested file holds **only the delta** — content already in the parent `SHALL NOT` be repeated. A directory with nothing repo-divergent to say doesn't need one.

Nested files follow the same scope as the root: operational instructions for an agent operating inside that directory. They `SHALL NOT` contain project description, architecture decisions, or roadmap — those belong elsewhere in the documentation hierarchy.

## ADR conventions

See [adr-conventions.md](/standards/adr-conventions.md).

## CONTEXT.md format

### Structure

The canonical stylized example is
[/standards/canonical/CONTEXT.md](/standards/canonical/CONTEXT.md) —
frontmatter, `## Language`, `## Relationships`, `## Example dialogue`,
`## Flagged ambiguities`.

### Rules

- **Be opinionated.** When multiple words exist for the same concept, pick the best one and list the others as aliases to avoid.
- **Flag conflicts explicitly.** If a term is used ambiguously, call it out in "Flagged ambiguities" with a clear resolution.
- **Keep definitions tight.** One sentence max. Define what it IS, not what it does.
- **Show relationships.** Use bold term names and express cardinality where obvious.
- **Only include terms specific to this project's context.** General programming concepts (timeouts, error types, utility patterns) don't belong even if the project uses them extensively. Before adding a term, ask: is this a concept unique to this context, or a general programming concept? Only the former belongs.
- **Group terms under subheadings** when natural clusters emerge. If all terms belong to a single cohesive area, a flat list is fine.
- **Write an example dialogue.** A conversation between a dev and a domain expert that demonstrates how the terms interact naturally and clarifies boundaries between related concepts.

### Location

One `CONTEXT.md` at the repo root.

## .gitignore baseline

The baseline entries are a canonical artifact — this document does not
restate them (see
[canonical.md](/standards/build/canonical.md)).
Repos `MAY` extend with project-specific paths.

## Cross-references

A cross-reference points from one document to another. Which form it takes depends on whether the target lives in the **same bundle** (this repo) or in **another repo**. Both forms are inline — there is no separate citations section.

### Link — same bundle

A reference to another document in *this* repo uses a **root-absolute path**: a target beginning with `/`, interpreted relative to the bundle root (the repo root).

```markdown
[doc-conventions.md](/standards/doc-conventions.md)
```

A root-absolute link resolves against the reader's *own* checkout root — the current working directory's repo — so it is **worktree-safe**: it points at the copy of the file that matches the checkout the reader is already in, whether that's the main checkout or a per-issue worktree. A same-repo reference `SHALL NOT` be written as `~/workspace/<this-repo>/…` — from inside a worktree that absolute path silently jumps to the main checkout, yielding a different (possibly stale) copy than the one the reader is working in.

The deciding factor is whether the referencing file has a **fixed repo root** — a single repo it is always read from. Concept documents do, and so does a repo's own `CLAUDE.md` (Claude Code only loads it when the session is already inside that repo), so both use the Link form for same-repo targets. Files with **no fixed repo root** — skills and global `~/.claude/` config such as `rules/`, loaded across arbitrary repos — have no root for `/` to resolve against, so they use the Citation form even for a same-repo target (see [skill-conventions.md — Cross-references](/standards/skill-conventions.md#cross-references)).

### Citation — another repo

A reference to a document in a *different* repo uses its **full workspace path**, beginning with `~/workspace/`:

```markdown
[SDD standards index](~/workspace/spec-tools/sdd-standards/README.md)
```

A cross-repo citation always resolves to that repo's canonical main checkout, which is the intended behavior — it references another repo's published state, not whatever worktree is currently open. `~/workspace/<repo>` is self-describing: the repo name is in the path, so no external convention is needed to interpret it.

VS Code does not expand `~/` in markdown links, and it resolves a leading `/` against the filesystem root rather than the bundle root, so neither form is clickable from the editor ([vscode#103542](https://github.com/microsoft/vscode/issues/103542)). Accepted — agents are the primary audience, and both forms are what the `ref-check` linter (`/tools/bin/ref-check`) validates. Anything else — backticked filenames like `` `conftest.py` ``, slash-skill invocations like `/commit` — is treated as prose by `ref-check`.

### Fenced code blocks

Fenced code blocks delimited by triple backticks or `~~~` may contain `~/workspace/` paths or `/`-root paths in shell examples or sample output; `ref-check` skips them. For example:

```bash
# Run ref-check from any workspace repo:
python3 ~/workspace/dev-playbook/tools/bin/ref-check .
```

### Fragment anchors

A cross-reference `MAY` append `#anchor` to target a specific heading in a markdown file. The anchor `MUST` match the heading's GitHub slug — `ref-check` computes and validates the slug, so a stale or misspelled anchor fails the commit.

**Prefer a stable named anchor over a positional one.** A numbered fragment (`#223-revision`) or an in-prose heading-number citation (`§2.10`, `§2.2.3`) breaks silently the moment its target is renumbered or reordered — nothing flags the stale anchor. Where the target heading carries a stable named slug, cite that. Where the target numbers every heading positionally and exposes no stable anchor, name the **concept** the heading carries and drop the number, so a reader finds it by name rather than by a position that drifts.
