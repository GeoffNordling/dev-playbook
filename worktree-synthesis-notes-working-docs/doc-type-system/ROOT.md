---
type: General-Sheet
title: Doc-Type System
description: The root of the doc-type system strand — the language of doc-types, verbs, and predicates, its principles, the rulings filed here, and the worklist from the Standard's new shape through the first instance and the vocabulary pass
---

# Doc-Type System

The strand that holds the language: what a doc-type is, its verbs, its
rules as predicates, its encodings as grammar. Speculative, per
[Synthesis Working Root](/worktree-synthesis-notes-working-docs/ROOT.md).
It defines Loop, one of its three doc-types
([Loop](/worktree-synthesis-notes-working-docs/loop/ROOT.md)), and each
encoding it writes defines an extractor of the fact base
([Fact Base Strand](/worktree-synthesis-notes-working-docs/fact-base/ROOT.md)).
The user's own words on the work are kept verbatim in
[Personal Notes](/worktree-synthesis-notes-working-docs/doc-type-system/personal-notes.md)
for use outside the set.

## Goal

Three DocTypes, ten verbs, in
[Reference Model](/worktree-synthesis-notes-working-docs/doc-type-system/reference-model.md),
the picture of the target state;
[Doc-Type Specification](/worktree-synthesis-notes-working-docs/doc-type-system/specification/doc-type.md)
is the same state as predicates, with one file per doc-type beside it.
The refactor that reaches them, then one loop that grows the
specification.

## Principles

- **Peers first.** Wherever a choice is open, pick the one that keeps
  the three doc-types parallel.
  [Three Peers](/worktree-synthesis-notes-working-docs/doc-type-system/three-peers.md)
  holds the parallel structure.
- **Verbs.** Each doc-type is defined by a short list of simple verbs,
  its operations. Overlap between doc-types is allowed.
- **Both forms.** A target state is written twice: as a reference
  model, the picture the user thinks in, and as a specification,
  falsifiable predicates that describe the whole set and not one member
  of it, never as a linear description plus actions. The reference
  model is the witness; the predicates are the spec; both are kept.
  Both use the words of
  [Glossary](/worktree-synthesis-notes-working-docs/glossary.md), one
  meaning each.
- **Predicates are written one way.**
  [Writing Predicates](/worktree-synthesis-notes-working-docs/doc-type-system/writing-predicates.md)
  is how; it may become the Standard that governs it.

## Decided

- **Stochasticity is a continuous scale per file.** A markdown file
  with no declared structure sits at one; code sits at zero; a file
  with embedded structure sits between. A file's stochasticity is what
  lies outside its declared structure, which is what the doc-type
  build loop already calls the residual. The bedrock of determinism is
  a threshold on content, not a line between file kinds.
  [System Legibility](/docs/system-legibility.md)'s sentence that
  documentation is the stochastic thing and code the deterministic one
  is imprecise and needs one clause to say this.
