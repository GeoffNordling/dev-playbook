---
type: General-Sheet
title: Loop Doc-Type Working Root
description: The set's root — goal, principles, terms, and the worklist for building the Loop doc-type as a peer of Runbook and Standard
---

# Loop Doc-Type Working Root

This set is speculative: its members write guesses as guesses, and every
member inherits that voice. The work builds the **Loop** doc-type, a
third bundle under `doc-types/` beside
[runbook/](/doc-types/runbook/index.md) and
[standard/](/doc-types/standard/index.md), and then its first instance.

## Goal

A Loop doc-type that is a full peer of Runbook and Standard under
[Doc-Type](/doc-types/doc-type.md): operations, a composition rule, a
shape, an encoding, and a residual ledger, in one bundle, with its row
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
- **Park, do not divert.** A stale or broken thing found on the way is
  recorded in
  [Stale Findings](/worktree-loop-document-type-working-docs/stale-findings.md)
  and left alone.

## Terms

- **Loop** — drives a state toward a target state by iteratively taking
  prescribed actions and validating against prescribed standards. The
  one-sentence definition; the shape carries its parts.
- **Target state** — the ruleset a loop's checks measure against. What
  the user wants beyond the ruleset is not a target state; it reaches
  the loop only as guidance to an act that proposes predicates.
- **Findings** — what a check returns: each names a member and the
  rule it fails. The loop's working state; acts read them.
- **Yield** — the third operation: a loop's programmed exit to
  something outside it, another loop or the user. An instance writes
  "yields when …"; the when is the instance's.
- **Predicate** — a statement about one member at one moment that is
  true or false of it. Defined in
  [Specifying a Loop](/worktree-loop-document-type-working-docs/specifying-a-loop.md#the-predicate),
  with the three written forms, goal, predicate, and objective.

## Planned

- **First instance.** One loop, `loops/<name>.md`, over the doc-type
  system. Its checks point at the Audit cell of a standard for the
  system's target state, aspirational, audited, never gated, that does
  not exist yet; its seed is in
  [Three Peers](/worktree-loop-document-type-working-docs/three-peers.md#the-first-instances-standard).
  The loop in iteration order: an act drafts candidate predicates for
  that standard, each with its citation or marked invented and the
  members that fail it today; a yield to the user, yes or no per
  predicate; an act applies the accepted ones; a check runs the
  standard's audit; a yield to the user with the diff. A no is recorded
  so the predicate is never re-proposed. The design behind it is
  [Specifying a Loop](/worktree-loop-document-type-working-docs/specifying-a-loop.md).
- **The standard.** Written before the loop, by the user and the
  agent, one predicate at a time; the loop grows it after. A predicate
  lands in a ruleset as a rule: a name, a condition, and the predicate.

## Completed

- **One-sentence definition.** Settled; recorded in Terms and in
  [Three Peers](/worktree-loop-document-type-working-docs/three-peers.md).
- **Family.** Files typed `Loop` under `loops/`, mirroring Standard.
  Recorded in Three Peers.
- **Shape, bundle, encoding, residual ledger.** Written to
  `doc-types/loop/`: [Acts, Checks, and Yields](/doc-types/loop/contract-shape.md),
  its [encoding](/doc-types/loop/encoding.md), and the
  [ledger](/doc-types/loop/residual-ledger.md), seeded empty.
- **Operations and composition rule.** Three verbs, act, check, yield;
  the checks carry the target. Recorded in Three Peers.
- **Location rule and registry.** okf-lint's `type-location` check
  holds a map of three bound types, `Standard-Card`, `Standard-Ruleset`,
  and `Loop`; the `Loop` row
  and the Typed Loop rule are in `document-types.md`; the rulings row
  and the roster entry are in `doc-type-system.md`; `loops/` exists
  with an empty index.
- **Obligation.** `scripts/loop-lint` is the detector behind
  [Loop Conventions](/standards/knowledge-organization/loop-conventions.md),
  the Standard that binds a `Loop` file to the encoding; enrolled in the
  `playbook-lint` roster, so a bad Loop file cannot be committed. Logic in
  `src/dev_playbook/loop_lint.py`, tests beside it. Loop has no generator
  and no `.txt` view: the Mermaid graph is the view.
- **Standard is one object.** One doc-type, four verbs, two file kinds,
  `Standard-Card` and `Standard-Ruleset`, in
  [doc-types/standard/](/doc-types/standard/index.md). `Object` defined
  and Contract defined by the cut in
  [Doc-Type](/doc-types/doc-type.md). The parallel is the table in
  [Three Peers](/worktree-loop-document-type-working-docs/three-peers.md#the-parallel-today).

## Acronyms

- **PR** — Pull Request.
