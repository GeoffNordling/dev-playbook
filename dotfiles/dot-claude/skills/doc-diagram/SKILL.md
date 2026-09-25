---
name: doc-diagram
description: Draw a documentation set and every set nested under it as an ASCII tree of filenames and section names, following the index rows, or the links from a head file where the set has one.
disable-model-invocation: true
model: inherit
effort: medium
arguments: [doc-hint]
---

# Doc Diagram

Draw one documentation set and every set nested under it. `doc-hint`
names a directory, its `index.md`, or a description; resolve it to the
directory whose `index.md` is the set's root
([Documentation Sets](~/workspace/dev-playbook/standards/knowledge-organization/documentation-sets/documentation-sets.md)).
Empty means the set already in focus: work from what you hold, since
its files are read. Then {Read `index.md` at the set's root}, every
member it lists, and every set nested beneath it the same way, to the
bottom.

## Two views

A set holding a `WORKSTREAM.md` is drawn in the reading view, and any
other set in the membership view.

- **Membership.** Each edge is a row of the index, in listing order
  ([one entry per concept document and child directory](~/workspace/dev-playbook/standards/knowledge-organization/indexes.md#one-entry-per-concept-document-and-child-directory)),
  `index.md` at the top.
- **Reading.** `index.md` at the top with one edge to `WORKSTREAM.md`,
  then each edge a link from one member to another, descending from
  `WORKSTREAM.md`
  ([every file reached from its head file](~/workspace/dev-playbook/standards/knowledge-organization/documentation-sets/workstream-files.md#every-file-reached-from-its-head-file)).
  A file with two children spends an elbow and puts the second child
  to the right. A member no path reaches stands alone at the bottom,
  under no edge. Each file is drawn once, under the first edge that
  reaches it.

A nested set chooses its own view. One with a view of its own, a set
in the membership view or a child workstream in the reading view, is
drawn under the edge that reaches it at the same detail, inside a
border that marks where it begins and ends. A directory without a
`WORKSTREAM.md` under a set in the reading view shares its head file,
so it gets no border: each of its files joins the link tree where a
link reaches it, its name drawn with the directory, such as
`notes/draft.md`.

## What each part is

Structure, never state: each part changes only when a file changes.

- **Node** — the filename, verbatim. A directory keeps its trailing
  slash.
- **Edge** — an index row or a link, as the view says. In the
  membership view a link never makes an edge, since a link reaches any
  file in any set.
- **Parent** — the directory of the index one level up, as one node
  above the root with one edge down to it, and nothing more.
- **Label** — a role phrase naming the file's concern, the one its
  frontmatter `description` states, then that file's `##` headings,
  verbatim, joined by `·`. An `index.md` and a directory carry no
  description, so they carry no label. A filename that runs past the
  annotation column puts its label on the next line.

Counts, tallies, statuses and dates stay out; they go stale between one
drawing and the next.

## The shape

ASCII box characters only, 78 columns wide, one annotation column every
label aligns to, fragments rather than sentences. Where two nodes stand
side by side, the left one's label narrows to make room. The membership
view, with a nested set bordered:

```
parent/
   │
index.md
├── first-member.md ················ role: section · section · section
├── child-set/
│   ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
│   ┃ index.md
│   ┃ └── a-long-filename-child.md
│   ┃                                role: section
│   ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
└── last-member.md ················· role: section · section ·
                                     section · section
```

The reading view, with an elbow and a child workstream bordered:

```
parent/
   │
index.md
   │
   ▼
WORKSTREAM.md ···························· role: section · section · section
   │
   ▼
branching-file.md ·················· role: section · section
   │        └───────────────────────┐
   ▼                                ▼
notes/draft.md ··········· role:    side-child.md
   │                       section  role: section · section
   ▼
child-workstream/
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃ index.md
┃    │
┃    ▼
┃ WORKSTREAM.md ···················· role: section · section
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

{Report the diagram} and nothing else — no commentary above or below it.

This shape is the set's standing form for the rest of the conversation.
Redraw it on request without loading this skill again.
