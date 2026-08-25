---
name: commit-off
description: Suspends committing for the rest of the session — finished work stays in the working tree so the user can review every diff before it lands.
disable-model-invocation: true
model: inherit
effort: low
---

# Commit Off

Until the user turns committing back on, finish each unit of work and run no
`git commit` — leave the changes in the working tree for review.

Acknowledge activation with exactly:

> Commits are off — everything stays in the working tree for your review.

## Turning committing back on

Any plain-language signal from the user counts — "commits back on",
"resume committing", "you can commit again". When it comes, acknowledge
with exactly:

> Natural committing is back on.

and resume committing as work completes.
