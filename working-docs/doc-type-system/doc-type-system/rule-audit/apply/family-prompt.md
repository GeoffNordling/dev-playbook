---
type: General-Sheet
title: Family Apply Prompt
description: The prompt a family agent loads to apply the step 11 rulings to one Standard family — the six rulings and what each changes, the principles, and the report
---

# Family apply: one Standard family

You apply the step 11 rulings to one Standard family. Your launch
message names the family's directory under `standards/` and its work
order, one file under `rule-audit/apply/`. You edit the Standards of
that family and its `index.md`, and nothing else. You commit nothing.

## Principles

1. **The ruling is law.** Apply it as written; never re-judge it,
   however the rule reads to you.
2. **Move words; do not invent.** Every sentence you write comes from
   the row's text cell.
3. **A row you cannot apply is a report row, not a decision.** Where
   the file no longer matches the row, the rule is already gone, its
   sentence already changed, a why block already stands and says
   something else, or the text cell lacks what the ruling needs, leave
   the rule as it is and report the row with both readings.
4. **Counts are not a test.** Report a difference with the rows behind
   it; the rows are what is checked.
5. **One family, one agent.** An edit a ruling needs outside your
   family's files is a report line, not an edit.

## Read, in this order

1. [The rule shape](/standards/doc-type/standard-conventions.md#the-rule-shape)
   and the three rules after it: what a rule, a why block, and a
   condition look like.
2. Your work order, then every Standard in your family.

## The rulings

Your work order has one row per rule: the id, the file, the ruling, the
trailer kind the rule ends with, and the text the ruling needs. Apply
every row, in file order.

- **keep**: the rule stands. Make the trailer's kind word match the
  kind column; it already does for nearly every row.
- **retrailer**: set the trailer's kind word to the kind column.
  Nothing else changes.
- **condition**: delete the trailer line and the blank line before it.
  The heading, its sentence, and its body stay, and the rules under it
  keep their trailers. Add no why block.
- **rewrite**: apply the text cell, part by part, and set the trailer's
  kind word to the kind column. A `Sentence:` part replaces the rule's
  first paragraph, verbatim. A `Block:` part changes only the block or
  clause it names; the first paragraph stays. A `Why:` part is the
  rule's why block: where the rule has none, write one, `> **Why.**`
  then the part's words, after the trailer and before the next heading;
  where the part opens `*stands.*`, a why block is already there: read
  it, confirm it says what the part says, and add nothing.
- **add**: the rule does not exist yet. The text cell is the whole
  rule, heading to why block; paste it verbatim after the rule the
  `After:` part names.
- **delete**: remove the heading, the first paragraph, any block, the
  trailer, and any why block.
- **guide**: the same removal as delete. The Guide the text cell names
  was written before you launched: confirm the file exists, then remove
  the rule, and write nothing into the Guide. Where the rule's whole
  file has already left `standards/` because a Guide agent moved it,
  the row is done; say so in your report.

Leave `standards/verifiers.yaml`, `standards/boundaries.yaml`, and
every script and test alone; the orchestrator regenerates the tables
and silences the emitters of deleted ids.

## After the rows

Fix what the removals leave behind, in your family's files only: a
sentence in a Standard's lead that names a deleted rule, a heading with
nothing under it, and a row in the family's `index.md` that describes
a file by rules that are gone. Then run `scripts/playbook-lint`; fix a
finding in a file you own and report one in a file you do not.

## Report

Per row, applied or not. Then: every row you could not apply, with its
ruling and what the file shows; every `*stands.*` why block that does
not say what the part says, with both texts; every edit a ruling needed
outside your family; and what `playbook-lint` said.
