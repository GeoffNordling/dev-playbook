# Agent-view worktrees and multi-phase continuity

**Status: open investigation.** This records the problem and a *candidate* solution to
validate — it is not settled. The candidate has not yet been tested against real
"claude agents" behavior; do that from scratch.

## 1. The objective

The workflow moves a single GitHub issue through several phases (nodes) — e.g.
requirements → design → implement → review → merge. Each phase runs as its own
human-dispatched session from the "claude agents" dashboard, one session per node.
Several issues are in flight at once. When an issue is approved, it squash-merges into
`main`.

Two hard requirements fall out of this:

- **Continuity** — every phase of one issue builds on the previous phase's commits; they
  all land on that issue's single branch.
- **Isolation** — simultaneous issues never touch each other's files or branches.

## 2. Git foundations (the model this rests on)

- A **branch** is a movable pointer to the latest commit on a line of work. `main` is one
  such pointer. Committing moves the pointer forward.
- **`main` is the trunk.** We never edit it directly — we branch off it and merge back. It
  only advances via merges.
- **One branch per issue.** All of an issue's phases commit onto that one branch, in
  sequence; the branch accumulates the issue's whole history. One PR tracks it end to end.
- A **worktree** is a second working folder, with a different branch checked out, sharing
  the same underlying repo (one shared commit history). It lets several branches be open at
  once, each in its own folder — this is how parallel issues stay isolated.
- **The rule that governs everything:** a given branch can be checked out in **at most one
  worktree at a time**.

Two issues in flight, each its own branch and worktree:

```
              A1─A2─A3        issue-42-branch   (checked out in issue-42-worktree)
             /
o──o──o──── M                 main              (never edited directly)
             \
              B1─B2           issue-43-branch   (checked out in issue-43-worktree)
```

```
~/repo/                                       → main
~/repo/.claude/worktrees/issue-42-worktree/   → issue-42-branch
~/repo/.claude/worktrees/issue-43-worktree/   → issue-43-branch
```

When an issue is done, its branch squash-merges into `main`, and its branch + worktree are
torn down. The other issue keeps going on its own worktree, undisturbed.

## 3. The problem with agent-view's worktrees

"claude agents" manages worktrees for *its* model — **one disposable worktree per
session** — not *one durable branch per issue*. Per the agent-view behavior
(see [agent-view-adoption.md](agent-view-adoption.md) for the broader survey):

- A session **starts in the directory it was dispatched from** (normally the `main`
  checkout).
- It **lazily creates an isolated worktree on the first file write** (the Write/Edit tool),
  under `.claude/worktrees/`, branched from wherever that start directory is — i.e. off
  `main`.
- The worktree is **auto-named** and effectively **leased to that one session**, and is
  **swept away when the session is deleted/exits**.

This collides with our model:

- **Continuity breaks.** Phase 2 is a new session; dispatched normally it cuts a *fresh*
  worktree off `main` and never sees phase 1's commits — the issue forks.
- **Read-only phases get no worktree** (no Write/Edit), so they run in the start directory
  on `main` — reviewing or testing the wrong tree.
- **Pre-edit git ops leak.** Anything done before the first Write/Edit runs in the shared
  start directory. A `git checkout` / `checkout -b` there mutates the real `main` checkout,
  and with several sessions sharing that one folder they race over its HEAD. The sandbox
  isolates *file writes*, not *git ref operations* done before isolation kicks in.

So we cannot lean on agent-view's automatic worktree as our per-issue workspace.

## 4. Candidate solution — commit handoff (to validate)

Stop treating the worktree as the durable thing. **The worktree is disposable scaffolding;
the durable thing is the commit on the issue's branch.** Each session builds its own
scaffold, stands on the previous session's commit, adds its own, and hands off the branch.

Per session:

1. Start in a fresh, disposable worktree (agent-view's own).
2. **Adopt the issue's branch** — fetch/check it out so the worktree holds every prior
   phase's commits.
3. Do the phase's work; commit.
4. **Push the branch** so the commit is durable — the worktree can then be swept with
   nothing lost.
5. **Record the durable handle** — the branch name (and, once it exists, the PR) — on the
   GitHub issue, so the next session knows what to adopt.

The branch (on origin) is the unbroken baton; worktrees appear, build one section, and
vanish. Every session is self-contained: it reads the issue, adopts the branch, works,
pushes — independent of where it ran or what came before.

```
issue #42:   phase 1 ──────────►  phase 2 ──────────►  phase 3 / merge
             fresh worktree       fresh worktree       fresh worktree
             do work              adopt branch         adopt branch
             push issue-42-       (prior commits       review, approve,
             branch, open PR      land), work, push    squash-merge, delete
               │ swept              │ swept
               ▼                    ▼
   ═══════ origin/issue-42-branch  (the baton) ═══════►  → merge → main
           A1 ───── A2 ──────────── A3 ─────────────────
```

Parallel issue #43 runs the same shape on its own branch; the two never share scaffolding
or a baton.

## Assumptions (deliberately relaxed for now)

- **Push is free.** The candidate assumes a session can push without friction. In reality
  push needs a YubiKey tap; that constraint is **relaxed on purpose** — prove a relaxed
  solution works first, then re-impose the human tap.
- **Keep the sandbox.** The candidate must preserve agent-view's file-write isolation; we
  do not disable worktree isolation to buy continuity.
