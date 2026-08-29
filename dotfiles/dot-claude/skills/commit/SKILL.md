---
name: commit
description: Commit staged work with a clean message, then push it. Use when the user asks to commit changes, or when a software factory skill needs to commit its work.
disable-model-invocation: false
model: sonnet
effort: low
arguments: [fast, amend]
allowed-tools: Bash(git *)
---

# Commit

Commit and push without narration; speak up only when something is unexpected.

A commit isn't done until it's on origin: after committing, `git push`.

## Args

Space-separated, any order. Recognized keywords:

- `fast` — staging shortcut: `git add -A`, then build a one-line message from `git diff --cached --stat`.
- `amend` — commit verb: use `git commit --amend --no-edit` instead of a fresh commit. Keeps the prior message (including its existing Co-Authored-By line) exactly as it stands.
  - **Pre-flight: skip the amend if HEAD has been pushed.** Run `git branch -r --contains HEAD`. {If it lists any remote branches, {report that amend was downgraded to a fresh commit because HEAD was already on `<remote/branch>`} — amending would rewrite pushed history, so make a fresh commit instead (still apply the rest of the skill, including the `Co-Authored-By` line)}.

`fast amend` is valid — fast governs staging, amend governs the commit verb.

### Without `fast` (default staging)

1. `git status` and `git diff --stat`
2. Stage the files carrying the work you did in this conversation, and leave the rest — other agents may own those changes
3. `git log --oneline -3` to match commit message style

## All modes

- Always stage `settings.json` changes — they are housekeeping
- Never commit `.env` files, credentials, or secrets
- For fresh commits (not `amend`), end the message with: `Co-Authored-By: Claude <noreply@anthropic.com>`
- Commit, then confirm with `git status`, then `git push`. {Report tree clean or which files remain uncommitted, and that the push landed}.