- **Shape is orthogonal to stochasticity.** A fully deterministic
  runbook or loop still gets its doc-type document, because the
  document is the legible form. The one requirement that follows is
  a drift check between the document and its substrate, the same
  deterministic rule chaingen applies to a runbook and its chain. The
  loop half is filed in the Loop strand
  ([Decided](/worktree-synthesis-notes-working-docs/loop/ROOT.md#decided)).
- **An encoding defines an extractor; it is not a spec.** Under the
  glossary a spec is a set of predicates. An `encoding.md` is mostly a
  function, the primitive map from written form to rows, which is the
  extractor's definition. The well-formedness predicates buried in it,
  a span nests at most two deep, one link names a target, belong in
  the Standard whose verifier is the drift check, or in the one coarse
  rule every grammar induces: the file parses.

## Open

- **Rule order.** Standard rules are unordered in
  [Population and Rules](/doc-types/standard/contract-shape.md) and in
  file order in the reference model. One must give.
- **The `External` target.** The reference model's `External`
  catch-all target sits against the fact base's total accounting.
- **Whether the fenced pseudocode becomes real Python.**
  [Ontology Solvers](/worktree-synthesis-notes-working-docs/doc-type-system/ontology-solvers.md)
  proposes the route: a module of dataclasses with no bodies, checked
  by mypy, introspected into an ontology.

## Planned

- **The system.** The refactor toward the reference model and the
  specification, in order; each step exists because the step after it
  binds to what the step produces, and the reasons are here because
  the agent doing the work was not in the conversation that decided
  them.
  1. *Standard takes its new shape.* Every rule gets an id,
     `<standard>.<slug>`, and a kind, deterministic or stochastic, on
     a trailer line after its predicate paragraph, and a rule may sit
     under another rule as its condition. Reason: a loop's check routes
     each rule to a verifier by id and kind, so a rule without both
     cannot be checked, and a stochastic rule is one an LLM judge
     decides, using the predicate paragraph as its prompt.
  2. *The verifier table and `audit`.* One table in the toolchain maps
     every rule id to exactly one script or judge, and one `audit`
     function in the package routes ids through it, skips a rule whose
     condition fails, and returns findings, each one member and one
     rule id. Reason: this is the one place the Standard files and the
     code meet, so a rule with no verifier or a verifier with no rule
     is a lint failure, not a silent gap. The table's shape as declared
     data the fact base extracts is the fact base strand's item
     ([Planned](/worktree-synthesis-notes-working-docs/fact-base/ROOT.md#planned)).
  3. *Boundaries read ids from config.* The commit hook, `make check`,
     CI, and a loop's check each name the rule ids they run, in config,
     not in the Standard. Reason: which boundary runs a rule is
     wiring, and a Standard that states its own enforcement cannot be
     audited by a loop without also being gated; the same rule must
     be gated in one repo and aspirational in another. The config's
     shape as declared data is the same fact base item as step 2's.
  4. *Retire the card.* Delete `Standard-Card`, its four cells, Define,
     Audit, Enforce, Adopt, `cardgen`, `rulegen`, and the `.txt`
     views, and bind the type `Standard` to `standards/<name>/<topic>.md`.
     Reason: the reference model places every cell elsewhere, Define is
     the Standard file, Audit is the verifier table, Enforce is the
     boundary config, and Adopt was never a primitive; and viewing is
     out of scope for this work.
     [Reference Model](/worktree-synthesis-notes-working-docs/doc-type-system/reference-model.md#what-goes-where)
     lists each disposition. The fact base's extractors item strikes
     the card extractor for this reason. `rulegen` goes as a script
     with its `.txt` view; its logic moves into the package as the
     `standard` extractor, per that item
     ([Planned](/worktree-synthesis-notes-working-docs/fact-base/ROOT.md#planned)).
  5. *`Object` becomes `DocType`, and the one-module lint.* Rename
     across `doc-type.md` and the three `contract-shape.md` files, nest
     each part inside its doc-type's class, and add the linter that
     concatenates the four pseudocode fences and parses them as one
     Python module. Reason: the parts, Edge, Rule, Act, Check, Yield,
     are not doc-types and must not extend the base; the linter is the
     first verifier for the specification and is what makes the three
     contract shapes one design instead of three.
  6. *Runbook's two edits.* `accept` replaces `args` as the verb for
     an input edge, and `never write` becomes a `banned` polarity on a
     write edge. Reason: every operation on an edge must be one of the
     doc-type's verbs, and `args` was a noun and `never` a negation,
     neither a verb.
  7. *The specification becomes a Standard.* Move
     [specification/](/worktree-synthesis-notes-working-docs/doc-type-system/specification/index.md)
     under `standards/` in the shape step 1 produces, bound to no repo
     boundary. Reason: the first loop's checks point at it, and a loop
     must not bind to the Standard shape that step 4 deletes.
  8. *Ban the word guard.* See the vocabulary pass below.
- **First instance.** One loop, `loops/<name>.md`, over the doc-type
  system, after step 7: its checks point at the specification as a
  Standard, and the loop grows it. In iteration order: an act drafts
  candidate predicates, each with its citation or marked invented and
  the members that fail it today; a yield to the user, yes or no per
  predicate; an act applies the accepted ones; a check audits; a yield
  to the user with the diff. A no is kept with its reason, and the
  reason is a candidate predicate itself. The design behind it is
  [Specifying a Loop](/worktree-synthesis-notes-working-docs/loop/specifying-a-loop.md).
  Whether Loop gains a part for the scalar this loop descends is the
  Loop strand's item
  ([Planned](/worktree-synthesis-notes-working-docs/loop/ROOT.md#planned)).
- **The `/write-predicates` skill.** A runbook that points at
  [Writing Predicates](/worktree-synthesis-notes-working-docs/doc-type-system/writing-predicates.md);
  after the guide settles. Also improve writing-predicates.md; it's
  a rough first draft user does not endorse it yet.
- **One meaning per word, one home per word.** A pass over every
  word the four strands use, in
  [Glossary](/worktree-synthesis-notes-working-docs/glossary.md),
  the reference model, the specification, the three doc-type
  directories, the fact base and viewer pages, and `CONTEXT.md`, that
  ends with every term defined once, in one place, in a sentence a
  verifier could read, and every other use linking to it. Reason: the
  same word carried two senses more than once in this work, guard
  beside condition, evaluator beside verifier, bundle beside
  directory, and each cost a round of correction; a loop reading these
  files cannot ask which sense was meant. What the pass produces: a
  list of every term with its one home; a merge or a rename for every
  overlap, duplication, or conflict found; and a banned-word entry in
  prose-lint for each word retired on the way, guard first, so a habit
  in the model's weights is caught at the commit boundary rather than
  by the user. The merge of the two branches found these collisions
  for the pass to rule on, one at a time with the user: rule, a
  Standard's predicate against the fact base's rows-to-rows function;
  kind, a view file's, a registry entry's, and `Rule.kind`; registry,
  the doc-type roster against the viewer's list of kinds; view;
  condition; extractor beside generator and encoding; `Object` beside
  `DocType`; adopt. The fact base page's claim to rule vocabulary on
  its own is withdrawn in favor of this pass.

## Completed

- **Standard is one doc-type.** Merged into one directory,
  [doc-types/standard/](/doc-types/standard/index.md), with Contract
  defined by the cut in [Doc-Type](/doc-types/doc-type.md). The shape
  it carries there is the one the refactor replaces with
  [Reference Model](/worktree-synthesis-notes-working-docs/doc-type-system/reference-model.md)'s.

## Acronyms

- **CI** — Continuous Integration.
- **LLM** — Large Language Model.
- **PR** — Pull Request.
