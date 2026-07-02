---
type: Standard
title: Repo Documentation Standard
description: Repo file hierarchy and scope — README, CLAUDE.md, index.md, docs/adr, CONTEXT.md — plus the OKF concept-doc/harness-owned bundle boundary
---

# Repo Documentation Standard

## Purpose

Define a consistent file hierarchy and scope boundary for every repository in the workspace, so that any human or agent can open a repo cold and immediately orient — what it is, how to operate it, and where to find the rest.

A repo's agent-navigated documentation is one Open Knowledge Format (OKF) bundle: every concept document declares its `type`, `title`, and `description` in frontmatter, so an agent triages by frontmatter and navigates by the per-directory `index.md` listings, loading full bodies only where relevant. [The OKF bundle](#the-okf-bundle) defines the boundary; [document-types.md](/standards/document-types.md) defines the types.

## Principles

**Scope is standardized; depth is not.** Every file has a defined scope (what goes in it), but depth varies by project. A CLI tool's README may be 10 lines. A simulation's may be 100. Both are conformant if the content stays within scope.

**Presence is the status signal.** There are no explicit status fields. The presence or absence of optional files tells you what stage the project is in. A missing `CONTEXT.md` means no domain terms have needed pinning yet; a populated `specs/` directory means the project is complex enough to warrant formal requirements.

