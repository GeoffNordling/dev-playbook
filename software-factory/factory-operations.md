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

**Single label writer.** One writer per issue at any moment: the session
sequencing it — or, while a traverse-workflow run is live, that run's clerk,
acting on the script's instruction. An ordinary subagent never writes a
label; a skill run inline in the sequencing session writes as that session.
The sequencing session makes no label move while a run is live, and the
clerk makes none outside one, so the board never advances out from under
whoever is sequencing it.

**Readiness at the crossing.** Two things gate a launch. The issue's phase must
sit in the factory region, per the refusal above; and the issue must meet the
readiness bar — a leaf, unblocked, with a brief-complete body — defined once in
the [tracking standard](/standards/tracking/issue-authoring.md#readiness) and
checked here, at the crossing.

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

**Commit authorization.** `git commit` is deny-by-default: the `git-authority`
PreToolUse hook permits it through exactly two mutually exclusive lanes, per
[git-authority](/software-factory/git-authority.md). A factory subagent
commits through lane 1 — its `agent_type` is on the hook's allowlist
(`builder`, `judgment-facilitator`), read from the payload the harness
writes, which no prompt or brief can forge. A human's interactive session
commits through lane 2 — a typed `/commit-on` marker in its transcript.
Every factory commit is a node's own: the traverse workflow's builder and
judgment-facilitator nodes commit through lane 1, and the sequencing
session commits nothing. Lane 2 remains the human's own interactive lane,
outside the factory. The lanes never mix: a subagent is judged by its type alone,
whatever its transcript holds. That exclusivity is what stops a node minting
its own grant — a subagent's transcript opens with the launch prompt its parent
model wrote, which lane 2 would otherwise read as a grant a human typed.
Delegation prompts carry no authorization of any kind — the classifier kills
a node whose brief asserts authority it structurally lacks.

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
| `build` | `/build` | AFK, inside the traverse workflow — a `builder`-typed node (lane 1 of the commit rule family). |
| `pr_review` | `/open-pr` first, always, then the [track](#track-rules) skills | AFK per skill, then the human's verdict on the whole stop ([pause 1](/software-factory/human-checkpoints.md#pause-1-the-review-verdict)). |
| `judgments` | none — the traverse workflow's judgment-facilitator rounds | AFK, entered only by the human's approve verdict; an ambiguous fix escalates ([pause 2](/software-factory/human-checkpoints.md#pause-2-judgments-conditional)). |

The table is factory-only. The definition region's skills — `/intake`,
`/design`, `/candidate-promote` — are invoked by the human and never dispatched,
and the `spike` node has no skill at all.

**Delegation.** An AFK node is delegated to a subagent whose prompt is the launch
line `run /<skill> <N>` and nothing more — nodes stay skills. The subagent gets a
fresh context window and inherits the issue's worktree as cwd; it reloads what it
needs from the issue (`gh issue view <N>`) and the worktree, does the work, and
ends with a terminal report. Nothing carries over from the overwatch's context.
The committing nodes are the traverse workflow's own — spawned by the
script as their factory agent types, with data-only briefs; no committing
node is delegated from the sequencing session, and no launch line carries
authorization of any kind. A helper
a skill invokes itself (`/commit`, `/grill-with-docs`) is not a node and is
never dispatched.

**The terminal report contract.** A subagent's final message MUST begin at
character one with exactly `DONE: <one-line outcome>` or
`ESCALATE: <one-line reason>`; detail follows below. Any non-matching final
message is treated as ESCALATE — malformed fails safe, toward the human. What the
overwatch does with an escalation is
[human-checkpoints.md](/software-factory/human-checkpoints.md#escalation).

## Worktrees and branches

Isolation — from other issues and from the main checkout — comes from git
worktrees, of two kinds. The machine phases run in the traverse workflow's
**throwaway fenced worktrees**, one per node, reaped when the run ends; the
`issue-<N>` branch on origin — the carrier — is what persists between them
([traverse.md](/software-factory/traverse.md)). The sequencing session opens
one **persistent review worktree** at the review stop, where the audits need
a checkout.

- **One branch, one PR per issue:** branch `issue-<N>` on origin carries the
  work; the review worktree lives at `<repo>/.claude/worktrees/issue-<N>`.
- **Opened at the review stop, then persisted.** cwd and worktree survive a
  `/clear`, so a sequencing session re-invoked after one inherits them.

### The worktree contract

Every file-touching node sits in a worktree; which one depends on the phase:

- **Open (the review stop).** The sequencing session opens it —
  `EnterWorktree(name=issue-<N>)`, rename to the bare `issue-<N>` — then
  syncs it so the tree stands at the carrier's tip, re-syncing the same way
  each later review cycle. The sync never discards committed work, and a
  sync that cannot land without discarding is an escalation.
  (`worktree.baseRef` pinned to `fresh` makes `EnterWorktree` branch from
  `origin/main`, so the fresh branch is *not* an ancestor of the carrier
  whenever `main` advanced during the build — a plain `--ff-only` pull would
  refuse there, and a routine merge to `main` would block every review stop.)
- **Inherit (the review stop's audits).** Audit subagents inherit the review
  worktree as their cwd, and the sequencing session keeps it across `/clear`.
  A machine-phase node inherits nothing: the traverse spawns it into a fenced
  tree of its own, and the carrier on origin is what it starts from.
- **Tear down (Agent-view overwatch, post-merge).** When the issue lands, the
  Agent-view overwatch removes the local side —
  `git worktree remove .claude/worktrees/issue-<N>` and
  `git branch -D issue-<N>` — only after the human confirms the merge happened. A
  spike's worktree goes the same way when its issue closes.

**The branch is pushed by its nodes.** A committing node publishes the
carrier itself — `git push --no-verify origin HEAD:issue-<N>`, within
[git-authority](/software-factory/git-authority.md)'s push rules — so origin
holds the work the moment a node ends, and the PR opens at the review stop
against a branch already published. Every intermediary push rides
`--no-verify` by standing ruling: the judgments phase is the verification
act, and the semantic bill settles there, once — see
[the judgments node](#the-judgments-node).

## The node-skill contract

A node skill does the node's work and reports; the issue overwatch launches it,
sequences what follows, and writes the labels. This contract fixes structure; the
authoring *style* behind the skills — voice, content, robustness, mechanics —
lives in [node-skill-authoring.md](/software-factory/node-skill-authoring.md).

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
  are, may gate on interviews and approvals, asked in prose at the terminal.
- **The report line.** Every node closes on one ` · `-delimited line: the handle
  `<repo>#<N>` · `phase: <node>`. A committing node appends
  `commit <sha> · check green · unpushed`; a node whose real output landed on
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
`/open-pr` authors it when it creates the PR, and the sequencing session
regenerates it from the final diff (a tap-free `gh pr edit`) after the
judgments phase returns green — the last act before the human's final read.
Nothing refreshes it in between — a message rewritten mid-traverse is authored
against a diff still moving.

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
`phase:judgments`, where the traverse workflow settles the semantic gate — see
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

**The traverse workflow runs it,** entered only by the human's approve
verdict: a script loop of at most 3 judged rounds, each one
judgment-facilitator node that records the prior round's passes, applies
focused fixes for its refuted verdicts, republishes the carrier, and
returns the fresh plan — a zero-job plan is green. Fixes commit through
lane 1; the sequencing session commits nothing. The full mechanics are
[traverse.md](/software-factory/traverse.md).

- **An ambiguous verdict escalates.** A refuted judgment that may be wrong
  about the code, or right about code that should change, ends the run as
  an escalation
  ([pause 2](/software-factory/human-checkpoints.md#pause-2-judgments-conditional));
  a clean green run stops for nothing.
- **A red cap escalates.** Still red after the final round, the run
  escalates with the refuted verdicts; judgments are never softened to
  pass, and nothing routes the issue anywhere while red.
- **No back edge.** Judgment fixes never reopen review — no new cycle, no
  fresh audit; the human has already approved the substance. The phase
  closes only green, and the sequencing session's close-out (merge-message
  refresh, the final read) follows.
