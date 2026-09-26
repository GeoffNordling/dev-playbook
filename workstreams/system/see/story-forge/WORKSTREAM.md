---
type: Workstream
title: Story-Forge Simulation
description: The head file of the story-forge simulation child workstream — the fact base and its views simulated by hand with agents on one consumer repo, story-forge, to prove they are worth building; its goal and principles, the open question, and the worklist
---

# Story-Forge Simulation

The child workstream that simulates the fact base and its views by
hand, with agents, on a consumer repository before any extractor is
coded: story-forge, the user's job-search repo at
`~/workspace/story-forge`, read on its main branch and never edited
from here. This workstream is speculative. It takes its
doc-types from [`doc-types/`](/doc-types/index.md) and its method from
the fact base child workstream
([Fact Base Workstream](/workstreams/system/see/fact-base/WORKSTREAM.md)),
whose Planned list names this work: one simulation is a consumer-repo
subsystem, the first data point for residual ownership across repos.
No child workstream's plan waits on it.

## Goal

Prove, by hand on a real repo, that the fact base and its views are
worth building. story-forge is a large, partly
vibe-coded project the user is willing to keep vibe-coding in small
pieces, provided deterministic doc-type and CLOA structure lets them
understand and steer the important parts without reading all of it.
The child workstream reconstructs what story-forge already does through a
hand-written fact base, the way
[Ralph Fact Base](/workstreams/system/see/fact-base/fact-base-ralph.md)
reconstructed the Ralph loop, and reads the residuals as the design of
the consumer's own layer. The specimen is surveyed in
[Story-Forge Survey](/workstreams/system/see/story-forge/story-forge-survey.md).

## Done when

The user rules the fact base and its views worth building, or not.

## Principles

- **A specimen, not a spec.** story-forge is sloppy in many places the
  user knows about and would fix given bandwidth. The survey records
  the kinds of things and relations that exist and where the bedrock
  is; it never treats a story-forge choice as correct because it is
  there.
- **Read-only across the boundary.** The child workstream reads story-forge on
  main and writes nothing there. Whatever the simulation shows
  story-forge owns moves there later, by the user, and that move is
  the answer to the fact base's open question on residual ownership.
- **Simulate before coding.** Per the fact base's plan: enumerate the
  questions a person asks, hand-write the rows with a receipt on every
  one, draw the seven views, record the residuals, and write no
  extractor until the simulations cover the use cases.
- **The specimen stays private.** dev-playbook is public and
  story-forge is not. What this child workstream commits about story-forge is
  its structure, never its content. Allowed: paths, ids, counts, line
  numbers, frontmatter keys and enumerated values such as `status`,
  tag names, relations, and the shape of a rule. Not allowed: the body
  text of any story, resume, or prep unit; a frontmatter `description`
  or `title` beyond the one needed to show a form; and any third party
  named in the files, an employer, an interviewer, a posting id, a
  contact. The line is drawn in file terms because the user's sense of
  what is private is latent, so it is ruled case by case: before a
  commit, the session lists every verbatim field the diff carries, the
  user rules each, and a ruling becomes a bullet here. A story's
  `description` is out, replaced in the fact base by
  `[redacted, N words]` so the row keeps its shape and the receipt its
  line; story `title` attrs and the resume filenames are allowed.
- **Views render locally.** Every view is a `.html` file in this workstream,
  which the user opens in their own browser or in VS Code, never the
  terminal and never a Claude artifact or any other hosted page, so no
  story-forge row leaves the machine to be drawn.
- **Code and pages are committed.** Every script and page the child
  workstream writes lives in this workstream, in git, the scripts under `code/`: the
  extractor `extract.py`, the queries `fact_base.py`, and `render.py`,
  which writes `stories-views.html` from `stories-fact-base.json` alone.
  The one exception is the extractor's output, which carries
  unredacted descriptions and is written outside the repo.
- **Slow and iterative.** One subsystem at a time, each step shown to
  the user before the next.
- **A hand-wave stands in for code, never for magic.** A simulation
  may put an agent where a script will go only when the agent's
  output is something deterministic code can produce later, and the
  agent must name what it assumed.

## Terms

The child workstream coins none. It uses the repo's
[CONTEXT.md](/CONTEXT.md) and See's
[Terms](/workstreams/system/see/WORKSTREAM.md#terms), and for its
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
- **Views as typed operations.** The views of the stories fact base do
  not work well for the user yet. The next attempt expresses each view
  in typed terms: the objects as classes, and what a view shows as
  typed methods on them, per See's
  [Type each verb's signature](/workstreams/system/see/WORKSTREAM.md#planned).
- **A view from a plain description.** The user describes a view in
  plain language. An agent builds it, then finds the typing in the
  fact base that supports it, and restates the user's description in
  the terms of the
  [deterministic wall](/workstreams/system/wall/WORKSTREAM.md)
  only. A part of the description that no typing supports is a
  residual.
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
  [Stories Fact Base](/workstreams/system/see/story-forge/stories-fact-base.md).
- **The survey, 2026-09-23.** The tree read by hand, then four Sonnet
  agents, one per slice — stories and resume, role-postings,
  interview-prep and unemployment-benefits, and the bedrock — each
  reporting under one shape. Merged into
  [Story-Forge Survey](/workstreams/system/see/story-forge/story-forge-survey.md).

## Acronyms

- **CI** — Continuous Integration.
- **PDF** — Portable Document Format.
- **VEC** — Virginia Employment Commission.
