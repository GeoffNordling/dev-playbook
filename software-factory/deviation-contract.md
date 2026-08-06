---
type: Guide
title: Deviation Contract
description: The contract a deviation runs under — the three limiters, escalation, and the deviation ledger
---

# Deviation Contract

What a build-region agent does when reality contradicts its brief. The
factory hands an agent a precisely-intended but incompletely-specified
mission, so contradictions are expected, not exceptional: the agent deviates
inside the guardrails below, and every deviation is visible afterward.

A **deviation** is any change the brief, read plainly, did not call for:
reality contradicted one of the brief's claims, or the specified change does
not fit what is actually there.

## The three deviation limiters

Before self-servicing a fix, the **implementing agent itself** answers three
yes/no questions:

1. Does the fix change an acceptance criterion of the issue?
2. Does the fix touch a surface the brief declared out of scope?
3. Does the fix contradict a decision recorded on the issue, PR, an epic's
   standing rulings, or a map?

Three no's — make the fix and log it in the deviation ledger. Any yes —
escalate. **An answer the agent cannot give cleanly counts as yes**:
ambiguity itself escalates. No separate checker audits the answers in
flight; the ledger plus PR review audit the agent's own rulings, so a bad
call becomes a review finding rather than a mid-flight stall.

## Escalation

On any yes: stop work, commit what is done so the branch holds it, and post
**one structured comment** — the deviation (brief said / reality is), which
limiter tripped, two or three fix options with a recommendation, and any
ledger entries already logged on this lap — to the PR if one exists,
otherwise to the issue — always the most current of the two. The human's
reply is the ruling: given as a comment, or spoken in the terminal and
transcribed onto the issue or PR by the session that received the
escalation, so it is always recorded. The brief body itself is never the
place — it is frozen, per
[the brief freeze](/standards/tracking/issue-authoring.md#the-brief-freeze).
Because the ruling lands on the issue or PR, limiter 3 automatically binds
every later deviation to it — escalations feed the limiter system.

## The deviation ledger

Every factory PR description carries a `## Deviation ledger` section. One
entry per deviation: *brief said / reality was / what was done / the three
limiter answers*. Written at PR-open, appended during rework. When there
were no deviations the section reads `No deviations.` explicitly — a
missing section is a checkable defect, never an ambiguous absence.

The entries originate with the building session — the only party that knows
them. On the lap that precedes the PR it records them on the issue at close;
the node that authors the PR description lifts them into the section. On a
rework lap, with the PR live, the builder appends to the section directly. A
lap that halts on an escalation never reaches its close, so its entries ride
the escalation comment instead.
