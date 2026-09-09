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
then {Read `index.md` at the set's root}, every member it lists, and every
child set beneath it the same way, to the bottom. No hint means the set
already in focus: work from what you hold, since its files are read.

## What the diagram shows

Structure, never state. Each part comes from something that changes only
when a file changes:

- **Node** — the filename, verbatim. A set's directory keeps its
  trailing slash.
- **Edge** — a row of the index, in listing order
  ([the listing](~/workspace/dev-playbook/standards/knowledge-organization/indexes.md#the-listing)):
  `index.md` at the top, its members beneath it. A link never makes an
  edge, since a link reaches any file in any set.
- **Parent** — the directory of the index one level up, as one node
  above the root with one edge down to it, and nothing more: the parent
  is an abstraction, the set it holds is not drawn.
- **Child set** — drawn under its directory node at the same detail as
  the main set, its own `index.md`, rows, and children, inside a border
  that marks where the child begins and ends.
- **Label** — a role phrase naming the file's concern, the one its
  frontmatter `description` states, then that file's `##` headings,
  verbatim, joined by `·`. An `index.md` and a directory carry no
  description, so they carry no label: nothing is made up for a node that
  has nothing. A filename that runs past the annotation column puts its
  label on the next line.

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

The tree of sets, the parent above, every row hanging from its index,
and a child set bordered:

```
parent/
   │
index.md
├── first-member.md ················ role: section · section · section
├── second-member.md ··············· role: section · section
├── child-set/
│   ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
│   ┃ index.md
│   ┃ ├── child-member.md ·········· role: section · section
│   ┃ └── a-long-filename-child.md
│   ┃                                role: section
│   ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
└── last-member.md ················· role: section · section ·
                                     section · section
```

The link tree of a working set, descending from `ROOT.md`:

```
parent/
   │
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
child-set/
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃ index.md
┃ ├── child-member.md ·············· role: section · section
┃ └── last-child.md ················ role: section
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

A child set of a working set is a set like any other, so it takes the
bordered index-row form even though its parent takes the link tree.

ASCII box characters only, 78 columns wide, one annotation column every
label aligns to, fragments rather than sentences. Where two nodes stand
side by side, the left one's label narrows to make room.

{Report the diagram} and nothing else — no commentary above or below it.

This shape is the set's standing form for the rest of the conversation.
Redraw it on request without loading this skill again.
