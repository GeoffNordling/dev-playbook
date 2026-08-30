---
name: commit-off
description: Suspends committing for the rest of the session — finished work stays in the working tree so the user can review every diff before it lands.
disable-model-invocation: true
model: inherit
effort: low
---

# Commit Off

Until the user turns committing back on, finish each unit of work and
{Never {Commit}} — leave the changes in the working tree for review.

Acknowledge activation with exactly:

> Commits are off — everything stays in the working tree for your review.

Then end the turn. Invoking this skill does not mean start or
continue work — wait for the user's next instruction.

## Commits remain off for the rest of the session until specifically turned back on

Only an explicit signal from the user turns automatic commits back on — "commit mode back on",
or similar language. In particular, invoking the `/commit` skill
does not count — the /commit skill gives permission to commit only once.

When the explicit signal comes, acknowledge with exactly:

> Natural committing is back on.

and resume committing as work completes.
