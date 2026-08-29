---
name: working-doc-set-deslop
description: Audit a working documentation set with agents each assigned a slice of the standards, then fix what they find, leaving every edit uncommitted for diff review.
disable-model-invocation: true
model: inherit
effort: high
arguments: [set-hint]
---

# Working Doc Set Deslop

Audit one working documentation set against the standards and fix what
the audits find, editing in place and committing nothing. The work runs
in a fork subagent; the session dispatches and reviews.

## Target

A set is a collection of working Markdown documents: one root file — the
plan the work started from — plus the files it links. Audit the set
`set-hint` names, or the one in focus in the conversation. Where neither
resolves to a root file, ask.

## Pre-flight

The target set must be committed and clean — the diff review that closes
this skill only reads true against a clean baseline. Run `git status`;
where a member carries uncommitted changes, commit them first.

## Dispatch

{Launch a fork subagent (`subagent_type: "fork"`) — it inherits this
conversation and the session model, the model that wrote the set}. A
fork reads no agent definition on its own, so construct its launch
prompt from three things:

1. The working directory.
2. The set's root file.
3. The instruction to read
   [working-doc-set-deslopper](~/.claude/agents/working-doc-set-deslopper.md)
   and carry out its procedure.

For example: "Working directory: `<worktree path>`. The set's root file
is `<root file path>`. Read `~/.claude/agents/working-doc-set-deslopper.md`
and carry out its procedure."

{Never {Commit}}.

## Review

The fork agent edits the set in place and replies with its report. Relay the
report, then read the working-tree diff yourself — every deletion is
visible in it — and give the user your own view. The user rules on the
edit as a whole: accepted, commit; rejected, restore the set's files to
`HEAD`.
