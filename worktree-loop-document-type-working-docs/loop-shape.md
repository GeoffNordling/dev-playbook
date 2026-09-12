---
type: General-Sheet
title: Loop Shape
description: Loop's contract shape — acts, checks, and a set of yield conditions, iterated — in prose, one screen of pseudocode, and the three tables every Loop collapses to
---

# Loop Shape

Acts, checks, and yields are Loop's contract shape
([Doc-Type](/doc-types/doc-type.md)): the form every Loop's contract
takes. A loop drives a state toward a target state by iteratively
taking prescribed actions and validating against prescribed standards.
This member is a draft, speculative per
[ROOT.md](/worktree-loop-document-type-working-docs/ROOT.md), written
to the pattern of
[Population and Rules](/doc-types/standard/contract-shape.md).

## The shape

- **Act.** A prescribed action: a pointer at a runbook, with a condition. The act reads the findings the
  last iteration's checks returned; that is how direction reaches it.
- **Check.** A prescribed standard: a pointer at `Standard.audit`, the
  auditors a card's audit cell locates, never the Standard document and
  never its gate, with a condition. A check returns
  findings, each naming a member and the rule it fails. Zero findings
  from every check is the target state, so no target is written.
- **Yield.** A programmed exit: a condition and a receiver, another
  loop or the user. The instance writes "yields when …". A yield is
  resumable: control comes back to the same point with the receiver's
  answer.
- **Condition.** What must hold for an act or check to fire, or for a
  yield to be taken. Runbook and Standard already name this part
  *condition*, an edge's and a rule's; Loop reuses the word rather than
  adding a third. A condition of `None` fires every iteration.

The composition rule: any number of acts and checks, ordered by the
iteration, and a set of yield conditions, unordered, the loop yielding
when any one is met. The grain is instance-level: every loop owns its
own acts, checks, and yields. The shape in pseudocode:

```python
class Loop(Object):
    """Acts, checks, and yields, iterated. Drives state, never binds it."""

    acts:   list[Act]               # any number, in iteration order
    checks: list[Check]             # any number, in iteration order
    yields: set[Yield]              # any number; yield when any is met

    location    = path == f"loops/{name}.md"
    frontmatter = type == "Loop"

    def drive(self, state, findings=()):
        while True:
            for act in self.acts:
                if act.condition(state):   state = act.runbook(state, findings)
            findings = [f for check in self.checks
                          if check.condition(state)
                          for f in check.standard.audit(state)]
            for y in self.yields:
                if y.condition(state, findings):
                    findings = yield_to(y.receiver, findings)   # resumes here


class Act:
    runbook:   Runbook              # a skill or an agent definition
    condition: Condition | None     # None fires every iteration

class Check:
    standard:  Standard             # composed as standard.audit; never its gate
    condition: Condition | None

class Yield:
    condition: str                  # "yields when …", English or code
    receiver:  Loop | User          # who takes control, and hands it back
```

## The graph

[Working in Loops](/docs/working-in-loops.md#a-loop-is-a-graph) says
every loop is a graph, and the graph form is the one used for
visualization, tracking, and resuming. The same shape drawn that way:
the three verbs are the nodes, the conditions are the edges.

```
        ┌───────────────────────────────────────────┐
        │                                 none met  │
        ▼                                           │
     ┌─────┐          ┌───────┐  findings  ┌────────┴─┐
     │ act ├─────────►│ check ├───────────►│  yield?  │
     └─────┘          └───────┘            └────┬─────┘
        ▲                                       │ a condition met
        │                                       ▼
        └────────────── resumes ─────────── receiver
```

The doc-type document carries both forms, the pseudocode for the
contract and the graph for the reader. An instance pivots to the graph:
its acts, checks, and yields drawn as nodes and edges, so the shape on
screen is the whole procedure and the position in it is data.

A loop carries no target field and no runtime: the checks are the
target, and whatever runs the loop, a workflow script, a skill, a
person at a terminal, is a JS file or a skill or a person, not a loop.

## The view

Every Loop in the tree collapses to rows of three relations, `acts`,
`checks`, and `yields`, in one file. `scripts/loopgen` writes the whole
tree to `doc-types/loop/loops.txt` and, with `--check`, fails on drift:

```
acts
loop                     act        runbook                     when
doc-type-system-checker  survey     doc-type-survey             —
doc-type-system-checker  ideate     doc-type-ideate             findings

checks
loop                     check         standard                       when
doc-type-system-checker  consistency   doc-types/verbs-and-composition —

yields
loop                     yield      when
doc-type-system-checker  round      every K rounds
```

Rows as the first instance might produce them; nothing generated yet.

The runbook and standard columns join on the existing `chains.txt` and
`standards.txt`, so the view may stitch a loop's full picture from the
other two views. Rows sort by loop, then act, check, or yield, so the
file diffs stably.

## Acronyms

None.
