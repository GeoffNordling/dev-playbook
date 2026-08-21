---
type: Guide
title: Deviation Contract
description: The contract a deviation runs under — the three limiters, the halt-commit-escalate lane, and the deviation ledger
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

On any yes: **halt, commit, escalate.** Nothing about an escalation is
written to GitHub.

1. **Halt.** Stop work where it stands.
2. **Commit and push**, so the branch holds what is done. A halt reaches its
   commit even when the gates refuse it: the agent commits and pushes with
   `--no-verify`, and says on its terminal report that it did so. One
   server-side exception is accepted — a push touching `.github/workflows/`
   is refused by the token at the server, which `--no-verify` cannot bypass,
   so that halt's commit lands in the worktree only and the report says so.
3. **Escalate on the report envelope.** The deviation detail — brief said /
   reality is / two or three fix options with a recommendation — rides the
   envelope's `gist`, together with which limiter tripped. Ledger entries
   already logged on this lap stay in the ledger; the run's stdout and its
   transcript are where they surface until `factory-status` exists.

The user's reply is the ruling, given as a comment on the issue or the pull
request. That mechanism is the user's and is unchanged: because the ruling
lands there, limiter 3 automatically binds every later deviation to it —
escalations feed the limiter system. The brief body itself is never the
place — it is frozen, per
[the brief freeze](/standards/tracking/issue-authoring.md#the-brief-freeze).

## The halt-commit-escalate lane

The lane above stops the traverse. What puts a node in it differs by node:

- **The build node** — any limiter yes, or an answer it cannot give cleanly,
  plus the general stuck bucket: anything that leaves it genuinely unable to
  proceed. There is no taxonomy of stuck reasons to match against.
- **A review node** — operational failures only. A problem a review can
  describe is a finding, never an escalation
  ([review contract](/software-factory/review-contract.md#findings-are-not-escalations)).
- **The traverse script** — **relay, never absorb**. A node's own report text
  rides its ledger row unedited; the script never overrides an escalation,
  retries it, or fixes it itself, so a limiter trip always reaches the user.

The three-no's fix is in neither lane: it is made, logged in the ledger, and
the work goes on.

A second lane runs beside this one — the PR-callout lane, where a decision is
documented on the pull request and the traverse proceeds. It belongs to the
Adjudicator alone and arrives with
[issue #442](https://github.com/GeoffNordling/dev-playbook/issues/442).

## The deviation ledger

The `## Deviation ledger` section of a factory PR description is mandated by
[the merge-message recipe](/software-factory/factory-operations.md#the-merge-message-recipe),
which also fixes its empty marker. What goes in it is this contract's: one
entry per deviation — *brief said / reality was / what was done / the three
limiter answers* — written at PR-open, appended during rework.

The entries originate with the building session — the only party that knows
them. On the lap that precedes the PR it records them on the issue at close;
the node that authors the PR description lifts them into the section. On a
rework lap, with the PR live, the builder appends to the section directly. A
lap that halts on an escalation never reaches its close, so its entries ride
the escalating run's `gist` and stay in the ledger.
