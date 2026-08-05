---
name: commit-on
description: Opens this session's commit lane, which the git-authority hook otherwise keeps shut. Use when the user wants their commits to stop being denied for want of a grant.
disable-model-invocation: true
model: sonnet
effort: xhigh
---

# Commit On

The commit lane is open for the remainder of this session: a `git commit` will
no longer be refused for want of a grant. Type /commit-off to revoke it.

That changes what is *possible*, not what is *wanted*. Whether to commit after
any given unit of work is still the user's word, on whatever standing
instructions this session already carries — so keep stopping after each unit
unless the user has said to commit as you go.

The lane is opened by the harness-written marker this command leaves in the
transcript, which the git-authority hook reads — this text itself grants
nothing. See
[git-authority](~/workspace/dev-playbook/software-factory/git-authority.md).
