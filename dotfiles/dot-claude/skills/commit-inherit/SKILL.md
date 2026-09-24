---
name: commit-inherit
description: Commit staged work with a clean message and push it, on the session's own model. Use when committing infrequently, such as when the user asks for a commit or a unit of work ends.
disable-model-invocation: false
model: inherit
effort: low
arguments: [target]
allowed-tools: Bash(git *), Read, Edit
---

# Commit

{Read [commit.md](references/commit.md)} and follow it, with these two
additions:

- **Staging.** Stage only the files carrying the work you did in this
  conversation. Leave any change you don't recognize — other agents may
  own it.
- **Push.** A commit isn't done until it's on origin: after committing,
  `git push`. {Report that the push landed}.
