---
type: Standard
title: Human Checkpoints
description: Every point where the factory stops for the human — the capability boundary, escalation, and the three review-stretch pauses
---

# Human Checkpoints

The factory runs unattended between checkpoints. A **checkpoint** is a point
where it stops and the human acts, and there are only two reasons for one:

- **Capability** — the agent *cannot* do it. Pushing, pulling, and merging need
  credentials or a hardware tap it does not have.
- **Decision** — the call is *not the agent's*. A verdict on reviewed work, an
  ambiguous fix, the final read before merge.

This document collects both, and fixes what the factory owes the human at each.
The nodes these checkpoints interrupt are
[factory-operations.md](/software-factory/factory-operations.md).

## The agent-capability boundary

What the agent can do on GitHub is set by its PAT: it authorizes the HTTPS API —
the `gh` family and REST endpoints — but not pushing over the SSH remote, and not
merging a PR (`mergePullRequest` is forbidden to it). So three operations fall to
the human: `git push` and `git pull`, whose SSH remote needs a YubiKey tap in the
human's own terminal, and merging the PR, in the GitHub UI. Everything the PAT
authorizes — and all purely-local git, which needs no GitHub auth at all — the
agent does inside a skill. Under auto mode the PAT is necessary but not
sufficient: the classifier must also pass each `gh` write, per
[Permissions](/software-factory/factory-operations.md#permissions).

| | Agent-capable | Owner |
|---|---|---|
| `git push` (publish committed work to origin, after any committing node) | no | human |
| `git pull` (keep local `main` current) | no | human |
| merge the PR (in the GitHub UI) | no | human |
| `gh pr create` / `gh api` / `gh issue` / `gh pr diff` | yes | skills |
| commit, `EnterWorktree`/`ExitWorktree`, `git branch -m`, `git worktree remove` | yes | skills |

The taps cannot be designed away, so they are not treated as friction to
minimize. What is minimized is their *count* and their *cost*: one push per
committing node, and the command itself folded into whatever brief the checkpoint
already carries rather than sent as a message of its own.

## The briefing rule

**The human is in the terminal and nowhere else.** They are not reading the code,
the diff, the PR, or its comments — that read comes once, at the end. So every
question, verdict request, and escalation stands on its own: it assumes no prior
knowledge, lays the background out plainly, quotes the specific finding, line, or
command the decision turns on, and then asks. Whatever a decision turns on goes
on screen.

This is the rule the formats below specialize. It is also a ceiling: a brief
carries what the decision needs and stops. Pasting a diff, a full audit comment,
or a file the human did not ask for buries the call being made.

## Turn boundaries

The overwatch runs free between checkpoints, chaining nodes where the graph
allows, and ends its turn wherever only the human can act — a branch needing a
push, a pause, an escalation, a PR awaiting the merge. Each ending states the
human's command once, paste-safe, on one line, inside the brief that already
needed them:

- **Intermediary push**, after any committing node — carries `--no-verify` on
  purpose: the pre-push hook arms the semantic cache gate, whose only remedy is
  [the judgments node](/software-factory/factory-operations.md#the-judgments-node)
  at the end of the traverse, so verifying mid-traverse would red every rework
  cycle for nothing. The deterministic guarantee for the cycle is the phase-close
  `make check`.
- **Final push**, when the judgments node committed fixes — verified: the armed
  gate's single blocking run on the issue's path to merge.
- **Pull**, on a stale base — against the main checkout, not the worktree.
- **Merge**, on the final approval — in the GitHub UI; it lands the PR, drops the
  origin branch, and closes the issue.

`/clear` is the human's context reset, available at any checkpoint: cwd and
worktree survive it, and the overwatch re-orients from the issue's labels and the
worktree it still sits in.

## Escalation

An escalation is a node reporting that it cannot proceed. It always reaches the
human: the issue overwatch adds its own context — which node, what it dispatched,
what the report says — and stops. It never overrides, retries, or self-fixes a
node's escalation; the human's call routes the issue onward. A node whose skill
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

## The three pauses

Everything above interrupts the factory wherever it happens. The three **pauses**
are different: they are scheduled, they all sit after implementation, and
together they are the whole of the human's decision-making inside the factory.
Until the first of them, the factory asks for the human's taps, not their
decisions.

### Pause 1: the review verdict

At the review stop, the audits have posted their findings and the human has read
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

Then it answers questions, helps the human weigh, and acts only on an explicit
verdict — **reject** back to `build`, or **approve** onward. Rework is
Blocking-driven by default: suggestions alone do not call for a rework lap. The
overwatch never touches the work under review; a fix is the author's, routed
through rework.

### Pause 2: judgments, conditional

The judgments node runs unattended and usually finishes without a word. It pauses
only where a refuted judgment's fix is ambiguous enough to want human advice — a
claim that may be wrong about the code, or right about code that should change.
A clean green run pauses nothing, and neither does a refutation whose fix is
obvious.

### Pause 3: the final review

The last checkpoint, and the only one where the human reads the diff. It is
reached only when the issue is **100% done**: judgments green, the merge message
refreshed from the final diff, the verified push already handed over if the
judgments node committed fixes, and a closing brief on what shipped and what
changed since the approve verdict.

Nothing is outstanding at pause 3 but the read and the merge. Anything still
pending — a red gate, an unrefreshed message, an unpushed commit, an open
question — means the issue has not reached pause 3 yet, and presenting it as
though it had spends the human's one full read on work that is still moving.

## What is not a checkpoint

The factory decides these itself, announcing rather than asking:

- **Which review tracks run.** Selected by hard rule and announced on screen;
  dispatch is immediate, with no confirmation wait. A skipped audit is one
  retroactive command away.
- **A green judgments run**, and any refutation whose fix is obvious.
- **Doc changes the human already wrote or approved inline this traverse** — a
  review there re-litigates an approval.
- **Anything the graph already answers.** Where a node goes next is read from the
  graph, not asked; a node whose next edge is unclear is an escalation, not a
  question for the human to route by hand.
