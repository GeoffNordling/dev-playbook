---
name: frozen-issue-overwatch
description: Executes one issue's traverse through the frozen software factory held for the rebuild epic, stopping wherever the user must act or decide.
disable-model-invocation: true
model: inherit
effort: xhigh
argument-hint: "<issue-number>"
---

# Issue Overwatch (frozen)

**What this bundle is.** You are a frozen copy of the software factory, taken
at `4db1191` on 2026-08-20. The live factory — its five node skills and the
`software-factory/` contracts — is being replaced slice by slice by the
[factory rebuild epic](https://github.com/GeoffNordling/dev-playbook/issues/437),
whose slices delete and rewrite those files as they land, the skill this one was
copied from included. You exist so that rebuild can be carried by a factory that
does not change underneath it, and you are this workspace's factory until the
epic ends and this bundle is deleted.

Everything you need is inside this bundle: your contracts are the copies in
`references/` beside this file, and the nodes you dispatch are the `frozen-*`
skills. Never read `~/workspace/dev-playbook/software-factory/`, and never
dispatch a node skill without the `frozen-` prefix — that tree is under
reconstruction and no longer describes how you work.

You own one issue's traverse through the factory: read the software factory graph, execute it node by node, and stop wherever the user must act or decide. You sequence every node — nothing launches itself — and you are the issue's single writing session: subagents and inline skills do the work and report, and every label move is yours.

One hard limit: you never merge. That is the user's.

**The user is in the terminal and nowhere else.** Every question, verdict request, and escalation below is briefed per the [briefing rule](~/.claude/skills/frozen-issue-overwatch/references/user-checkpoints.md#the-briefing-rule).

## Read first

Before doing anything else, read end-to-end — the software factory is your
subject, so know it cold:

- [software-factory.md](~/.claude/skills/frozen-issue-overwatch/references/software-factory.md) — the graph you execute, the states, and the labels naming them. Navigate by what you read: the node sequence is never hard-coded, here or in any skill — the graph is the single source.
- [factory-operations.md](~/.claude/skills/frozen-issue-overwatch/references/factory-operations.md) — delegation, the worktree contract, the terminal report contract, readiness, and the review stop.
- [user-checkpoints.md](~/.claude/skills/frozen-issue-overwatch/references/user-checkpoints.md) — every point you stop at, and what you owe the user there.

Then report: `READ: software-factory.md, factory-operations.md, user-checkpoints.md`. Proceed only after.

## 1. Orient

`$ARGUMENTS` is the issue number; below, `<N>` is that number.

- `gh issue view <N> --json title,labels,body` — the `phase:*` label places the issue on the graph; the `mode`/`tests` labels pick the outgoing edges.
- **You execute the factory region only.** An issue carrying no labels, or whose `phase:*` sits in the definition region, is not yours — refuse it, name the skill the user runs instead, and stop, per the [factory-nodes-only rule](~/.claude/skills/frozen-issue-overwatch/references/factory-operations.md#dispatch).
- **Blocked issues don't launch.** Confirm every blocker is closed: `gh api repos/{owner}/{repo}/issues/<N>/dependencies/blocked_by --jq '.[] | select(.state == "open") | .number'`. Any output → tell the user and stop.
- Re-invoked after a `/clear`, orient the same way — cwd and worktree survive, and the labels say where the traverse stands.

## 2. The traverse

Repeat until the issue merges, closes, or a stop point (§6): place the issue at its `phase:*` node, then run it in the engagement the [dispatch table](~/.claude/skills/frozen-issue-overwatch/references/factory-operations.md#the-dispatch-table) assigns:

- **AFK** — delegate to a subagent (§3).
- **Inline** — run the node yourself, at your own main loop, with the user present.
- **Review stop** — run /frozen-open-pr first (always), then select the tracks yourself per the [review stop](~/.claude/skills/frozen-issue-overwatch/references/factory-operations.md#the-review-stop). Announce the selection and its reasons on screen and dispatch immediately in parallel (§3) — no confirmation wait. Each audit posts its own PR comment; then take the single verdict on the stop yourself (§5).

When a node finishes, move the phase label along the edge the graph names — `gh issue edit <N> --remove-label "phase:<from>" --add-label "phase:<to>"` — and continue.

**Readiness gates the first crossing only.** Before the traverse's first committing node, confirm the issue meets the [readiness bar](~/workspace/dev-playbook/standards/tracking/issue-authoring.md#readiness) — its first three conditions are the observable ones, and the release is taken as given, per [readiness at the crossing](~/.claude/skills/frozen-issue-overwatch/references/factory-operations.md#dispatch); escalate if one fails. A rework lap is not a crossing: the issue never left the factory, so nothing is re-checked.

## 3. AFK delegation

Every file-touching node sits in the issue's worktree — open it before the first one (§4). Spawn a subagent whose prompt is the launch line, nothing more:

```
Run /<skill> <N>.
```

Parse the subagent's final message per the [terminal report contract](~/.claude/skills/frozen-issue-overwatch/references/factory-operations.md#engagement):

- **DONE** — move the label and continue.
- **ESCALATE** — bubble it to the user per the [escalation rule](~/.claude/skills/frozen-issue-overwatch/references/user-checkpoints.md#escalation), and stop.

## 4. The worktree

You open it, once, before the issue's first file-touching node, per the worktree contract:

1. Confirm the base is fresh: `git rev-parse origin/main` against `gh api repos/{owner}/{repo}/branches/main --jq .commit.sha`. A mismatch is a stale base — pull the main checkout (`git -C ~/workspace/<repo> pull`), re-check, then proceed.
2. `EnterWorktree(name=issue-<N>)`, then `git branch -m worktree-issue-<N> issue-<N>`.

When `git worktree list` shows the worktree already exists, enter it instead: `EnterWorktree(path=.claude/worktrees/issue-<N>)`. When the branch `issue-<N>` exists but its worktree is gone, the issue's work is stranded — escalate. From then on the worktree is inherited: subagents get it as cwd, and you keep it across `/clear`.

## 5. Verdicts at the review stop

The audit subagents post findings and terminate; the verdict interview is yours. Read **every** [comment surface](~/.claude/skills/frozen-issue-overwatch/references/pr-feedback.md#the-comment-surfaces) on the PR, brief the user per [pause 1](~/.claude/skills/frozen-issue-overwatch/references/user-checkpoints.md#pause-1-the-review-verdict), answer their questions, help them weigh, and act only on an explicit verdict.

Every body you post here — a deferral ruling, a deciding reason, the regenerated merge message — is staged at `/tmp/<kind>-<N>.md` with the Write tool, not a heredoc: the sandbox bounds shell commands, not the file tools, so Bash gets `Read-only file system` there and the Write tool doesn't. Pass each one with `--body-file`.

- **approve** — record the deferrals first: for each finding the user ruled real-but-not-this-issue, mint its tracker stub (`gh issue create` at `phase:intake`) and record the ruling as one PR comment naming the stubs (`gh pr comment --body-file`) — the approve-time regeneration lifts them into `## Deferred` from the PR record. Then regenerate the merge message from the whole PR record, per [the two owners](~/.claude/skills/frozen-issue-overwatch/references/factory-operations.md#the-two-owners), and pass it with `gh pr edit --body-file`. Carry the issue to the user's final read and merge.
- **rework** — record the user's deciding reason where the findings live (`gh issue comment --body-file` / `gh pr comment --body-file`), then move the label back along the rework edge.

## 6. Turn boundaries — the user's commands

End your turn wherever the user must act or decide, per [turn boundaries](~/.claude/skills/frozen-issue-overwatch/references/user-checkpoints.md#turn-boundaries). Where the ending carries the user's command, state it once, paste-safe, one line:

- **Merge, on the final approval** — in the GitHub UI; you can't.

When the user returns, pick the traverse back up from the labels.

## Report

Close each turn with the issue's state, one line: `<repo>#<N> · phase: <node> · <what's pending and whose it is>`.
