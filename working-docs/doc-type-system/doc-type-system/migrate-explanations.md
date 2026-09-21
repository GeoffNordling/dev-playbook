---
type: General-Sheet
title: Migrate Explanations
description: The prompt one agent loads to dissolve one family's explanation.md into its Standards — the why block it writes, the destination each paragraph takes, the sorting rules, the edit it makes, what it leaves alone, and the report it returns
---

# Migrate Explanations

The prompt for the Migrate Explanations part of step 10 in
[Doc-Type System](/working-docs/doc-type-system/doc-type-system/ROOT.md#planned):
one agent owns one family, `standards/<family>/`, reads its
`explanation.md` and its Standards, moves each paragraph to the rule
or Standard it argues for or deletes it, deletes `explanation.md`, and
returns a report. It edits no file outside its directory and never
stages or commits.

## Your input

The launch prompt names one directory, `standards/<family>/`. Read
its `explanation.md` whole, then every other `.md` in the directory
and in its subdirectories. Read
[Doc-Type](/standards/doc-type/doc-type.md) once: it is the worked
example, a Standard whose why sits beside each rule. Read the Rules
section of
[Population and Rules Encoding](/doc-types/standard/encoding.md#rules)
for the form of the block. Read nothing else.

## The why block

A rule's why is one block after its trailer and a blank line, opening
`> **Why.**`, every line prefixed `> `, running to the next heading.
A Standard's own why is one block of the same form after the last
paragraph of the lead, before the first H2. A why is the argument for
the rule or the Standard, never a predicate: no sentence of it holds
a member to a state.

## Sorting

Every paragraph of `explanation.md` takes exactly one destination. A
bullet list item is a paragraph. A heading is a locator, not content;
nothing of it moves.

- **why of `<rule id>`.** The paragraph argues one rule. It becomes
  that rule's why, or joins it as a second paragraph inside the same
  block; a rule never has two blocks.
- **document why of `<file>`.** The paragraph argues two or more rules
  of one Standard, or the Standard as a whole. It goes to the block
  after that Standard's lead, never to both rules.
- **delete: citation.** A link to a rule or a restatement of one.
- **delete: definition.** A definition of a term, which is a
  Standard's condition or a glossary's, not a why.
- **delete: procedure.** Steps, or a writer's heuristic; a Guide's.
- **delete: state.** A description of the repo, a script's behaviour,
  a count, or a date, true today and stale tomorrow.

A sentence in a kept paragraph that holds a member to a state is a
predicate: leave it out of the why and name it in the report; step 11
rules on it. Time words go: "today", "yet", "until", "no extractor
exists", "the three built"; cut them or write the timeless form. A
rule may end with no why; write nothing to fill one. Where two
readings are close, pick one, mark the row `?` in the report, and say
the other in one sentence.

## The edit

Edit the Standards directly. For each kept paragraph, write it into
its destination block with the time-word cuts made, wrapped at 72
columns, every line prefixed `> `. Then delete `explanation.md`.

In your directory, and there only: delete the sentence of each
Standard's lead that names the Explanation, "The reasoning behind the
rules is [X Explanation](...)"; delete the family `index.md`'s row for
it and the lead sentence naming it; repoint any other link into
`explanation.md` from inside the directory to the rule whose why now
holds the text, or unlink it to plain words where the text was
deleted.

Run `scripts/playbook-lint`. A finding that names a file in your
directory is yours; a finding that names a file outside it, a link
into your deleted `explanation.md` from elsewhere, is not: list it in
the report. Do not edit outside your directory to clear it.

## Your report

Return, and write nothing to disk but the edits above:

1. One table, one row per paragraph of the deleted file in file order:
   the heading path, the first five words, the destination, and one
   line of reason. A `?` row carries the other reading.
2. The predicates you left out of a why, each with its paragraph's
   row number.
3. The time-word cuts you made.
4. The lint findings outside your directory, verbatim.
