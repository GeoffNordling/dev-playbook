---
type: General-Sheet
title: Design
description: How a panel is designed — the design space as selections from the fact base, and the renderer ideas recorded for the runbook views, none of them settled
---

# Design

How a panel comes to look the way it does. The parent is
[CLOA Viewer](/worktree-synthesis-notes-working-docs/viewer/ROOT.md), whose
principles and working agreements bind here. The kinds a design becomes
are entries in the
[Registry](/worktree-synthesis-notes-working-docs/viewer/registry.md). Nothing
in this member is settled. It records what one brainstorm produced, so
the next design session starts from it and not from nothing.

## The design space

A screen is a composition of views, and every view is a selection from
the fact base
([Views are selections](/worktree-synthesis-notes-working-docs/fact-base/fact-base.md#views-are-selections)).
The space of possible screens is the set of selections the schema
admits, and it is walked by the questions a person asks of the system,
the use cases the fact base simulations enumerate
([Planned](/worktree-synthesis-notes-working-docs/fact-base/ROOT.md#planned)).
Design is filtering it: which selection answers which question at a
glance. A selection that answers no question is not drawn.

The CLOA object is the default face and the markdown behind it is one
click further
([CLOA Viewer](/worktree-synthesis-notes-working-docs/viewer/ROOT.md#principles)).
The space is bounded by the CLOA objects; the drill-in is outside it and
needs no design of its own.

## Ideas for one runbook

Renderer ideas for the interface card and the control flow of one
runbook, as the brainstorm left them:

- Root block. First, the node type as its glyph and word, the name,
  `Skill · in-process` or `Agent · a subprocess`, the node data
  verbatim, then the signature on one line,
  `args ──► name ──► reports`, then `WRITES` with its buckets and
  `NEVER` with its bans.
- Chain. Below the root block, one row per edge in firing order: the
  operation, the target, the condition, the annotation.
- Channels. Hue carries the operation: reads, does, writes; args and
  reports in ink. A glyph carries the node type, always with its word
  beside it, per the legend below. The edge line is dashed when
  conditional and solid otherwise. Vertical position is firing order. A
  ban mark ⊘ marks never. Red stays for defects.
- Stitching. A twist on a do-edge opens the target's chain in place,
  lazily, by identity. A Skill nests flush, because it runs in the
  caller's context. An Agent nests framed, because it is a subprocess.
- Annotation. Muted, wrapping, after target and condition.

The glyph legend:

| Glyph | Node type |
| ----- | --------- |
| ▤ | Standard |
| ● | Skill |
| ◆ | Agent |
| ▪ | Script |
| ⛁ | bucket |
| plain text | imported node |

Open on this panel: whether the root's `WRITES` and `NEVER` are its own
edges only or reach through its do-edges; whether a stitched chain shows
its full root block or its edges only; whether the operation is colored
text or a pill; whether an empty signature slot shows `—` or nothing.

## Acronyms

None.
