---
name: commit
description: Commit staged work with a clean message, then push it. Use when the user asks to commit changes, or when a software factory skill needs to commit its work.
disable-model-invocation: false
model: sonnet
effort: low
arguments: [fast]
allowed-tools: Bash(git *)
---

# Commit

Commit and push without narration; speak up only when something is unexpected.

A commit isn't done until it's on origin: after committing, `git push`.

## Args

Recognized keyword:

- `fast` — staging shortcut: `git add -A`, then build a one-line message from `git diff --cached --stat`.

### Without `fast` (default staging)

1. `git status` and `git diff --stat`
2. Stage the files carrying the work you did in this conversation, and leave the rest — other agents may own those changes
3. `git log --oneline -3` to match commit message style

## All modes

- Always stage `settings.json` changes — they are housekeeping
- Never commit `.env` files, credentials, or secrets
- End the message with: `Co-Authored-By: Claude <noreply@anthropic.com>`
- Commit, then confirm with `git status`, then `git push`. {Report tree clean or which files remain uncommitted, and that the push landed}.
