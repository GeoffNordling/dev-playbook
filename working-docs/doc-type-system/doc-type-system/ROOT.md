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

Three DocTypes, ten verbs, in
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
  10. *Verify every rule.* Last. A holistic pass over every
     deterministic predicate, not a rush to the end, and not a Loop:
     iteration, dynamic workflows, or subagents may do the work, but no
     `loops/` file is written for it. No
     new check is added one rule at a time, and no GitHub issue is
     opened: every rule is fixed, reclassified, merged, or deleted in
     this PR.
     - **Reclassify.** Check every rule's kind. A deterministic rule
       with a null row that no script could decide becomes stochastic.
       A stochastic rule a script could decide becomes deterministic.
     - **Deterministic only.** Stochastic rules stay null in the
       verifier table. This step is deterministic cleanup.
     - **Design the checking system as one unit.** Today's detectors
       grew one at a time over months and were never refactored
       together. Take every deterministic predicate together: which
       kinds and groups of predicates exist, which files each reads, and
       how they group into scripts with public APIs. Design a general,
       modular, extensible system of checking scripts from that,
       refactor the existing detectors into it, wire it into the
       pre-commit hooks, and keep it at least as fast as the hooks are
       today.
     - **The design comes first.** Before any detector is rewritten, a
       design document under this strand states the reclassified rule
       set, the kinds of deterministic predicates, and the proposed
       scripts and their APIs, and the user approves it. The rewrite
       follows the approved design.
     - **Remove redundancy.** A predicate that duplicates or overlaps
       another is merged into it or deleted.
     - **A rule the repo breaks** is fixed or deleted here.
     Reason: step 1 tagged a rule deterministic when a script could
     decide it, not when one does. A Standard that states what the repo
     does not do is slop, and a checking system built greedily is one
     nobody can extend.

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

- **One meaning per word, one home per word, 2026-09-15.** Every word
  the four strands use is defined once, in the set's
  [Terms](/working-docs/doc-type-system/ROOT.md#terms) or in one
  strand's root, and every other use links to it. Reason: the same word
  carried two senses more than once in this work, and a loop reading
  these files cannot ask which was meant.
- **One doc-type for Standard.** Merged into one directory,
  [doc-types/standard/](/doc-types/standard/index.md), whose shape the
  refactor replaces with the
  [Reference Model](/working-docs/doc-type-system/doc-type-system/reference-model.md)'s.
- **Standard takes its new shape, 2026-09-20.** Step 1 of The system.
  Every rule under `standards/` is a heading, a predicate, and a trailer
  `` `<name>.<slug>` · deterministic|stochastic ``, drained one ruleset
  at a time by the
  [Body Drain](/working-docs/doc-type-system/doc-type-system/body-drain.md)
  rubric; the teaching the drains displaced became guides. Reason: a
  loop cannot route a rule without an id and a kind.
- **The verifier table, 2026-09-20.** Step 2 of The system.
  `standards/verifiers.yaml` maps every rule id under `standards/` to
  the one check that decides it, or null. `scripts/verifier-table`
  derives it from the trailers, each detector's `--list-rules`, and a
  dependency map; `--write` writes it and the bare call lints it on
  every commit, failing loud by the rules of `standard/detectors.md`. A
  consumer's table holds only its own rules; the union is read from the
  pinned clone.
- **Boundaries: where each check runs, 2026-09-20.** Step 3 of The
  system. `standards/boundaries.yaml` maps every address the verifier
  table names to the gates that run it, `commit`, `push`, `ci`,
  `on-demand`. `scripts/boundary-table` derives it from the wiring, the
  pre-commit config, the pre-push `make check`, the workflows, and
  playbook-lint's ungated audits, never from prose. `standard/gates.md`
  is deleted: the rungs are the file's columns.
- **Isolate the software factory, 2026-09-20.** Step 4 of The system.
  Everything of the factory lives in `working-docs/software-factory/`,
  whose `ROOT.md` names each piece and where it came from; every link
  into it from the rest of the repo was cut or repointed.
  `candidate-promote` does not work without intake, and its fate goes
  with the factory's.
- **Guide and Explanation, 2026-09-20.** Step 5 of The system. The
  registry defines `Guide`, how to do a kind of work, homed in
  `guides/`, and `Explanation`, the reasoning behind one Standard's
  rules at `standards/<name>/explanation.md`; standards-lint admits
  only a Standard, an Explanation, and a Guide in a Standard directory.
  Target state that lived in explanations became rules, each null in
  the verifier table until a check exists.
- **Retire the card, 2026-09-20.** Step 6 of The system. The `card.md`
  files, the type `Standard-Card`, `cardgen`, `rulegen`, and the `.txt`
  views are gone, and `Standard-Ruleset` is `Standard` everywhere. Each
  directory index opens with the sentence its card carried and the
  catalog repeats it. `standard/cards.md` is `standard/tree.md`, The
  Standards Tree. A consumer's leftover card is an unknown type at the
  next pin bump.
- **Tidy the doc-type definitions, 2026-09-21.** Step 7 of The system.
  The pseudocode is four blocks, the base in `doc-types/doc-type.md`
  and one class per `contract-shape.md`, none carrying a location; the
  reference model holds all four and `tests/test_pseudocode_sync.py`,
  temporary, fails when the texts differ. `chaingen` and `chains.txt`
  are deleted, kept at `b266ce4`.
- **The specification becomes a Standard, 2026-09-21.** Step 8 of The
  system. `standards/doc-type/` holds
  [Doc-Type](/standards/doc-type/doc-type.md), seven rules over any
  doc-type directory, and the three Standards over the files a doc-type
  types, Standard, Runbook, and Loop Conventions. The placement rule: a
  rule over what is inside a file is the doc-type's Standard's; a rule
  over where a file sits is the family's. The Standards Tree gained
  `standard.the-statement`, the sentence every directory index opens
  with and the catalog repeats. The draft `specification/` is deleted;
  Loop's three drafted rules are a planned item of the Loop strand.
- **Ban the word guard, 2026-09-21.** Step 9 of The system. A guard is
  one kind of condition, so `condition` is always correct where `guard`
  is. prose-lint's banned word became a vocabulary in two layers: the
  workspace's actor noun, fixed in the module, and the repo's own words
  in a tracked root `.prose-lint-vocabulary` of word, `say`, and
  `where`, the directories the ban covers; a faulty declaration is exit
  2. dev-playbook bans `guard` under `doc-types/` and
  `standards/doc-type/`; the rule is `prose.the-repo-vocabulary` in Doc
  Conventions.

## Acronyms

- **CI** — Continuous Integration.
- **PR** — Pull Request.
