---
name: commit-sonnet
description: Commit staged work with a clean message and push it, on Sonnet. Use when committing frequently on a long run, such as once per iteration of a loop.
disable-model-invocation: false
model: sonnet
effort: low
arguments: [target]
allowed-tools: Bash(git *), Read, Edit
---

# Commit

{Read [commit.md](~/.claude/skills/commit-inherit/references/commit.md)}
and follow it, with these two additions:

- **Staging.** Stage only the files carrying the work you did in this
  conversation. Leave any change you don't recognize — other agents may
  own it.
- **Push.** A commit isn't done until it's on origin: after committing,
  `git push`. {Report that the push landed}.
