---
type: Candidate-List
title: Candidates
description: Uncommitted future work — described, not yet promoted to issues
---

# Candidates

## Sandboxing

- **Container fence for AFK nodes** — a headless node can be denied a tool
  outright but never confined to a directory, so unattended work has no
  filesystem boundary at all; a container would give it one. The open questions
  are in [sandboxing.md](/docs/sandboxing.md).

## Standards tooling

- **Skill mirror check** — the Harness card once claimed a
  `harness.skill-mirror` check that an authored skill under
  `dotfiles/dot-claude/skills/` matches its installed copy under
  `~/.claude/skills/`; no detector ever emitted it. Stow makes the two one
  tree, so the check is whether every link resolves and no stray copy sits
  beside it.
- **Slug a code span the way GitHub does** — `github_slug` in
  `src/dev_playbook/md.py` strips backticks before emphasis, so a heading
  holding `__init__` slugs to `initpy` where GitHub keeps the underscores.
  Protect code spans first, then run ref-lint over every anchor in the tree
  to see which ones the fix moves.

## Doc-type system

- **The registry pass's remaining rows** — the rulings table in
  [Doc-Type System](/doc-types/doc-type-system.md) reads *pending* on every
  kind but Standard, Standard-Card, Runbook, Guide, and Vocabulary; each is
  ruled, and a thin doc-type built where the ruling says so. Log and Survey
  are the user's: at the last count Log had 35 files (story-forge 31, of
  which 27 are tooled Assessment Records; mission-control 3;
  sysadmin-playbook 1) and Survey had 5 (idea-tree 2, sounds 1, media-tools
  1, one stray worktree).
- **The doc-type build loop over Guides** — Guide is roughly half of the
  meaningful documentation in this repo and has no doc-type. Run the loop
  there, new doc-types as peers of Standard and Runbook, possibly more than
  one level; with Standard and Runbook as exemplars, Fable proposes the
  abstractions, the user accepts, rejects, and steers, and the instruction
  states the constraints outright, above all that every CLOA object is 100%
  deterministic.
- **General-Sheet's replacement** — the deliberately-broad placeholder type
  is replaced, and the type working-set files carry is settled with it.
- **The doc-type family's own type** — the files under `doc-types/` carry
  `General-Sheet` today; decide what type they carry.
- **Guide as the procedure kind** — decide whether Guide is the kind a
  procedure carries. The two `consuming.md` are typed `Standard` and
  describe themselves as recipes; Bootstrap and Tracker Operations, the
  same shape, are typed `Guide`.
- **Where exclusions are written** — decide whether a population's
  exclusions are written in the population mark or in the file's prose.
- **The parser's trigger** — `scripts/chaingen` writes
  `doc-types/runbook/chains.txt` by hand today, a temporary location; the
  end state is a gate that fails when a declared chain and reality disagree.
  The same work settles runbook shadowing: a lint parallel to
  `standard.card-shadows-upstream`, and a home for the no-shadowing rule,
  which sits in the Standard-Card definition's Scope today. Hierarchical
  imports across repositories are the mechanism under both.
- **The software factory's split** — when the factory is rewritten, its
  object-state rules (the pull request body's sections, the cycle header,
  the label four-tuple) become a Standard under `standards/software-factory/`,
  the two regions and the moves between them become a Guide where they are,
  and the `gh` mechanics move into the review runbooks
  ([0027](/docs/decisions/0027-registry-refactor-rulings.md)).
- **Instruments remade** — the instruments are due for a redesign; nothing
  new is built on their current form until then.
- **The inheritance pattern's home** — dev-playbook declares a system once,
  consumers inherit it, a repo declares only what is local; this is stated
  per system in `CLAUDE.md`, the Standard doc-type's Scope, and Document
  Types' local extensions, and has no single home.

## Documentation quality

- **Markdown complexity detectors** — static analyzers for markdown, exactly
  as code has them, 100% deterministic: size, line count, headings and their
  depth, and the cross-reference complexity the already-linted link graph
  makes extractable. Reports before gates, since a report points at hot
  spots even where it produces no understanding; the prediction is that the
  software factory tops the list.
- **Duplication detectors** — the document twin of complexity: find the same
  content or vocabulary declared in more than one place and reduce it. The
  grammar triplication, three files declaring one vocabulary and caught only
  by hand, is the case study.
- **Concern counting** — an audit trigger on significant change to a
  document that forces the question of how many concerns the file now
  holds. No static analyzer can count concerns, and pointing an agent at
  every document is too expensive.
- **Doc linters, re-aimed** — the existing linters check that certain
  headings are present; decide what is worth linting for and design toward
  that.
- **Deslop regression gate** — something that keeps a rewritten document
  from sliding back into slop. Deterministic rules cannot judge prose
  quality; the judgments machinery may fit.
- **Vocabulary change discipline** — a process that forces a conscientious
  decision on every term added to or removed from `CONTEXT.md`, so terms do
  not accrete unexamined.
- **CLOA change discipline** — the same discipline for every term used in a
  CLOA communication.
- **The document-writing flywheel** — each major document the AI writes
  takes several corrective passes before it reads well; every pass is a
  chance to codify rules, procedures, and algorithms for writing the next
  one correctly, and no flywheel exists today.
- **OKF graphs and traces** — the
  [file-graph](/instruments/file-graph.md) instrument already renders the
  corpus as a force graph; lean on it and on OKF views generally to
  understand the system. "OKF trace" has no definition; decide whether a
  trace is the Reference chain `scripts/chaingen` draws or something more.

## Code legibility

- **The legibility campaign** — turn the tools below on this repo's own
  scripts and `src/` packages, largely AI-written, and understand the
  system from their outputs rather than line by line: file trees, import
  graphs, call graphs, rendered API surfaces, complexity and size reports.
  A **gray module** is one whose tests the user understands and which pass;
  that is an approximate understanding of the code beneath, and the
  campaign refactors what the reports condemn.
  - **ruff `C901`** — over-complex functions fail lint; no new dependency.
  - **mypy, tightened** — exact flags undecided, not necessarily full
    `--strict`.
  - **import-linter** — a declared contract over module dependencies,
    failing CI when an import crosses a forbidden line. The contract file is
    a CLOA object: the user programs at the level of architecture by
    authoring it, and the AI builds until it passes without editing it.
  - **Rendered API surface** — public signatures plus docstrings, the
    read-a-module-at-a-glance view, for scripts as well as `src/` packages;
    evaluate `griffe-outline` before mkdocstrings or pdoc.
  - **Complexity reports** — gates and reports are different tools: ruff
    gates thresholds, and the campaign also needs measured distributions,
    cyclomatic complexity per function, lines per method, methods per class.
    radon generates those, `pydeps` draws the import graph, `code2flow` the
    call graph.
- **The acceptance test tier** — `tests/acceptance/`, small and capped,
  written in `CONTEXT.md` terminology, one test per behavior the user could
  state in a sentence, read 100%; the **unread tier** is the existing unit
  suite, largely machine-written and judged by passing rather than read
  line by line. The deterministic gate that keeps the acceptance tier from
  bloating is undesigned.
- **Hypothesis** — one readable property can replace fifty example tests.
- **Gherkin** — the most readable acceptance tests; worth remembering, not
  worth shoehorning in.
- **Mermaid sequence diagrams** — cheap to generate when tracing one
  operation.
- **coverage.py as a detector** — not a percentage: uncovered code is code
  nothing forces to be correct.
