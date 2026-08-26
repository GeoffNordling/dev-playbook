---
name: working-doc-set-deslop
description: Send a working documentation set through an agent that audits it against the working-documentation-sets standard and then fixes the findings, leaving every edit uncommitted for diff review. Use when a set of working docs has drifted and should be cleaned up in one autonomous pass.
disable-model-invocation: false
model: sonnet
effort: high
arguments: [set-hint]
---

# Working Doc Set Deslop

Audit one working documentation set against
[Working Documentation Sets](~/workspace/dev-playbook/standards/knowledge-organization/working-documentation-sets.md)
and fix what the audit finds, editing in place and committing nothing.

## Target

`set-hint` may name the set: its root file, its directory, or a
description such as "the no-more-slop working files."

- If `set-hint` is absent, operate on the set most clearly in focus in
  the current conversation. Where none is, ask which.
- If `set-hint` is present, resolve it to a root file. Where it
  matches nothing, ask.

## Pre-flight

The target set must be committed and clean: run `git status` and confirm
no member carries uncommitted changes. Where one does, stop and tell the
user — the diff review that closes this skill only reads true against a
clean baseline.

## Dispatch

{Launch the [set-deslopper](~/.claude/agents/set-deslopper.md) subagent,
`model: opus`}, naming the working directory and the set's root file in
the prompt.

This skill never commits.

## Review

The subagent edits the set in place and replies with a minimal report of
what it did. Relay the report, then read the working-tree diff yourself —
every deletion is visible in it — and give the user your own view. The
user rules on the edit as a whole: accepted, commit; rejected, restore
the set's files to `HEAD`.
