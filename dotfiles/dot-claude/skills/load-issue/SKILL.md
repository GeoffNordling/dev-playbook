---
name: load-issue
description: Read a GitHub issue. Use when the user or invoking context asks to load, view, or read an issue by number or URL.
disable-model-invocation: false
model: opus
effort: low
argument-hint: "<issue-number-or-url> [--repo <owner/repo>]"
allowed-tools: Bash(gh issue view *)
---

# Load Issue

## Args: $ARGUMENTS

Run `gh issue view $ARGUMENTS`.
