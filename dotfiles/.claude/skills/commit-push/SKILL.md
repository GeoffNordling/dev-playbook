---
name: commit-push
description: "Commit and push. Normal mode: only files from current work. Fast mode (/commit-push fast): stage everything."
disable-model-invocation: true
---

# Commit-Push

Commit and push. Do not narrate — just do it. Only speak up if something is unexpected.

## Arguments

- No argument: **normal mode**
- `fast`: **fast mode**

## Normal Mode

1. `git status` and `git diff --stat`
2. Stage files related to the work you did in this conversation
3. Do NOT stage unrelated changes — other agents may own those
5. `git log --oneline -3` to match commit message style
6. Commit with a concise message, then push

## Fast Mode

1. `git add -A`
2. `git diff --cached --stat` to build a one-line commit message
3. Commit, then push

## Both Modes

- Always stage `settings.json` changes — these are housekeeping, always include them
- Never commit `.env` files, credentials, or secrets
- End the commit message with: `Co-Authored-By: Claude <noreply@anthropic.com>`
