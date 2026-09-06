---
name: working-doc-set-diagram
description: Draw the working document set in focus as an ASCII tree of filenames, links, and section names.
disable-model-invocation: true
model: inherit
effort: medium
---

# Working Doc Set Diagram

Draw the working document set already in focus. Work from what you hold —
the set is established and its files are read, so this skill carries only
the rendering rules.

## What the diagram shows

Structure, never state. Each part comes from something that changes only
when a file changes:

- **Node** — the filename, verbatim. A directory keeps its trailing slash.
- **Edge** — a cross-reference from one member to another, in whichever
  form
  [cross-references.md](~/workspace/dev-playbook/standards/knowledge-organization/cross-references.md)
  gives that member: a root-absolute Link for a concept document, a
  `~/workspace/` Citation for a runbook. One root at the top, the tree
  descending from it. A file with two children spends an elbow and puts
  the second child to the right.
- **Label** — a role phrase naming the file's job in the set, then that
  file's `##` headings, verbatim, joined by `·`.

Counts, tallies, statuses and dates stay out. They go stale between one
drawing and the next.

## The shape

```
index.md
   │
   ▼
ROOT.md ···························· role: section · section · section
   │
   ▼
BRANCHING-FILE.md ·················· role: section · section ·
   │        │                        section · section
   │        └───────────────────────┐
   ▼                                ▼
MAIN-CHILD.md ············ role:    SIDE-CHILD.md
   │                       section  role: section · section
   │                       section
   ▼
LEAF-FILE.md ······················· role: section · section
   │
   ▼
subdirectory/ ······················ file · file
```

ASCII box characters only, 78 columns wide, one annotation column every
label aligns to, fragments rather than sentences. Where two nodes stand
side by side, the left one's label narrows to make room.

{Report the diagram} and nothing else — no commentary above or below it.

This shape is the set's standing form for the rest of the conversation.
Redraw it on request without loading this skill again.
