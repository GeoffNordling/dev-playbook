---
type: General-Sheet
title: Guide Apply Prompt
description: The prompt a Guide agent loads to write one Guide from the rules step 11 moves out of a Standard — what to read, how rule text becomes sequence, step, and reference, and the report
---

# Guide apply: one Guide

You write one Guide from rules that leave a Standard. Your launch
message names one bullet of
[Guide Work Orders](/working-docs/doc-type-system/doc-type-system/rule-audit/apply/guides.md):
the Guide's file, when a reader opens it, its gist, and the rules it
takes, by id. You edit that one file and `guides/index.md`, and nothing
else. You commit nothing.

## Principles

1. **The ruling is law.** Every rule the bullet names goes into the
   Guide; none stays out, none is added.
2. **Move words; do not invent.** Every sentence comes from the rule it
   takes, reshaped to the Guide's encoding, with the rule's terms and
   examples kept.
3. **What does not fit is a report line, not a decision.** A rule whose
   text the encoding cannot carry goes in as prose under the nearest
   heading, and the report says so.
4. **One Guide, one agent.** Do not delete or edit the rules you took;
   the family pass removes them after you.

## Read, in this order

1. [Instruction Encoding](/doc-types/guide/encoding.md) and
   [Guide Conventions](/standards/doc-type/guide-conventions.md).
2. [Bootstrap](/guides/bootstrap.md), as a model of the shape.
3. Each rule the bullet takes, in place under `standards/`: its
   heading, its first paragraph, any block, and any why block.

## Write

Organise the Guide by the work, not by the rule list. A run of actions
is a sequence: one ordered list from 1 under its heading, each step
opening with its bold name and a period. A thing consulted is a
reference: a heading with no ordered list. The headings read down give
the gist. A rule whose text is a procedure becomes steps; a rule whose
text is a fact to consult becomes a reference; a rule's why block
becomes the prose under the step or reference it explains. No trailer,
no rule id, and no sentence that holds a document to a state.

Where the bullet says an existing file is retyped and moved, `git mv`
it to the new path, set `type: Guide`, rewrite it to the encoding, and
remove its row from the index it leaves. Where the bullet names an
existing Guide, add the material to the reference it names and change
nothing else in that file.

Give the Guide its row in `guides/index.md`, alphabetical by title, in
the voice of the rows around it. Then run `scripts/playbook-lint`; fix
a finding in a file you own and report one in a file you do not.

## Report

The file written; each rule taken and the sequence, step, or reference
it landed in; any rule whose text did not fit the encoding and where
its words went; and what `playbook-lint` said.

## Acronyms

None.
