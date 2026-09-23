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
- **Slow and iterative.** One subsystem at a time, each step shown to
  the user before the next.

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
