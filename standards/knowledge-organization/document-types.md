---
type: Standard
title: Document Types
description: The frontmatter profile every concept document carries — a registered type, a title, a one-breath description, and a resource where an asset backs the document
population: "a concept document"
---

# Document Types

The frontmatter a concept document carries, the prose `.md` file a
reader loads to understand something
([File Roles](/standards/knowledge-organization/file-roles.md)). The
boundary is drawn by exclusion from a repo's `.md` files: `index.md` is a
typeless listing ([Indexes](/standards/knowledge-organization/indexes.md));
the members of the Claude Code file registry
([Claude Code Files](/standards/harness/files.md)) are harness-owned, a
tool consumes them as configuration or runs them as code, and they carry
no frontmatter; and `classify()` in [md.py](/src/dev_playbook/md.py)
holds the boundary in code with its further exclusions, the transient
`PLAN.md` and `PROGRESS.md` pair, the root `tmp/` tree, and every
top-level `tests/` tree. okf-lint is the authority
([Knowledge Organization](/standards/knowledge-organization.md)).

## Frontmatter block

A concept document opens with a YAML frontmatter block.

## Types

`type` is present and names one row of the table below, or of the repo's
own local extension of it
([Type Registry](/standards/knowledge-organization/type-registry.md)).

This table is the global registry, the vocabulary every repo inherits,
and its shape is Type Registry's rule. Alphabetical by type name.

| Type | What it is |
|------|------------|
| `Candidate-List` | A repo's register of uncommitted future work — Candidates described but not yet promoted to issues (see [tracking/candidates.md](/standards/tracking/candidates.md)); lives in `CANDIDATES.md`, one per repo. |
| `Decision-Record` | An immutable, numbered record of one hard-to-reverse decision and its rationale (see [decisions/records.md](/standards/decisions/records.md)). |
| `General-Sheet` | A deliberately-broad genre for a working document whose type is not yet settled. |
| `Guide` | A teaching or procedure doc, read to learn how to do or think about something, not to be measured against. |
| `Instrument-Spec` | The prescriptive contract for an instrument — a purpose-built artifact format with tooling, employed by standards but never a standard itself; implementations must satisfy it. |
| `Log` | A chronological operational record whose entries are appended as events occur (e.g. a friction log). |
| `README` | The GitHub-rendered landing/orientation doc for a directory or the repo; prose, with any listing delegated to a sibling `index.md`. Role-based: filename `README.md` ⟺ `type: README`. |
| `Recipe-Description` | A prose description of a reusable harness pattern; the recipe itself is the backing code/skill/workflow, this doc only describes it. |
| `Reference` | A verbatim mirror of an external document, vendored so agents read it without network access; `resource` points at the upstream original. |
| `Spec-Item` | One item of a machine-validated specification tree — a functional requirement or design node with typed edges, operated on by tooling rather than only read. |
| `Standard` | A normative conformance target: rules a repo, doc, or agent must follow, that a reviewer or linter could cite to reject work; lives under `standards/`, the one tree reserved for it (see [the Standard doc-type](/doc-types/standard/definition.md#where-a-standard-lives)). |
| `Standard-Card` | The thin catalog record for one standard — pointer cells (define, audit, enforce, adopt) locating the standard's contract, checkers, gates, and adoption helpers. |
| `Survey` | An evaluative analysis of options or tradeoffs, gathered to inform a decision. |
| `Vocabulary` | The canonical definitions of the workspace's established vocabulary (lives in `CONTEXT.md`). |

## Title

`title` is present and holds the readable title.

## Description

`description` is present and holds a one-line summary: a sentence
fragment naming what the document is or what it governs, present tense,
no trailing period, leading with what distinguishes it, roughly one
breath, twenty words as a soft limit.

The description powers triage and the authored `index.md` listings
([Indexes](/standards/knowledge-organization/indexes.md)).

## resource

`resource`, when present, holds a repo-root path or an external URI to
the asset the document describes:
`/dotfiles/dot-claude/workflows/ralph-loop.js`.

## No tags or timestamp

`tags` and `timestamp`, the OKF spec's optional keys, are absent.

## Recipe-Description

A concept document whose `type` is `Recipe-Description`, whose whole job
is to describe a backing `.js`.

### resource present

`resource` is present and names the backing file.

A companion skill is linked in the body, not in `resource`.

## Typed Standard

A concept document whose `type` is `Standard`.

### Under standards/

The file lives under `standards/`, the one tree reserved for the label
([Standard](/doc-types/standard/definition.md#where-a-standard-lives)).
