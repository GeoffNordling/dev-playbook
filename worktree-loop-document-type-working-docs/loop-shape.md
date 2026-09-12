---
type: General-Sheet
title: Loop Shape
description: Loop's contract shape — acts, checks, and a set of yield conditions, iterated — in prose, one screen of pseudocode, and the Mermaid graph every Loop is drawn as
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

- **Act.** A prescribed action: a pointer at a runbook, with a
  condition. The act reads the findings the last iteration's checks
  returned; that is how direction reaches it.
- **Check.** A prescribed standard: a pointer at `Standard.audit`, the
  auditors a card's audit cell locates, never the Standard document and
  never its gate, with a condition. A check returns findings, each
  naming a member and the rule it fails. Zero findings from every check
  is the target state. The target is written once, in the standards:
  an act reads a standard's definition to know what the target looks
  like, a check runs its audit to measure the distance.
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

A loop carries no target field and no runtime: the standards the
checks point at describe the target, and whatever runs the loop is the
substrate, not the loop.

## The view

The view is the graph itself. A loop instance's source of truth is a
fenced Mermaid block: its nodes are the acts, checks, and yields, its
edge labels the conditions, and GitHub renders it. Around the block
sit frontmatter, one paragraph saying what state the loop drives and
toward what, and three sections headed by the verbs, **Acts**,
**Checks**, **Yields**, each a list with one entry per node: the
node's id, the pointer the Mermaid label cannot carry (a runbook, a
`Standard.audit`), and the condition or the "yields when …" in full.

`scripts/loopgen --check` is a checker of the embedded graph, not an
extractor into a table: every node id in the Mermaid appears once under
the matching verb heading, every entry under a heading is a node in the
Mermaid, every pointer resolves, and the three-verb shape holds, acts
to checks, checks to yields, yields back or out. This is a different
kind of generator from `chaingen` and `rulegen`; peers share the
bundle, not the file format.

## Acronyms

None.
