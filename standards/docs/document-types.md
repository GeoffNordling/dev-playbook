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
| `Candidate-List` | A repo's register of uncommitted future work — Candidates described but not yet promoted to issues (see [tracking/candidates.md](/standards/tracking/candidates.md)); lives in `CANDIDATES.md`, one per repo. |
| `Decision-Record` | An immutable, numbered record of one hard-to-reverse decision and its rationale (see [decisions/records.md](/standards/decisions/records.md)). |
| `General-Sheet` | A deliberately-broad genre for a working loop document whose precise genre is not yet settled — e.g. a live record read on a cadence (a board of declared metrics, a register of selected items). Used when no crisper genre fits and the document's shape may still change. |
| `Guide` | A teaching or procedure doc, read to learn how to do or think about something, not to be measured against. |
| `Instrument-Spec` | The prescriptive contract for an instrument — a purpose-built artifact format with tooling, employed by standards but never a standard itself; implementations must satisfy it. |
| `Log` | A chronological operational record whose entries are appended as events occur (e.g. a friction log). |
| `README` | The GitHub-rendered landing/orientation doc for a directory or the repo; prose, with any listing delegated to a sibling `index.md`. Role-based: filename `README.md` ⟺ `type: README`. |
| `Recipe-Description` | A prose description of a reusable harness pattern; the recipe itself is the backing code/skill/workflow, this doc only describes it. |
| `Reference` | A verbatim mirror of an external document, vendored so agents read it without network access; `resource` points at the upstream original. |
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

## Local extensions

The registry is hierarchical, exactly two levels deep. **This file, in
dev-playbook, is the global registry** — the upstream vocabulary every repo
inherits. A consumer repo that carries a document type no other repo shares
declares it in a **local extension**: its own `standards/docs/document-types.md`,
a `## Types` table of the same shape. okf-lint resolves a document's `type`
against **upstream ∪ local** — the global registry plus the audited repo's
extension, defaulting to upstream alone when the repo carries no extension.
(okf-lint tells the two apart by the canonical consumer template, not by the
registry file's presence: only dev-playbook hosts that template, so a consumer's
extension never flips the audit into replacing the global registry.)

Extension is **additive and downhill only**:

- **Add, never shadow, loosen, or drop.** A local table may only introduce new
  types. A local name that case-insensitively equals an upstream one is a shadow
  — okf-lint's `knowledge-organization.type-shadows-upstream` rule flags it, one
  finding per offending row. (Membership itself stays exact-case; the
  case-insensitive shadow rule is what stops a consumer aliasing upstream `Guide`
  as a distinct `GUIDE`.) A consumer cannot loosen or remove an upstream type,
  because it never edits this file.
- **Downhill only.** A local type is legal only in the repo that declares it (and
  any repo downstream of it); it is invisible uphill to dev-playbook and sideways
  to sibling consumers. A type is exactly as local as the population that carries
  it — a vocabulary word lives where its documents live.
- **Name and description only.** A local type carries just its name and its
  `## Types` cell. The per-type constraints upstream types may impose (a
  `resource` on `Recipe-Description`, an `## Employed by` section on
  `Instrument-Spec`) stay hardcoded upstream; a local type cannot declare its
  own.
- **Broken extension degrades, never aborts.** A malformed or empty extension
  table yields findings on that file (`knowledge-organization.registry-row`,
  `knowledge-organization.index-ordering`) while the rest of the repo is still
  fully checked — never a whole-repo scan abort.

Authoring a local extension is one step of the
[repo-scoped standard recipe](/standards/standard/consuming.md); it is itself a
concept document, so the same Title-Case, alphabetical-table, and index-listing
rules this file follows apply to it.
