---
name: doc-deslop
description: Bring documentation into line with the standards — one or more files, or a documentation set and every set nested under it — in passes from the widest reach to the narrowest, leaving every edit uncommitted for diff review.
disable-model-invocation: true
model: inherit
effort: high
arguments: [doc-hint, rule-filter]
---

# Doc Deslop

Judge documentation against the stochastic rules of the standards and
fix what the judges find, editing in place and committing nothing. The
judges only report; the repairers decide and edit; the session
dispatches the passes and reviews.

## Target

`doc-hint` names what to deslop: a path, a partial path, a directory,
its `index.md`, or a description such as "the auth setup doc".

- **A file, or several.** Each `.md` file the hint resolves to is a
  unit of the file pass.
- **A directory.** Resolve it to the directory whose `index.md` is a
  set's root
  ([Documentation Sets](~/workspace/dev-playbook/standards/knowledge-organization/documentation-sets/documentation-sets.md));
  the target is that set and every set nested under it, a tree of one
  set where it has none.
- **Empty.** The Markdown documents most clearly in focus in the
  conversation, typically what was just written or edited.

A hint that matches nothing, names two unrelated directories, or is
empty with nothing in focus stops the skill before anything runs: ask,
since a run is one target and one diff.

`rule-filter` is optional and names the rules to run, such as "slop
tics". Given one, each pass runs only the rules it names, and a pass
left with none is skipped.

## Pre-flight

A directory target must be committed and clean — the diff review that
closes this skill only reads true against a clean baseline. Run
`git status`; where a file under the target carries uncommitted
changes, commit them first. A file target may carry uncommitted
changes: {Read each target file} before dispatch, and the review
compares against what you read.

## The passes

A rule's reach is how far a judge reads to decide it, and a fix at a
wide reach moves content that a narrow fix would only polish, so the
passes run widest first. Each pass starts when the last one's edits are
on disk. A directory target runs all three; a file target runs the file
pass alone. The rules each pass judges are
[doc-repairer](~/.claude/agents/doc-repairer.md)'s. Any briefing the
user's invocation adds goes into every launch prompt verbatim.

1. **Tree.** {Launch [doc-repairer](~/.claude/agents/doc-repairer.md)
   as a fork subagent (`subagent_type: "fork"`)}, over the whole
   target: where each fact lives and where each term is defined,
   across sets. The fork inherits this conversation and the session
   model, and reads no agent definition on its own, so its prompt
   names the working directory, the tree pass, the target directory,
   the rule filter, and the instruction to read
   `~/.claude/agents/doc-repairer.md` and carry out its procedure.
2. **Set.** {Launch [doc-repairer](~/.claude/agents/doc-repairer.md)
   subagents in one message, one per set, the target's root set and
   every set nested under it at any depth, `model: opus`}: each set's
   index, membership, and concerns. Each prompt names the working
   directory, the set pass, the set's directory, and the rule filter.
3. **File.** {Launch [doc-repairer](~/.claude/agents/doc-repairer.md)
   subagents in one message, one per file, `model: sonnet`}: each
   document's prose, its content held fixed. Each prompt names the
   working directory, the file pass, the file, and the rule filter.
   The files are every Markdown member of every set in the target, or
   the target files themselves.

{Never {Commit}}.

## Review

Relay each pass's report, the tree pass first, then read the
working-tree diff yourself — every deletion is visible in it — and
give the user your own view. The user rules on the edit as a whole:
accepted, commit; rejected, restore the target's files to what they
were before the run.
