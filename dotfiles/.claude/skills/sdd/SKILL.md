---
name: sdd
description: Dispatch SDD work to the correct phase skill based on the issue's phase label. Use when advancing an SDD-mode issue, when invoking the SDD workflow on a specific issue number, or when continuing work on a partially-completed SDD issue regardless of phase.
disable-model-invocation: true
model: opus
effort: low
argument-hint: "<issue-number>"
---

# SDD Dispatcher

Reads the issue's `phase/*` label and invokes the matching phase skill. The phase skill performs worktree setup, runs its phase logic, bumps the label on success, and exits.

For the full workflow, label scheme, and worktree convention, see the [workflow standard](~/workspace/dev-playbook/standards/workflow.md).

## First steps

1. **Require an issue number.** If `$ARGUMENTS` is empty, stop and tell the user to invoke with an issue number (e.g., `/sdd 18`).
2. Run `gh-show $ARGUMENTS` to load the issue.
3. **Verify the `sdd` label.** If absent, refuse: "Issue #N is not SDD-mode. Work on it without the dispatcher — open the worktree and code directly."
4. **Read the `phase/*` label** and dispatch:

| Label | Invoke |
|---|---|
| `phase/spec` | sdd-spec |
| `phase/design` | sdd-design |
| `phase/build` | sdd-tdd |
| `phase/review` | Refuse: "PR is open for #N. Review and merge from there." |
| (none) / `wontfix` | Refuse: "No active phase on #N." |

## Worktree resolution

Worktrees live at `.claude/worktrees/<issue#>-<slug>/`. Resolve by glob `.claude/worktrees/<N>-*`:

- Exactly one match → enter (`cd`).
- Zero matches → create per the [worktree convention](~/workspace/dev-playbook/standards/workflow.md#branch-and-worktree). The slug is the issue title, kebab-cased and truncated.
- Multiple matches → error and ask the user.

The phase skill inherits the worktree as its working directory.
