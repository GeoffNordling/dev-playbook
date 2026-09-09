---
name: doc-set-deslop
description: Audit a documentation set, or a set and its child sets, with Sonnet auditors each assigned a slice of the standards, then fix what they find, leaving every edit uncommitted for diff review.
disable-model-invocation: true
model: inherit
effort: high
arguments: [set-hint]
---

# Doc Set Deslop

Audit one documentation set, or a set and its child sets, against
the standards and fix what the audits find, editing in place and
committing nothing. The auditors only report; a fork of this session
decides and edits; the session dispatches and reviews.

## Target

The argument is a set hint: anything that plainly names one
documentation set, a directory, its `index.md`, a card's name. Resolve
it to the directory whose `index.md` is the set's root; the target is
that set and every child set nested under it
([Documentation Sets](~/workspace/dev-playbook/standards/knowledge-organization/documentation-sets/documentation-sets.md)).
A working set is the directory `<branch>-working-docs/` whose root is
`ROOT.md`
([where a set lives](~/workspace/dev-playbook/standards/knowledge-organization/documentation-sets/working-documentation-sets.md#where-a-set-lives)).
A hint that names two unrelated sets, or no hint at all, stops the
skill before anything runs: ask which set, since a run is one set and
one diff.

## Pre-flight

The target must be committed and clean — the diff review that closes
this skill only reads true against a clean baseline. Run `git status`;
where a file under the target carries uncommitted changes, commit them
first.

## Dispatch

Resolve the hint, then decide one thing: is the target one set, or a
set with child sets. That, with the paths, is all the fork needs.
{Launch [doc-set-deslopper](~/.claude/agents/doc-set-deslopper.md) as
a fork subagent (`subagent_type: "fork"`)}; the fork inherits this
conversation and the session model. A fork reads no agent definition
on its own, so construct its launch prompt from four things:

1. The working directory.
2. The target directory.
3. Whether the target is one set or a set with child sets, plus any
   briefing the user's invocation adds.
4. The instruction to read
   [doc-set-deslopper](~/.claude/agents/doc-set-deslopper.md)
   and carry out its procedure.

For example: "Working directory: `<worktree path>`. Target:
`<directory>`, one set. Read `~/.claude/agents/doc-set-deslopper.md`
and carry out its procedure."

{Never {Commit}}.

## Review

The fork edits in place and replies with its report. Relay the
report, then read the working-tree diff yourself — every deletion is
visible in it — and give the user your own view. The user rules on the edit as
a whole: accepted, commit; rejected, restore the target's files to
`HEAD`.