**Triage by frontmatter.** Every concept document opens with OKF frontmatter — `type`, `title`, `description`. An agent reads the frontmatter (and the directory's `index.md`) to decide what a document is and whether to open it, before paying the context cost of the body.

**No duplication across files.** Each piece of information has exactly one home. Files reference each other rather than repeating content.

**Voice and structure are standardized.** Every doc in this hierarchy follows [doc-conventions.md](/standards/doc-conventions.md) — declarative present tense, one rule per section, current-state only.

## The OKF bundle

This repo's agent-navigated documentation is one [Open Knowledge Format (OKF)](https://github.com/GoogleCloudPlatform/knowledge-catalog) bundle. The bundle is the whole repository: an agent triages a document by its frontmatter and navigates between documents by the per-directory `index.md` listings, loading full bodies only when a document is relevant.

Not every file in the repo is a **concept document**. The bundle divides in two:

- **Concept documents** — prose knowledge you read to *understand* something: standards, guides, surveys, ADRs, READMEs, the domain vocabulary. Each carries OKF frontmatter (`type` + `title` + `description`, per [document-types.md](/standards/document-types.md)) and is subject to the type-lint.
- **Harness-owned files** — files a tool *consumes as configuration or runs as code*, not prose a reader loads to learn: `CLAUDE.md`, skill `SKILL.md` and their `references/`, `rules/`, `settings*.json`, `hooks/`, `.js` workflows, and Python under `tools/`. These carry no OKF frontmatter and are not type-linted. They keep whatever format their consumer requires — a `SKILL.md` keeps its Claude Code frontmatter (`name`, `model`, …), not OKF frontmatter.

The test is *how the file is used*, not where it sits: everything is in the repo, hence in the bundle; harness-owned files are simply in-bundle non-concept-documents. `CLAUDE.md` is the worked example — it is prose a human could read, but an agent's harness loads it as operating configuration, so it is harness-owned and carries no OKF frontmatter.

See [document-types.md](/standards/document-types.md) for the concept-document type registry and the frontmatter field profile.

## Audience and presence

Every file in the documentation hierarchy has two properties.

### Audience

Who is expected to read the file. These are intended audiences, not access
restrictions — a human may read CLAUDE.md; an agent may read a human-audience
file.

### Presence

Whether the file is required or optional.

| Presence | Meaning |
|---|---|
| Required | Every repository `SHALL` have this file. |
| Optional | A repository `MAY` have this file. Exists when needed, absent when not. |

## Files

| File | Type | Audience | Presence | Scope |
|---|---|---|---|---|
| `CLAUDE.md` | Harness-owned | Agent | Required | How to operate in this repo: build/run/test commands, rules, pointers to other docs. `SHALL NOT` contain what the project is, why it exists, or developer profile information. |
| `README.md` | `README` | Human + Agent | Required | What the project does, prerequisites, how to run it. `SHALL NOT` contain agent instructions or architecture decisions. |
| `index.md` | — (typeless) | Human + Agent | Optional | Per-directory navigational listing: the directory's README, its concept documents (each with its `description`), and links to child indexes. Present in any directory that holds concept documents; carries no OKF frontmatter. See [index.md](#indexmd). |
| `specs/` | — (SDD) | Human + Agent | Optional | Functional requirements and optionally system design, as flat files or hierarchical folders. Governed by the SDD standards, not this OKF profile. See the [SDD standards index](~/workspace/spec-tools/sdd-standards/README.md) for content conventions and [spec-standard.md — File organization](~/workspace/spec-tools/sdd-standards/spec-standard.md#4-file-organization) for file layout and splitting rules. |
| `docs/` | Concept docs | Human + Agent | Optional | Supplementary documentation that does not belong in README, specs, or CLAUDE.md — guides, surveys, and the ADR subdirectory. Each file is a concept document with its own `type`. |
| `docs/adr/` | `ADR` | Human + Agent | Optional | Architectural decision records. One per file, immutable once written, listed by `docs/adr/index.md`. See [ADR conventions](#adr-conventions) for numbering, template, and offer-gate. |
| `CONTEXT.md` | `Vocabulary` | Human + Agent | Optional | Domain glossary at the repo root: canonical terms, their relationships, and illustrative scenarios. Created lazily as terminology ambiguity surfaces; do not pre-populate. See [CONTEXT.md format](#contextmd-format) for the structure. |
| `<sub-project>/CLAUDE.md` | Harness-owned | Agent | Optional | Sub-project rules within a repo, when the repo holds distinct sub-projects with divergent operating conventions. See [CLAUDE.md hierarchy](#claudemd-hierarchy). |
| `.gitignore` | Harness-owned | Tooling | Required | Git ignore rules. Every repo has one. See [.gitignore baseline](#gitignore-baseline). |

## index.md

Every directory that holds concept documents carries an `index.md`: a navigational listing that lets an agent see what a directory contains — and read each document's one-line `description` — without opening every file. `index.md` is **typeless**: it carries no OKF `type` and is not itself a concept document.

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

Every workspace repo's `README.md` starts from this baseline:

````markdown
---
type: README
title: <repo-name>
description: <one-line summary of what the repo is>
---

# <repo-name>

<one-line purpose>
````

This is the floor, not the ceiling. README depth varies by project — see
"Scope is standardized; depth is not." A README `MAY` add prerequisites,
quick-start, architecture overview, or examples as the project earns
them.

## CLAUDE.md baseline

`CLAUDE.md` is harness-owned — an agent's harness loads it as operating
configuration, not as prose to learn from — so it carries no OKF frontmatter.
Every workspace repo's `CLAUDE.md` starts from this baseline:

````markdown
# <repo-name>

## Rules

- See README.md for what this project is.

## Build

`make check` runs the full check surface. See
[build-conventions.md](~/workspace/dev-playbook/standards/build-conventions.md).

## Domain awareness

- Before exploring code, read `CONTEXT.md` and any ADRs in `docs/adr/` touching the area you'll work in. If `CONTEXT.md` is absent, proceed silently — don't flag it or suggest creating it.
- Name domain concepts (issue titles, refactor proposals, hypotheses, test names) using terms defined in `CONTEXT.md`. If a needed concept isn't there, decide: inventing language the project doesn't use (reconsider) or real gap (flag for `/grill-with-docs`).
- If your output contradicts an existing ADR, surface it: `_Contradicts ADR-NNNN — but worth reopening because…_`.
````

The `## Build` section applies only to Python repos. Meta/docs-only repos
omit it. Project-specific operating rules accumulate under `## Rules` as
the repo evolves.

## CLAUDE.md hierarchy

Claude Code loads `CLAUDE.md` files by walking up the directory tree from the session's cwd, stacking each file it finds. A session inside `<repo>/<sub-project>/` therefore receives both the sub-project's `CLAUDE.md` and the repo-root `CLAUDE.md`.

A repository `MAY` add nested `CLAUDE.md` files at sub-project roots when the sub-project has its own build/run/test commands or rules that diverge from the repo root. The nested file holds **only the delta** — content already in the parent `SHALL NOT` be repeated. If a sub-project has nothing repo-divergent to say, it doesn't need a `CLAUDE.md`.

Nested files follow the same scope as the root: operational instructions for an agent operating inside the sub-project. They `SHALL NOT` contain project description, architecture decisions, or roadmap — those belong elsewhere in the documentation hierarchy.

## ADR conventions

See [adr-conventions.md](/standards/adr-conventions.md).

## CONTEXT.md format

### Structure

```md
# {Context Name}

{One or two sentence description of what this context is and why it exists.}

## Language

**Order**:
{A concise description of the term}
_Avoid_: Purchase, transaction

**Invoice**:
A request for payment sent to a customer after delivery.
_Avoid_: Bill, payment request

**Customer**:
A person or organization that places orders.
_Avoid_: Client, buyer, account

## Relationships

- An **Order** produces one or more **Invoices**
- An **Invoice** belongs to exactly one **Customer**

## Example dialogue

> **Dev:** "When a **Customer** places an **Order**, do we create the **Invoice** immediately?"
> **Domain expert:** "No — an **Invoice** is only generated once a **Fulfillment** is confirmed."

## Flagged ambiguities

- "account" was used to mean both **Customer** and **User** — resolved: these are distinct concepts.
```

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

Every workspace repo's `.gitignore` includes these baseline entries:

```
.DS_Store
__pycache__/
*.pyc

# python tooling caches
.venv/
.mypy_cache/
.ruff_cache/
.pytest_cache/

# per-issue git worktrees — keeps the main checkout's `git status` clean;
# does not affect commits/pushes from inside a worktree
.claude/worktrees/
```

Repos `MAY` extend with project-specific paths. Python tooling entries
are harmless in non-Python repos and stay for uniformity.

## Cross-references

A cross-reference points from one document to another. Which form it takes depends on whether the target lives in the **same bundle** (this repo) or in **another repo**. Both forms are inline — there is no separate citations section.

### Link — same bundle

A reference to another document in *this* repo uses a **root-absolute path**: a target beginning with `/`, interpreted relative to the bundle root (the repo root).

```markdown
[doc-conventions.md](/standards/doc-conventions.md)
```

A root-absolute link resolves against the reader's *own* checkout root — the current working directory's repo — so it is **worktree-safe**: it points at the copy of the file that matches the checkout the reader is already in, whether that's the main checkout or a per-issue worktree. A same-repo reference `SHALL NOT` be written as `~/workspace/<this-repo>/…` — from inside a worktree that absolute path silently jumps to the main checkout, yielding a different (possibly stale) copy than the one the reader is working in.

The deciding factor is whether the referencing file has a **fixed repo root** — a single repo it is always read from. Concept documents do, and so does a repo's own `CLAUDE.md` (Claude Code only loads it when the session is already inside that repo), so both use the Link form for same-repo targets. Files with **no fixed repo root** — skills and global `~/.claude/` config such as `rules/`, loaded across arbitrary repos — have no root for `/` to resolve against, so they use the Citation form even for a same-repo target (see [In skill bundles](#in-skill-bundles)).

### Citation — another repo

A reference to a document in a *different* repo uses its **full workspace path**, beginning with `~/workspace/`:

```markdown
[SDD standards index](~/workspace/spec-tools/sdd-standards/README.md)
```

A cross-repo citation always resolves to that repo's canonical main checkout, which is the intended behavior — you reference another repo's published state, not whatever worktree you happen to have open. `~/workspace/<repo>` is self-describing: the repo name is in the path, so no external convention is needed to interpret it.

VS Code does not expand `~/` in markdown links, and it resolves a leading `/` against the filesystem root rather than the bundle root, so neither form is clickable from the editor ([vscode#103542](https://github.com/microsoft/vscode/issues/103542)). Accepted — agents are the primary audience, and both forms are what the `ref-check` linter (`/tools/bin/ref-check`) validates. Anything else — backticked filenames like `` `conftest.py` ``, slash-skill invocations like `/commit` — is treated as prose by `ref-check`.

### In skill bundles

Skill bundles (`SKILL.md` and any reference files under `.claude/skills/<name>/` or `.agents/skills/<name>/`) are harness-owned, not concept documents, and they follow a **target-based** rule instead of the bundle Link/Citation split. The wrapper records intent: an inline link means "go open this"; inline code means "this file exists conceptually."

A skill has **no fixed repo root**. The same skill can be invoked from a session in any repo's checkout, so there is no stable bundle root for a `/`-absolute Link to resolve against. A skill therefore cites a workspace document by its full `~/workspace/<repo>/…` path even when that document lives in the same repo as the skill bundle — the root-absolute Link form is unavailable to it.

| Target | Style | Example |
|---|---|---|
| File inside the same skill bundle (sibling, `references/`, parent) | Inline link, relative path | `[UI.md](references/UI.md)` |
| File at a stable workspace location | Inline link, absolute `~/workspace/...` path | `[Spec standard](~/workspace/spec-tools/sdd-standards/spec-standard.md)` |
| File in the human's repo whose location varies (e.g. `CLAUDE.md`, `specs/design.md`, `Makefile`) | Inline code | `` `CLAUDE.md` `` |
| Directory | Inline code | `` `docs/adr/` `` |
| Slash-skill invocation | Bare — no markup | `/commit` |

### Fenced code blocks

Fenced code blocks delimited by triple backticks or `~~~` may contain `~/workspace/` paths or `/`-root paths in shell examples or sample output; `ref-check` skips them. For example:

```bash
# Run ref-check from any workspace repo:
python3 ~/workspace/dev-playbook/tools/bin/ref-check .
```

### Fragment anchors

A cross-reference `MAY` append `#anchor` to target a specific heading in a markdown file. The anchor `MUST` match the heading's GitHub slug, computed as:

1. Strip inline markdown from the heading text — backtick code spans (keep the text), link syntax `[text](url)` (keep `text`), and emphasis markers. Asterisk emphasis (`*`, `**`) is stripped anywhere, including mid-word. Underscore emphasis (`_`, `__`) is stripped only at word boundaries; underscores flanked by word characters (e.g. `foo_bar_baz`) are literal and kept. This mirrors GitHub, which derives the anchor from the heading's *rendered* text, where intraword underscores are not emphasis.
2. Lowercase.
3. Drop every character that is not a letter, digit, underscore, hyphen, or whitespace.
4. Replace each whitespace character with `-`. Consecutive whitespace produces consecutive hyphens; no collapsing.

Examples:

- `## Branch and worktree` → `#branch-and-worktree`
- `#### 2.2.3 revision` → `#223-revision`
- `## Step 1 — See the shape` → `#step-1--see-the-shape`
- `## Issue body format (the brief is the body)` → `#issue-body-format-the-brief-is-the-body`
- `## load_issue helper` → `#load_issue-helper` (intraword underscores kept)

**Prefer a stable named anchor over a positional one.** A numbered fragment (`#223-revision`) or an in-prose heading-number citation (`§2.10`, `§2.2.3`) breaks silently the moment its target is renumbered or reordered — nothing flags the stale anchor. Where the target heading carries a stable named slug, cite that. Where the target numbers every heading positionally and exposes no stable anchor, name the **concept** the heading carries and drop the number, so a reader finds it by name rather than by a position that drifts.
