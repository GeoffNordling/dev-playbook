---
name: document-deslop
description: Rewrite a Markdown document to remove the named slop tics, changing style but never content. Use when a document reads as slop, when asked to deslop or clean up the writing in a doc, or after generating a long document that has not been style-checked.
disable-model-invocation: false
model: sonnet
effort: high
argument-hint: "[doc-hint]"
---

# Document Deslop

Transform one Markdown document so that it says the same things without
committing any of the tics in
[slop-tics.md](/standards/prose/slop-tics.md). Conformance to the standard is
the goal. The result is usually shorter, but as a side effect not the objective.

## Target

`$ARGUMENTS` is a hint identifying which document to operate on. It need not
be a literal path — a path, a partial path, a filename fragment, or a
description such as "the auth setup doc" all resolve.

- **Empty.** Operate on the Markdown document most clearly in focus in the
  current conversation. Where no document is clearly in focus, ask which file.
- **Non-empty.** Resolve the hint to a single `.md` file. Where the hint
  matches zero or several files, ask.

The document must be committed and its working tree clean for that path. The
faithful-reader check below reads `git diff` against `HEAD`, so an
already-dirty file makes the check meaningless. Where the target carries
uncommitted changes, say so and stop.

## Transform

Read these first, and nothing else:
[slop-tics.md](/standards/prose/slop-tics.md),
[conventions.md](/standards/prose/conventions.md), and the target in full.

Where the target is an agent-facing instruction file — a skill, an agent
definition, a rule, or a `CLAUDE.md` — read
[writing-for-agents](/dotfiles/.agents/skills/writing-for-agents/SKILL.md) as
well. Read it to learn what the file is doing, so the rewrite does not break
it. It is not a standard to bring the target into line with: leave a
conformance gap where you find one. The job is the slop-tics and nothing else.

**One pass, one write.** Write the whole rewritten document in a single
`Write` call. Do not build it up through `Edit` calls, and do not inspect the
file while the rewrite is in progress. Then read the finished document back
in full and check it against the rules below.

The rules, in order of importance:

1. **Do not change the content.** Every fact, instruction, path, command,
   name, condition, ordering constraint, and cross-reference survives.
   Someone acting on the new document reaches the same result as someone
   acting on the old one. Invent nothing.
2. **Delete freely.** Prose matching a named tic carries nothing and goes
   without hesitation. An example is information when it is the only place a
   concrete value, command, or name appears — that one stays.
3. **Keep the frontmatter, the heading structure, and the document's Markdown
   conventions.** Heading text itself is rewritable.
4. **Match the file's existing wrap width.**

Leave the change uncommitted. This skill never commits.

## The faithful-reader check

Launch the `faithful-reader` subagent. Its prompt names the working
directory, the target path, and
[slop-tics.md](/standards/prose/slop-tics.md) as the standard the rewrite
followed.

It replies with a verdict line. Findings follow it only where it stalled.

## Hand off the diff

Report the target path, its `git diff --stat` line, and the verdict. Where the
verdict is `I STALLED`, the findings follow.

The change stays uncommitted so the user reads the diff in their IDE. They
decide what to accept. Stop there.
