---
type: Standard
title: Document Types
description: The frontmatter profile every concept document carries — a registered type, a title, a description, and a resource where an asset backs the document
population: "a concept document"
---

# Document Types

The frontmatter a concept document carries, the prose `.md` file a
reader loads to understand something. The
boundary is drawn by exclusion from a repo's `.md` files: `index.md` is a
typeless listing ([Indexes](/standards/knowledge-organization/indexes.md));
the members of the Claude Code file registry
([Claude Code Files](/standards/harness/files.md)) are harness-owned, a
tool consumes them as configuration or runs them as code, and they carry
no frontmatter; and `classify()` in [md.py](/src/dev_playbook/md.py)
holds the boundary in code with its further exclusions, the transient
`PLAN.md` and `PROGRESS.md` pair, the root `tmp/` tree, and every
top-level `tests/` tree.

## Frontmatter block

A concept document opens with a `---`-delimited frontmatter block whose
YAML is a mapping.

`knowledge-organization.frontmatter-block` · deterministic

## Types

A concept document's frontmatter has a `type` key whose value names one
row of the table below, or one entry of the `okf_types` mapping in the
frontmatter of the repo's own root `index.md`
([Type Registry](/standards/knowledge-organization/type-registry.md#local-declaration)).

| Type | What it is |
|------|------------|
| `Candidate-List` | A repo's register of uncommitted future work — Candidates described but not yet promoted to issues (see [Candidates](/standards/tracking/candidates.md)); lives in `CANDIDATES.md`, one per repo. |
| `Decision-Record` | An immutable, numbered record of one hard-to-reverse decision and its rationale (see [decisions/records.md](/standards/decisions/records.md)). |
| `General-Sheet` | A deliberately-broad genre for a working document whose type is not yet settled. |
| `Guide` | Instruction on how to do a kind of work, read before doing it and organized by the work; cites rules in passing and is never cited to reject work; lives under `guides/`, the one tree reserved for it. |
| `Log` | A chronological operational record whose entries are appended as events occur (e.g. a friction log). |
| `Loop` | A document that drives a state toward a target state by iteratively taking prescribed actions and validating against prescribed standards; lives under `loops/`, the one tree reserved for it (see [the Loop doc-type](/doc-types/loop/definition.md#where-a-loop-lives)). |
| `Mirror` | A verbatim mirror of an external document, vendored so agents read it without network access; `resource` points at the upstream original. |
| `README` | The GitHub-rendered landing/orientation doc for a directory or the repo; prose, with any listing delegated to a sibling `index.md`. Role-based: filename `README.md` ⟺ `type: README`. |
| `Recipe-Description` | A prose description of a reusable harness pattern; the recipe itself is the backing code/skill/workflow, this doc only describes it. |
| `Standard` | One population and its rules, a normative target a reviewer or linter could cite to reject work; lives under `standards/<name>/`, the one tree reserved for it, one directory per Standard (see [the Standard doc-type](/doc-types/standard/definition.md#where-a-standard-lives)). |
| `Survey` | An evaluative analysis of options or tradeoffs, gathered to inform a decision. |
| `Vocabulary` | The canonical definitions of the workspace's established vocabulary (lives in `CONTEXT.md`). |

`knowledge-organization.types` · deterministic

## Title

A concept document's frontmatter has a `title` key with a non-empty
value.

`knowledge-organization.title` · deterministic

## Description

A concept document's frontmatter has a `description` key whose value is
non-empty and does not end with a period.

`knowledge-organization.description` · deterministic

## Description voice

A concept document's `description` is a sentence fragment in the present
tense that names what the document is, what it governs, or, for a
`Decision-Record`, the decision it records.

`knowledge-organization.description-voice` · stochastic

> **Why.** The description is what a reader triages on and what every
> `index.md` listing carries verbatim, so it is read far more often,
> and far further from its document, than the document itself.

## resource

A concept document's `resource`, where present, is a repo-root path
beginning with `/` or an external URI.

`knowledge-organization.resource` · deterministic

## resource names the asset

A concept document's `resource`, where present, names the asset the
document describes, never a companion file that only supports it.

`knowledge-organization.resource-names-the-asset` · stochastic

## No tags or timestamp

A concept document's frontmatter has no `tags` key and no `timestamp`
key.

`knowledge-organization.no-tags-or-timestamp` · deterministic

## Recipe-Description

A concept document typed `Recipe-Description` has a `resource` key with
a non-empty value.

`knowledge-organization.recipe-description` · deterministic

## Typed Standard

A concept document typed `Standard` lives under `standards/`.

`knowledge-organization.typed-standard` · deterministic

## Typed Loop

A concept document typed `Loop` lives under `loops/`.

`knowledge-organization.typed-loop` · deterministic

## Typed Guide

A concept document typed `Guide` lives under `guides/`.

`knowledge-organization.typed-guide` · deterministic
