---
type: General-Sheet
title: Doc-Type System
description: The root of the doc-type system strand — the language of doc-types, verbs, and predicates, its principles and terms, the open questions, and the completed refactor from the Standard's new shape through every rule settled
---

# Doc-Type System

The strand that holds the language: what a doc-type is, its verbs, its
rules as predicates, its encodings as grammar. Speculative, per
[Synthesis Working Root](/working-docs/doc-type-system/ROOT.md).
It defines Loop, one of its four doc-types
([Loop](/working-docs/doc-type-system/loop-and-workstream/ROOT.md)), and each
encoding it writes defines an extractor of the fact base
([Fact Base Strand](/working-docs/doc-type-system/fact-base/ROOT.md)).
The user's own words on the work are kept verbatim in
[Personal Notes](/working-docs/doc-type-system/doc-type-system/personal-notes.md)
for use outside the set.

## Goal

Four DocTypes, eleven verbs, in
[Reference Model](/working-docs/doc-type-system/doc-type-system/reference-model.md),
the picture of the target state; the Standard
[Doc-Type](/standards/doc-type/doc-type.md) is the same state as
predicates over any doc-type.
The refactor that reaches them, then one loop that grows the
specification.

## Principles

- **Peers first.** Wherever a choice is open, pick the one that keeps
  the four doc-types parallel.
  [Reference Model](/working-docs/doc-type-system/doc-type-system/reference-model.md)
  holds the parallel structure, and each peer has its conventions
  Standard under `standards/doc-type/`.
- **Verbs.** Each doc-type is defined by a short list of simple verbs,
  its operations. Overlap between doc-types is allowed.
