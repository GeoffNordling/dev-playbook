---
type: General-Sheet
title: Design
description: How a panel is designed — the design space as combinations of kinds, the questions a person asks of the runbook system, and the ideas recorded for the runbook kind, none of them settled
---

# Design

How a panel comes to look the way it does. The parent is
[CLOA Viewer](/worktree-cloa-viewer-tool-working-docs/ROOT.md), whose
principles and working agreements bind here. The kinds a design becomes
are entries in the
[Registry](/worktree-cloa-viewer-tool-working-docs/registry.md). Nothing
in this member is settled. It records what one brainstorm produced, so
the next design session starts from it and not from nothing.

## The design space

A screen is a composition of registry kinds. The space of possible
screens is the set of combinations of those kinds, and each kind is
simple, so the space is small enough to walk. Design is filtering it:
which combinations answer a question a person asks of the system at a
glance. A combination that answers no question is not drawn.

The CLOA object is the default face and the markdown behind it is one
click further
([CLOA Viewer](/worktree-cloa-viewer-tool-working-docs/ROOT.md#principles)).
The space is bounded by the CLOA objects; the drill-in is outside it and
needs no design of its own.

For the runbook, three combinations came up: one runbook as its chain;
every runbook at once, organized and measured; and runbooks in relation
to one another.

## Questions of the runbook system

The questions a person asks, each answered by a term the
[Reference chain](/doc-types/runbook/contract-shape.md) already has:

1. **What is there** — the population, split Agent and Skill.
2. **Where do I enter** — the entry points, a runbook no other runbook
   does. Its complement is the leaves, a runbook that does nothing.
3. **Who does whom** — the do-graph, the chains joined by their
   do-edges. Its connected clusters are the system's own groups.
4. **What can each touch** — the writes buckets and the never bans.
   "Which runbooks write GitHub" is one column.
5. **What does the fleet run on** — node data: model, effort, and tools,
   per Agent.
6. **How heavy is each** — two families of measure. The object's own:
   edges, do-edges, reads, conditions, imported nodes. The file's: words,
   headings, links, files in the directory. Both are facts. Neither adds
   a meaning the object lacks.

## Ideas for one runbook

The panel of one runbook, as the brainstorm left it:

- A root block first: glyph, name, `Skill · in-process` or
  `Agent · a subprocess`, the node data verbatim, then the signature on
  one line, `args ──► name ──► reports`, then `WRITES` with its buckets
  and `NEVER` with its bans.
- Below it the chain, one row per edge in firing order: the operation,
  the target, the condition, the annotation.
- Channels. Hue carries the operation: reads, does, writes; args and
  reports in ink. A glyph carries the node type, always with its word
  beside it: ▤ Standard, ● Skill, ◆ Agent, ▪ Script, ⛁ bucket, and an
  imported node as plain text. The edge line is dashed when conditional
  and solid otherwise. Vertical position is firing order. A ban mark ⊘
  marks never. Red stays for defects.
- Stitching. A twist on a do-edge opens the target's chain in place,
  lazily, by identity. A Skill nests flush, because it runs in the
  caller's context. An Agent nests framed, because it is a subprocess.
- Annotation muted, wrapping, after target and condition.

Open on this panel: whether the root's `WRITES` and `NEVER` are its own
edges only or reach through its do-edges; whether a stitched chain shows
its full root block or its edges only; whether the operation is colored
text or a pill; whether an empty signature slot shows `—` or nothing.

## Ideas for every runbook

One table, grouped by do-graph cluster, each group headed by its entry
points, sorted by edges, with the measures as quiet columns:

```
RUNBOOKS 43     ◆ 9 Agents  ● 34 Skills     29 entry points · 24 leaves

                             edges  do  rd  writes        words  H2  files
▼ from design · intake · wayfinder · research …            (15)
  ● design          Skill      17   6   2   GitHub         1.9k   7   1
  ● intake          Skill      14   5   2   GitHub         1.4k   5   1
  ● grilling        Skill       1   –   –   –               .3k   1   1
  ⋯
▼ from build · rewind-compact                              (4)
  ◆ build           Agent      10   1   –   GitHub          .9k   4   1
  ⋯
▼ alone                                                    (19)
  ◆ adjudicator     Agent      15   –   –   GitHub          .9k   5   1
  ◆ bug-pr-review   Agent       9   –   –   GitHub  ⊘ code  .7k   4   1
  ⋯
```

The word, heading, and file columns in the sketch are made up. The
counts of runbooks, clusters, and edges are the facts below.

Open: whether the first cut groups by cluster or hangs everything under
its entry points as a tree; which measures earn a column; whether a
rhythm strip, the chain's operations as a run of colored marks, belongs
on each row; whether the table is one kind or the index-tree with a
variable.

## Facts found

At commit `7f7f5a8`, counted from `chains.txt`, which is right for
counting whatever its future:

- 43 runbooks, 9 Agents and 34 Skills. 29 are entry points, 24 are
  leaves.
- The do-graph has one cluster of 15 (candidate-promote, design,
  diagnosing-bugs, domain-modeling, grilling,
  improve-codebase-architecture, intake, issue-review-claims,
  issue-review-simulation, prototype, ralph-setup, research,
  user-intent-mini-interview, wayfinder, wayfinder-to-build), one of 4
  (build, commit, compact-prep, rewind-compact), one of 3 (the
  working-doc-set-deslop set), one of 2 (document-remove-tics,
  tics-remover), and 19 singletons.
- The software factory's agents, adjudicator, bug-pr-review,
  code-pr-review, doc-pr-review, and open-pr, are singletons, and so is
  issue-overwatch. No runbook does them, because the factory's graph
  lives in `software-factory.md`, which issue-overwatch reads as a bare
  imported node. The runbooks alone cannot show how the factory operates.
  That is structure the system lacks, a fact worth showing, not a defect
  of the viewer. Whether the factory graph becomes a CLOA object of its
  own is open.

## Acronyms

None.
