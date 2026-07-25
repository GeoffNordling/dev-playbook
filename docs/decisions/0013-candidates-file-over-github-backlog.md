---
type: Decision-Record
title: Uncommitted Work Lives in CANDIDATES.md, Not GitHub
status: accepted
description: Record uncommitted future work in a per-repo CANDIDATES.md rather than as open GitHub issues, reserving issues for work already committed to
---

# Uncommitted Work Lives in CANDIDATES.md, Not GitHub

Future work had no declared home. A survey of the four active repos found 21
open issues, none carrying a conforming brief, none using sub-issue or
dependency relationships, and an epic convention invented twice independently
in issue *titles* (`[Epic draft] …`, `… (tracking issue)`) because the standard
derives the epic role from sub-issues and mints no label for it. One repo also
carried a `ROADMAP.md`, typed `General-Sheet`, passing every gate. We split the
two: **committed work is a GitHub issue at any size; uncommitted work is a
Candidate in that repo's root `CANDIDATES.md`.** The ability to write the brief
is the test that separates them, and a unit of work sits in exactly one home.

## Considered Options

**All work in GitHub, with a `phase:candidate` label.** Simpler — one system, no
bridge, native relationships, no merge conflicts. Rejected on two counts. It
destroys the meaning of "open issue": at 21 open, "open" currently means "I
intend to do this," and a working queue polluted with speculation becomes the
familiar graveyard where real work is unfindable. And GitHub sits outside all
three gates, so nothing there can ever be enforced — the drift documented above
ran for months, silently, which is the empirical case against trusting that
medium with a second job.

**GitHub Projects.** Rejected — another out-of-gate system with no linting, and
it duplicates the four-tuple the software factory already carries.

## Consequences

The tracking card's Enforce cell moves from `none` to the **commit gate** for
the tree half, while GitHub itself stays unenforceable. Only the file's
existence and OKF header are checked: `tracking.rogue-future-work-file` bans
`ROADMAP.md`, `TODO.md`, `BACKLOG.md`, and `IDEAS.md` anywhere in the tree, and
okf-lint checks the `Candidate-List` frontmatter like any concept document.

Entry shape inside the file is deliberately **convention, not a checked rule**.
An earlier design enforced a closed grammar — banning bold-colon fields,
checkboxes, and unbounded prose to make "a Candidate is not a brief"
mechanical. That was rejected as disproportionate: a register that drifts into
a shadow issue tracker is an authoring problem, and the cost of policing it
exceeds the cost of occasionally fixing it.

Because the ban ships inside the pinned clone, consumers adopt it when their
`rev` moves, not at once — so a repo carrying a rogue file keeps committing
until its pin is bumped.
