---
type: Guide
title: Governed Repo
description: What a repo in the workspace declares rather than leaves to be inferred — the GOVERNED roster that names it, where a Decision Record sits, what a merged record freezes, and the working documentation set it stands up on main; read when adding a repo to the workspace or writing a Decision Record
---

# Governed Repo

What a repo in the workspace declares rather than leaves to be
inferred: that it is governed, what it decided, and what work is in
flight inside it. The roster is consulted when a repo is added to the
workspace, at the [roster enrollment](/guides/bootstrap.md#enroll-in-the-governed-roster)
that ends [Bootstrap](/guides/bootstrap.md); the rest is consulted
when a Decision Record or a working documentation set is written.

## Which repos are governed

workspace-lint's `GOVERNED` roster names every governed repo, and
behind every name in it is a repo under the workspace root. Repos land
under the workspace root for reasons the standard has no say in, so
the directory listing cannot tell a governed repo from a neighbour,
and inclusion is declared instead. A name with no repo behind it is a
false claim, and a sweep that quietly covers less is worse than one
that stops.

## Where a Decision Record sits

A Decision Record's home is the `docs/decisions/` of the repo it
governs, and the home of a decision that governs several repos is the
repo that governs them. The rest of the record's form — the bar that
warrants one, the template, the numbering, the status vocabulary — is
[Decision Record Conventions](/standards/decisions/records.md).

## What a merged Decision Record freezes

Once `main` carries a Decision Record, its body, and every frontmatter
key other than `status`, stay byte-identical to the first commit on
`main` that carries the file. A record is the one exemption from
[current state and next steps only](/standards/prose/conventions.md#current-state-and-next-steps-only):
it is a dated record of a past decision, the choice made, the
alternatives rejected, and the context that forced it. A body
rewritten to match later state, or to correct a decision that was
reversed, destroys the one thing the record holds. The `status` key is
the one exception, so a superseded record points at the record that
replaced it.

## Where a working documentation set stands

A working documentation set, the one
[an index in every directory](/standards/knowledge-organization/documentation-sets/documentation-sets.md#an-index-in-every-directory)
makes a set, is present on `main`.
[A guess written as a guess](/standards/knowledge-organization/documentation-sets/working-documentation-sets.md#a-guess-written-as-a-guess)
is what lets a set stand on `main`: a reader meets a guess marked as a
guess, and the worklist shows where the work is.
