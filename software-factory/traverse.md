---
type: Guide
title: Traverse
description: The traverse workflow — the arcs it runs over an issue's machine phases, the node topology and carrier, the judgments loop, and its escalate and error contracts
---

# Traverse

A **traverse** is one issue's passage through the factory region. Its two
machine phases — build and judgments — are executed by the **traverse
workflow** (`dotfiles/dot-claude/workflows/traverse.js`), a named dynamic
workflow the issue's sequencing session launches and awaits:
`Workflow({name: 'traverse', args: "<repo> <N>"})`, args always one plain
string. One run serves one contiguous arc; the review stop between the arcs
belongs to the sequencing session, per
[factory-operations.md](/software-factory/factory-operations.md).

## The dispatcher

A run's first act is a clerk label read — fresh truth; label state passed by
the launcher is never trusted. The label selects the arc:

- `phase:build` — the build arc.
- `phase:judgments` — the judgments arc.
- Anything else — the run escalates without touching anything: it refuses to
  guess.

That read is what makes **relaunch the universal recovery**: a relaunched run
acts on where the issue actually stands, so the human's answer to any failure
is one launch, not an investigation into resumable state.

## Nodes and the fence

Traverse nodes are ephemeral agents spawned with `isolation: 'worktree'`
from the root-anchored session; the harness fence is the containment —
writes outside the node's own worktree are refused. Node briefs carry
**data only** (repo, issue number, verdicts, commands, carrier state);
procedure lives in the agent definitions under `dotfiles/dot-claude/agents/`.
Models ride the definitions' frontmatter; the script pins `effort` per node
type — clerk and reaper at `low`, builder and judgment-facilitator at
`xhigh`.

Every node that returns data returns it through harness schema enforcement,
and every node schema requires `status: done|escalate`. Fenced nodes also
return their worktree path — the script derives the run's `wf_…` worktree
prefix from reported paths, never from a guess.

The script itself never runs `gh` or touches a file: a workflow script has
no shell. Every label read and move is the clerk's, on the script's
instruction; while a run is live the clerk is the issue's one label writer,
and outside a run label authority is the sequencing session's.

## The carrier

The `issue-<N>` branch **on origin** is the sole carrier of work between
nodes and between runs. It is born via `git push origin HEAD:issue-<N>` from
inside the fence — the harness-named local branch is never renamed. A node
that starts from published work adopts the carrier as its first act:
`git fetch origin issue-<N>`, then
`git switch -c <worktree-name>-adopt origin/issue-<N>`, where
`<worktree-name>` is the node's worktree-directory basename — so the
adoption branch falls under the run's reapable prefix and never leaks. The
spelling refuses rather than discards when a tree is unexpectedly dirty; no
factory process is built on `git reset --hard` or any other
silently-destructive spelling, by standing epic ruling.

Cross-run state is exactly three things: the carrier, the content-keyed
judgments seen-set, and script memory within a single run. No worktree
survives a node.

## The build arc

One builder-typed node in a fenced worktree: adopt the carrier when the
brief says it exists (a rework relaunch rebuilding on published work), run
/build, commit through its agent type, publish the carrier. On its `done`
the clerk moves `phase:build` → `phase:pr-review`, the reaper cleans the
run's worktrees, and the run returns DONE. The review stop that follows is
the sequencing session's.

## The judgments arc

Entered only after the human's approve verdict has moved the issue to
`phase:judgments`. A plain script `for` loop, capped at **3 judged rounds**.
Each round is one judgment-facilitator node in a fenced worktree: adopt the
carrier, run the prior round's record command (absent on the entry round),
apply focused fixes for the prior round's refuted verdicts (absent on the
entry round — its job is the plan alone), commit and republish the carrier,
re-run `judgments-run plan`, return the plan stdout. The script parses the
plan: **zero jobs is green**. Jobs spawn the judges via
`workflow('judgments', planString)` — the nested call spends the one legal
nesting level, and the plan travels as a string, byte-identical — and the
verdicts feed the next round's brief. Still red at the cap →
`escalate('judgments-red', <refuted verdicts>)`. **Judgments are never
softened to pass.**

On green there is no onward label move: the issue sits at `phase:judgments`
through the human's final read and merge. The sequencing session's close-out
(merge-message refresh, the final read) follows the run's DONE.

## The escalate contract

On any node's `escalate`, the run stops — no further nodes, no reap, labels
untouched — and the ESCALATE payload is the run's return value. It carries:
issue handle · node · one-line reason · a node-authored brief · a
cwd/worktree/branch/SHA state block. The state block is a **report, not a
guarantee** — harness auto-clean removes unchanged trees at agent end
regardless, so consumers tolerate dead paths. The launcher posts the payload
verbatim as a comment on the issue (escalations are durable on the issue)
and relays the node-authored brief to the human.

## The error lane

Every `agent()` result is checked. The harness swallows agent errors into
`null`, so a `null` gets one retry, then a self-describing throw. At the
launcher, a `failed` run and a completed run whose return parses as neither
DONE nor ESCALATE are both handled as escalations, never ignored. The
auto-mode classifier's gating is stochastic: a blocked launch or node is a
normal operational event — retry or escalate — never answered with a more
persuasive brief; a relaunch carries the human's decision verbatim.

## Re-entrancy

Recovery is relaunch, on the human's word only. A relaunched run resumes
from fresh labels, `origin/issue-<N>`, and the seen-set. `resumeFromRunId`
is same-session cache replay and is never used on live work.

## Reaping

On the clean DONE path the run's last node is the reaper, handed the
worktree prefixes its nodes reported: it removes those worktrees and
branches by prefix, never by guessed count, tolerating already-cleaned
entries. An escalated run's trees are left standing (best-effort) for
inspection; sweeping them belongs to the manager conversion, not to any
run.
