---
type: General-Sheet
title: Story-Forge Simulation
description: The root of the story-forge simulation strand — the doc-type system and the fact base tried by hand on one consumer repo, story-forge, its goal and principles, the open questions, and the worklist from survey through one hand-written fact base
---

# Story-Forge Simulation

The strand that tries the doc-type system on a consumer repository
before any extractor is coded: story-forge, the user's job-search repo
at `~/workspace/story-forge`, read on its main branch and never edited
from here. Speculative, per
[Synthesis Working Root](/working-docs/doc-type-system/ROOT.md). It
depends on the doc-type system strand for the language
([Doc-Type System](/working-docs/doc-type-system/doc-type-system/ROOT.md))
and on the fact base strand for the method
([Fact Base Strand](/working-docs/doc-type-system/fact-base/ROOT.md)),
whose Planned list names this work: one simulation is a consumer-repo
subsystem, the first data point for residual ownership across repos.
No strand's plan waits on it.

## Goal

Prove the concept on a real case. story-forge is a large, partly
vibe-coded project the user is willing to keep vibe-coding in small
pieces, provided deterministic doc-type and CLOA structure lets them
understand and steer the important parts without reading all of it.
The strand reconstructs what story-forge already does through a
hand-written fact base, the way
[Ralph Fact Base](/working-docs/doc-type-system/fact-base/fact-base-ralph.md)
reconstructed the Ralph loop, and reads the residuals as the design of
the consumer's own layer. The general system is briefed in
[System Brief](/working-docs/doc-type-system/story-forge-simulation/system-brief.md);
the specimen is surveyed in
[Story-Forge Survey](/working-docs/doc-type-system/story-forge-simulation/story-forge-survey.md).

## Principles

- **A specimen, not a spec.** story-forge is sloppy in many places the
  user knows about and would fix given bandwidth. The survey records
  the kinds of things and relations that exist and where the bedrock
  is; it never treats a story-forge choice as correct because it is
  there.
- **Read-only across the boundary.** The strand reads story-forge on
  main and writes nothing there. Whatever the simulation shows
  story-forge owns moves there later, by the user, and that move is
  the answer to the fact base's open question on residual ownership.
- **Simulate before coding.** Per the fact base's plan: enumerate the
  questions a person asks, hand-write the rows with a receipt on every
  one, draw the seven views, record the residuals, and write no
  extractor until the simulations cover the use cases.
- **The specimen stays private.** dev-playbook is public and
  story-forge is not. What this strand commits about story-forge is
  its structure, never its content. Allowed: paths, ids, counts, line
  numbers, frontmatter keys and enumerated values such as `status`,
  tag names, relations, and the shape of a rule. Not allowed: the body
  text of any story, resume, or prep unit; a frontmatter `description`
  or `title` beyond the one needed to show a form; and any third party
  named in the files, an employer, an interviewer, a posting id, a
  contact. The line is drawn in file terms because the user's sense of
  what is private is latent, so it is ruled case by case: before a
  commit, the session lists every verbatim field the diff carries, the
  user rules each, and a ruling becomes a bullet here. Rulings,
  2026-09-23: a story's `description` is out, replaced in the fact
  base by `[redacted, N words]` so the row keeps its shape and the
  receipt its line; story `title` attrs and the resume filenames were
  seen and allowed.
- **Views render to `~/views/`.** Every view is a `.html` page that
  `render.py` writes into `~/views/`, one fixed directory outside
  every repo, which the user bookmarks as `file:///home/geoff/views/`
  and opens in their own browser or in VS Code, never the terminal and
  never a Claude artifact or any other hosted page. The path is fixed
  so the bookmark survives restarts and worktree moves and always
  shows the latest render, committed or not. Pages are never
  committed: they are derived, and keeping them out of git keeps
  them off public GitHub.
- **Code is committed, output is not.** Every script the strand writes
  lives in this set, in git, under `code/`: the extractor
  `extract.py`, the queries `fact_base.py`, and `render.py`, which
  writes `stories-views.html` from `stories-fact-base.json` alone.
  What the scripts write stays outside the repo: the pages in
  `~/views/`, and the extractor's output, which carries unredacted
  descriptions, in the scratchpad.
- **Slow and iterative.** One subsystem at a time, each step shown to
  the user before the next.
- **A hand-wave stands in for code, never for magic.** A simulation
  may put an agent where a script will go only when the agent's
  output is something deterministic code can produce later, and the
  agent must name what it assumed. Sanity check of 2026-09-23: every
  assumption in `code/extract.py` is a regex over a convention a
  doc-type can declare, so none is magic.
- **An extractor is the inverse of a declared encoding.** An agent
  that writes an extractor also writes the doc-type it read from, in
  the reference model's pseudocode, so its assumptions are inspected
  as a short class and not as the parsing code.
- **Permissions, rules, and views read one fact base.** The ontology
  grants which kinds may point at which; a rule checks one fact, such
  as whether a `related` target exists; a view draws the facts. A
  dangling edge violates a rule, never the ontology.
- **Views are code, registered by name.** Each view is a function in
  `code/render.py` with one stated question it answers; the code is
  the spec, and the question is the only prose it needs.

## Terms

The strand coins none. It uses the set's
[Terms](/working-docs/doc-type-system/ROOT.md#terms), and for its
domain words story-forge's own vocabulary at
`~/workspace/story-forge/CONTEXT.md`, capitalised as that file writes
them: Story, Assessment Record, Prep-unit, Work-Search Contact.

## Open

- **What "ready to memorize" means in file terms.** The user ruled
  `status: complete` a good sign, loosely applied. Whether readiness is
  that field, the nine predicates, or a new declared fact is open.

## Planned

- **Operations and views over the stories fact base.** What a person
  does with the base once it exists: the views the user asks for next,
  the two thresholds ruled, and a Sonnet agent sent to check the
  surrogate's assumptions against the real files before each new view.
- **The domain layer read off the residuals.** Which node types,
  extractors, and primitives story-forge owns and dev-playbook does
  not: the first data point for the fact base's open question.
- **The survey as a loop.** The four-agent survey is repeatable, one
  prompt per subsystem and per repo; it becomes a loop once the row
  shape settles, per the fact base's own plan.

## Completed

- **The stories fact base, 2026-09-23.** The hand simulation, worked
  backwards from the user's question about story health: seven
  questions agreed, one Sonnet agent surveying the Story shape, one
  acting as the extractors, 299 nodes and 537 edges with receipts, nine
  predicates, five views, and five residuals, in
  [Stories Fact Base](/working-docs/doc-type-system/story-forge-simulation/stories-fact-base.md).
- **The survey, 2026-09-23.** The tree read by hand, then four Sonnet
  agents, one per slice — stories and resume, role-postings,
  interview-prep and unemployment-benefits, and the bedrock — each
  reporting under one shape. Merged into
  [Story-Forge Survey](/working-docs/doc-type-system/story-forge-simulation/story-forge-survey.md).

## Acronyms

- **CLOA** — Correct Level of Abstraction.
- **JSON** — JavaScript Object Notation.
