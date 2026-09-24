---
name: commit-sandbox
description: Commit work with a clean message and never push, for an agent sealed in a sandbox with no GitHub access. Use when committing inside a Sandcastle container, such as once per iteration of a stint.
disable-model-invocation: false
model: inherit
effort: low
allowed-tools: Bash(git *), Read, Edit
---

# Commit

{Read [commit.md](~/.claude/skills/commit-inherit/references/commit.md)}
and follow it. Commit to the branch checked out. Never push: the sandbox
has no GitHub access, and the host brings your commits out.
