---
name: load-issue
description: Load a GitHub issue body verbatim into the transcript. Use when a subsequent skill in this session needs the issue's acceptance criteria and out-of-scope clauses — e.g., before /code-review on a PR that closes an issue.
disable-model-invocation: false
model: opus
effort: low
argument-hint: "<issue-number> [--repo <owner/repo>]"
allowed-tools: Bash(gh issue view *)
---

# Load Issue

Print the issue body verbatim into the transcript so downstream skills in this session can reference its acceptance criteria and out-of-scope clauses. No analysis, no summary.

## Args: $ARGUMENTS

Issue number (required). Optional `--repo <owner/repo>` (defaults to current repo).

## Procedure

1. Run `gh issue view <n> [--repo <owner/repo>] --json number,title,body,labels,state`.
2. Print the result as a fenced JSON block, prefaced with one line: `Loaded issue #<n>: <title>`.
3. Stop.
