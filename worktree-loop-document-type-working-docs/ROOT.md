---
type: General-Sheet
title: Loop Doc-Type Working Root
description: The set's root — goal, principles, terms, and the worklist for building the Loop doc-type as a peer of Runbook and Standard
---

# Loop Doc-Type Working Root

This set is speculative: its members write guesses as guesses, and every
member inherits that voice. The work builds the **Loop** doc-type, a
third directory under `doc-types/` beside
[runbook/](/doc-types/runbook/index.md) and
[standard/](/doc-types/standard/index.md), and then its first instance.

## Goal

A Loop doc-type that is a full peer of Runbook and Standard under
[Doc-Type](/doc-types/doc-type.md): operations, a composition rule, a
shape, an encoding, and a residual ledger, in one directory, with its row
in the registry table and its entry in the roster of
[Doc-Type System](/doc-types/doc-type-system.md). Then one loop that
uses it.

## Principles

- **Peers first.** Wherever a choice is open, pick the one that keeps
  the three doc-types parallel.
  [Three Peers](/worktree-loop-document-type-working-docs/three-peers.md)
  holds the parallel structure.
- **Verbs.** Each doc-type is defined by a short list of simple verbs,
  its operations. Overlap between doc-types is allowed.
- **Simple and composable.** The definition carries no policy. Yield is
  where a loop is programmed to yield; the doc-type does not rule when a
  loop is worth writing. The user decides that.
- **Predicates, not fixes.** An idea about the doc-type system is
  written as a goal, a predicate, or an objective, never carried out as
  an instruction.
  [Specifying a Loop](/worktree-loop-document-type-working-docs/specifying-a-loop.md)
  holds the forms.
- **Both forms.** A target state is written twice: as a reference
  model, the picture the user thinks in, and as a specification,
  predicates that describe the whole set and not one member of it.
  [Reference Model](/worktree-loop-document-type-working-docs/reference-model.md)
  is the picture. Both use the words of
  [Glossary](/worktree-loop-document-type-working-docs/glossary.md),
  one meaning each.
- **Predicates are written one way.**
  [Writing Predicates](/worktree-loop-document-type-working-docs/writing-predicates.md)
  is how; it may become the Standard that governs it.
- **Park, do not divert.** A stale or broken thing found on the way is
  recorded in
  [Stale Findings](/worktree-loop-document-type-working-docs/stale-findings.md)
  and left alone.

## Terms

- **Loop** — drives a state toward a target state by iteratively taking
  prescribed actions and validating against prescribed standards. The
  one-sentence definition; the shape carries its parts.
- **Target state** — the set of states that satisfy the spec a loop's
  checks measure against. What the user wants beyond the spec is not a
  target state; it reaches the loop only as guidance to an act that
  proposes predicates.
- **Findings** — what a check returns: each names a member and the
  rule it fails. The loop's working state; acts read them.
- **Yield** — the third operation: a loop's programmed exit to
  something outside it, another loop or the user. An instance writes
  "yields when …"; the when is the instance's.