- **Both forms.** A target state is written twice: as a reference
  model, the picture the user thinks in, and as a specification,
  falsifiable predicates that describe the whole set and not one member
  of it, never as a linear description plus actions. The reference
  model is the witness; the predicates are the spec; both are kept.
  Both use the words of
  [Terms](/working-docs/doc-type-system/ROOT.md#terms), one
  meaning each.
- **Predicates are written one way.**
  [Writing Predicates](/guides/writing-predicates.md)
  is how.
- **A predicate is a test over state, and kind is judged from the
  sentence.** The rule and its argument are
  [Every predicate decidable of one member](/standards/doc-type/standard-conventions.md#every-predicate-decidable-of-one-member);
  the step 11 sort found behaviour, instruction, outside facts, and
  scoping definitions each mis-filed as a rule. Whether a check exists
  yet is a separate question; an unchecked predicate of either kind is
  allowed.
- **A scoping heading is not a rule.** An H2 with no trailer is a
  condition, per
  [A rule: heading, predicate, trailer](/standards/doc-type/standard-conventions.md#a-rule-heading-predicate-trailer).
- **The why sits with the rule it argues, in the same file.** The
  block's form is
  [A why states no predicate](/standards/doc-type/standard-conventions.md#a-why-states-no-predicate);
  a rule may have none. Decided 2026-09-21 from the scrub in step 10,
  which is why the Explanation type is deleted: the user cannot read a
  rule and its why across two files.
- **Three working policies** that shaped the step 11 rulings and hold
  for any later review: repo change is the expensive way out; no credit for rule count, so
  delete is the default for a rule that restates another or binds
  something too small to matter; and "keep it because a check
  emits the id" is backwards, since the check follows the rule.
- **Stochasticity is a continuous scale per file.** A markdown file
  with no declared structure sits at one; code sits at zero; a file
  with embedded structure sits between. A file's stochasticity is what
  lies outside its declared structure, which is what
  [the doc-type build loop](/doc-types/doc-type.md#the-doc-type-build-loop)
  already calls the residual. The bedrock of determinism is a
  threshold on content, not a line between file kinds.
- **Shape is orthogonal to stochasticity.** A fully deterministic
  runbook or loop still gets its doc-type document, because the
  document is the legible form. For a runbook, a drift check binds
  the document to the code it describes, the deterministic rule the
  deleted prototype chaingen applied to a runbook and its chain. A
  loop has none yet
  ([Unfiled](/working-docs/doc-type-system/loop-and-workstream/ROOT.md#unfiled)).

## Terms

- **DocType** — the base class of
  [Reference Model](/working-docs/doc-type-system/doc-type-system/reference-model.md):
  a class extends it when its instance is one markdown file of that
  type. `Object`, its earlier name, is retired.
- **Part** — a class nested inside a DocType: an Edge, a Rule, an
  Act, a Check, a Yield. A part has no verbs.
- **Why** — a block opening `> **Why.**`: the argument for the rule
  whose trailer it follows, or for the file when it ends the opening
  prose. It holds no predicate.

## Open

- **Rule order.** Standard rules are unordered in
  [Population and Rules](/doc-types/standard/contract-shape.md) and in
  file order in the reference model. One must give.
- **The `External` target.** The reference model's `External`
  catch-all target sits against the fact base's total accounting.
- **Whether the fenced pseudocode becomes real Python.**
  [Ontology Solvers](/working-docs/doc-type-system/doc-type-system/ontology-solvers.md)
  proposes the route: a module of dataclasses with no bodies, checked
  by mypy, introspected into an ontology.

## Planned

None.

## Completed

- **Step 11 wave 5, reheadlining, 2026-09-22.** Thirty-seven Opus
  agents, one per Guide or Standard file, in two batches of 8 and 29,
  rewrote 169 headings into propositions; the orchestrator applied the
  union repo-wide, since a rule's id is its heading's slug. 112 ids
  moved, in three forms — plain, escaped regex, and one bare slug —
  66 inbound citations repointed, most carrying their link text to the
  new heading and the rest to the target's title where the heading
  would not sit in the sentence, and both yaml tables regenerated.
  `okf-lint` found the type registry by that heading's slug and went
  blind on the rename; the slug is a named constant now, and the
  check rewrite carried the coupling. Dropped: trimming the body openings the
  new headings absorb, since the overlap is no finding. Commits
  b76047e, ae587cd, dedc625, 4439ea5, 0d22ed4, and this one.

- **Step 11 wave 4, 2026-09-22.** The orchestrator pass, by hand in
  the session, closing what the family waves left across files. The
  twelve emitters of deleted ids went silent, and the four GitHub
  audits of `workspace-lint` kept their checks under a new Standard,
  `tracking/github-settings.md`, after the user ruled that a check
  needs a predicate over state, not a Guide. The two yaml tables
  regenerated, five catalog rows took their indexes' openings, and
  fifteen anchors into deleted rules were unlinked. The reported rows
  settled: one why block rewritten, three why blocks under conditions
  moved or dropped, two terminal periods, a factory skill's stale
  gloss, and the doc-type lead's rule count. Three routing citations
  wave 2 had tightened away were restored, and the deslopper gained
  the `assertion-headings` slice. Commits 88d0381 and this one.

- **Step 11 wave 3, 2026-09-22.** The repo changes, by hand in the
  session rather than by agent, after the first agent run was rolled
  back unseen. Eight of the eleven bullets landed: three skill models
  to `inherit`, the repeatable-work rule under `CLAUDE.md`'s
  Behaviors, acronym appendices on 35 files, two index openings, two
  Flourish tics, two wayfinder headings recased, sixteen second-person
  uses rewritten, and the settings-symlink design moved out of
  `dotfiles/README.md` into record 0030. Struck: the `CONTEXT.md`
  terms and the `ROOT.md` link tree, both duplicating what exists;
  held for wave 5: the four prose headings. Commit 9000802.

- **Step 11 waves 1 and 2, 2026-09-22.** Five Opus agents wrote four
  Guides and one reference from rule text, and moved
  `tracking/repo-settings.md` to `guides/`; thirteen Opus agents then
  applied all 283 rulings, one family each. Decided on the way: the
  modules family retires, its seven rules all judgments and now in the
  Design and Testing Guide; `prose.assertion-headings` replaces the
  Guide gist rule, every parsed heading one clause stating its point;
  a reheadlining wave follows the family passes. Commits b5a0c08 and
  b01d0fd.

- **Explanation and Guide shaped, 2026-09-21.** Step 10 of The
  system, first half. Thirteen Opus agents tagged every paragraph of
  the 13 `explanation.md` files with the rule ids it explains; the
  tables were noise and were discarded, but they settled the shape: a
  Reason is one decision naming one or more rules of the one Standard
  beside it, a rule may have none, and an Explanation holds nothing
  else. The reference model gained `Id`, the Condition part,
  Explanation, and Guide.
- **Explanation and Guide built, 2026-09-21.** Step 10, second half.
  `doc-types/explanation/` and `doc-types/guide/` in the four-file
  form, `Id` in the base page and the Condition part on Standard's,
  the pinned test over six pages and passing, the registry rows, and
  `explanation-conventions.md` and `guide-conventions.md` under
  `standards/doc-type/`, eight rules with null verifier rows. Guide's
  parts are left undecided until its Guides are migrated.
- **Explanation undone, the why folded into Standard, 2026-09-21.**
  Step 10, third part. Moving the Explanation file to
  `<dir>/explanations/<topic>.md` surfaced that the user cannot read a
  rule and its why across two files. `doc-types/explanation/`,
  Explanation Conventions, the registry rule `typed-explanation`, and
  its okf-lint check are deleted; the reference model drops
  `Explanation`, four DocTypes now. `Standard.Rule` and `Standard`
  each gained a `why: str | None`, a `> **Why.**` block after a
  rule's trailer or after the lead, never a predicate; the predicate
  stays heading to trailer, so no check or judge prompt changed.
  `standards/doc-type/doc-type.md` carries the ten Reasons sorted for
  the deleted Explanation, folded in as the test of the encoding.
- **Explanations migrated, the type deleted, 2026-09-21.** Step 10,
  fourth part. Thirteen Opus agents, one per family, sorted each
  `explanation.md` into rule whys, the Standard's own why, or a
  delete, per the Migrate Explanations prompt, since deleted.
  The Explanation type, its registry rows, rule, okf-lint check, and
  `ADMITTED_TYPES` entry are gone; 22 inbound links repointed. The
  predicates the agents left out are in their reports, for step 11.
- **Guides migrated, 2026-09-21.** Step 10, last part. Guide's parts
  are Sequence, Step, and Reference; the parse is the headings and
  the step names. The verbatim-mirror type became `Mirror` and
  Runbook's chain the chain to free the word. Five Opus agents
  rewrote the Guides per the Migrate Guides prompt, since deleted;
  `headless.md` moved to `docs/` as a General-Sheet. The residual
  ledger holds five entries.

## Acronyms

None.
