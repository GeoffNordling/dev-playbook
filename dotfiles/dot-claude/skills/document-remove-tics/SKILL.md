---
name: document-remove-tics
description: Send a Markdown document through an isolated subagent that strips the named slop tics, changing style but never content.
disable-model-invocation: true
model: sonnet
effort: high
arguments: [doc-hint]
---

# Document Remove Tics

Dispatch one or more Markdown documents to the `tics-remover` subagent, which
rewrites each so it says the same things without committing any of the tics
in [slop-tics.md](~/workspace/dev-playbook/standards/prose/slop-tics.md).

## Target

`doc-hint` identifies which document or documents to operate on.
A path, a partial path, a filename fragment, or a description such as "the
auth setup doc" all resolve.

- **Empty.** Operate on the Markdown document(s) most clearly in focus in the
  current conversation — typically what was just written or edited. Where
  nothing is clearly in focus, ask which file.
- **Non-empty.** Resolve the hint to one or more `.md` files. Where it
  matches none, ask.

## Dispatch

For each resolved target, {Launch the
[tics-remover](~/.claude/agents/tics-remover.md) subagent, `model: sonnet`},
naming the working directory and the target path in the prompt. Launch
one subagent per file; for more than one target, send all the launches
in a single message so they run in parallel — each file's rewrite is
independent of the others.

{Never {Commit}}.

## Review, then stay silent

The subagent edits the file in place and replies either `DONE` or, on a
problem, free text describing it.

- **It escalated.** Relay the problem to the user.
- **It replied `DONE`.** Read its diff yourself — you own the document's
  content, so check the edit the way you'd check your own work.
  - **Looks right.** Say nothing and go on with whatever you were doing.
  - **Changed something you didn't want.** Tell the user what changed and
    why you disagree, the same as any other edit you'd push back on.
