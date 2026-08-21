---
type: Guide
title: User Checkpoints
description: Every point where the factory stops for the user — the merge prohibition, escalation, the issue-review verdict, and the final-review pause
---

# User Checkpoints

The factory runs unattended between checkpoints. A **checkpoint** is a point
where it stops and the user acts, and there are only two reasons for one:

- **Prohibition** — the agent *can* do it and *must not*. Merging a PR is the
  only one ([The merge prohibition](#the-merge-prohibition)).
- **Decision** — the call is *not the agent's*. An ambiguous fix, the final read
  before merge.

This document collects both, and fixes what the factory owes the user at each.
The nodes these checkpoints interrupt are
[factory-operations.md](/software-factory/factory-operations.md). One checkpoint
sits just outside that span — the
[issue-review verdict](#the-issue-review-verdict), which rules on a leaf before
the factory ever picks it up — and it is collected here too, because what it
owes the user is the same.

## The merge prohibition

The agent's PAT *can* merge a PR — GitHub's `Pull requests: write` permission
bundles create, edit, close, comment, and merge, indivisibly — and nothing
server-side prevents it: `protect-main` blocks only force-pushes and deletion.
The written rule is the only control.

The rule: **no agent merges a pull request — ever**, by any route — `gh pr
merge`, the merge API, auto-merge, or landing a branch on `main` by hand. A PR
ready to merge ends the agent's turn; the user merges it in the GitHub UI.
Under auto mode the classifier must additionally pass each `gh` write, per
[Permissions](/software-factory/factory-operations.md#permissions).

| | Agent-capable | Permitted to the agent | Owner |
|---|---|---|---|
| merge the PR (in the GitHub UI) | yes | **no — never** | user |
| `git push` (rides every commit) / `git pull` (keep local `main` current) | yes | yes | skills |
| `gh pr create` / `gh api` / `gh issue` / `gh pr diff` | yes | yes | skills |
| commit (rides every node that changes files) | yes | yes | skills |
| create a factory issue's worktree and branch | yes | yes | `traverse-issue` |
| remove a factory issue's worktree and branch after a merge | yes | **no — the user's** | user |
| `EnterWorktree`/`ExitWorktree`, `git branch -m` (definition-region trees) | yes | yes | skills |

## The briefing rule

**The user is primarily in the terminal.** They do not typically read the documents or the code. They read the PR once, at the very end of the process. So every
question, verdict request, and escalation stands on its own: it assumes no prior
knowledge, lays the background out plainly, quotes the specific finding, line, or
command the decision turns on, and then asks. Whatever a decision turns on goes
on screen.

## Turn boundaries

The overwatch runs free between checkpoints, chaining nodes where the graph
allows, and ends its turn wherever only the user can act — a pause, an
escalation, a PR awaiting the merge. Each ending states the user's command
once, paste-safe, on one line, inside the brief that already needed them:

- **Merge**, on the final approval — in the GitHub UI; it lands the PR, drops the
  origin branch, and closes the issue.

## Escalation

An escalation is a node reporting that it cannot proceed. It always reaches the
user: the issue overwatch adds its own context — which node, what it dispatched,
what the report says — and stops. It never overrides, retries, or self-fixes a
node's escalation; the user's call routes the issue onward. A node whose skill
doesn't exist is an escalation, not an improvisation. For a deviation escalation
the call is also recorded as a comment on the issue or PR, per the
[deviation contract](/software-factory/deviation-contract.md#escalation) —
limiter 3 binds later deviations only to what is written there.

An escalation is not a finding. A problem a review node can describe belongs in
its findings; it escalates only when something stops it producing the review at
all. The mechanics of the report itself — the `DONE:`/`ESCALATE:` line a subagent
must emit — are
[the terminal report contract](/software-factory/factory-operations.md#engagement).

## The pause

Everything above interrupts the factory wherever it happens. The **pause** is
different: it is scheduled, it sits after implementation and after review, and it
is the whole of the user's decision-making inside the factory. Until it, the
factory asks the user for nothing.

### The final review

The last checkpoint, and the only one where the user reads the diff. It is
reached only when the issue is **100% done**: the merge message regenerated
from the whole PR record, every commit on origin, and a closing brief on what
shipped and what the review loop settled on the way.

Nothing is outstanding at the pause but the read and the merge. Anything still
pending — a red gate, an unrefreshed message, an unpushed commit, an open
question — means the issue has not reached it yet, and presenting it as though
it had spends the user's one full read on work that is still moving.

## The issue-review verdict

One decision checkpoint sits before the factory rather than inside it: the
**issue-review verdict**, at the end of a factory-bound leaf's definition beat.
The two fresh-context review lenses — **claims audit** and **implementation
simulation** — are the session's tools, not the user's: latent instruments it
runs to sharpen its own brief. The session dispatches both, merges and
deduplicates their findings, and disposes of each on its own judgment, editing
the brief in place until an autonomous builder could be handed it. It never
pauses for the user to rule, and it records nothing about the run on the issue —
the repaired brief is the whole output. It then brings the user a finished
issue. The verdict is the user's:

- **Ready** — the leaf moves to `phase:build`. That label is the release, and no
  label crosses out of the definition region before it.
- **Not ready** — asked-for changes are applied and the issue re-presented; a
  leaf sent back for re-authoring moves to `phase:design`, or stays there if it
  is a design-exit leaf. Re-review is a full fresh run of both lenses.

The review binds the factory's autonomous path, never the user, who may always
skip the beat, cut it short, or advance anyway.

## What is not a checkpoint

The factory decides these itself, announcing rather than asking:

- **Which review tracks run.** Elected from the pull request's changed files by
  [hard rule](/software-factory/factory-operations.md#track-rules), recomputed
  every cycle, and never asked.
- **The verdict on a review cycle.** Computed by the traverse script from thread
  state: any open Blocking thread is a rework lap, none is convergence. It is
  arithmetic over what the reviews posted, so there is no judgment in it for the
  user to make — and the findings themselves reach the user at the final review,
  on the pull request where they live.
- **Anything the graph already answers.** Where a node goes next is read from the
  graph, not asked; a node whose next edge is unclear is an escalation, not a
  question for the user to route by hand.