- **Predicate** — a statement about one member at one moment that is
  true or false of it, per
  [Glossary](/worktree-loop-document-type-working-docs/glossary.md).
  [Specifying a Loop](/worktree-loop-document-type-working-docs/specifying-a-loop.md#the-three-written-forms)
  holds the three written forms, goal, predicate, and objective;
  [Writing Predicates](/worktree-loop-document-type-working-docs/writing-predicates.md)
  is how one is written.

## Planned

- **The system.** Three DocTypes, ten verbs, in
  [Reference Model](/worktree-loop-document-type-working-docs/reference-model.md):
  the picture of the target state;
  [Doc-Type Specification](/worktree-loop-document-type-working-docs/specification/doc-type.md)
  is the set. The refactor toward them, in order; each step exists
  because the step after it binds to what the step produces, and the
  reasons are here because the agent doing the work was not in the
  conversation that decided them.
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
     is a lint failure, not a silent gap.
  3. *Boundaries read ids from config.* The commit hook, `make check`,
     CI, and a loop's check each name the rule ids they run, in config,
     not in the Standard. Reason: which boundary runs a rule is
     wiring, and a Standard that states its own enforcement cannot be
     audited by a loop without also being gated; the same rule must
     be gated in one repo and aspirational in another.
  4. *Retire the card.* Delete `Standard-Card`, its four cells, Define,
     Audit, Enforce, Adopt, `cardgen`, `rulegen`, and the `.txt`
     views, and bind the type `Standard` to `standards/<name>/<topic>.md`.
     Reason: the reference model places every cell elsewhere, Define is
     the Standard file, Audit is the verifier table, Enforce is the
     boundary config, and Adopt was never a primitive; and viewing is
     out of scope for this work.
     [Reference Model](/worktree-loop-document-type-working-docs/reference-model.md#what-goes-where)
     lists each disposition.
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
     [specification/](/worktree-loop-document-type-working-docs/specification/index.md)
     under `standards/` in the shape step 1 produces, bound to no repo
     boundary. Reason: the first loop's checks point at it, and a loop
     must not bind to the Standard shape that step 4 deletes.
  8. *Ban the word guard.* See its own entry below.
  Then the first instance. This branch merges with a related branch
  that overlaps on part of this list; on merge, take whichever side
  has done a step and keep the reason.
- **First instance.** One loop, `loops/<name>.md`, over the doc-type
  system, after step 7: its checks point at the specification as a
  Standard, and the loop grows it. In iteration order: an act drafts
  candidate predicates, each with its citation or marked invented and
  the members that fail it today; a yield to the user, yes or no per
  predicate; an act applies the accepted ones; a check audits; a yield
  to the user with the diff. A no is kept with its reason, and the
  reason is a candidate predicate itself. The design behind it is
  [Specifying a Loop](/worktree-loop-document-type-working-docs/specifying-a-loop.md).
  One thing the doc-type cannot yet carry: infinitely many states
  satisfy the specification, so a loop that proposes doc-types needs a
  scalar to descend, lexicographic, residuals, then doc-types, then
  verbs, then shared verbs, with a stop on stagnation. Whether Loop
  gains a part for it, and what the part is, is decided when this
  loop is written.
- **The `/write-predicates` skill.** A runbook that points at
  [Writing Predicates](/worktree-loop-document-type-working-docs/writing-predicates.md);
  after the guide settles. Also improve writing-predicates.md; it's
  a rough first draft user does not endorse it yet.
- **One meaning per word, one home per word.** A pass over every
  word the doc-type system uses, in
  [Glossary](/worktree-loop-document-type-working-docs/glossary.md),
  the reference model, the specification, the three doc-type
  directories, and `CONTEXT.md`, that ends with every term defined
  once, in one place, in a sentence a verifier could read, and every
  other use linking to it. Reason: the same word carried two senses
  more than once in this work, guard beside condition, evaluator
  beside verifier, bundle beside directory, and each cost a round of
  correction; a loop reading these files cannot ask which sense was
  meant. What the pass produces: a list of every term with its one
  home; a merge or a rename for every overlap, duplication, or
  conflict found; and a banned-word entry in prose-lint for each word
  retired on the way, guard first, so a habit in the model's weights
  is caught at the commit boundary rather than by the user.

## Completed

- **One-sentence definition.** Settled; recorded in Terms and in
  [Three Peers](/worktree-loop-document-type-working-docs/three-peers.md).
- **Family.** Files typed `Loop` under `loops/`, mirroring Standard.
  Recorded in Three Peers.
- **Shape, directory, encoding, residual ledger.** Written to
  `doc-types/loop/`: [Acts, Checks, and Yields](/doc-types/loop/contract-shape.md),
  its [encoding](/doc-types/loop/encoding.md), and the
  [ledger](/doc-types/loop/residual-ledger.md), seeded empty.
- **Operations and composition rule.** Three verbs, act, check, yield;
  the checks carry the target. Recorded in Three Peers.
- **Location rule and registry.** okf-lint's `type-location` check
  binds `Loop` to `loops/`; the `Loop` row and the Typed Loop rule are
  in `document-types.md`; the registry ruling and the roster entry are
  in `doc-type-system.md`; `loops/` exists with an empty index.
- **Obligation.** `scripts/loop-lint` is the detector behind
  [Loop Conventions](/standards/knowledge-organization/loop-conventions.md),
  the Standard that binds a `Loop` file to the encoding; enrolled in the
  `playbook-lint` roster, so a bad Loop file cannot be committed. Logic in
  `src/dev_playbook/loop_lint.py`, tests beside it.
- **Standard is one doc-type.** Merged into one directory,
  [doc-types/standard/](/doc-types/standard/index.md), with Contract
  defined by the cut in [Doc-Type](/doc-types/doc-type.md). The shape
  it carries there is the one the refactor replaces with
  [Reference Model](/worktree-loop-document-type-working-docs/reference-model.md)'s.

## Acronyms

- **PR** — Pull Request.
