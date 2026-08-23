---
name: document-deslop
description: Send a Markdown document through an isolated subagent that strips the named slop tics, changing style but never content. Use when a document reads as slop, when asked to deslop or clean up the writing in a doc, or after generating a long document that has not been style-checked.
disable-model-invocation: false
model: sonnet
effort: high
argument-hint: "[doc-hint]"
---

# Document Deslop

Dispatch one or more Markdown documents to the `deslopper` subagent, which
rewrites each so it says the same things without committing any of the tics
in [slop-tics.md](/standards/prose/slop-tics.md).

## Target

`$ARGUMENTS` is a hint identifying which document or documents to operate on.
A path, a partial path, a filename fragment, or a description such as "the
auth setup doc" all resolve.

- **Empty.** Operate on the Markdown document(s) most clearly in focus in the
  current conversation — typically what was just written or edited. Where
  nothing is clearly in focus, ask which file.
- **Non-empty.** Resolve the hint to one or more `.md` files. Where it
  matches none, ask.

## Dispatch

For each resolved target, launch the `deslopper` subagent (Agent tool,
`subagent_type: deslopper`), naming the working directory and the target
path in the prompt. Launch one subagent per file; for more than one target,
send all the launches in a single message so they run in parallel — each
file's rewrite is independent of the others.

This skill never commits, and it runs no check on the result: the user reads
each diff and decides what to keep.

## Hand off the diff

For each target, report its path, `git diff --stat` line, and the tics the
subagent named as most recurrent. The user reads the diff in their IDE and
decides what to accept.
