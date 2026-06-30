---
type: Standard
title: Repo Documentation Standard
description: What files every repo carries — README, CLAUDE.md, specs, docs/adr, CONTEXT.md, ROADMAP.md — and their scope and audiences
---

# Repo Documentation Standard

## Purpose

Define a consistent file hierarchy and scope boundary for every repository in the workspace, so that any human or agent can open a repo cold and immediately orient — what it is, how to operate it, and what's next.

## Principles

**Scope is standardized; depth is not.** Every file has a defined scope (what goes in it), but depth varies by project. A CLI tool's README may be 10 lines. A simulation's may be 100. Both are conformant if the content stays within scope.

**Presence is the status signal.** There are no explicit status fields. The presence or absence of optional files tells you what stage the project is in. A missing ROADMAP.md means nothing is planned. A populated specs/ directory means the project is complex enough to warrant formal requirements.

**No duplication across files.** Each piece of information has exactly one home. Files reference each other rather than repeating content.

**Voice and structure are standardized.** Every doc in this hierarchy follows [doc-conventions.md](doc-conventions.md) — declarative present tense, one rule per section, current-state only.

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

| File | Audience | Presence | Scope |
|---|---|---|---|
| `CLAUDE.md` | Agent | Required | How to operate in this repo: build/run/test commands, rules, pointers to other docs. `SHALL NOT` contain what the project is, why it exists, or developer profile information. |
| `README.md` | Human + Agent | Required | What the project does, prerequisites, how to run it. `SHALL NOT` contain agent instructions, roadmap items, or architecture decisions. |
| `ROADMAP.md` | Human + Agent | Optional | Strategy: broad goals and aspirations for the project. No priority ordering, timelines, or assignees. `SHALL NOT` contain actionable work items — those belong in GitHub Issues. |
| `BUSINESS_CONTEXT.md` | Human + Agent | Optional | Domain context for corporate/business projects: the business problem, stakeholders, and why the project exists. Not applicable to non-corporate projects. |
| `specs/` | Human + Agent | Optional | Functional requirements and optionally system design, as flat files or hierarchical folders. See the [SDD standards index](~/workspace/spec-tools/sdd-standards/README.md) for content conventions and [spec-standard.md — File organization](~/workspace/spec-tools/sdd-standards/spec-standard.md#4-file-organization) for file layout and splitting rules. |
| `docs/` | Human + Agent | Optional | Supplementary documentation that does not belong in README, specs, or CLAUDE.md. |
| `docs/adr/` | Human + Agent | Optional | Architectural decision records. One per file, immutable once written, indexed by `docs/adr/README.md`. See [ADR conventions](#adr-conventions) for numbering, template, and offer-gate. |
| `CONTEXT.md` | Human + Agent | Optional | Domain glossary at the repo root: canonical terms, their relationships, and illustrative scenarios. Created lazily as terminology ambiguity surfaces; do not pre-populate. See [CONTEXT.md format](#contextmd-format) for the structure. |
| `<sub-project>/CLAUDE.md` | Agent | Optional | Sub-project rules within a repo, when the repo holds distinct sub-projects with divergent operating conventions. See [CLAUDE.md hierarchy](#claudemd-hierarchy). |
| `.gitignore` | Tooling | Required | Git ignore rules. Every repo has one. See [.gitignore Baseline](#gitignore-baseline). |

## README.md baseline

Every workspace repo's `README.md` starts from this baseline:

````markdown
# <repo-name>

<one-line purpose>
````

This is the floor, not the ceiling. README depth varies by project — see
"Scope is standardized; depth is not." A README `MAY` add prerequisites,
quick-start, architecture overview, or examples as the project earns
them.

## CLAUDE.md baseline

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

See [adr-conventions.md](adr-conventions.md).

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

Cross-references to a stable workspace location `SHALL` use the full path starting with `~/workspace/` — e.g., `~/workspace/spec-tools/sdd-standards/spec-standard.md`. The `ref-check` tool (`~/workspace/dev-playbook/tools/bin/ref-check`) lints every reference in this form and reports broken links. Anything else — backticked filenames like `` `conftest.py` ``, repo-relative paths, slash-skill invocations like `/commit` — is treated as prose by `ref-check`.

VS Code does not expand `~/` in markdown links, so clicking these references from the editor fails ([vscode#103542](https://github.com/microsoft/vscode/issues/103542)). Accepted — agents are the primary audience, and the workspace-portable form is what `ref-check` lints.

How a reference is wrapped — inline link, inline code, or bare — depends on the file kind doing the referencing.

### In repo documentation

Files in the documentation hierarchy above (`CLAUDE.md`, `README.md`, `ROADMAP.md`, `BUSINESS_CONTEXT.md`, files under `specs/` and `docs/`) use inline markdown links with the full path as the target:

```markdown
[Repo documentation standard](~/workspace/dev-playbook/standards/repo-documentation.md)
```

### In skill bundles

Skill bundles (`SKILL.md` and any reference files under `.claude/skills/<name>/` or `.agents/skills/<name>/`) use a target-based rule. The wrapper records intent: an inline link means "go open this"; inline code means "this file exists conceptually."

| Target | Style | Example |
|---|---|---|
| File inside the same skill bundle (sibling, `references/`, parent) | Inline link, relative path | `[UI.md](references/UI.md)` |
| File at a stable workspace location | Inline link, absolute `~/workspace/...` path | `[Spec standard](~/workspace/spec-tools/sdd-standards/spec-standard.md)` |
| File in the human's repo whose location varies (e.g. `CLAUDE.md`, `specs/design.md`, `Makefile`) | Inline code | `` `CLAUDE.md` `` |
| Directory | Inline code | `` `docs/adr/` `` |
| Slash-skill invocation | Bare — no markup | `/commit` |

### Fenced code blocks

Fenced code blocks delimited by triple backticks or `~~~` may contain `~/workspace/` paths in shell examples or sample output; `ref-check` skips them. For example:

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

