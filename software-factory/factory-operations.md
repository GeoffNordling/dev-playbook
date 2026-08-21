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

The unit of dispatch is the **issue**, and the build region is dispatched by a
program rather than by a session. `traverse-issue <owner/name> <issue> <mode>`
carries an issue from its phase label to an open pull request: it takes the
issue's lock, creates or reuses the worktree, launches `build` and `open-pr`, and
ends `pr-ready` or `escalated`. Every branch in that sequence is conditional
logic in the script; judgment happens only inside the agents it launches. From
the review stop on, the **issue overwatch** — one session per issue, launched by
the user in **Agent view**, the official name of the `claude agents` dashboard —
still sequences the traverse and stops where the user must act.

Two overwatch scopes, two screens:

- **Agent-view overwatch** — fleet scope: reads the board and recommends what to
  launch next.
- **Issue overwatch** — issue scope, one per issue: sequences the review stop
  onward and surfaces the commands the user must run.

**One traverse per issue.** `traverse-issue` takes a non-blocking per-issue lock
and exits at once, writing nothing, when another traverse of that issue holds it.
Concurrency across issues is unbounded; concurrency within one is not.

**Factory nodes only.** The factory region is all that is dispatched, by the
script and by a session alike. An issue whose phase sits in
[definition](/software-factory/software-factory.md#the-definition-region) — or an
unlabeled one — is refused outright by both, and each says what it can:
`traverse-issue` escalates naming the phase the issue carries and the phases it
runs, and a session names the skill the user should run instead. Definition is
user-led by construction; a dispatcher that improvised its way through intake
would be extracting intent with nobody to extract it from.

**Single label writer.** One writer per issue moves its `phase:*` label. Across
the build region that writer is `traverse-issue`, which moves the label only
after verifying for itself what the node claims to have done; from the review
stop on it is the sequencing session. A launched agent never writes a label, so
nothing can advance the board out from under whatever is sequencing it.

**Readiness at the crossing.** An issue must meet the readiness bar — a leaf,
unblocked, brief-complete, released at an issue-review verdict — defined once in
the [tracking standard](/standards/tracking/issue-authoring.md#readiness). The
whole bar is a definition-region obligation, carried across the crossing by the
`phase:build` label the user's approval sets.

`traverse-issue` re-derives none of it. The phase label is the program counter
and the only readiness signal read back: `phase:build` runs build then open-pr,
`phase:pr-review` runs open-pr alone, and any other phase — or none, or more than
one — escalates. `mode:spike` is read ahead of the phase and refused on sight,
because a spike opens no pull request for this graph to reach. Asking anything
further here would let a script overrule a decision that is the user's.

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

- **AFK** — the node runs hands-off and reports. The user sees only the report.
- **Inline** — a session runs the node at its own main loop, with the user
  present in the terminal.

A review node (a diamond) is several AFK runs followed by the sequencing
session's own verdict interview, within the one node.

### The dispatch table

The factory's nodes, what runs each, and how each engages the user:

| Node | Run by | Engagement |
|---|---|---|
| `build` | the `build` agent definition, launched by `traverse-issue` | AFK. |
| `pr_review` | the `open-pr` agent definition, launched by `traverse-issue`, always first; then the [track](#track-rules) skills | AFK per node, then the user's verdict on the whole stop ([pause 1](/software-factory/user-checkpoints.md#pause-1-the-review-verdict)). |

The table is factory-only. The definition region's skills — `/intake`,
`/design`, `/candidate-promote` — are invoked by the user and never dispatched,
and the `spike` node has no runner at all.

**Headless launch.** `build` and `open-pr` are typed agent definitions in
`dotfiles/dot-claude/agents/`, and `traverse-issue` launches each as its own
headless `claude -p` process under `--agent <name>`. Model, effort, and tool
roster all bind from the definition's frontmatter — the launch adds no flag that
would outrank them. The process is given the issue's worktree as its cwd and one
hour on the wall clock, and its stream is watched live: a run placed outside its
worktree, or billed to anything but the subscription, is killed rather than
allowed to finish.

**The fixed prompt.** The prompt is the issue number and nothing else. Everything
a node needs it reloads for itself — the brief from `gh issue view <N>`, the work
so far from the worktree — so nothing carries over from whatever launched it, and
two launches of one node at one issue are given identical input.

**The report envelope.** A launched node ends on structured output, never a
message alone: a required top-level `outcome` of `"done"` or `"escalated"`, and a
`gist` in prose. The launch is refused a report that does not validate. Nothing
else is read from it — what the traverse needs next is durable in git and on
GitHub, and it reads it from there rather than taking the agent's word, so a
node's claim never advances the board on its own.

**The terminal report contract.** A subagent delegated by a session — the track
reviews — MUST begin its final message at character one with exactly
`DONE: <one-line outcome>` or `ESCALATE: <one-line reason>`; detail follows
below. Any non-matching final message is treated as ESCALATE — malformed fails
safe, toward the user. What a session does with an escalation is
[user-checkpoints.md](/software-factory/user-checkpoints.md#escalation). A helper
invoked inside a node (`/commit`, `/grill-with-docs`) is not a node and is never
dispatched.

**Escalation is terminal, and retries are the caller's.** A traverse runs no node
twice. Any way a job comes back other than a clean process reporting `done` — the
node's own `escalated`, a crash, the deadline, a refused report, a misconfigured
run — ends the traverse on `traverse-escalation` then `traverse-end`. The
escalating node's own label move is what does not happen; a move an earlier node
in the same traverse already made stands. So a retry — the caller invoking
`traverse-issue` again from the top — resumes at whatever phase the last node to
finish left behind, not at the phase the traverse started on: a build that
verified and then an `open-pr` that escalated leaves `phase:pr-review`, and the
next invocation runs `open-pr` alone.

## Worktrees and branches

An issue's work is isolated — from other issues and from the main checkout — by
giving each issue its own **git worktree**, created once and kept for the issue's
life.

- **One worktree, one branch, one PR per issue,** at
  `<repo>/.claude/worktrees/issue-<N>` on branch `issue-<N>` (`N` is the issue
  number).
- **Created once, then persisted.** The worktree outlives every session that
  works in it, so each node arrives at a tree the last one left.

### The worktree contract

The worktree's whole lifecycle belongs to `traverse-issue`, not to anything
running inside it. A node never creates, enters, or removes one: the script
creates the tree before the first launch and hands it to every node as its
working directory.

- **Create or reuse (the traverse, before its first node).** A worktree already
  at the path is reused exactly as found — no freshness check and no rebase,
  because whether work in flight should move onto a newer `main` is a judgment
  about the issue rather than about this run. What is checked is that it is one:
  `git worktree list --porcelain` must register it, on branch `issue-<N>`, and a
  bare directory left behind by a refused removal escalates instead. Otherwise
  the traverse fetches `origin/main`, compares the fetched ref against origin
  (`git rev-parse origin/main` against
  `gh api repos/<owner>/<name>/branches/main` — the slug written out, because gh
  fills the `{owner}/{repo}` placeholders from the repo of the current directory
  and the traverse runs from wherever it was launched), escalates if the base is
  still stale, and branches `issue-<N>` from `origin/main`.
- **Inherit (every node).** Each node is launched with the worktree as its cwd
  and does its work there.
- **Remove (the user).** A merged issue's worktree and branch are removed by
  hand — `git worktree remove .claude/worktrees/issue-<N>` and
  `git branch -D issue-<N>`.

**The branch is pushed as it is committed.** A committing node pushes what it
commits — the push is part of `/commit` — so the branch is on origin whenever
the node ends, verified by the pre-push hook's full `make check` on the way out.
The traverse then checks that for itself, and all four checks precede the label
move: the worktree is on `issue-<N>` rather than a detached HEAD, it has nothing
uncommitted, `issue-<N>` is on origin at all, and it is there at the sha the
worktree holds. The last one alone
would not do — neither sha moves when a node edits and never commits, so on a
rework lap, where the branch is already on origin when the node starts, the
comparison would agree with itself and pass over work the pull request will never
show.

## The node-skill contract

A node does the node's work and reports; what launched it sequences whatever
follows and writes the labels. The contract binds both kinds of node — the typed
agent definitions the traverse launches and the skills a session dispatches —
and four clauses below say where the two differ. This contract fixes structure;
the authoring *style* behind both — voice, content, robustness, mechanics — lives
in [node-agent-and-skill-authoring.md](/software-factory/node-agent-and-skill-authoring.md).

- **Read first.** When a node has required reading, it front-loads that reading
  and closes it with a `READ: <files>` confirmation before it edits anything;
  when it has none, it carries neither. The confirmation is what binds — where
  it sits is the node's own: a skill puts it under a `## Read first` heading, a
  definition may fold it into a numbered step of its own.
- **Worktree.** Every file-touching node does its work in the issue's worktree.
  A definition is placed there by `traverse-issue`, which owns the whole
  lifecycle per [the worktree contract](#the-worktree-contract) and never asks
  the node to create or enter one; a skill dispatched by a session inherits it as
  cwd.
- **AFK** — the node runs hands-off. A definition terminates on
  [the report envelope](#engagement); a skill terminates per
  [the terminal report contract](#engagement), `DONE:` on success and
  `ESCALATE:` when stuck. Each states its own escalation triggers in its body.
- **Inline** — a skill the user invokes directly, as the definition region's
  are, may gate on interviews and approvals, asked in prose at the terminal.
- **The report line.** A skill closes on one ` · `-delimited line: the handle
  `<repo>#<N>` · `phase: <node>`. A committing node appends
  `commit <sha> · check green · pushed`; a node whose real output landed on
  GitHub appends a pointer only (`findings on PR #<n>`, `brief in issue`), never
  a re-paste — the line points, GitHub holds the detail. An AFK skill carries it
  on the `DONE:`/`ESCALATE:` line; an inline skill omits the token and closes
  with the line alone. A definition carries the same content as the envelope's
  `gist` instead, because nothing parses its prose.
- **Gate.** A committing node runs `make check` — the full gate, not just the
  commit hooks — before finishing its phase; a phase never closes over a red
  tree. The rule is per-phase, not per-commit: individual commits are already
  covered by the commit gate's hook suite, and the full gate is the phase-close
  ritual.
- **Judgments sit outside every node.** `make check` leaves the semantic
  [cache gate](/standards/judgments/cache-gate.md) skipped, and no node arms it
  or runs a judge — judgments are settled by the periodic sweep, outside the
  factory. For a **review** skill the exclusion is total: the
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
