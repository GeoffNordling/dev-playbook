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
[standard/](/doc-types/standard/index.md), the way those two were once
built from their families.

## Goal

A Loop doc-type that is a full peer of Runbook and Standard under
[Doc-Type](/doc-types/doc-type.md): operations, a composition rule, a
shape, an encoding, a generated view, and a residual ledger, in the same
five-file bundle, with its row in the registry table and its entry in the
roster of [Doc-Type System](/doc-types/doc-type-system.md).

## Principles

- **Peers first.** Wherever a choice is open, pick the one that keeps
  the three doc-types parallel.
  [Three Peers](/worktree-loop-document-type-working-docs/three-peers.md)
  holds the parallel structure.
- **Verbs.** Each doc-type is defined by a short list of simple verbs,
  its operations. Overlap between doc-types is allowed.
- **The meta object, not an instance.** The work is the doc-type; no
  specific loop is built here. Specific loops are examples that test the
  shape.
- **Simple and composable.** The definition carries no policy. Yield is
  where a loop is programmed to yield; the doc-type does not rule when a
  loop is worth writing. The user decides that.
- **Park, do not divert.** A stale or broken thing found on the way is
  recorded in
  [Stale Findings](/worktree-loop-document-type-working-docs/stale-findings.md)
  and left alone.

## Terms

- **Loop** — drives a state toward a target state by iteratively taking
  prescribed actions and validating against prescribed standards. The
  one-sentence definition; the shape carries its parts.
- **Target state** — what the loop drives toward. Its definiteness varies
  by instance: a mergeable PR is definite; a vision of the repo is not.
  Both are valid target states.
- **Findings** — what a check returns: each names a member and the
  rule it fails. The loop's working state; acts read them.
- **Yield** — the third operation: a loop's programmed exit to
  something outside it, another loop or the user. An instance writes
  "yields when …"; the when is the instance's.

## Planned

- **Bundle.** `contract-shape.md`, `encoding.md`, `residual-ledger.md`
  in `doc-types/loop/`, from the drafts in this set. `definition.md` is
  written.
- **Encoding.** A Mermaid block as the source of truth; frontmatter, one
  paragraph, and three verb sections around it.
- **Generator.** `scripts/loopgen --check`, a checker of the embedded
  graph against the verb sections and the pointers.
- **Location rule.** The okf-lint `type-location` check extended to
  `Loop` under `loops/`.
- **Residual ledger.** Seeded empty.
- **Registry and roster.** The `Loop` kind in the Types table of
  `document-types.md` with its location rule, the rulings row and the
  roster entry in `doc-type-system.md`, and the empty `loops/` tree.
- **Obligation.** The doc-type binds nobody. A small Standard,
  population "files typed `Loop`", rules the encoding rules, auditor
  `loopgen --check`, is what makes every Loop file carry its shape at
  commit time, the way `harness/runbook-conventions` and the chain
  drift check do for Runbook.
- **First instance.** The doc-type system improver: a loop that drives
  the doc-type system toward the target state in
  [Three Peers](/worktree-loop-document-type-working-docs/three-peers.md#the-first-instances-standard).
  Its checks need a Standard for that target state, aspirational,
  audited, never gated, written first. Whether its acts include a
  deterministic ontology solver is open; not discussed yet.

## Completed

- **One-sentence definition.** Settled; recorded in Terms and in
  [Three Peers](/worktree-loop-document-type-working-docs/three-peers.md).
- **Family.** Files typed `Loop` under `loops/`, mirroring Standard.
  Recorded in Three Peers.
- **Shape.** Drafted in
  [Loop Shape](/worktree-loop-document-type-working-docs/loop-shape.md);
  awaiting the user's reaction.
- **Operations and composition rule.** Three verbs, act, check, yield;
  target dropped, since the checks carry it. Recorded in Three Peers.

## Acronyms

- **PR** — Pull Request.
