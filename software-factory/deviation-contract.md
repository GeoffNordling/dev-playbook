---
type: Guide
title: Deviation Contract
description: The contract a deviation runs under — the three limiters, the halt-commit-escalate lane, the PR-callout lane, and the deviation ledger
---

# Deviation Contract

What a build-region agent does when reality contradicts its brief. The
factory hands an agent a precisely-intended but incompletely-specified
mission, so contradictions are expected: the agent deviates inside the
guardrails below, and every deviation is visible afterward.

A **deviation** is any change the brief, read plainly, did not call for:
reality contradicted one of the brief's claims, or the specified change does
not fit what is actually there.

## The three deviation limiters

Before self-servicing a fix, the **implementing agent itself** answers three
yes/no questions:

1. Does the fix change an acceptance criterion of the issue?
2. Does the fix touch a surface the brief withheld — a path, module, or
   interface named under `Prohibited surfaces`, or an idea the brief put
   under `Out of scope`? The first half is mechanical: compare the file about
   to be edited against the path list, and no judgment is owed
   ([the two headings](/standards/tracking/issue-shapes.md#build-headings)).
3. Does the fix contradict a decision recorded on the issue, PR, an epic's
   standing rulings, or a map?

Three no's — make the fix and log it in the deviation ledger. Any yes —
escalate. **An answer the agent cannot give cleanly counts as yes** —
ambiguity escalates. The ledger plus PR review audit the agent's own
rulings after the fact, so a bad call becomes a review finding rather than
a mid-flight stall.

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

The user's reply is the ruling, recorded as a comment on the issue or the
pull request — typed there by the user, or said at the terminal and posted by
the session that heard it. That comment is what limiter 3 reads, so every
later deviation binds to it automatically. The brief body itself is never
the place: it is frozen from launch, and rulings live beside it.

## The halt-commit-escalate lane

The lane above stops the traverse. What puts a node in it differs by node:

- **The build node** — any limiter yes, or an answer it cannot give cleanly,
  plus the general stuck bucket: anything that leaves it genuinely unable to
  proceed. There is no taxonomy of stuck reasons to match against.
- **A review node** — operational failures only. A problem a review can
  describe is a finding, never an escalation
  ([review contract](/software-factory/review-contract.md#findings-are-not-escalations)).
- **The traverse script** — a node's own report text rides its ledger row
  unedited; the script never overrides an escalation, retries it, or fixes
  it itself, so a limiter trip always reaches the user.
- **The Adjudicator** — any judgment call that fails the routing test of
  [the second lane](#the-pr-callout-lane) below.

The three-no's fix is in neither lane: it is made, logged in the ledger, and
the work goes on.

## The PR-callout lane

A second lane runs beside the one above: the decision is documented on the
pull request, and the traverse proceeds. It belongs to the **Adjudicator**
alone.

Kinds of call that ride it:

- **A ruling on a surfaced-decision finding** — a review that named a decision
  the user faces ("someone must decide whether this is safe") rather than a
  defect.
- **An overruling** — a finding judged wrong, or outside the jurisdiction of the
  review that wrote it.
- **A suggestion disposition** — every one of them
  ([review-contract.md](/software-factory/review-contract.md#suggestion-dispositions)).
- **Routing an out-of-scope real problem** — a genuine problem the pull request
  is not the place to fix goes to `## Deferred` with a stub behind it.

**The routing test.** A call rides this lane only when each of these holds.
Any one of them failing — or an answer that cannot be given cleanly — is an
escalation instead, the same halt the limiters above produce:

1. It contradicts no decision recorded on the issue, the pull request, an epic's
   standing rulings, or a map.
2. Its whole effect is contained in the pull request and the deferral stubs
   this lane mints.
3. A confident recommendation exists.

Three questions, like the limiters above and for the same reason: a node with
more authority answers to the same discipline.

**Why question 2 names the stubs.** Declining the merge undoes everything this
lane wrote on the pull request, and that reversibility is what earns the lane
its authority. A deferral stub is the one thing it leaves standing outside —
a tracker entry that survives whether the pull request merges or not, and the
whole point of deferring rather than declining. So the stub is written into the
question as the sanctioned exception rather than left to contradict it: without
it, no deferral could pass a test every deferral must pass. Nothing else the
lane touches gets that license.

An escalation out of this lane is written nowhere on GitHub, exactly as above.
The call itself is always written somewhere a reader is already looking, and
which place that is depends on the kind. A ruling and an overruling have no
other home, so each is written as a pull request comment and repeated in the
run's report. A disposition and an out-of-scope routing already have one: the
suggestion's own thread carries the reply, and the pull request body's
`## Suggestion dispositions` and `## Deferred` sections carry the line and
the stub. Neither is repeated as a comment. Every one of them ends in the
attribution line every factory writer signs with.

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
