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

{Read [commit.md](references/commit.md)} and
{Read [host.md](references/host.md)}, and follow both.
