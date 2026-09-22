---
type: General-Sheet
title: Doc-Type System
description: The root of the doc-type system strand — the language of doc-types, verbs, and predicates, its principles and terms, and the worklist from the Standard's new shape through the first instance
---

# Doc-Type System

The strand that holds the language: what a doc-type is, its verbs, its
rules as predicates, its encodings as grammar. Speculative, per
[Synthesis Working Root](/working-docs/doc-type-system/ROOT.md).
It defines Loop, one of its three doc-types
([Loop](/working-docs/doc-type-system/loop/ROOT.md)), and each
encoding it writes defines an extractor of the fact base
([Fact Base Strand](/working-docs/doc-type-system/fact-base/ROOT.md)).
The user's own words on the work are kept verbatim in
[Personal Notes](/working-docs/doc-type-system/doc-type-system/personal-notes.md)
for use outside the set.

## Goal

Five DocTypes, twelve verbs, in
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
  [Writing Predicates](/working-docs/doc-type-system/doc-type-system/writing-predicates.md)
  is how; it may become the Standard that governs it.
- **A predicate is a test over state.** It is decided from the bytes
  of the repo at one commit, by reading them or by a pure function of
  them such as a formatter. It is not a test over run-time behaviour
  (what a script exits or prints), not an instruction to an author
  (where a helper sits, which double a test uses), not a fact held
  outside the files (the day a decision was made, the latest upstream
  release, a GitHub setting, git history, another repo), and not a
  definition that scopes other rules. Behaviour and instruction go to
  a Guide; the why goes to an Explanation; a scoping definition is an
  H2 with no trailer. The step 11 sort
  ([Rule Rulings](/working-docs/doc-type-system/doc-type-system/rule-audit/rulings.md#rules-by-family))
  found each of these mis-filed as a rule.
- **Kind is judged from the sentence, not the trailer.** A sentence a
  script decides from the files with no judgment call is
  deterministic; a sentence with a judgment word ("describes",
  "names the concept", "small against") is stochastic. Where a
  sentence mixes the two, the mechanical part stays deterministic and
  the judgment moves to the Explanation. Whether a check exists yet
  is a separate question; an unchecked predicate of either kind is
  allowed until the detector rewrite lands.
- **A scoping heading is not a rule.** An H2 with no trailer names
  which members the H3 rules under it bind. It is one shape whether
  it has one child or eleven, and its definition is never repeated in
  the children.
- **An Explanation is the Reasons for one Standard, and nothing
  else.** A Reason is one design decision and the argument for it: a
  heading, a body, and one line naming the rule ids it explains. A
  decision lands as one rule or several of the same Standard, a
  deterministic rule beside its stochastic partner or several
  deterministic rules cut apart to be checkable, so a Reason names one
  id or several, and every id resolves in the Standard beside it. A
  Reason is optional: a rule may have none, and none is written for a
  rule whose why nobody holds. Text that is a reason for no rule is
  not an Explanation: a definition goes to the Standard's lead or the
  glossary, a procedure to a Guide, and the rest is deleted. The
  pseudocode names the explained document by its base type, so a later
  doc-type is explained the same way. Decided 2026-09-21 from the
  scrub in step 10.
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
- **Reason** — the one Part of an Explanation: one design decision
  and the argument for it, naming the rule ids of the Standard beside
  it that the decision landed as.

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
  11. *Settle every rule.* Go through every rule and rule on each:
     keep, rewrite, delete, merge with another, or fold under a
     condition. The ruling per rule, the text each ruling needs, and
     the order of the pass are in
     [Rule Rulings](/working-docs/doc-type-system/doc-type-system/rule-audit/rulings.md).
     Text that is not a predicate leaves the rule: a why becomes the
     rule's why block, a procedure goes to a Guide, a scoping
     definition becomes a condition. A rule with a judgment
     word is stochastic and stays null in the verifier table; a rule a
     script decides from the files is deterministic. A rule the repo
     breaks is rewritten, deleted, or, where the state is a small
     named oversight, the repo is fixed. Documents only: trailers and
     the two yaml tables update, a detector that emits a deleted id
     stops emitting it, and no detector logic changes. Output: the
     Standards say only what is true of the files.
     Reason: the audit found intentions, run-time behaviour, scoping
     definitions, and code-style instruction filed as predicates, and
     a checker is only worth building against a settled spec.
  12. *The checking system.* A greenfield refactor, after step 11
     merges. Today's detectors grew one at a time over months and were
     never refactored together. Take every deterministic predicate of
     the settled Standards together: which kinds and groups exist,
     which files each reads, and how they group into scripts with
     public APIs. Design a general, modular, extensible system of
     checking scripts from that, build it, wire it into the pre-commit
     hooks, and keep it at least as fast as the hooks are today. It
     absorbs what step 11 leaves unchecked: the sixteen weak checks,
     the thin-shim moves, the `doc-type.one-base` check, and the
     H2-without-trailer condition shape.
     - **The design comes first.** Before any detector is rewritten, a
       design document under this strand states the kinds of
       deterministic predicates and the proposed scripts and their
       APIs, and the user approves it. The rewrite follows the approved
       design.
     Reason: a checking system built greedily is one nobody can extend,
     and a checker is only worth building against a spec that is
     settled.

  13. *The rule id namespace.* A rule id is `<family>.<slug>`, the
     directory and the heading, while the Explanation's check and the
     Standard's own population are per file: an id names a family and
     the verifier then finds which Standard it landed in. Decide
     whether the id becomes `<standard>.<slug>`, or the family stays the
     namespace and a Standard directory is the unit that owns it, and
     move the trailers, the two yaml tables, and every detector that
     emits an id together. Reason: the id scheme thinks in families and
     the doc-types think in files, and one of them should give; not
     before step 12, which touches every emitter anyway.

  A step once here, scrubbing every file under `docs/` into a long-term
  home, is dropped 2026-09-20: step 1 sent nothing to `docs/` except
  `docs/guides/`, and the eight loose files there predate this work.
  The one move this plan causes is named at its step, `okf-spec` at
  step 6.
- **First instance.** One loop, `loops/<name>.md`, over the doc-type
  system, after step 8: its checks point at the Standard
  [Doc-Type](/standards/doc-type/doc-type.md), and the loop grows it. In iteration order: an act drafts
  candidate predicates, each with its citation or marked invented and
  the members that fail it today; a yield to the user, yes or no per
  predicate; an act applies the accepted ones; a check audits; a yield
  to the user with the diff. A no is kept with its reason, and the
  reason is a candidate predicate itself. The design behind it is
  [Specifying a Loop](/working-docs/doc-type-system/loop/specifying-a-loop.md).
  Whether Loop gains a part for the scalar this loop descends is the
  Loop strand's item
  ([Planned](/working-docs/doc-type-system/loop/ROOT.md#planned)).
- **The `/write-predicates` skill.** A runbook that points at
  [Writing Predicates](/working-docs/doc-type-system/doc-type-system/writing-predicates.md);
  after the guide settles. Also improve writing-predicates.md; it's
  a rough first draft user does not endorse it yet.
- **One clause in System Legibility.** Its sentence that
  documentation is the stochastic thing and code the deterministic
  one is imprecise; one clause says that stochasticity is a scale per
  file ([Principles](/working-docs/doc-type-system/doc-type-system/ROOT.md#principles)).

## Completed

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
  delete, per
  [Migrate Explanations](/working-docs/doc-type-system/doc-type-system/migrate-explanations.md).
  The Explanation type, its registry rows, rule, okf-lint check, and
  `ADMITTED_TYPES` entry are gone; 22 inbound links repointed. The
  predicates the agents left out are in their reports, for step 11.
- **Guides migrated, 2026-09-21.** Step 10, last part. Guide's parts
  are Sequence, Step, and Reference; the parse is the headings and
  the step names. The verbatim-mirror type became `Mirror` and
  Runbook's chain the chain to free the word. Five Opus agents
  rewrote the Guides per
  [Migrate Guides](/working-docs/doc-type-system/doc-type-system/migrate-guides.md);
  `headless.md` moved to `docs/` as a General-Sheet. The residual
  ledger holds five entries.

## Acronyms

- **CI** — Continuous Integration.
- **PR** — Pull Request.
