---
type: Registry
title: OKF Type Registry
description: Every OKF type a concept document may declare in its frontmatter, each with what it is
---

# OKF Type Registry

An **OKF type** is the `type` value in a concept document's frontmatter,
the one field the OKF spec requires
([OKF spec](/docs/mirrors/okf-spec.md)). This table is the global set
every repo inherits; a consumer repo adds its own
([Local OKF Types](/standards/knowledge-organization/local-okf-types.md)). An
OKF type is a label, not a contract: which OKF types a doc-type covers
is the [Doc-Type Registry](/registries/doc-types.md).

## OKF types

| OKF type | What it is |
|----------|------------|
| `Candidate-List` | A repo's register of uncommitted future work — Candidates described but not yet promoted to issues (see [Candidates](/standards/tracking/github/candidates.md)); lives in `CANDIDATES.md`, one per repo. |
| `Decision-Record` | An immutable, numbered record of one hard-to-reverse decision and its rationale (see [decisions/records.md](/standards/decisions/records.md)). |
| `General-Sheet` | A deliberately-broad genre for a working document whose type is not yet settled. |
| `Guide` | Instruction on how to do a kind of work, read before doing it and organized by the work; cites rules in passing and is never cited to reject work; lives under `guides/`, the one tree reserved for it. |
| `Log` | A chronological operational record whose entries are appended as events occur (e.g. a friction log). |
| `Loop` | A document that drives a state toward a target state by iteratively taking prescribed actions and validating against prescribed standards; lives under `loops/`, the one tree reserved for it (see [the Loop doc-type](/doc-types/loop/definition.md#where-a-loop-lives)). |
| `Mirror` | A verbatim mirror of an external document, vendored so agents read it without network access; `resource` points at the upstream original. |
| `README` | The GitHub-rendered landing/orientation doc for a directory or the repo; prose, with any listing delegated to a sibling `index.md`. Role-based: filename `README.md` ⟺ `type: README`. |
| `Recipe-Description` | A prose description of a reusable harness pattern; the recipe itself is the backing code/skill/workflow, this doc only describes it. |
| `Registry` | A table of entries that documents and checks read as data; it states no rules, and a Standard that reads it links it; lives under `registries/`, the one tree reserved for it. |
| `Standard` | One population and its rules, a normative target a reviewer or check could cite to reject work; lives under `standards/<name>/`, the one tree reserved for it, one directory per Standard (see [the Standard doc-type](/doc-types/standard/definition.md#where-a-standard-lives)). |
| `Survey` | An evaluative analysis of options or tradeoffs, gathered to inform a decision. |
| `Vocabulary` | The canonical definitions of the workspace's established vocabulary (lives in `CONTEXT.md`). |
| `Workstream` | The head file of one line of work, its ideas, target state, and context, driven by a loop; `WORKSTREAM.md`, the head of its directory (see [the Workstream doc-type](/doc-types/workstream/definition.md#where-a-workstream-lives)). |
