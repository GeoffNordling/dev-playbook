---
type: General-Sheet
title: Working in Loops
description: The doctrine — agents work in loops, and the user works on the loops
---

# Working in Loops

How work gets done in the workspace: agents work in loops, and the user
works on the loops. This sheet says what a loop is, where it sits relative
to the harness, where the user sits inside it, and how the user improves
it.

## The goal

Linear work — one session, the user and one agent, one task at a time,
powering through — is unsustainable. It built this repository, and the
backlog grew faster than the sessions drained it. The user has less free
time and the models are stronger every month; a way of working that spends
the scarce resource one result at a time does not survive that.

The user's time goes into loops, contracts, and detectors. A loop runs
without the user. A detector catches its class of slop before it bubbles up.

## Why linear work fails

A shape is defined and agents are dispatched. The output comes back in
the right shape and full of slop: comments through the prose, claims the
user cannot tell from inventions. The user fixes it in the loop, turn by
turn. The fix is consumed once, and the next dispatch makes the same
slop. The shape was a contract and the agents obeyed it; nothing
verified what the shape did not say.

## What a loop stands on

Improvement needs verification. Verification needs measurement.
Measurement needs expression: a property written as a programmable
operation over the object's state. Each layer stands on the one below.

Verification reads the object's state after the run and treats the
agent's own report of what it did as feedback for the next attempt. The user
leaves a loop at the moment the predicate that replaces the user is
written; a loop without that predicate still has the user in it.

## The harness is the innermost loop

Every loop in the workspace has Claude Code as its innermost loop: the
model plans, acts through a tool, observes the result, and repeats until
it has an answer or runs out of turns. The workspace writes no
model-and-tool loop of its own, because API billing is out of scope
([Headless Operation, Billing](/docs/headless.md#billing)).

A linear session yields: the loop suspends, the user types, and the
loop resumes with the same context. A headless run (`claude -p`) returns:
the process exits, its context is gone, and only stdout and the disk
survive.

## Loops

A **loop** is a named, registered procedure: it dispatches agents over a
population against a contract, verifies the output, and stops at an exit
condition. It runs without the user, and stops at the end or at a named
wait where the user decides.

In code, with `claude(prompt)` standing for one headless run that returns
its stdout:

```python
def batch(
    work_items: list[str],
    task: Callable[[str], str],
    ok: Callable[[str], bool],
    max_retries: int = 2,
) -> list[str]:
    """Run every item through the harness and return the ones that need the user."""
    parked: list[str] = []
    for work_item in work_items:
        prompt = task(work_item)
        for _ in range(max_retries):
            out = claude(prompt)
            if ok(work_item):
                break
            prompt += f"\n\nLast attempt failed verification:\n{out}"
        else:
            parked.append(work_item)
    return parked
```

The population is `work_items`, one independent unit of work each. The
contract is `task(work_item)`, the prompt, and it states what `ok` checks,
because the model cannot see
`ok`. Verification is `ok(work_item)`. The exit condition is the end of
`work_items`; `parked` is what the user reads.

Each `claude(prompt)` starts with an empty context, so the population can
be large.

A loop is described in markdown, so Loop is a doc-type; its shape is
found the way every doc-type's is, by running the loop on the family
([Doc-Type](/doc-types/doc-type.md)). The registry of loops is its
generated view — one place lists every loop.

## A loop is a graph

Every loop is a graph, and every graph is run by a loop. Written out, a
**node** is a function that reads and writes a shared state object and
returns either the next node or a stop; an **edge** is that returned
choice. Each branch of the loop body becomes a node, each `return` becomes
a stop, and the driver that walks the nodes is a `while`.

What the graph form buys: the position in the loop becomes data, so a run
can stop at a node, save the state, and resume later — which a wait on the
user needs, because the wait can be days. The diagram is derived from the
node table, so it cannot go stale. Fan-out and join are native.

The loop form is the debugging angle: one function, one stack, one
breakpoint. The graph form is the altitude angle: the shape on screen is
the whole procedure, legible to a reader who knows the primitives. The
graph form is the intended default, with the loop underneath it: agents
make the boilerplate cheap.

## Where a loop lives

The user is in the loop when the harness can yield the user a turn: a
linear session. A headless run cannot, so a loop that runs without the
user lives either inside the harness or outside it.

Inside the harness, the loop is prose in the task: the model executes it
by reading it, so a step can be skipped or the loop stopped early, and
its state is the context window. Outside the harness, the loop is code:
`claude -p` is one tool inside it, and the `for` terminates.

Whether the predicate can be written decides where a loop waits for the
user: a node that needs the user's judgment waits, and so does an
irreversible action. Whether the loop has to be code decides whether it
lives inside the harness or outside.

## The user's position

The user reads a run's outputs and looks below them often, as a
scientist samples and a manager checks in. Looking below is
what earns the claim of understanding. At the end of a run the user
reads the diff.

The agent cooks; the user checks back later. When the user does not
like the result, the user changes the loop — a contract, a detector, a
standard — and runs it again. The user does not fix the output by hand.
The aim is a flywheel of autonomy: user time is never spent on work a
loop could do.

A linear session is for work that does not repeat: a foundational
document, a decision. Work that repeats gets a loop.

Whether work repeats depends on the level one thinks at. This specific
document is written once, but many documents are written every week. Ask
the question one level up, then one level again, until the repetition
shows.

## How a loop improves

A loop improves by error analysis: the user reads what the review caught
and the detectors missed, and the most common kind gets a detector.
