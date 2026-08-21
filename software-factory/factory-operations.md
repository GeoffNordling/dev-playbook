---
type: Guide
title: Factory Operations
description: The factory's operating contract — how a ready issue is dispatched, built, reviewed, and carried to the merge
---

# Factory Operations

How the factory carries a ready issue from `build` to a merged pull request with
nobody driving it. The map it executes — the two regions, the states, the labels
— is [software-factory.md](/software-factory/software-factory.md); every point
where it stops for the user is
[user-checkpoints.md](/software-factory/user-checkpoints.md).

## Dispatch

The unit of dispatch is the **issue**. The user launches one **issue overwatch**
per issue in **Agent view** — the official name of the `claude agents` dashboard
— and that overwatch owns the issue's whole traverse: it reads the graph and
executes it, delegating each node and stopping where the user must act. The node
sequence is never hard-coded into any skill — the graph is the single source.

Two overwatch scopes, two screens:

- **Agent-view overwatch** — fleet scope: reads the board,
  recommends what to launch next, tears down worktrees after confirmed merges.
- **Issue overwatch** — issue scope, one per issue: executes that
  issue's traverse and surfaces the git commands the user must run.

**Factory nodes only.** An issue overwatch executes the factory region and
nothing else. Launched on an issue whose phase sits in
[definition](/software-factory/software-factory.md#the-definition-region) — or on
an unlabeled one — it refuses outright and names the skill the user should run
instead. Definition is user-led by construction; an overwatch that improvised
its way through intake would be extracting intent with nobody to extract it from.

**Single label writer.** One writing session per issue — the session sequencing
it. A subagent never writes a label; a skill run inline in the sequencing session
writes as that session. Every label move is the overwatch's, made as a node
finishes, so no subagent can advance the board out from under the session
sequencing it.

**Readiness at the crossing.** Two things gate a launch. The issue's phase must
sit in the factory region, per the refusal above; and the issue must meet the
readiness bar — a leaf, unblocked, brief-complete, released at an issue-review
verdict — defined once in the
[tracking standard](/standards/tracking/issue-authoring.md#readiness).

What the crossing checks is the first three: each is observable on the issue,
and an overwatch escalates when one fails. The release is a definition-region
obligation — carried by the `phase:build` label the user's approval sets, and
overridable by them — so the crossing takes it as given rather than re-deriving
it. A rework
lap is not a crossing: the issue never left the factory, so nothing is
re-checked.

## Permissions

The issue overwatch's session runs in **auto mode**: a classifier judges each
tool call and self-approves the safe ones. It does not honor the tool-pattern
`permissions.allow` list — on entry it drops broad and wildcarded `Bash(...)`
allows — so nothing reaches a node on a saved pattern. To permit something the
classifier would otherwise block, add a natural-language entry to the
`autoMode.allow` list in `settings.json`, whose first entry is the literal
`"$defaults"` so added entries extend the built-in rules rather than replace
them. It is honored from user and project-local scope, never from checked-in
project settings.

**Subagent permissions are consciously wide.** Subagent-level tool permissions
are out of scope for this model: subagents run under auto mode with wide
permissions. This is accepted deliberately; a later pass may tighten it.

**The reviewer read-only guarantee is enforced, not asked for.** A reviewer
reports findings and never rewrites the work under review, and the harness holds
it to that: `code-pr-review`, `bug-pr-review`, and `doc-pr-review` each carry a
`disallowed-tools` entry denying `Edit`, `MultiEdit`, `NotebookEdit`, and
`Write`, so an attempted write is refused rather than merely discouraged by the
prompt.

From the first file-touching node on, the session is cwd-bound to the issue's
worktree, which confines its file reach.

Canonical front-matter and syntax:
[skills](https://code.claude.com/docs/en/skills.md),
[permissions](https://code.claude.com/docs/en/permissions).

## Engagement

Each node engages the user one of two ways — the terms themselves are fixed in
[the vocabulary](/CONTEXT.md):

- **AFK** — the overwatch delegates the node to a subagent, which does the work
  hands-off and reports. The user sees only the report.
- **Inline** — the overwatch runs the node itself at its own main loop, with the
  user present in the terminal.

A review node (a diamond) is several AFK delegations followed by the overwatch's
own verdict interview, sequenced within the one node.

### The dispatch table

The factory's nodes, what runs each, and how each engages the user:

| Node | Skill | Engagement |
|---|---|---|
| `build` | `/build` | AFK. |
| `pr_review` | `/open-pr` first, always, then the [track](#track-rules) skills | AFK per skill, then the user's verdict on the whole stop ([pause 1](/software-factory/user-checkpoints.md#pause-1-the-review-verdict)). |

The table is factory-only. The definition region's skills — `/intake`,
`/design`, `/candidate-promote` — are invoked by the user and never dispatched,
and the `spike` node has no skill at all.

**Delegation.** An AFK node is delegated to a subagent whose prompt is the launch
line `run /<skill> <N>` and nothing more — nodes stay skills. The subagent gets a
fresh context window and inherits the issue's worktree as cwd; it reloads what it
needs from the issue (`gh issue view <N>`) and the worktree, does the work, and
ends with a terminal report. Nothing carries over from the overwatch's context.
A helper a skill invokes itself (`/commit`,
`/grill-with-docs`) is not a node and is never dispatched.

**The terminal report contract.** A subagent's final message MUST begin at
character one with exactly `DONE: <one-line outcome>` or
`ESCALATE: <one-line reason>`; detail follows below. Any non-matching final
message is treated as ESCALATE — malformed fails safe, toward the user. What the
overwatch does with an escalation is
[user-checkpoints.md](/software-factory/user-checkpoints.md#escalation).

## Worktrees and branches

An issue runs under one issue overwatch that builds a continuous line of work
across its nodes. Isolation — from other issues and from the main checkout —
comes from giving each issue its own **git worktree**, opened once and kept for
the issue's life.

- **One worktree, one branch, one PR per issue,** at
  `<repo>/.claude/worktrees/issue-<N>` on branch `issue-<N>` (`N` is the issue
  number).
- **Opened once, then persisted.** cwd and worktree survive a `/clear`, so an
  overwatch re-invoked after one inherits them with no re-entry.

### The worktree contract

Every file-touching node sits in the issue's worktree:

- **Open (first file-touching node).** The issue overwatch opens it, gated on a
  check that the local `origin/main` ref matches origin
  (`git rev-parse origin/main` against `gh api …/branches/main`); on a stale
  base the overwatch pulls the main checkout current and re-checks. Open with
  `EnterWorktree(name=issue-<N>)`, which branches from `origin/main` because
  `worktree.baseRef` is pinned to `fresh` in user `settings.json` — so the base is
  `origin/main` whatever branch the main checkout sits on. Then rename the branch
  to the bare `issue-<N>`: Agent view's cleanup keys on the `worktree-` prefix, so
  dropping it lets the worktree outlive a torn-down session.
- **Inherit (everything after).** AFK subagents inherit the worktree as their
  cwd; the overwatch keeps it across `/clear`. Every later node confirms the
  worktree is present — escalating if it's gone, since the issue's work would be
  lost.
- **Tear down (Agent-view overwatch, post-merge).** When the issue lands, the
  Agent-view overwatch removes the local side —
  `git worktree remove .claude/worktrees/issue-<N>` and
  `git branch -D issue-<N>` — only after the user confirms the merge happened. A
  spike's worktree goes the same way when its issue closes.

**The branch is pushed as it is committed.** A committing node pushes what it
commits — the push is part of `/commit` — so the branch is on origin whenever
the node ends, verified by the pre-push hook's full `make check` on the way
out.

## The node-skill contract

A node skill does the node's work and reports; the issue overwatch launches it,
sequences what follows, and writes the labels. This contract fixes structure; the
authoring *style* behind the skills — voice, content, robustness, mechanics —
lives in [node-agent-and-skill-authoring.md](/software-factory/node-agent-and-skill-authoring.md).

- **Read first.** When a skill has required reading, it front-loads a
  `## Read first` section ending in a `READ: <files>` confirmation; when it has
  none, it omits the section entirely.
- **Worktree.** Every file-touching node sits in the issue's worktree before
  doing anything else, per [the worktree contract](#the-worktree-contract), and
  escalates when it is missing.
- **AFK** — the skill runs hands-off and terminates per
  [the terminal report contract](#engagement): `DONE:` on success, `ESCALATE:`
  when stuck. Each skill states its own escalation triggers in its body.
- **Inline** — a skill the user invokes directly, as the definition region's
  are, may gate on interviews and approvals, asked in prose at the terminal.
- **The report line.** Every node closes on one ` · `-delimited line: the handle
  `<repo>#<N>` · `phase: <node>`. A committing node appends
  `commit <sha> · check green · pushed`; a node whose real output landed on
  GitHub appends a pointer only (`findings on PR #<n>`, `brief in issue`), never
  a re-paste — the line points, GitHub holds the detail. An AFK skill carries it
  on the `DONE:`/`ESCALATE:` line per
  [the terminal report contract](#engagement); an inline skill omits the token
  and closes with the line alone.
- **Gate.** A committing node runs `make check` — the full gate, not just the
  commit hooks — before finishing its phase; a phase never closes over a red
  tree. The rule is per-phase, not per-commit: individual commits are already
  covered by the commit gate's hook suite, and the full gate is the phase-close
  ritual.
- **Judgments sit outside every node skill.** `make check` leaves the semantic
  [cache gate](/standards/judgments/cache-gate.md) skipped, and no node skill
  arms it or runs a judge — judgments are settled by the periodic sweep, outside
  the factory. For a **review** skill the exclusion is total: the
  `judgments/*.yaml` declarations are outside its jurisdiction
  whether or not the diff changes them, and a judgment — its content, its
  verdict, or its cache state — appears nowhere in its findings. A stale or red
  cache mid-traverse is the expected condition, not a defect to report.

## Pull requests

One PR per issue — spikes open none — born at the review stop and squash-merged
by the user. Because [repository settings](/standards/tracking/repo-settings.md)
take the squash message from the PR, its title and body become the permanent
commit message on `main`: they are authored from the issue brief, the diff, and
the record the issue and its PR carry, never left as a placeholder.

### The merge-message recipe

- **Title** — states the change: it is the commit subject `main`'s history will
  carry.
- **Body** — three mandatory sections, each checkable by absence:
  - `## Summary` — what changed and why, drawn from the issue brief and the
    current diff, ending with the mandatory `Closes #<N>` line that closes
    the issue on merge. The claim that the acceptance criteria are met
    lives here as prose.
  - `## Deviation ledger` — the deviation entries of the
    [deviation contract](/software-factory/deviation-contract.md#the-deviation-ledger),
    which defines the entry shape and the hand-off; `No deviations.`
    explicitly when empty.
  - `## Deferred` — orthogonal work discovered after the brief froze:
    incidental bugs, cleanups, adjacent improvements, and review findings
    the user rules real-but-not-this-issue. Each entry is a real tracker
    stub at `phase:intake`, named by issue link — never a Candidate
    ([the one-goal principle](/standards/tracking/issue-authoring.md#brief-principles)).
    `Nothing deferred.` explicitly when empty.

A missing section is a checkable defect: the code and doc reviews open with a
mechanical presence check, and absence is an automatic Blocking finding.

### The two owners

The message is written twice from that one recipe, so the two cannot diverge:
`/open-pr` authors it when it creates the PR — lifting the build session's
recorded entries into `## Deviation ledger` per the
[contract's hand-off](/software-factory/deviation-contract.md#the-deviation-ledger)
— and the overwatch regenerates it at the approve verdict (`gh pr edit`).
The regeneration synthesizes the entire PR record — the final diff,
the comments, and the rulings — into an accurate squash-commit message for
the whole issue, preserving the mandatory sections' content rather than
rewriting from the recipe alone: the body is `main`'s permanent record, and
the accuracy of the final record wins. In between, only the ledger moves —
rework laps append its entries by spec; a full message rewritten mid-traverse
is authored against a diff still moving.

## The review stop

`pr_review` is a diamond: audits run, then the user gives one verdict on the
whole stop. Which audits run is fixed by the [track rules](#track-rules) below,
never by asking.

- **Code track.** `/bug-pr-review` posts its bug findings; `/code-pr-review` adds
  the fidelity and convention findings it does not cover.
- **Doc track.** `/doc-pr-review` audits the diff's documentation.
- **Lockdown re-review.** From the third cycle on, each live track runs its
  fidelity-and-convention review alone — `/code-pr-review` on the code track,
  `/doc-pr-review` on the doc track — and `/bug-pr-review` stands down: a
  lockdown verifies fixes and needs no fresh bug hunt. The track rules still
  elect the tracks, so a doc-only diff is re-reviewed by the doc track.

There is exactly one verdict per stop, and it is the user's — the first of the
two pauses, briefed per
[pause 1](/software-factory/user-checkpoints.md#pause-1-the-review-verdict). A
**reject** returns the issue to `build`, with the deciding reason recorded where
the findings live so the rework carries it. An **approve** advances it to the
user's final read and merge.

### Track rules

Content kind picks the track, not file format — by hard rule, announced, never
asked:

- **Code track — default on.** Launch whenever the diff touches executable or
  machine-consumed content: source, scripts, tests, build or config files. Skip
  only when the diff has none.
- **Doc track — earned, never defaulted.** Launch only when documentation is a
  substantive deliverable of the diff: a new document, a new or restructured
  section, or the issue's brief names docs as a deliverable. Skip when the doc
  changes are incidental to a code deliverable — mechanical echoes such as
  renames, links, and wording the code change forces, or small edits (roughly
  under 10 changed doc lines). Always skip when the user already wrote or
  approved those doc changes inline this traverse: a review there re-litigates an
  approval.
- **Doubt skips.** A skipped track is one retroactive command away; an
  over-launched audit spends a review on content nobody questioned and posts
  noise to the PR.
