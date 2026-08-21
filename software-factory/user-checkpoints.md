---
type: Guide
title: User Checkpoints
description: Every point where the factory stops for the user — the merge prohibition, escalation, the issue-review verdict, and the two review-stretch pauses
---

# User Checkpoints

The factory runs unattended between checkpoints. A **checkpoint** is a point
where it stops and the user acts, and there are only two reasons for one:

- **Prohibition** — the agent *can* do it and *must not*. Merging a PR is the
  only one ([The merge prohibition](#the-merge-prohibition)).
- **Decision** — the call is *not the agent's*. A verdict on reviewed work, an
  ambiguous fix, the final read before merge.

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
| commit, `EnterWorktree`/`ExitWorktree`, `git branch -m`, `git worktree remove` | yes | yes | skills |

## The briefing rule

**The user is primarily in the terminal.** They do not typically read the documents or the code. They read the PR once, at the veryy end of the process. So every
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
the call is also recorded: spoken in the terminal, it is transcribed onto the
issue or PR by the overwatch, per the
[deviation contract](/software-factory/deviation-contract.md#escalation) —
limiter 3 binds later deviations only to what is written there.

An escalation is not a finding. A problem a review node can describe belongs in
its findings; it escalates only when something stops it producing the review at
all. The mechanics of the report itself — the `DONE:`/`ESCALATE:` line a subagent
must emit — are
[the terminal report contract](/software-factory/factory-operations.md#engagement).

## The two pauses

Everything above interrupts the factory wherever it happens. The two **pauses**
are different: they are scheduled, they all sit after implementation, and
together they are the whole of the user's decision-making inside the factory.
Until the first of them, the factory asks the user for nothing.

### Pause 1: the review verdict

At the review stop, the audits have posted their findings and the user has read
none of them. The overwatch reads every comment surface on the PR itself, then
briefs — one brief per call it needs, not one per finding — in four parts:

1. **Current state** — what is true in the code or docs today, stated plainly
   enough to follow without opening them.
2. **Goal** — what this issue is trying to achieve, so the finding can be weighed
   against it.
3. **Proposed new state** — what the finding asks to change, and what the work
   looks like afterward.
4. **Specific example** — one concrete instance: the finding's own words, the
   line, the snippet. The example is what makes the first three parts checkable.

Then it answers questions, helps the user weigh, and acts only on an explicit
verdict — **reject** back to `build`, or **approve** onward. Rework is
Blocking-driven by default: suggestions alone do not call for a rework lap. The
overwatch never touches the work under review; a fix is the author's, routed
through rework.

### Pause 2: the final review

The last checkpoint, and the only one where the user reads the diff. It is
reached only when the issue is **100% done**: the merge message regenerated
from the whole PR record, every commit on origin, and a closing brief on what
shipped and what changed since the approve verdict.

Nothing is outstanding at pause 2 but the read and the merge. Anything still
pending — a red gate, an unrefreshed message, an unpushed commit, an open
question — means the issue has not reached pause 2 yet, and presenting it as
though it had spends the user's one full read on work that is still moving.

## The issue-review verdict

One decision checkpoint sits before the factory rather than inside it: the
**issue-review verdict**, at the end of a factory-bound leaf's definition beat.
It interrupts nothing unattended — the definition session is manned — but the
call is not the agent's. The session dispatches the two fresh-context review
lenses, **claims audit** and **implementation simulation**, synthesizes their
findings into a **consolidated disposition list**, and briefs the user on
dispositions, never raw findings one by one. The verdict is the user's:

- **Pass** — apply or demote per the dispositions (the brief is editable until
  launch), then move the leaf to `phase:build`.
- **Back to design** — the leaf returns to design for re-authoring: a fast-path
  leaf moves to `phase:design`, a design-exit leaf stays there. Re-review is a
  full fresh run of both lenses.

After the ruling the session posts one **verdict-record comment** on the issue —
date, lenses run, findings count, disposition gist, verdict. It is the evidence
behind the readiness bar's "released at an issue-review verdict" and, on a
back-to-design, the next session's work order. The review binds the factory's
autonomous path, never the user, who may always skip the beat, cut it short, or
advance anyway.

## What is not a checkpoint

The factory decides these itself, announcing rather than asking:

- **Which review tracks run.** Selected by hard rule and announced on screen;
  dispatch is immediate, with no confirmation wait. A skipped audit is one
  retroactive command away.
- **Doc changes the user already wrote or approved inline this traverse** — a
  review there re-litigates an approval.
- **Anything the graph already answers.** Where a node goes next is read from the
  graph, not asked; a node whose next edge is unclear is an escalation, not a
  question for the user to route by hand.
