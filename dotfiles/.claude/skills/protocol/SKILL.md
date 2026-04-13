---
name: protocol
description: Load a protocol instruction for the current session
disable-model-invocation: true
model: opus
effort: high
---

# Protocol

Load a protocol instruction for the current session.

## Default protocol

When only one protocol exists, load it automatically without requiring
an argument. Currently hardcoded to:

`directed-workflow-faithful-projection`

When multiple protocols exist in the directory, remove this default and
require the user to specify which one (via `$ARGUMENTS`).

## Steps

1. Glob `~/workspace/idea-tree/protocols/*.instruction.md` to find
   available protocols.
2. If only one exists, or if `$ARGUMENTS` is empty, load the default.
   If `$ARGUMENTS` is provided, match it against filenames using
   case-insensitive word matching. If ambiguous or no match, list
   available protocols and ask.
3. Read the matched `.instruction.md` file **at HEAD**. Do not look at
   git history, prior commits, or older versions of the protocol. The
   current file is the authoritative instruction.
4. Confirm which protocol was loaded with a one-sentence summary.
