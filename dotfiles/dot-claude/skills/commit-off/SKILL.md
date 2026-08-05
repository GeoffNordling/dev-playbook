---
name: commit-off
description: Revokes the session's autonomous-commit authorization. Use when the user wants commits to stop until a fresh /commit-on.
disable-model-invocation: true
model: sonnet
effort: xhigh
---

# Commit Off

Autonomous commits are revoked from this point in the session: do not run
`git commit` again unless the user types /commit-on anew — the git-authority
hook honors whichever marker is later in the transcript.

The revocation is the harness-written marker this command leaves in the
transcript — this text itself decides nothing. See
[git-authority](~/workspace/dev-playbook/software-factory/git-authority.md).
