---
name: commit
description: Commit staged work locally with a clean message; the user pushes. Use when the user asks to commit changes or invokes /commit, or when a workflow skill needs to commit its work via Skill(commit).
disable-model-invocation: false
model: sonnet
effort: low
argument-hint: "[fast] [amend]"
allowed-tools: Bash(git *)
---

# Commit

Commit locally. Do not narrate — just do it. Only speak up if something is unexpected.

`git push` requires a YubiKey tap, so the user pushes. Do not run `git push` yourself.

## Args: $ARGUMENTS

Space-separated, any order. Recognized keywords:

- `fast` — staging shortcut: `git add -A`, then build a one-line message from `git diff --cached --stat`.
- `amend` — commit verb: use `git commit --amend --no-edit` instead of a fresh commit. Keeps the prior message (including its existing Co-Authored-By line); do not rewrite it.
  - **Pre-flight: skip the amend if HEAD has been pushed.** Run `git branch -r --contains HEAD`. If it lists any remote branches, amending would rewrite pushed history and produce a diverged-remote error on the next push. Make a fresh commit instead (still apply the rest of the skill, including the `Co-Authored-By` line). After committing, tell the user: amend was downgraded to a fresh commit because HEAD was already on `<remote/branch>`.

`fast amend` is valid — fast governs staging, amend governs the commit verb. They compose.

### Without `fast` (default staging)

1. `git status` and `git diff --stat`
2. Stage files related to the work you did in this conversation
3. Do NOT stage unrelated changes — other agents may own those
4. `git log --oneline -3` to match commit message style

## All modes

- Always stage `settings.json` changes — these are housekeeping, always include them
- Never commit `.env` files, credentials, or secrets
- For fresh commits (not `amend`), end the message with: `Co-Authored-By: Claude <noreply@anthropic.com>`
- Confirm with `git status`, then report whether the tree is clean or which files remain uncommitted.
