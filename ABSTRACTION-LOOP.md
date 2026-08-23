---
type: General-Sheet
title: The Abstraction Loop
description: Offshoot of the branch plan — constructing the noun-and-verb abstractions that make documentation understandable at the CLOA
---

# The Abstraction Loop

An offshoot of [NO-MORE-SLOP.md](/NO-MORE-SLOP.md), deleted when its results
merge back into that plan or the branch of ideas terminates. The same
speculative voice applies: a guess is written as a guess, and a sentence is
settled only when it says so.

## Goal

Construct the minimal set of abstractions that let the user understand what
a body of documentation does — anything from one file to one skill to the
whole software factory — without reading all of it.

## Premise

Documentation does things, because agents make things happen and an agent
is a collection of documentation plus a permission set. So a documentation
unit has an operational meaning — what reads it, when it fires, what
changes as a result — and an abstraction names that meaning at the CLOA.

## Abstraction shape

One noun carrying a small fixed verb set — an interface. Nouns describe;
verbs predict. Tentatively accepted rule: the operations are always verbs,
which is deterministic structure at the level of ideas.

The exemplar is the **Standard**: define, audit, enforce, adopt. Its top
level works — the user predicts every card's behavior from four verbs
without reading the rule prose or the scripts. Its bottom level does not —
opening one standard lands in a sprawl of markdown files and scripts. The
loop owes an answer at both levels.

## The loop

An expectation-maximization shape over a chosen target artifact:

- **E-step.** An agent re-expresses the target entirely in the current
  abstractions. Whatever forces a drop to file-level detail is the
  residual.
- **M-step.** Propose abstraction changes — add, merge, rename, delete —
  that shrink the residual. The user filters candidates on intuition; the
  model's job is to challenge the filter.
- **Convergence** is the pandas test: the user predicts the target's
  behavior without reading its bodies, and the abstraction count is
  minimal. Good abstractions are a codebook the corpus gets short in.

The bootstrap run is freeform — a discussion, with several branching
possibilities live in the same context window. Rigidity applies later, to
adopted abstractions: see the change-cost note under the code heuristic.

Candidate generation may run outside this context window — an agent reads
the target and returns candidates for filtering here — or inline; which
fits is not yet known.

Before looping on a target, interview the user on what they want to
understand about it. The CLOA is relative to the repository's purpose and
the user's wants, so without the interview the loop optimizes explanation
in the abstract.

## Constraints

- **Deterministic backpressure where it reaches.** A claim stated in an
  abstraction's terms is worth more when a lint can check it — "skill X
  references skills Y and Z" is grepable; "skill X is elegant" is not — so
  prefer lintable claims wherever a lint can reach, and accept that much
  of what the abstractions say will never be lintable.
- **User eyes.** The artifacts the loop produces must be easy for the
  user to read — everything before this point optimized for agent
  readers. An application of constrain to optimize understanding.
- **Types respected.** The loop keeps the stochastic/deterministic
  distinction and the document-type distinctions explicit.

## Heuristic: pivot to code

Documentation is a fuzzy, stochastic version of code. When the
documentation form of a problem is stuck, translate it to the code form,
solve it there, and port the analogy back.

One port is made: change cost. An adopted abstraction changes the
way a codebase does — renaming or replacing one is a refactor, a
significant investment, never a whim two weeks later. The CLOA change
discipline from the branch plan guards everyday operations against that
jitter; the bootstrap run, before anything is adopted, stays freeform.

## Abstractions so far

| Noun            | Verbs                         | Is                                                |
| --------------- | ------------------------------ | ------------------------------------------------- |
| Standard        | define, audit, enforce, adopt | A rule the workspace runs under                   |
| Agent           | do                            | Documentation that runs on its own permission set |
| Skill           | do                            | Documentation that runs on the session's permissions |
| Reference chain | —                              | A doc unit's references, declared, edge-labeled   |

- **Standard** is established and live. Its open problem: the top level is
  elegant and simple; the bottom level is a messy collection of
  non-user-readable documents and scripts.
- **Agent and Skill** get one verb, **do**, and no more, ever. Specificity
  comes from the verb being done, which a Standard defines — the deslopper
  does not "enforce," it does slop-tics.enforce. The two differ only in
  permission binding: an agent brings its own set, a skill runs on the
  session's. The steps inside a skill are that skill's program, file-level
  detail below the CLOA, never an interface.
- **Reference chain** carries its verbs on its edges: **does** (a
  Standard's verb, possibly via an agent) and **reads** (consulted, not
  done). The declaration is lintable against the actual links. Absorbs
  skills as signatures, OKF traces, and the OKF graph — one object seen
  from three angles.

## Targets

Chosen, in order: `document-deslop` (minimal, known cold — the
calibration run), `grill-with-docs` (mid-size — five skills and a
standard), `design` (the hub — eight skills and four docs, the chain least
likely to fit in the user's head).

The software factory is the graduation exercise, not a target yet: the
abandoned attempt to understand it whole failed because the factory is
only a collection of abstractions, and none of them had been constructed
yet.

### Run 1: document-deslop — zero residual

The chain, declared:

    document-deslop (Skill)  — does: slop-tics.enforce, via ↓
    └─ deslopper (Agent: Read, Write)
       ├─ does:  slop-tics.enforce
       ├─ reads: conventions.md
       └─ reads (conditional): writing-for-agents

One sentence carries the target: document-deslop is the enforce arm of the
Slop Tics Standard — a Skill that resolves a hint to files and dispatches
the deslopper Agent once per file. Everything else in the two files — the
one-pass write rule, the DONE protocol, the rewrite rules — is internals
below the CLOA, the pandas method body, and is not residual.

What the run bought: the **do**-only verb rule for Agent and Skill, and the
two edge labels. The enforce/consult distinction that first appeared as
residual dissolved into them — enforce is *does* the Standard's verb,
consult is merely *reads*.
