---
type: Standard
title: Document Types
description: The OKF document-type registry and the frontmatter profile every concept doc carries
---

# Document Types

The registry of document types for this repo's Open Knowledge Format (OKF)
bundle, and the frontmatter profile every concept document carries. The
type-lint (a pre-commit hook) asserts that every concept document's `type` is
one of the names below.

This governs **concept documents** — the prose `.md` files an agent crawls and
loads to understand something. Harness-owned files are in the bundle too, but a
tool consumes them as configuration or runs them as code rather than reading
them as prose, so they are not concept documents and carry no OKF frontmatter.
The boundary and the harness-owned list live in
[bundle.md](/standards/docs/bundle.md).

## Types

Title Case; acronyms stay upper.

| Type | What it is |
|------|------------|
| `Standard` | A normative conformance target: rules a repo, doc, or agent must follow, that a reviewer or linter could cite to reject work. |
| `README` | The GitHub-rendered landing/orientation doc for a directory or the repo; prose, with any listing delegated to a sibling `index.md`. Role-based: filename `README.md` ⟺ `type: README`. |
| `ADR` | An immutable, numbered record of one architectural decision and its rationale. |
| `Guide` | A teaching or procedure doc you read to learn how to do or think about something, not to be measured against. |
| `Survey` | An evaluative analysis of options or tradeoffs, gathered to inform a decision. |
| `Protocol` | A formal algorithm for structured human–agent collaboration. |
| `Vocabulary` | The canonical definitions of the workspace's domain terms (lives in `CONTEXT.md`). |
| `Recipe Description` | A prose description of a reusable harness pattern; the recipe itself is the backing code/skill/workflow, this doc only describes it. |
| `Reference` | A verbatim mirror of an external document, vendored so agents read it without network access; `resource` points at the upstream original. |
| `Box Artifact` | One file of an [agentic-box](/standards/agentic-box.md) definition — contract, charter, emissions spec, or prompt — consumed by a boxed agent as mission configuration. A box `README.md` stays `type: README`. |

## Frontmatter profile

Every concept document opens with a YAML frontmatter block:

- **`type`** — REQUIRED. Exactly one of the names above.
- **`title`** — the human title.
- **`description`** — the one-line summary that powers triage and the authored
  `index.md` listings: a sentence fragment naming what the document *is* or what
  it *governs*, present tense, no trailing period, leading with the
  distinguishing noun, roughly one breath (~20 words).
- **`resource`** — a path or URI to the underlying asset a document describes
  (a repo-root path like `/dotfiles/dot-claude/workflows/ralph-loop.js`, or an
  external URI). Optional in general; required on `Recipe Description`, whose
  whole job is to describe a backing `.js`. For those, link any companion skill
  in the body, not here.

Not used: `tags`, `timestamp`.
