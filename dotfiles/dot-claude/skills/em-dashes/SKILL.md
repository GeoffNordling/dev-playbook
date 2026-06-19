---
name: em-dashes
description: Replace em dashes with contextually appropriate punctuation
disable-model-invocation: true
model: opus
effort: xhigh
---

# Em Dashes

Replace every em dash in files changed during this session with the
contextually appropriate punctuation.

## Replacement rules

Claude tends to produce em dashes in two situations. Each has a different
correct replacement:

### Introducing or projecting

The em dash introduces what follows: a list, explanation, or elaboration.
Replace with a **colon**.

- "three options — X, Y, Z" → "three options: X, Y, Z"
- "the fix is simple — remove it" → "the fix is simple: remove it"

### Pausing or aside

The em dash creates a pause, parenthetical, or pivot in the sentence.
Replace with a **semicolon** or, when the clauses are truly independent
thoughts, a **period**.

- "this works today — it may break" → "this works today; it may break"
- "we shipped — users were happy" → "we shipped. Users were happy"

Paired em dashes acting as parentheses should become actual parentheses:

- "the module — now deprecated — should go" → "the module (now deprecated) should go"

## Workflow

1. Identify all files changed in the current session (staged, unstaged, and
   untracked files in the git working tree).
2. Read each file and locate every em dash (U+2014: `—`).
3. For each occurrence, read the surrounding sentence and apply the
   replacement rules above. Use your judgment; the rules are guidelines, not
   a mechanical mapping.
4. Edit the file in place using the Edit tool.
5. After all replacements, report a summary: how many em dashes were replaced,
   in which files, and what punctuation each became.
