---
name: protocol
description: Load a protocol instruction for the current session
disable-model-invocation: true
model: opus
effort: high
argument-hint: "<protocol name>"
---

# Protocol

Load a protocol instruction for the current session.

## Input: $ARGUMENTS

Fuzzy protocol name — may be voice-dictated, title-cased, abbreviated,
or misspelled.

## Steps

1. Glob `~/workspace/idea-tree/protocols/*.instruction.md` to find
   available protocols.
2. Match `$ARGUMENTS` against filenames using case-insensitive word
   matching. If ambiguous or no match, list available protocols and ask.
3. Read the matched `.instruction.md` file.
4. Confirm which protocol was loaded with a one-sentence summary.
