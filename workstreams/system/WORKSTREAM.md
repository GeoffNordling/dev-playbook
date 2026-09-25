---
type: Workstream
title: System Workstream
description: The head file of the system workstream — the user sees the workspace's systems and drives work on them without always being in the loop, through two child workstreams, See and Drive, with the principles and terms they share and the worklist
---

# System Workstream

This workstream is speculative: every member writes a guess as a guess,
and every member inherits that voice. The workstream holds the user's
one aim for the systems of `~/workspace`, split in two child
workstreams, and this head file holds only what crosses them.

## Goal

The user sees and steers the workspace's systems without reading them,
and work on them advances without the user always in the loop. The
reason is [System Legibility](/docs/system-legibility.md). Two child
workstreams carry the goal:

- **See**: deterministic code shows what a checkout does, at the CLOA.
  Head file: [See Workstream](/workstreams/system/see/WORKSTREAM.md).
- **Drive**: work advances in stints, most of them unattended, and the
  user gives verdicts. Head file:
  [Drive Workstream](/workstreams/system/drive/WORKSTREAM.md).

Two parts are built and closed, and each lives in the main part of
the repo, outside `workstreams/`:

- **The doc-type system**, part of See: five doc-types, Runbook,
  Standard, Guide, Loop, and Workstream, under
  [`doc-types/`](/doc-types/index.md), drawn whole in
  [Reference Model](/doc-types/reference-model.md) and held to the
  Standard [Doc-Type](/standards/doc-type/doc-type.md). No more
  doc-types are expected.
- **The `stint` command**, a tool Drive uses: it runs one unattended
  stint in sealed Sandcastle containers, from launch to its end
  ([Running a Stint](/guides/running-a-stint.md)). It is complete, and
  no further development of it is planned.

```
SYSTEM · see and drive the workspace's systems
├─ SEE · understand a checkout without reading it all
│    doc-type system ──enables──▶ FACT BASE ⊃ ontology ──enables──▶ VIEWER
│     (built, closed)             (not built)                        (a slice built)
│                                      ▲
│                       STORY-FORGE ───┘ simulates the fact base and its views
│                                        by hand on a real repo, to prove value
└─ DRIVE · work advances without the user in the loop
     workstream · loop · stint · driver ──unattended stints run on──▶ stint command
                                                                      (built, closed)
```

The two meet at one seam: a loop's verification reads the facts that
See extracts.

## Done when

None: the goal is standing.

## Principles

- **Logic and statistics meet at one seam.** Predicates define a set,
  with no probabilities attached. An act is a draw from a distribution
  over states, and the draw lands in the set or outside it. A loop does
  not change the LLM; it changes what the next draw is given: a
  verification finds where the last sample fell outside, and the act
  draws again with those findings in the prompt, so successive samples
  land in the set more often. Deterministic rules decide membership
  exactly; stochastic rules decide it with an error rate.
- **Three working policies for rules.** A change to the repo is the
  expensive way out. No credit goes to the count of rules, so delete is
  the default for a rule that restates another or binds something too
  small to matter. "Keep it because a check emits the id" is backwards,
  since the check follows the rule.

## Terms

The terms that cross into the main part of the repo, such as
predicate, fact base, workstream, and stint, are in
[CONTEXT.md](/CONTEXT.md). The terms this head file coins:

- **Distribution** — the states an act could leave behind, each
  weighted by how likely it is, given the state it starts from and the
  prompt it is given. Some of the weight falls inside the target state,
  some outside. A distribution is not a set.
- **Sample** — one state an act did leave behind: one draw from its
  distribution. The samples of one loop are not independent: each
  starts from the last, with its findings in the prompt, so the loop is
  a path through the space of states.

## Planned

- **Reconsider System Legibility from scratch.** After See and Drive
  are refactored,
  [System Legibility](/docs/system-legibility.md), the oldest document
  of this work, is read again against them, and each of its ideas is
  kept, rewritten, or dropped.

## Acronyms

- **CLOA** — Correct Level of Abstraction.
- **LLM** — Large Language Model.
