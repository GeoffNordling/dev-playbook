---
type: General-Sheet
title: Migrate Guides
description: The prompt one agent loads to rewrite one Guide to Instruction Encoding — the parts it sorts the file into, the marks it writes, what it keeps and what it leaves alone, and the report it returns
---

# Migrate Guides

The prompt for the Migrate Guides part of step 10 in
[Doc-Type System](/working-docs/doc-type-system/doc-type-system/ROOT.md#planned):
one agent owns one Guide under `guides/`, reorganizes it so every
part is a sequence, a step, or a reference in the marks
[Instruction Encoding](/doc-types/guide/encoding.md) fixes, changes
nothing the Guide says, and returns a report. It edits no file
outside its Guide and never stages or commits.

## Your input

The launch prompt names one file, `guides/<work>.md`. Read it whole.
Read [Instruction](/doc-types/guide/contract-shape.md) for the three
parts, [Instruction Encoding](/doc-types/guide/encoding.md) for the
marks, and [Guide Conventions](/standards/doc-type/guide-conventions.md)
for the rules the file is held to. Read nothing else.

## The parse

The test of your rewrite is the parse: the headings, in order and
nested as written, with each sequence's step names under it. Before
you edit, write that parse down for the file as it stands; after, for
the file as you left it. The second is the gist of the Guide, and a
reader who sees only it should know what the Guide covers and, for a
recipe, what they will do.

## Sorting

Every heading's section is one of two things, and every ordered list
is one thing.

- **A sequence.** Actions a reader performs in order. It is a heading
  holding one ordered list from `1.`, at most one sentence before the
  list, nothing after it. Each item opens `**<Name>.**`, the name one
  action; the rest of the item is the instruction as it stood, a
  fenced block or a table included. A procedure written as numbered
  headings, `## 1. Grow the tree`, becomes one list under one heading.
  A single action standing in prose under its own heading becomes a
  list of one. Two procedures are two headings, each numbered from
  one, never one list of their sum.
- **A reference.** Everything else under a heading: a concept, a
  call, a catalogue entry, a table of findings. Its body stays as it
  is, bulleted lists included. Named items in a bulleted list that a
  reader looks up one at a time, four `gh api` calls each with a bold
  name, become headings of their own.
- **A bulleted list** that ranks, enumerates, or lists alternatives
  stays bulleted; an ordered list that does so becomes bulleted, since
  the parse reads every ordered list as a sequence.
- **The lead**, between the H1 and the first heading, is neither. It
  says what the work is and, where the Guide has more than one
  sequence, how they relate. A paragraph after a sequence's list that
  belongs to no step moves here or into the step it qualifies.

## Headings

The heading is all the parse shows of its section, so each one names
its section specifically: `Path-scoped permissions do not work`, not
`Permissions`; `Wire the pin`, not `Step 2`. Rename a heading that
does not, in the section's own words. Keep the heading's slug where
another file links it (`grep -rn "<work>.md#" --include=*.md` from
the worktree root shows them); where the rename is worth a broken
anchor, list the inbound link in your report and do not edit it.

## What you do not change

The Guide's meaning: no sentence gains or loses a claim, no
instruction changes what it tells the reader to do, no link is
dropped. Reorder, regroup, rename headings, convert list forms, split
a paragraph between two steps; do not cut, summarize, or add. Time
words go only where the encoding page or the conventions demand
nothing of them: leave them, and name them in the report.

## The edit

Edit the Guide in place, wrapped at the file's own column. Run
`scripts/playbook-lint` by its absolute path under the worktree root;
the relative form is refused. A finding that names your Guide is
yours; a finding naming another file, an inbound anchor you broke, is
not: list it in the report and do not edit outside your Guide.

## Your report

Return, and write nothing to disk but the Guide:

1. The parse before and the parse after, as two indented outlines.
2. One row per heading you renamed: old, new, and the inbound links
   that break.
3. Each place you were unsure whether a section is a sequence or a
   reference, with the reading you took and the other in one sentence.
4. The lint findings outside your Guide, verbatim.
