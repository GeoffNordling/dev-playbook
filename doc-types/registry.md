---
type: Registry
title: Type Registry
description: Every document type a concept document may declare and every kind of harness file, each with what it is and the doc-type that covers it
---

# Type Registry

Every kind of file in the workspace has one row here, in one of two
tables. Document types are the `type` values a concept document may
declare, the global vocabulary every repo inherits; a consumer repo adds
its own in an `okf_types` mapping
([Local Types](/standards/knowledge-organization/local-types.md)).
Harness kinds are the files the Claude Code harness consumes
([Claude Code Files](/standards/harness/files.md)); they carry no
frontmatter, so no document declares one as its `type`.

The Doc-type cell names the built doc-type that covers the kind
([Reference Model](/doc-types/reference-model.md)). A kind is finer
than a doc-type: the harness kinds Skill and Agent definition are both
covered by Runbook. A cell reads *None* when no doc-type covers the
kind, with the reason where one is known; *None* is a complete answer,
not a promise that a doc-type is coming.

The rule
[`type` names a registered type](/standards/knowledge-organization/document-types.md#type-names-a-registered-type)
reads the first table, and
[Registered](/standards/doc-type/doc-type.md#registered) reads the
Doc-type cells of both.

## Document types

| Type | What it is | Doc-type |
|------|------------|----------|
| `Candidate-List` | A repo's register of uncommitted future work — Candidates described but not yet promoted to issues (see [Candidates](/standards/tracking/candidates.md)); lives in `CANDIDATES.md`, one per repo. | None |
| `Decision-Record` | An immutable, numbered record of one hard-to-reverse decision and its rationale (see [decisions/records.md](/standards/decisions/records.md)). | None |
| `General-Sheet` | A deliberately-broad genre for a working document whose type is not yet settled. | None — its replacement is an open question ([Candidates](/CANDIDATES.md)) |
| `Guide` | Instruction on how to do a kind of work, read before doing it and organized by the work; cites rules in passing and is never cited to reject work; lives under `guides/`, the one tree reserved for it. | [Guide](/doc-types/guide/definition.md) |
| `Log` | A chronological operational record whose entries are appended as events occur (e.g. a friction log). | None |
| `Loop` | A document that drives a state toward a target state by iteratively taking prescribed actions and validating against prescribed standards; lives under `loops/`, the one tree reserved for it (see [the Loop doc-type](/doc-types/loop/definition.md#where-a-loop-lives)). | [Loop](/doc-types/loop/definition.md) |
| `Mirror` | A verbatim mirror of an external document, vendored so agents read it without network access; `resource` points at the upstream original. | None |
| `README` | The GitHub-rendered landing/orientation doc for a directory or the repo; prose, with any listing delegated to a sibling `index.md`. Role-based: filename `README.md` ⟺ `type: README`. | None |
| `Recipe-Description` | A prose description of a reusable harness pattern; the recipe itself is the backing code/skill/workflow, this doc only describes it. | None |
| `Registry` | A table of entries that documents and checks read as data, such as this one; it states no rules, and a Standard that reads it links it. | None — typed frontmatter only, not a doc-type |
| `Standard` | One population and its rules, a normative target a reviewer or check could cite to reject work; lives under `standards/<name>/`, the one tree reserved for it, one directory per Standard (see [the Standard doc-type](/doc-types/standard/definition.md#where-a-standard-lives)). | [Standard](/doc-types/standard/definition.md) |
| `Survey` | An evaluative analysis of options or tradeoffs, gathered to inform a decision. | None |
| `Vocabulary` | The canonical definitions of the workspace's established vocabulary (lives in `CONTEXT.md`). | None — the vocabulary API ([System Legibility](/docs/system-legibility.md)) |
| `Workstream` | The head file of one line of work, its ideas, target state, and context, driven by a loop; `WORKSTREAM.md`, the head of its directory (see [the Workstream doc-type](/doc-types/workstream/definition.md#where-a-workstream-lives)). | [Workstream](/doc-types/workstream/definition.md) |

## Harness kinds

| Member | Class | Role | Content standard | Doc-type |
|---|---|---|---|---|
| `CLAUDE.md`, `<dir>/CLAUDE.md` | context | injected into every session at or below its directory | [claude-content.md](/standards/harness/claude-content.md) | None |
| skill bundles | runbook | loaded when a skill is invoked | [Runbook Conventions](/standards/doc-type/runbook-conventions.md) | [Runbook](/doc-types/runbook/definition.md) |
| `agents/*.md` | runbook | loaded when a typed agent is launched | [Runbook Conventions](/standards/doc-type/runbook-conventions.md) | [Runbook](/doc-types/runbook/definition.md) |
| `rules/*.md` | context | injected into every session | none yet | None |
| `settings.json`, `settings.local.json` | configuration | read as configuration | none yet | None |
| `hooks/` | code | run as code around harness events | none yet | None |
| `workflows/*.js` | code | run as code by the Workflow tool | none yet | None — a runtime that runs loops, not the [Loop](/doc-types/loop/definition.md) family |
| `statusline.sh` | code | run as code to draw the status line | none yet | None |
