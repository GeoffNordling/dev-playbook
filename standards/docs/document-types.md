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
The boundary rule lives in [bundle.md](/standards/docs/bundle.md); the
Claude Code file set is enumerated in
[the harness-files registry](/standards/claude-code/files.md).

## Types

Title Case, hyphen-joined for multi-word names (e.g. `Decision-Record`,
`Standard-Card`); acronyms stay upper. Listed alphabetically.

| Type | What it is |
|------|------------|
| `Decision-Record` | An immutable, numbered record of one hard-to-reverse decision and its rationale (see [decisions/records.md](/standards/decisions/records.md)). |
| `General-Sheet` | A deliberately-broad genre for a working loop document whose precise genre is not yet settled — e.g. a live record read on a cadence (a board of declared metrics, a register of selected items). Used when no crisper genre fits and the document's shape may still change. |
| `Guide` | A teaching or procedure doc, read to learn how to do or think about something, not to be measured against. |
| `Idea` | A captured idea the author wants to store; a record, not a commitment. |
| `Instrument-Spec` | The prescriptive contract for an instrument — a purpose-built artifact format with tooling, employed by standards but never a standard itself; implementations must satisfy it. |
| `Log` | A chronological operational record whose entries are appended as events occur (e.g. a friction log). |
| `Protocol` | A formal algorithm for structured human–agent collaboration. |
| `README` | The GitHub-rendered landing/orientation doc for a directory or the repo; prose, with any listing delegated to a sibling `index.md`. Role-based: filename `README.md` ⟺ `type: README`. |
| `Recipe-Description` | A prose description of a reusable harness pattern; the recipe itself is the backing code/skill/workflow, this doc only describes it. |
| `Reference` | A verbatim mirror of an external document, vendored so agents read it without network access; `resource` points at the upstream original. |
| `Spec-Item` | One SDD spec item — a `feat`/`req`/`dsn` node in a `specs/` tree; body format owned by the [SDD standards](~/workspace/spec-tools/sdd-standards/README.md); frontmatter exists for OKF navigation only. |
| `Standard` | A normative conformance target: rules a repo, doc, or agent must follow, that a reviewer or linter could cite to reject work. |
| `Standard-Card` | The thin catalog record for one standard — four pointer cells (define, audit, enforce, adopt) locating the standard's contract, checkers, gates, and adoption helpers. |
| `Survey` | An evaluative analysis of options or tradeoffs, gathered to inform a decision. |
| `Vocabulary` | The canonical definitions of the workspace's established vocabulary (lives in `CONTEXT.md`). |

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
  external URI). Optional in general; required on `Recipe-Description`, whose
  whole job is to describe a backing `.js`. For those, link any companion skill
  in the body, not here.

Not used: `tags`, `timestamp`.
