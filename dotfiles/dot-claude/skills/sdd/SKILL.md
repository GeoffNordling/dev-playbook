---
name: sdd
description: Dispatch SDD work to the correct phase skill based on the issue's phase label. Use when advancing an SDD-mode issue, when invoking the SDD workflow on a specific issue number, or when continuing work on a partially-completed SDD issue regardless of phase.
disable-model-invocation: true
model: opus
effort: low
argument-hint: "<issue-number>"
---

# SDD Dispatcher

Reads the issue's `phase/*` label, resolves the issue's worktree, and invokes the matching phase skill. The phase skill runs its phase logic in that worktree, bumps the label on success, and exits.

## First steps

1. **Read the [workflow standard](~/workspace/dev-playbook/standards/workflow.md).** It defines the label scheme, worktree convention, and PR mechanics this dispatcher and its phase skills implement.
2. **Run `pwd`.** The env header's CWD was captured before this skill ran. Trust `pwd`, not the header.
3. **Confirm local `main` is current.** Compare local and remote `main` SHAs:
   ```bash
   git rev-parse main
   gh api repos/{owner}/{repo}/branches/main --jq .commit.sha
   ```
   If they differ, stop and tell the user: "Local `main` is behind `origin/main` — `git pull` on `main` before starting the phase (YubiKey tap required; the agent does not hold the SSH credential)." Do not proceed until the user confirms.
4. **Require an issue number.** If `$ARGUMENTS` is empty, stop and tell the user to invoke with an issue number (e.g., `/sdd 18`).
5. Run `gh-show $ARGUMENTS` to load the issue.
6. **Verify the `sdd` label.** If absent, refuse: "Issue #<issue-number> is not SDD-mode. Work on it without the dispatcher — open the worktree and code directly."
7. **Read the `phase/*` label** and dispatch:

| Label | Invoke |
|---|---|
| `phase/requirements` | sdd-requirements |
| `phase/design` | sdd-design |
| `phase/build` | sdd-tdd |
| `phase/review` | Refuse: "PR is open for #<issue-number>. Review and merge from there." |
| (none) / `wontfix` | Refuse: "No active phase on #<issue-number>." |

## Worktree resolution

Resolve and enter the issue's worktree per [Branch and worktree](~/workspace/dev-playbook/standards/workflow.md#branch-and-worktree) in the workflow standard. The phase skill inherits the worktree as its working directory.
