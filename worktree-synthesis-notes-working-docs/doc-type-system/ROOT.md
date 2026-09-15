---
type: General-Sheet
title: Doc-Type System
description: The root of the doc-type system strand — the language of doc-types, verbs, and predicates, its principles and terms, and the worklist from the Standard's new shape through the first instance
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
  [Reference Model](/worktree-synthesis-notes-working-docs/doc-type-system/reference-model.md)
  holds the parallel structure, and each peer has its conventions
  Standard: `harness/runbook-conventions` for Runbook, the
  Meta-Standard under `standard/` for Standard, and
  `knowledge-organization/loop-conventions` for Loop.
- **Verbs.** Each doc-type is defined by a short list of simple verbs,
  its operations. Overlap between doc-types is allowed.
- **Both forms.** A target state is written twice: as a reference
  model, the picture the user thinks in, and as a specification,
  falsifiable predicates that describe the whole set and not one member
  of it, never as a linear description plus actions. The reference
  model is the witness; the predicates are the spec; both are kept.
  Both use the words of
  [Terms](/worktree-synthesis-notes-working-docs/ROOT.md#terms), one
  meaning each.
- **Predicates are written one way.**
  [Writing Predicates](/worktree-synthesis-notes-working-docs/doc-type-system/writing-predicates.md)
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
  deterministic rule chaingen applies to a runbook and its chain. The
  loop half is in the Loop strand
  ([Principles](/worktree-synthesis-notes-working-docs/loop/ROOT.md#principles)).

## Terms

- **DocType** — the base class of
  [Reference Model](/worktree-synthesis-notes-working-docs/doc-type-system/reference-model.md):
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
     files, and bind the type `Standard` to `standards/<name>/<topic>.md`.
     Reason: the reference model places every cell elsewhere, Define is
     the Standard file, Audit is the verifier table, Enforce is the
     boundary config, and Adopt was never a primitive; and viewing is
     out of scope for this work.
     [Reference Model](/worktree-synthesis-notes-working-docs/doc-type-system/reference-model.md#what-goes-where)
     lists each disposition. The fact base's extractors item strikes
     the card extractor for this reason. `rulegen` goes as a script
     with its `.txt` file; its logic moves into the package as the
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
  8. *Ban the word guard.* See the banned words below.
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
- **Banned words in prose-lint.** One entry for each retired word,
  guard, generator, and adopt, each message naming the word to use
  instead, so a habit in the model's weights is caught at the commit
  boundary rather than by the user. The three doc-type directories
  and `CONTEXT.md` take the set's terms when the strand drains.
- **One clause in System Legibility.** Its sentence that
  documentation is the stochastic thing and code the deterministic
  one is imprecise; one clause says that stochasticity is a scale per
  file ([Principles](/worktree-synthesis-notes-working-docs/doc-type-system/ROOT.md#principles)).
- **One frontmatter line after the merge.** Minor.
  [Working Documentation Sets](/standards/knowledge-organization/documentation-sets/working-documentation-sets.md)
  went to `main` ahead of this branch, with the doc-set skills and
  agents, on a branch that carried its frontmatter as `type: Standard`
  because `main` has no `Standard-Ruleset` yet. When this branch
  merges, that line must read `type: Standard-Ruleset` like every other
  Standard; check it after the merge.

## Completed

- **One meaning per word, one home per word, 2026-09-15.** Every
  word the four strands use is defined once, in the Terms bucket of
  the set's root where more than one strand uses it and of a strand's
  root where one does, and every other use links to it. Reason: the
  same word carried two senses more than once in this work, guard
  beside condition, evaluator beside verifier, bundle beside
  directory, and each cost a round of correction; a loop reading these
  files cannot ask which sense was meant. The words are in the set's
  [Terms](/worktree-synthesis-notes-working-docs/ROOT.md#terms).
- **One doc-type for Standard.** Merged into one directory,
  [doc-types/standard/](/doc-types/standard/index.md), with Contract
  defined by the cut in [Doc-Type](/doc-types/doc-type.md). The shape
  it carries there is the one the refactor replaces with
  [Reference Model](/worktree-synthesis-notes-working-docs/doc-type-system/reference-model.md)'s.

## Acronyms

- **CI** — Continuous Integration.
- **PR** — Pull Request.
