---
type: Guide
title: Factory Operations
description: The factory's operating contract — how a ready issue is dispatched, built, reviewed, and carried to the merge
---

# Factory Operations

How the factory carries a ready issue from `build` to a merged pull request with
nobody driving it. The map it executes — the regions, the states, the labels —
is [software-factory.md](/software-factory/software-factory.md); every point
where it stops for the user is
[user-checkpoints.md](/software-factory/user-checkpoints.md).

## Dispatch

The unit of dispatch is the **issue**, and a program dispatches it.
`traverse-issue <owner/name> <issue> <mode>` carries an issue from its phase
label to a reviewed pull request: it takes the issue's lock, creates or reuses
the worktree, launches `build` and `open-pr`, then runs the
[review stop](#the-review-stop) — reviews, verdict, and rework laps — and ends
`pr-ready` or `escalated`. Every branch in that sequence is conditional logic in
the script; judgment happens only inside the agents it launches. From the merge
boundary on, the **issue overwatch** — one session per issue, launched by the
user in **Agent view**, the official name of the `claude agents` dashboard —
sequences what is left and stops where the user must act.

The overwatch scopes:

- **Agent-view overwatch** — fleet scope: reads the board and recommends what to
  launch next.
- **Issue overwatch** — issue scope, one per issue: sequences the merge boundary
  and surfaces the commands the user must run.

**One traverse per issue.** `traverse-issue` takes a non-blocking per-issue lock
and exits at once, writing nothing, when another traverse of that issue holds
it. Concurrency across issues is unbounded.

**Factory nodes only.** The factory region is all that is dispatched, by the
script and by a session alike. An issue whose phase sits in
[definition](/software-factory/software-factory.md#the-definition-region) — or an
unlabeled one — is refused outright by both, and each says what it can:
`traverse-issue` escalates naming the phase the issue carries and the phases it
runs, and a session names the skill the user should run instead. Definition is
user-led: a dispatcher improvising its way through intake would be extracting
intent with nobody to extract it from.

**Single label writer.** One writer per issue moves its `phase:*` label. Across
the factory that writer is `traverse-issue`, which moves the label only after
verifying for itself what the node claims to have done; from the merge boundary
on it is the sequencing session. The review stop moves no label at all — a
rework lap runs the build node over an issue already at `phase:pr-review`, and
there is nowhere for the label to go. A launched agent never writes a label, so
nothing can advance the board out from under whatever is sequencing it.

**Readiness at the crossing.** An issue must meet the readiness bar — a leaf,
unblocked, brief-complete, released at an issue-review verdict — defined in the
[tracking standard](/standards/tracking/issue-authoring.md#readiness). The whole
bar is a definition-region obligation, carried across the crossing by the
`phase:build` label the user's approval sets.

`traverse-issue` re-derives none of it. The phase label is the program counter
and the only readiness signal read back: `phase:build` runs build then open-pr,
`phase:pr-review` runs open-pr alone, and any other phase — or none, or more
than one — escalates. `mode:spike` is read ahead of the phase and refused on
sight, because a spike opens no pull request for this graph to reach. Asking
anything further would let the script overrule a decision that is the user's.

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

**Subagent permissions are wide.** Subagent-level tool permissions are out of
scope for this model: subagents run under auto mode with wide permissions,
accepted deliberately, and a later pass may tighten it.

**The reviewer read-only guarantee is enforced.** A reviewer reports findings
and never rewrites the work under review, and the harness holds it to that:
`code-pr-review`, `bug-pr-review`, and `doc-pr-review` each pin
`tools: Read, Bash`, so the file-writing tools are absent. The roster is
accident-grade rather than containment — `Bash` sits on it because every GitHub
write rides `gh`, and searching rides it too, this harness having no separate
search tool. A pin naming a tool the harness does not have is discarded in
silence, so a roster states only names the harness reports.

From the first file-touching node on, the session is cwd-bound to the issue's
worktree, which confines its file reach.

Canonical front-matter and syntax:
[skills](https://code.claude.com/docs/en/skills.md),
[permissions](https://code.claude.com/docs/en/permissions).

## Engagement

A node engages the user in one of two ways:

- **AFK** — the node runs hands-off and reports; the user sees only the
  report. No user is attached, so the node runs to completion or escalates —
  it never waits. Substrate does not decide it: a delegated subagent and a
  headless `claude -p` process are both AFK.
- **Inline** — a session runs the node at its own main loop, with the user
  present in the terminal, free to interview, gate on the answers, and hand
  back mid-task.

A review node (a diamond) is several AFK runs followed by a verdict the script
computes from what they left on the pull request, within the one node.

### The dispatch table

| Node | Run by | Engagement |
|---|---|---|
| `build` | the `build` agent definition, launched by `traverse-issue` | AFK. |
| `pr_review` | the `open-pr` agent definition, launched by `traverse-issue`, always first; then the [elected](#the-review-stop) reviewer definitions, launched together each cycle; then the `adjudicator` definition, at the verdict points its [launch rule](#the-review-stop) names | AFK throughout — the verdict on the stop is the script's, computed from thread state. |

The table is factory-only. The definition region's skills — `/intake`,
`/design`, `/candidate-promote` — are invoked by the user and never dispatched,
and the `spike` node has no runner.

**Headless launch.** `build`, `open-pr`, the reviewers and the `adjudicator` are
typed agent definitions in `dotfiles/dot-claude/agents/`, and `traverse-issue`
launches each as its own headless `claude -p` process under `--agent <name>`.
Model, effort, and tool roster all bind from the definition's frontmatter — the
launch adds no flag that would outrank them. The process is given the issue's
worktree as its cwd and one hour on the wall clock, and its stream is watched
live: a run placed outside its worktree, or billed to anything but the
subscription, is killed.

**The prompt is fully determined by durable state.** Nothing carries over from
whatever launched a node: every value in a prompt is read from the pull request
or the issue at launch time, so two launches that find the same durable state are
given identical input. Most prompts are the issue number alone. The rest carry
more, and each carries an address rather than content:

- A **review** prompt carries the issue number and, from its own second cycle,
  the sha its own last cycle header names — which is where its delta starts. Per
  review, never across: election is recomputed every cycle, so a track that sat
  one out and handed a sibling's sha would start at a commit it never read.
- A **rework** prompt carries the issue number and the id and location of every
  unresolved Blocking thread. No finding text: the thread is the record and it
  keeps moving, so the node reads each one live from GitHub. The order is the
  node's own.

  It also carries each **fix-now item** the verdict point ruled — its thread id
  and the one line of fix text the ruling states
  ([suggestion dispositions](/software-factory/review-contract.md#suggestion-dispositions)).
  That text is the one exception: the ruling was made moments earlier and
  written onto no thread, so there is no live copy to read. Every thread id in
  the prompt, fix-now threads included, is still read from GitHub.

**The report envelope.** A launched node ends on structured output: a required
top-level `outcome` of `"done"` or `"escalated"`, and a `gist` in prose. A
review's envelope adds the counts of what it posted
([the report envelope](/software-factory/review-contract.md#the-report-envelope)).
The launch is refused a report that does not validate. Nothing else is read from
it — what the traverse needs next is durable in git and on GitHub, so a node's
claim never advances the board on its own.

**The terminal report contract.** A subagent delegated by a session MUST begin
its final message at character one with exactly `DONE: <one-line outcome>` or
`ESCALATE: <one-line reason>`; detail follows below. Any non-matching final
message is treated as ESCALATE — malformed fails safe, toward the user. What a
session does with an escalation is
[user-checkpoints.md](/software-factory/user-checkpoints.md#escalation).

It binds no factory node. Every node the traverse launches — the reviews
included — is a headless process ending on the report envelope above. A helper
invoked inside a node (`/commit`, `/grill-with-docs`) is not a node and is never
dispatched.

**Escalation is terminal, and retries are the caller's.** A traverse never runs a
job again after it has failed. Any way a job comes back other than a clean
process reporting `done` — the node's own `escalated`, a crash, the deadline, a
refused report, a misconfigured run — ends the traverse on `traverse-escalation`
then `traverse-end`. A failure inside the review loop's fan-out waits for its
siblings first, so their books land before the traverse ends, and then every
failure is relayed onto the escalation row in the node's own words. The
escalating node's own label move is what does not happen; a move an earlier node
in the same traverse already made stands. So a retry — the caller invoking
`traverse-issue` again from the top — resumes at whatever phase the last node to
finish left behind: a build that verified and then an `open-pr` that escalated
leaves `phase:pr-review`, and the next invocation runs `open-pr` and falls into
the review loop behind it.

A rework lap is not a retry: it is the loop's ordinary next step over a job that
finished cleanly, launching `build` again against findings that did not exist
when the last one ran.

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

The worktree's whole lifecycle belongs to `traverse-issue`. A node never creates,
enters, or removes one: the script creates the tree before the first launch and
hands it to every node as its working directory.

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
The traverse then checks that for itself, and the checks precede the label move:
the worktree is on `issue-<N>` rather than a detached HEAD, it has nothing
uncommitted, `issue-<N>` is on origin at all, and it is there at the sha the
worktree holds. The last one alone would not do — neither sha moves when a node
edits and never commits, so on a rework lap, where the branch is already on
origin when the node starts, the comparison would agree with itself and pass over
work the pull request will never show.

## The node-skill contract

A node does the node's work and reports; what launched it sequences whatever
follows and writes the labels. The contract binds every node — the typed
agent definitions the traverse launches and the skills a session dispatches —
and the clauses below say where the two differ. This contract fixes structure;
the authoring *style* behind both — voice, content, robustness, mechanics — lives
in [node-agent-and-skill-authoring.md](/software-factory/node-agent-and-skill-authoring.md).

- **Read first.** When a node has required reading, it front-loads that reading
  and closes it with a `READ: <files>` confirmation before it edits anything;
  when it has none, it carries neither. The confirmation is what binds; where it
  sits is the node's own: a skill puts it under a `## Read first` heading, a
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
  a re-paste. An AFK skill carries it on the `DONE:`/`ESCALATE:` line; an inline
  skill omits the token and closes with the line alone. A definition carries the
  same content as the envelope's `gist` instead, because nothing parses its
  prose.
- **Gate.** A committing node runs `make check` — the full gate, not just the
  commit hooks — before finishing its phase; a phase never closes over a red
  tree. The rule is per-phase, not per-commit: individual commits are already
  covered by the commit gate's hook suite.
- **Judgments sit outside every node.** `make check` leaves the semantic
  [cache gate](/standards/semantic-validation/cache-gate.md) skipped, and no node arms it
  or runs a judge — judgments are settled by the periodic sweep, outside the
  factory. For a **review** skill the exclusion is total: the
  `judgments/*.yaml` declarations are outside its jurisdiction
  whether or not the diff changes them, and a judgment — its content, its
  verdict, or its cache state — appears nowhere in its findings. A stale or red
  cache mid-traverse is the expected condition, not a defect to report.

## Pull requests

One PR per issue — spikes open none — opened at the review stop and
squash-merged by the user. Because
[repository settings](/standards/tracking/repo-settings.md) take the squash
message from the PR, its title and body become the permanent commit message on
`main`: they are authored from the issue brief, the diff, and the record the
issue and its PR carry, never left as a placeholder.

### The merge-message recipe

- **Title** — states the change: it is the commit subject `main`'s history will
  carry.
- **Body** — mandatory sections, each checkable by absence:
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
  - `## Suggestion dispositions` — one line per Suggestion thread the review
    loop settled, naming its outcome and the thread. It is the merge read's
    one-place summary of what became of every suggestion. `None.` explicitly
    when empty, which is what the node opening the pull request scaffolds.

The code and doc reviews open with a mechanical presence check, and a missing
section is an automatic Blocking finding.

### The two owners

The message is written twice from that one recipe, so the two cannot diverge:
`/open-pr` authors it when it creates the PR — lifting the build session's
recorded entries into `## Deviation ledger` per the
[contract's hand-off](/software-factory/deviation-contract.md#the-deviation-ledger)
— and the `adjudicator` regenerates it at convergence (`gh pr edit`).
The regeneration synthesizes the entire PR record — the final diff,
the comments, and the rulings — into an accurate squash-commit message for
the whole issue, preserving the mandatory sections' content rather than
rewriting from the recipe alone. In between, only the ledger moves —
rework laps append its entries by spec; a full message rewritten mid-traverse
is authored against a diff still moving.

## The review stop

`pr_review` is a loop `traverse-issue` runs, and the user is not in it. Each
**cycle** is one pass of the same steps, and the loop stops only when it
converges, escalates, or is killed:

1. **Elect the tracks** from the pull request's changed files
   ([track rules](#track-rules) below), recomputed every cycle.
2. **Run every elected review at once**, as concurrent headless launches.
3. **Read the threads and compute the verdict** — the arithmetic is
   [the verdict and the cap](/software-factory/review-contract.md#the-verdict-and-the-cap),
   and the counts it reached are recorded on a `verdict` ledger row.
4. **Act on it.** Both live verdicts run the `adjudicator` over the open
   Suggestion threads first, on a rule the verdict word alone decides:
   `converged` always runs it, and `rework` runs it only when Suggestion
   threads are open. `converged` then ends the traverse `pr-ready`. `rework`
   relaunches `build` against the open Blocking threads, plus each fix-now item
   the adjudicator ruled, and goes round again. `cap-escalated` runs nothing and
   ends the traverse escalated — nothing settled now would be read.

**`pr-ready` means converged on Blocking alone.** Only Blocking threads are
weighed for convergence. The adjudicator settles every open Suggestion at each
verdict point, and the run at convergence always happens, so a traverse ends
`pr-ready` with its suggestions settled. The verdict is computed before that run,
so a Suggestion counted open in a `verdict` row is the ordinary case.

- **Code track.** `bug-pr-review` posts its bug findings; `code-pr-review` adds
  the fidelity and convention findings it does not cover.
- **Doc track.** `doc-pr-review` audits the diff's documentation.

**Every elected track runs every cycle.** No review stands down — the election
takes the changed files and nothing else. A stand-down would deadlock the loop:
only the next cycle's reviewer may resolve a
thread
([resolution ownership](/software-factory/review-contract.md#resolution-ownership)),
so a stood-down track's fixed threads would have nobody left to resolve them, the
open Blocking count would never reach zero, and a pull request that had actually
converged would cap out. A stand-down reintroduced later has to move resolution
ownership with it.

**The loop keeps no state of its own.** Everything it needs is on the pull
request: the cycle headers give the cycle number and each track's last-reviewed
sha, and the threads give the verdict. So a traverse relaunched after a crash
runs the identical code path — there is no resume branch and no label moves
inside the loop. It costs one burned cycle number when a traverse dies after its
reviews have posted, and the cap's clock is never turned back to pay for it.

**A diff no review reads escalates.** Every verdict rests on threads some review
posted, so a cycle that elects nothing would find no Blocking thread, declare
convergence, and hand back a pull request nobody had read.

### Track rules

Content kind picks the track, and the kinds are told apart mechanically, by
suffix: `.md` is documentation, `.html` is rendered output no review reads as
source, and everything else is code.

- **Code track — whenever any code file changed.** It is the diff's default
  reader.
- **Doc track — earned, while there is code beside it.** It runs when the diff
  adds a document, or changes 10 or more documentation lines. Below that the doc
  change is the echo a code change forces, and reviewing it spends a run on
  content nobody questioned.
- **A documentation-only diff always earns the doc track**, however small. With
  no code track there is nothing else to read the diff.
