---
name: commit
description: Commit locally; user pushes
disable-model-invocation: true
effort: low
argument-hint: "[fast]"
allowed-tools: Bash(git *)
---

# Commit

Commit locally. Do not narrate — just do it. Only speak up if something is unexpected.

`git push` requires a YubiKey tap, so the user pushes. Do not run `git push` yourself.

## Mode: $0

### Normal (default)

1. `git status` and `git diff --stat`
2. Stage files related to the work you did in this conversation
3. Do NOT stage unrelated changes — other agents may own those
4. `git log --oneline -3` to match commit message style
5. Commit with a concise message
6. Tell the user to push.

### Fast

1. `git add -A`
2. `git diff --cached --stat` to build a one-line commit message
3. Commit
4. Tell the user to push.

## All Modes

- Always stage `settings.json` changes — these are housekeeping, always include them
- Never commit `.env` files, credentials, or secrets
- End the commit message with: `Co-Authored-By: Claude <noreply@anthropic.com>`
- Report whether the working tree is clean or if any uncommitted files remain.
