---
name: commit-on
description: Authorizes autonomous commits for the rest of the session. Use when the user wants commits to land without a per-commit go-ahead.
disable-model-invocation: true
model: sonnet
effort: xhigh
---

# Commit On

Commits are authorized for the remainder of this session: when a unit of work
is complete, commit it via /commit without asking, unless the session's
standing instructions say to wait for the user's word per unit. Type
/commit-off to revoke.

The authorization is the harness-written marker this command leaves in the
transcript, which the git-authority hook reads — this text itself grants
nothing. See
[git-authority](~/workspace/dev-playbook/software-factory/git-authority.md).
