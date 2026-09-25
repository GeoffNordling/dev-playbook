---
type: General-Sheet
title: Acts, Verifications, and Yields
description: Loop's contract shape — acts, verifications, and yields, peers ordered by the graph, iterated to drive a workstream — in prose, and the graph every Loop is drawn as
---

# Acts, Verifications, and Yields

Acts, verifications, and yields are Loop's contract shape
([Doc-Type](/doc-types/doc-type.md)): the form every Loop's contract
takes. A loop drives a state toward a target state by iteratively
taking prescribed actions and validating against prescribed standards
([Loop](/doc-types/loop/definition.md)).

## The shape

- **Act.** A prescribed action: a pointer at a runbook, with a
  condition. The act reads the findings the verifications before it
  returned; that is how direction reaches it.
- **Verification.** Prescribed standards: a pointer at one or more
  Standards, with a condition. A verification runs the verifier of
  each of those Standards' rules, a check or a judge, and returns their findings,
  each naming a member and the rule it fails. Zero findings from every
  verification is the target state. The target is written once, in the
  standards, and a verification measures the distance to it.
- **Yield.** A programmed exit: a condition and a receiver, another
  loop or an External one, the user or a stint's principal, named in
  the instance. The instance writes "yields when …". A yield is
  resumable: control comes back to the same step with the receiver's
  answer.
- **Condition.** What must hold for a step to fire. Runbook and Standard already name this part
  *condition*, an edge's and a rule's; Loop reuses the word rather than
  adding a third. A condition of `None` fires every iteration.

The composition rule: any number of acts, verifications, and yields,
as peers. The graph orders them; a step whose condition holds fires,
and a yield that fires hands control out at its place in the graph.
The loop drives a workstream and names none: one loop drives many,
and each workstream's Stints records which loop drove it.

The shape as code, one module importing the base in
[Doc-Type](/doc-types/doc-type.md#the-base); the reference model holds
the same text whole and a test keeps them identical.

```python
from doc_type import DocType
from runbook import Runbook
from standard import Finding, Standard


class Loop(DocType):
    """Acts, verifications, and yields, iterated. Drives a workstream.
    Its instance draws the steps as a graph, and the graph carries their order."""
    operations  = {act, verify, yield, drive}
    frontmatter = DocType.frontmatter | {type, title}

    class Act:                    # a part: one step that runs a runbook
        runbook:   Runbook
        condition: str | None     # None fires every iteration
    class Verification:           # a part: one step that runs the verifiers of its standards
        standards: list[Standard] # one or more
        condition: str | None
        findings:  list[Finding]  # every standard's, together; the next act and a yield read them
    class Yield:                  # a part: one programmed exit
        receiver:  "Loop | External"   # External: the user, or a stint's principal, named in the instance
        condition: str | None     # "yields when …"

    acts:          list[Act]      # peers; the graph, not the list, orders them
    verifications: list[Verification]
    yields:        list[Yield]
    # no workstream: one loop drives many, and each workstream's Stints records which loop drove it
```

A loop carries no target field and no runtime: the standards the
verifications point at describe the target, and whatever runs the loop
is its driver, not the loop
([System Legibility](/docs/system-legibility.md#standing-principles)).

## The graph

[Working in Loops](/docs/working-in-loops.md#a-loop-is-a-graph) says
every loop is a graph, and the graph form is the one used for
visualization, tracking, and resuming. The same shape drawn that way:
the three verbs and the receiver are the nodes, the conditions are the
edges.

```mermaid
flowchart LR
    act[act] -->|condition| verify[verify]
    verify -->|findings| yield{yield?}
    yield -->|condition false| act
    yield -->|condition true| receiver([receiver])
    receiver -->|resumes| act
```

An instance pivots to the graph: its steps drawn as nodes and edges, so the shape on screen is the whole procedure and the
position in it is data.

## The view

The view is the graph itself. A Loop instance's source of truth is one
fenced Mermaid block, and GitHub renders it; there is no generated
file. That the graph and the prose around it agree is decided by
checks, as [the encoding](/doc-types/loop/encoding.md) lays out; the
peers share the bundle, not the file format.
