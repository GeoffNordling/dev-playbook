---
type: General-Sheet
title: Doc-Type System
description: The root of the doc-type system strand — the language of doc-types, verbs, and predicates, its principles and terms, and the worklist from the Standard's new shape through the first instance
---

# Doc-Type System

The strand that holds the language: what a doc-type is, its verbs, its
rules as predicates, its encodings as grammar. Speculative, per
[Synthesis Working Root](/working-docs/doc-type-system/ROOT.md).
It defines Loop, one of its four doc-types
([Loop](/working-docs/doc-type-system/loop/ROOT.md)), and each
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
  the three doc-types parallel.
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
  allowed until the detector rewrite lands.
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
  for any later audit: repo change is the expensive way out; no credit for rule count, so
  delete is the default for a rule that restates another or binds
  something too small to matter; and "keep it because a detector
  emits the id" is backwards, since the detector follows the rule.
- **Stochasticity is a continuous scale per file.** A markdown file
  with no declared structure sits at one; code sits at zero; a file
  with embedded structure sits between. A file's stochasticity is what
  lies outside its declared structure, which is what
  [the doc-type build loop](/doc-types/doc-type.md#the-doc-type-build-loop)
  already calls the residual. The bedrock of determinism is a
  threshold on content, not a line between file kinds.
- **Shape is orthogonal to stochasticity.** A fully deterministic
  runbook or loop still gets its doc-type document, because the
  document is the legible form. The one requirement that follows is
  a drift check between the document and its substrate, the same
  deterministic rule the deleted prototype chaingen applied to a
  runbook and its chain. The
  loop half is in the Loop strand
  ([Principles](/working-docs/doc-type-system/loop/ROOT.md#principles)).

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

- **The system.** The refactor toward the reference model and the
  specification. The target shape of one rule, decided 2026-09-20: a heading,
  the predicate, and a trailer line, nothing else. The predicate is
  everything between the heading and the trailer, a list of exemptions
  included when the check needs one, and it is written so that
  deterministic code lifts it verbatim into a judge's prompt, alone or
  concatenated with other stochastic rules for one judge call. A body
  after the trailer is not part of the target: what the 232 bodies
  hold today is enforcement wiring, which step 3 removes, pointers to
  other Standards, which the fact base carries, and exemptions, which
  belong inside the predicate. Reason: text that no verifier reads is
  text the state is not held to, and the split between a checked first
  paragraph and an unchecked body is where the prose and the verifier
  drift apart.
  1. *Standard takes its new shape.* Done 2026-09-20; the entry is in
     [Completed](#completed).
  2. *The verifier table.* Done 2026-09-20; the entry is in
     [Completed](#completed).
  3. *Boundaries: where each check runs.* Done 2026-09-20; the entry is
     in [Completed](#completed).
  4. *Isolate the software factory.* Done 2026-09-20; the entry is in
     [Completed](#completed).
  5. *Guide and Explanation.* Done 2026-09-20; the entry is in
     [Completed](#completed).
  6. *Retire the card.* Done 2026-09-20; the entry is in
     [Completed](#completed).
  7. *Tidy the doc-type definitions.* Done 2026-09-21; the entry is in
     [Completed](#completed).
  8. *The specification becomes a Standard.* Done 2026-09-21; the
     entry is in [Completed](#completed).
  9. *Ban the word guard.* Done 2026-09-21; the entry is in
     [Completed](#completed).
  10. *Doc-types before migration.* Done 2026-09-21; the entries are
     in [Completed](#completed).
  11. *Settle every rule.* Done 2026-09-22 over five waves; the
     entries are in [Completed](#completed). What the audit found
     and step 11 does not close is in
     [Detector Fixes](/working-docs/doc-type-system/doc-type-system/detector-fixes.md),
     the detector suite's input.

  A step once here, scrubbing every file under `docs/` into a long-term
  home, is dropped 2026-09-20: step 1 sent nothing to `docs/` except
  `docs/guides/`, and the eight loose files there predate this work.
  The one move this plan causes is named at its step, `okf-spec` at
  step 6.
- **The detector suite.** One holistic pass over the checking system:
  refactor, reconsider, redesign. The detectors grew one at a time over
  months and were never refactored together, and step 11 settled the
  Standards they answer to, so the pass rewrites the whole Python
  detector suite against the settled rules, from scratch where that is
  cleaner. It must stay at least as fast as the hooks are today.
  - **Four layers name the same rules, and no two of them agree.** At
    step 11's close, 217 rules carry a trailer:

    | Layer | What it is | Where it lives |
    | --- | --- | --- |
    | Family | the directory, and the id's namespace | 12 of them |
    | Standard | the file, and the population a rule binds | 31 rule-carrying files |
    | Detector | the script that decides the rule | 18 addresses over 98 rules; 119 rules have none |
    | Gate | when the detector runs | commit, push, ci, or on-demand |

    Family and Standard part company in 6 of the 12 families:
    `knowledge-organization.` spans 8 files, `doc-type.` 5,
    `tracking.` 4, `build.` 3, `harness.` and `standard.` 2 each. A
    detector crosses both — `repo-lint` decides 20 rules from 3
    families and 6 files, `harness-files-lint` 12 rules from 2
    families. The gate is a fourth cut again: `workspace-lint` holds
    14 rules and runs at no gate at all.
  - **The id schema is designed with the scripts, not after them.** An
    id is `<family>.<slug>`, the directory and the heading's slug, so
    the namespace is coarser than the population it binds. One fix
    has been proposed and measured, `<standard>.<slug>`, and the
    evidence is against it: it moves 210 of the 217 ids, only 7 match
    their file; it drops the word that carries the meaning
    (`build.ciyml-byte-identical-to-canonical` becomes
    `canonical.ciyml-…`); and it lands `prose/conventions.md`,
    `shell/conventions.md` and `testing/conventions.md` on one
    `conventions.` namespace. There are no slug collisions today, so
    nothing is broken. The design rules on the schema — including
    leaving it alone — with the layer map above in front of it,
    because what names a group of rules and what script owns them are
    the same question.
  - **Its input.**
    [Detector Fixes](/working-docs/doc-type-system/doc-type-system/detector-fixes.md)
    holds what step 11 leaves unchecked: the fourteen rules whose
    detector tests less than the sentence, with the survey behind
    them, the thin-shim moves, the `doc-type.one-base-class` check,
    and the H2-without-trailer condition shape. The 52 deterministic
    rules with a null verifier are the rest of the ground.
  - **A detector may key on something that is not an id.** `okf-lint`
    finds the type registry by that heading's slug, so a rename of the
    heading lands in the detector. The design gives every such
    coupling one named place.

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
  detector suite's item carries the coupling. Dropped: trimming the body openings the
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
  stays heading to trailer, so no detector or judge prompt changed.
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
