---
type: General-Sheet
title: Working in Loops
description: The doctrine — agents work in loops, and the user works on the loops
---

# Working in Loops

How we think about loops in the workspace.

## The goal

Computation is abundant and the user's attention is scarce. Loops
maximize the work done per unit of the user's attention.

The user delegates more of their own work to agentic loops, and tracks
every instantiated loop in one parsimonious place, so that all of them
stay legible at once. We strive for all repeatable work
to live in asynchronous loops.

The user should spend most of their time helping
build and improve loops. Loops run without the user.
Detectors catch slop before it bubbles up.

## Linear work

Linear work is one session: the user and one agent, one task at a time,
powering through. The user is in the loop on every turn, and the user's
turn is the most expensive resource there is, so linear work is the
least effective way to work. It built this repository, and the backlog
grew faster than the sessions drained it. The user has less free time and the models
are stronger every month; a way of working that spends the scarce
resource one result at a time does not survive that.

Linear work fails like this: a shape is defined and agents are
dispatched. The output comes back in the right shape and full of slop:
comments through the prose, claims the user cannot tell from inventions.
The user fixes it in the session, turn by turn. The fix is consumed
once, and the next dispatch makes the same slop.

## A loop

A **loop** is a worker pursuing a goal under constraints, with something
checking the work. The worker is a model or the user. The constraints
are a contract, the standards, and the detectors. The check is a
predicate, a reviewer, or the user.

```
until the goal is met:
    a worker takes the next step          a model, or the user
    the step obeys the constraints        the contract, the standards
    the work is checked                   a predicate, a reviewer, or the user
    a failed check goes back to the worker
    what nobody in the loop can judge is yielded
```

Who the worker is and who checks are the loop's two free choices, and
every kind of loop is one assignment of them. A linear session assigns
both to the user on every turn. A headless run assigns the worker to a
model and the check to a predicate.

The worker is told what the check looks for, because the worker cannot
see the check. The check reads the work's state after the step and
treats the worker's own report of what it did as feedback for the next
attempt. A check needs measurement, and measurement needs expression: a
property written as a programmable operation over the work's state. The
user leaves a loop at the moment the predicate that replaces the user is
written; a loop without that predicate still has the user in it.

A loop improves by error analysis: the user reads what the review caught
and the detectors missed, and the most common kind gets a detector.

Every loop has Claude Code as its innermost loop: the model plans, acts
through a tool, observes the result, and repeats until it has an answer
or runs out of turns.

## The autonomy scale

Every loop sits on one continuous scale: how much of its contract a
predicate checks instead of the user. At the left end is headless
operation, where every check is a predicate and the loop runs to its
exit without the user. At the right end is the linear session, where the
harness yields to the user every turn and the user is the only verifier.

```
 every check a predicate                            the user checks every turn
 ◄──────────────────────────────────────────────────────────────────────►
 headless run        review with a stop        design session        linear session
                                                            constructing a constraint

 ◄── more definition, more verifiers, smaller scope
                          inventing what future loops will be checked against ──►
```

Better definition and more verifiers move a loop left: a verifier can
be written only for work defined well enough to state a predicate over.
Scope is the lever, since a unit small enough to define is a unit a
predicate can check.

Constructing a constraint — a standard, a doc-type, a detector — sits
at the far right, because it invents the thing future predicates will
check. Every constraint built there moves other work left. The user's
time is spent at the right end, making things that move work to the
left.

The higher the risk or cost of a wrong decision, the more often a loop
yields, at any position on the scale.

## Yielding

Yielding is a property of every loop; the question is what a loop yields
to. A loop yields when its goal is met, and before that when a unit
needs judgment its predicates cannot give. It yields more often as the
risk or cost of a wrong decision rises.

A loop can yield to another loop: a model, which carries its own
responsibility and its own cost. Or a loop can yield to the user, who
holds the final responsibility and is the most expensive thing a loop
can yield to.

The agent cooks; the user checks back later. The user reads a run's
outputs and samples below them, as a scientist samples and a manager
checks in, and at the end of a run reads the diff. When the user does
not like the result, the user changes the loop — a contract, a detector,
a standard — and runs it again. The user does not fix the output by
hand, because that is linear work; their time is better spent improving
the loop.

## Work that repeats

A linear session is for work that does not repeat: a foundational
document, a decision. Work that repeats gets a loop. Whether work
repeats depends on the level one thinks at. One chunk of work is done
once. How that kind of work is done is written once and followed every
time. A check that the work was done that way runs every time. Ask the
question one level up, then one level again, until the repetition
shows.

```
 running the work and the check without the user   the loop        ◄── stop here
   ▲
 writing down a check that the work was done        the process
 the way it was written down
   ▲
 writing down how that kind of work is done         the contract
   ▲
 doing one chunk of work                            the work        ◄── start here
```

## A loop is a graph

Every loop is a graph: each branch of the body is a node, and each
choice of what runs next is an edge. The same loop, written both ways:

```
 loop                                        graph

 until the goal is met:                             ┌──────┐
     the worker takes a step              ┌────────►│ step │◄───────┐
     the work is checked                  │         └──┬───┘        │
     a failed check goes back             │            ▼            │
         to the worker                    │         ┌───────┐ fail  │
     what nobody can judge                │  yield ◄┤ check ├───────┘
         is yielded                       │  cannot └──┬────┘
                                          │  judge     │ pass
                                          │            ▼
                                          │       ┌───────────┐
                                          └──no───┤ goal met? │
                                                  └─────┬─────┘
                                                        │ yes
                                                        ▼
                                                      done
```

The graph form is the one used for visualization, tracking, and
communication, because the shape on screen is the whole procedure,
legible to a reader who knows the primitives. The position in the loop
becomes data, so a run can stop at a node, save its state, and resume
after a wait on the user that lasts days.

As the work behind a step grows more complex, the loop becomes worth
building; the graph the loop is drawn as does not grow with it. More
branches and more checks add nodes and edges, never a deeper nesting a
reader has to hold in their head.
