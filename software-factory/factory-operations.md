---
type: Standard
title: Factory Operations
description: The factory's operating contract — how a ready issue is dispatched, built, reviewed, and carried to the merge
---

# Factory Operations

How the factory carries a ready issue from `build` to a merged pull request with
nobody driving it. The map it executes — the two regions, the states, the labels
— is [software-factory.md](/software-factory/software-factory.md); every point
where it stops for the human is
[human-checkpoints.md](/software-factory/human-checkpoints.md).

## Dispatch

The unit of dispatch is the **issue**. The human launches one **issue overwatch**
per issue in **Agent view** — the official name of the `claude agents` dashboard
— and that overwatch owns the issue's whole traverse: it reads the graph and
executes it, delegating each node and stopping where the human must act. The node
sequence is never hard-coded into any skill — the graph is the single source.

Two overwatch scopes, two screens:

- **Agent-view overwatch** — fleet scope: reads the board,
  recommends what to launch next, tears down worktrees after confirmed merges.
- **Issue overwatch** — issue scope, one per issue: executes that
  issue's traverse and surfaces its human git commands.

**Factory nodes only.** An issue overwatch executes the factory region and
nothing else. Launched on an issue whose phase sits in
[definition](/software-factory/software-factory.md#the-definition-region) — or on
an unlabeled one — it refuses outright and names the skill the human should run
instead. Definition is human-led by construction; an overwatch that improvised
its way through intake would be extracting intent with nobody to extract it from.

**Single label writer.** One writing session per issue — the session sequencing
it. A subagent never writes a label; a skill run inline in the sequencing session
writes as that session. Every label move is the overwatch's, made as a node
finishes, so no subagent can advance the board out from under the session
sequencing it.

**Readiness at the crossing.** Two things gate a launch. The issue's phase must
sit in the factory region, per the refusal above; and the issue must meet the
readiness bar — a leaf, unblocked, with a brief-complete body — defined once in
the [tracking standard](/standards/tracking/issues.md#readiness) and checked
here, at the crossing.

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

**The commit-authorization token.** The literal token
`⟦AUTONOMOUS-COMMIT-AUTHORIZED⟧` pre-authorizes `Skill(commit)` for the session
carrying it — an uncommon bracketed string recognized as the lone commit
exception. Two sessions carry it, and no others:

- **A committing node's subagent**, from the delegation prompt the overwatch
  prefixes. A subagent is a separate session, its delegation prompt is its launch
  prompt, and it commits with no human present to say "commit now" — the token is
  what lets it, with the work reviewed at the PR rather than diff-by-diff. A node
  that only reads or only calls `gh` gets the bare launch line; granting the token
  where it goes unused is privilege the node doesn't need.
- **The issue overwatch**, from its own skill, for one purpose: the fixes it makes
  at [the judgments node](#the-judgments-node) are its own work, made with the
  human present, and they land without a checkpoint of their own. It commits
  nothing else — the work under review is never the overwatch's to touch.

**Subagent permissions are consciously wide.** Subagent-level tool permissions
are out of scope for this model: subagents run under auto mode with wide
permissions, and the reviewer read-only guarantee — a reviewer reports findings,
never rewrites the work under review — is prompt-level for now. This is accepted
deliberately; a later pass may tighten it.

From the first file-touching node on, the session is cwd-bound to the issue's
worktree, which confines its file reach.

Canonical front-matter and syntax:
[skills](https://code.claude.com/docs/en/skills.md),
[permissions](https://code.claude.com/docs/en/permissions).

## Engagement

Each node engages the human one of two ways:

- **AFK** (away from keyboard) — the overwatch delegates the node to a subagent,
  which does the work hands-off and reports. The human sees only the report.
- **Inline** — the overwatch runs the node itself at its own main loop, with the
  human present in the terminal.

A review node (a diamond) is several AFK delegations followed by the overwatch's
own verdict interview, sequenced within the one node.

### The dispatch table

The factory's nodes, what runs each, and how each engages the human:

| Node | Skill | Engagement |
|---|---|---|
| `build` | `/build` | AFK; the subagent carries the commit token. |
| `pr_review` | `/open-pr` first, always, then the [track](#track-rules) skills | AFK per skill, then the human's verdict on the whole stop ([pause 1](/software-factory/human-checkpoints.md#pause-1-the-review-verdict)). |
| `judgments` | none — the overwatch invokes `/run-judgments` | Inline; it stops only where a fix is ambiguous ([pause 2](/software-factory/human-checkpoints.md#pause-2-judgments-conditional)). |

The table is factory-only. The definition region's skills — `/intake`,
`/design`, `/candidate-promote` — are invoked by the human and never dispatched,
and the `spike` node has no skill at all.

**Delegation.** An AFK node is delegated to a subagent whose prompt is the launch
line `run /<skill> <N>` and nothing more — nodes stay skills. The subagent gets a
fresh context window and inherits the issue's worktree as cwd; it reloads what it
needs from the issue (`gh issue view <N>`) and the worktree, does the work, and
ends with a terminal report. Nothing carries over from the overwatch's context.
A committing node's launch line is prefixed with the commit token, per
[Permissions](#permissions). A helper a skill invokes itself (`/commit`,
`/grill-with-docs`) is not a node and is never dispatched.

**The terminal report contract.** A subagent's final message MUST begin at
character one with exactly `DONE: <one-line outcome>` or
`ESCALATE: <one-line reason>`; detail follows below. Any non-matching final
message is treated as ESCALATE — malformed fails safe, toward the human. What the
overwatch does with an escalation is
[human-checkpoints.md](/software-factory/human-checkpoints.md#escalation).

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
  tap-free check that the local `origin/main` ref matches origin
  (`git rev-parse origin/main` against `gh api …/branches/main`); a stale base
  escalates, since pulling is the human's. Open with
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
  `git branch -D issue-<N>` — only after the human confirms the merge happened. A
  spike's worktree goes the same way when its issue closes.

**The branch is pushed by the human.** A committing node commits and stops; the
push needs a hardware tap the agent cannot give, so it is a checkpoint — see
[the capability boundary](/software-factory/human-checkpoints.md#the-agent-capability-boundary).
Two consequences shape everything downstream: a node can never open the PR
itself, because the branch isn't on origin when the node ends; and every
intermediary push rides `--no-verify`, deferring the semantic gate to
[the judgments node](#the-judgments-node).

## The node-skill contract

A node skill does the node's work and reports; the issue overwatch launches it,
sequences what follows, and writes the labels. This contract fixes structure; the
authoring *style* behind the skills — voice, content, robustness, mechanics —
lives in [skill-authoring.md](/software-factory/skill-authoring.md).

- **Read first.** When a skill has required reading, it front-loads a
  `## Read first` section ending in a `READ: <files>` confirmation; when it has
  none, it omits the section entirely.
- **Worktree.** Every file-touching node sits in the issue's worktree before
  doing anything else, per [the worktree contract](#the-worktree-contract), and
  escalates when it is missing.
- **AFK** — the skill runs hands-off and terminates per
  [the terminal report contract](#engagement): `DONE:` on success, `ESCALATE:`
  when stuck. Each skill states its own escalation triggers in its body.
- **Inline** — a skill the human invokes directly, as the definition region's
  are, may gate on interviews and approvals, asked in prose at the terminal, and
  closes with a plain report rather than a report line.
- **Gate.** A committing node runs `make check` — the full gate, not just the
  commit hooks — before finishing its phase; a phase never closes over a red
  tree. The rule is per-phase, not per-commit: individual commits are already
  covered by the commit gate's hook suite, and the full gate is the phase-close
  ritual.
- **Judgments sit outside every node skill.** `make check` leaves the semantic
  [cache gate](/standards/judgments/cache-gate.md) skipped, and no node skill
  arms it or runs a judge — the whole semantic bill is settled once, at
  [the judgments node](#the-judgments-node). For a **review** skill the exclusion
  is total: the `judgments/*.yaml` declarations are outside its jurisdiction
  whether or not the diff changes them, and a judgment — its content, its
  verdict, or its cache state — appears nowhere in its findings. A stale or red
  cache mid-traverse is the expected condition, not a defect to report.

## Pull requests

One PR per issue — spikes open none — born at the review stop and squash-merged
by the human. Because [repository settings](/standards/tracking/repo-settings.md)
take the squash message from the PR, its title and body become the permanent
commit message on `main`: they are authored from the issue brief and the diff,
never left as a placeholder.

### The merge-message recipe

- **Title** — states the change: it is the commit subject `main`'s history will
  carry.
- **Body** — a summary of what changed and why, drawn from the issue brief and
  the current diff, plus the mandatory `Closes #<N>` line that closes the issue
  on merge.

### The two owners

The message is written twice from that one recipe, so the two cannot diverge:
`/open-pr` authors it when it creates the PR, and the overwatch regenerates it
from the final diff at the approve verdict (a tap-free `gh pr edit`), after
[the judgments node](#the-judgments-node) has landed its fixes. Nothing
refreshes it in between — a message rewritten mid-traverse is authored against a
diff still moving.

## The review stop

`pr_review` is a diamond: audits run, then the human gives one verdict on the
whole stop. Which audits run is fixed by the [track rules](#track-rules) below,
never by asking.

- **Code track.** `/bug-pr-review` posts its bug findings; `/code-pr-review` adds
  the fidelity and convention findings it does not cover.
- **Doc track.** `/doc-pr-review` audits the diff's documentation.
- **Lockdown re-review.** From the third cycle on, only `/code-pr-review` runs: a
  lockdown verifies fixes and needs no fresh bug hunt.

There is exactly one verdict per stop, and it is the human's — the first of the
three pauses, briefed per
[pause 1](/software-factory/human-checkpoints.md#pause-1-the-review-verdict). A
**reject** returns the issue to `build`, with the deciding reason recorded where
the findings live so the rework carries it. An **approve** advances it to
[the judgments node](#the-judgments-node).

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
  under 10 changed doc lines). Always skip when the human already wrote or
  approved those doc changes inline this traverse: a review there re-litigates an
  approval.
- **Doubt skips.** A skipped track is one retroactive command away; an
  over-launched audit spends a review on content nobody questioned and posts
  noise to the PR.

## The judgments node

The traverse's one armed pass of the semantic
[cache gate](/standards/judgments/cache-gate.md). Every intermediary push rode
`--no-verify`, so a red cache never blocked a work cycle; the whole semantic bill
comes due here, once, after review approves and before the human's final read.
The node is preparation for that read: it exists so the human meets a PR whose
judgments are already green.

**The overwatch runs it inline, at its own main loop.** The node cannot be
delegated — `/run-judgments` dispatches its judges through the `Workflow` tool,
which a subagent does not have — so there is no wrapper skill and no subagent:
the overwatch invokes `/run-judgments` itself, in the issue's worktree.

- **Fixes are the overwatch's own.** A refuted judgment is fixed here, focused
  and on the issue branch, and committed on the overwatch's own commit token
  (see [Permissions](#permissions)) — no separate go-ahead.
- **An ambiguous failure escalates.** Where a fix is unclear enough to want human
  advice, the node stops and asks
  ([pause 2](/software-factory/human-checkpoints.md#pause-2-judgments-conditional));
  a clean green run stops for nothing.
- **No back edge.** Judgment fixes never reopen review — no new cycle, no fresh
  audit; the human has already approved the substance. A gate that stays red
  parks the issue at the node rather than routing it anywhere. The node closes
  only green.
