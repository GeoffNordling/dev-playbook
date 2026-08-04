---
name: commit
description: Commit staged work locally with a clean message. Use when the user asks to commit changes, or when a software factory skill needs to commit its work.
disable-model-invocation: false
model: sonnet
effort: low
argument-hint: "[fast] [amend]"
allowed-tools: Bash(git *)
---

# Commit

Commit locally without narration; speak up only when something is unexpected.

This skill commits and stops there. Pushing is a separate act with its own authority — see [git-authority](~/workspace/dev-playbook/software-factory/git-authority.md) — so don't fold a push into a commit request the user didn't make.

## Args: $ARGUMENTS

Space-separated, any order. Recognized keywords:

- `fast` — staging shortcut: `git add -A`, then build a one-line message from `git diff --cached --stat`.
- `amend` — commit verb: use `git commit --amend --no-edit` instead of a fresh commit. Keeps the prior message (including its existing Co-Authored-By line) exactly as it stands.
  - **Pre-flight: skip the amend if HEAD has been pushed.** Run `git branch -r --contains HEAD`. If it lists any remote branches, amending would rewrite pushed history and produce a diverged-remote error on the next push. Make a fresh commit instead (still apply the rest of the skill, including the `Co-Authored-By` line). After committing, tell the user: amend was downgraded to a fresh commit because HEAD was already on `<remote/branch>`.

`fast amend` is valid — fast governs staging, amend governs the commit verb. They compose.

### Without `fast` (default staging)

1. `git status` and `git diff --stat`
2. Stage the files carrying the work you did in this conversation, and leave the rest — other agents may own those changes
3. `git log --oneline -3` to match commit message style

## All modes

- Always stage `settings.json` changes — they are housekeeping
- Never commit `.env` files, credentials, or secrets
- For fresh commits (not `amend`), end the message with: `Co-Authored-By: Claude <noreply@anthropic.com>`
- Confirm with `git status`, then report whether the tree is clean or which files remain uncommitted.
