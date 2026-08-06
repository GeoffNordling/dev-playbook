---
name: clean-up-branch-worktree
description: Prove a merged worktree branch is fully absorbed into main, then remove the worktree and its branch. Use when the PR has merged and the user asks to tear down the branch and its worktree.
disable-model-invocation: true
model: sonnet
effort: low
---

# Clean Up Branch and Worktree

Tear down the worktree this session created with `EnterWorktree`, after
its PR merged.

## Why the tools resist

Merges here are squash merges. A squash merge copies the branch's
*content* onto main as one new commit; the branch's own commits never
become ancestors of main. So every ancestry-based check calls the branch
unmerged — `git branch --merged main` lists nothing, `git branch -d`
refuses, and `ExitWorktree` refuses with `Worktree has N commits on
<branch>`.

None of that is evidence of a problem. Prove the work landed by
comparing **trees**, not history, then remove without hesitating.

## 1. Check for uncommitted work

From inside the worktree:

```
git status --porcelain
```

It must print nothing. Any output is uncommitted work — stop and show
the user.

## 2. Refresh `origin/main`

```
git fetch --prune origin
```

`--prune` also drops the remote-tracking refs for branches GitHub
auto-deleted at merge.

## 3. Prove the work is on main

```
git diff --stat origin/main HEAD
```

**Empty output is the green light.** The branch's tree and main's tree
are byte-identical, so removing the branch cannot lose anything. This is
the check that survives squash merge.

If it prints anything, main has moved on since the merge — or the work
never landed. Get the exact answer instead of guessing:

```
gh pr list --head <branch> --state merged --json number,headRefOid
git rev-parse HEAD
```

Same SHA in both: every commit on the branch is inside that merged PR,
so proceed. Different SHAs, or an empty PR list: **stop**, and show the
user both outputs.

## 4. Remove the worktree and branch — one call

```
ExitWorktree({action: "remove", discard_changes: true})
```

Pass `discard_changes: true` on the **first** call. Step 3 already is
the confirmation the tool asks for, so calling without it only earns the
refusal you know is coming.

This deletes the branch too — but only under the name `EnterWorktree`
created it with, `worktree-<name>`. Never rename a worktree branch
mid-session; a renamed branch is silently left behind.

## 5. Land clean

`ExitWorktree` has already returned the session to the main checkout.
Fast-forward it onto the main you fetched in step 2:

```
git merge --ff-only origin/main && git log --oneline -1
```

Report one line: worktree and branch removed, main at that commit.
