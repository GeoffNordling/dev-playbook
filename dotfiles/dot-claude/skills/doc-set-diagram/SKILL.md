---
name: doc-set-diagram
description: Draw a documentation set as an ASCII tree of filenames, links, and section names.
disable-model-invocation: true
model: inherit
effort: medium
arguments: [set-hint]
---

# Doc Set Diagram

Draw one documentation set. The argument is a set hint: anything that
plainly names one set, a directory, its `index.md`, a card's name.
Resolve it to the directory whose `index.md` is the set's root
([Documentation Sets](~/workspace/dev-playbook/standards/knowledge-organization/documentation-sets/documentation-sets.md)),
then {Read `index.md`, the set's root} and every member it lists, one
level of child set down. No hint means the set already in focus: work from what
you hold, since its files are read.

## What the diagram shows

Structure, never state. Each part comes from something that changes only
when a file changes:

- **Node** — the filename, verbatim. A child set is its directory,
  trailing slash kept.
- **Edge** — a row of the index, in listing order
  ([the listing](~/workspace/dev-playbook/standards/knowledge-organization/indexes.md#the-listing)):
  `index.md` at the top, its members beneath it, and a child set nested
  under its directory node as its own `index.md` and rows. A link never
  makes an edge, since a link reaches any file in any set.
- **Label** — a role phrase naming the file's concern, the one its
  frontmatter `description` states, then that file's `##` headings,
  verbatim, joined by `·`.

Counts, tallies, statuses and dates stay out. They go stale between one
drawing and the next.

{If the set is a working set, the directory `<branch>-working-docs/`,
{Read [the link tree](~/workspace/dev-playbook/standards/knowledge-organization/documentation-sets/working-documentation-sets.md#the-link-tree)}}
and draw that tree in place of the index rows: `index.md` at the top
with one edge to `ROOT.md`, then each edge a link from one member to
another, descending from `ROOT.md`. A file with two children spends an
elbow and puts the second child to the right. A member no path from
`ROOT.md` reaches stands alone at the bottom, under no edge.

## The shape

The tree of sets, every row hanging from its index:

```
index.md ··························· role
├── first-member.md ················ role: section · section · section
├── second-member.md ··············· role: section · section
├── child-set/ ····················· role
│   ├── index.md
│   ├── child-member.md ············ role: section · section
│   └── last-child.md ·············· role: section
└── last-member.md ················· role: section · section ·
                                     section · section
```

The link tree of a working set, descending from `ROOT.md`:

```
index.md
   │
   ▼
ROOT.md ···························· role: section · section · section
   │
   ▼
branching-file.md ·················· role: section · section ·
   │        │                        section · section
   │        └───────────────────────┐
   ▼                                ▼
main-child.md ············ role:    side-child.md
   │                       section  role: section · section
   │                       section
   ▼
leaf-file.md ······················· role: section · section
   │
   ▼
child-set/ ························· file · file
```

ASCII box characters only, 78 columns wide, one annotation column every
label aligns to, fragments rather than sentences. Where two nodes stand
side by side, the left one's label narrows to make room.

{Report the diagram} and nothing else — no commentary above or below it.

This shape is the set's standing form for the rest of the conversation.
Redraw it on request without loading this skill again.
