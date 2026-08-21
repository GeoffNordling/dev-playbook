---
type: Guide
title: Deviation Contract
description: The contract a deviation runs under — the three limiters, the halt-commit-escalate lane, the PR-callout lane, and the deviation ledger
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
2. Does the fix touch a surface the brief withheld — a path, module, or
   interface named under `Prohibited surfaces`, or an idea the brief put
   under `Out of scope`? The first half is mechanical: compare the file about
   to be edited against the path list, and no judgment is owed
   ([the two headings and the split between them](/standards/tracking/issue-authoring.md#the-build-leaf-brief-modedirect)).
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

The user's reply is the ruling, recorded as a comment on the issue or the
pull request — typed there by the user, or said at the terminal and posted by
the session that heard it. That comment is what limiter 3 reads, so every
later deviation binds to it automatically: escalations feed the limiter
system. The brief body itself is never the place — it is frozen, per
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
- **The Adjudicator** — any judgment call that fails the routing test of
  [the second lane](#the-pr-callout-lane) below.

The three-no's fix is in neither lane: it is made, logged in the ledger, and
the work goes on.

## The PR-callout lane

A second lane runs beside the one above: the decision is documented on the pull
request, and the traverse proceeds. It belongs to the **Adjudicator** alone —
no other node may take a call and carry on.

Four kinds of call ride it:

- **A ruling on a surfaced-decision finding** — a review that named a decision
  the user faces ("someone must decide whether this is safe") rather than a
  defect.
- **An overruling** — a finding judged wrong, or outside the jurisdiction of the
  review that wrote it.
- **A suggestion disposition** — every one of them
  ([review-contract.md](/software-factory/review-contract.md#suggestion-dispositions)).
- **Routing an out-of-scope real problem** — a genuine problem the pull request
  is not the place to fix goes to `## Deferred` with a stub behind it.

**The routing test.** A call rides this lane only when all three of these hold.
Any one of them failing — or an answer that cannot be given cleanly — is an
escalation instead, the same halt the limiters above produce:

1. It contradicts no decision recorded on the issue, the pull request, an epic's
   standing rulings, or a map.
2. Its whole effect is contained in the pull request, so declining the merge
   undoes it.
3. A confident recommendation exists.

Three questions, like the limiters above and for the same reason: a node with
more authority answers to the same discipline, not to less of it.

An escalation out of this lane is written nowhere on GitHub, exactly as above.
What is written on GitHub is the callout itself — a pull request comment, ending
in the attribution line every factory writer signs with — and the run's report
repeats it, so the decision is on the record twice over and in one place a
reader is already looking.

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
