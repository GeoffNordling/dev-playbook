---
type: Candidate-List
title: Candidates
description: Uncommitted future work — described, not yet promoted to issues
---

# Candidates

## Standards tooling

- **Slug a code span the way GitHub does** — `github_slug` in
  `src/dev_playbook/md.py` strips underscores inside a code span, so a
  heading `` `__init__.py` files `` slugs to `initpy-files` where GitHub
  gives `__initpy-files`. An anchor to such a heading fails the anchor
  check or passes it wrongly.

## Doc-type system

- **General-Sheet's replacement** — `General-Sheet` is a deliberately-broad
  placeholder type, and 56 files carry it, among them every file under
  `doc-types/`, most of `docs/`, and the unsettled files of each workstream. No type says
  what these files are.

## Documentation quality

- **Markdown complexity checks** — code has static analyzers for size and
  complexity; markdown has none. Nothing measures a document's size, line
  count, heading count and depth, or link-graph complexity, so no report
  shows where the hot spots are.
- **Duplication checks** — nothing detects the same content or vocabulary
  declared in more than one place. The grammar triplication, three files
  declaring one vocabulary, was found only by hand.
- **Vocabulary change discipline** — terms enter and leave `CONTEXT.md`
  without a deliberate decision, so the vocabulary accretes unexamined.
- **CLOA change discipline** — the same problem for the terms used in a
  CLOA communication.

## Code legibility

- **The legibility campaign** — this repo's scripts and `src/` packages
  are largely AI-written, and the user cannot understand them without
  reading them line by line. No tool output — file tree, import graph,
  call graph, API surface, complexity report — gives that understanding.
  - **ruff `C901`** — nothing fails an over-complex function.
  - **import-linter** — nothing stops an import from crossing a module
    boundary the user intends.
  - **Rendered API surface** — no view shows a module's public signatures
    and docstrings at a glance.
  - **Complexity reports** — no report shows the distribution of
    cyclomatic complexity per function, lines per method, or methods per
    class.
- **The acceptance test tier** — the unit suite is largely machine-written
  and judged by passing, not read. No small set of tests states the
  behaviors the user could describe in a sentence, in `CONTEXT.md` terms.
- **Hypothesis** — many example tests check what one property could state.
- **Mermaid sequence diagrams** — tracing one operation through the code
  has no diagram.
- **coverage.py as a check** — code no test runs is code nothing forces to
  be correct, and nothing reports it.
