---
name: commit-off
description: Suspends committing for the rest of the session — finished work stays in the working tree so the user can review every diff before it lands.
disable-model-invocation: true
model: inherit
effort: low
---

# Commit Off

The user wants to review every diff before it is committed. From now until
the user turns committing back on, finish each unit of work and stop with
the changes left uncommitted in the working tree — run no `git commit`.

Acknowledge activation with exactly:

> Commits are off — everything stays in the working tree for your review.

## Turning committing back on

Any plain-language signal from the user counts — "commits back on",
"resume committing", "you can commit again" — no fixed phrase required.
When it comes, acknowledge with exactly:

> Natural committing is back on.

and resume committing as work completes.
