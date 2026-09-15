---
type: General-Sheet
title: Nodes and Edges
description: Runbook's contract shape — nodes joined by labeled edges, the Reference chain, rooted at one runbook — in prose, one screen of pseudocode, and the view every runbook collapses to
---

# Nodes and Edges

Nodes joined by labeled edges, the **Reference chain**, are Runbook's
contract shape ([Doc-Type](/doc-types/doc-type.md)): the form every
runbook's contract takes. A runbook is an invocable command written as
documentation ([Runbook](/doc-types/runbook/definition.md)).

## The shape

- **Node.** An abstraction an edge lands on: a Standard, an agent, a
  skill, a script, or an imported name such as GitHub or a file path.
- **Edge.** One of Runbook's operations, applied: a verb connecting the
  runbook to a node, rooted at the runbook whose text declares it.
- **Condition.** What must hold for an edge to fire; an edge with no
  condition fires always. The word is shared with Standard, where it is
  what must hold of a member for a rule to bind it, and with Loop,
  where it is what must hold for an act or check to fire.

The composition rule: any number of edges, coarsely ordered, rooted at
one runbook. The chain is the contract written down: the signature —
args in, reports out — plus the effects, in the coarse order they
fire. It is a collapse of the runbook's program: the fine-grained
sequencing it drops stays below the CLOA, in the instance's body. The
shape in pseudocode:

```python
class Runbook(Object):
    """One invocable command. Its chain is its contract, written as spans in its own prose."""

    operations = {read, write, do, override, never, args, report}   # one per Edge, below

    summary: str                        # frontmatter description
    args:    list[str]                  # frontmatter arguments, names only
    chain:   list[Edge]                 # any number, coarsely ordered, rooted here

    # rules: each a predicate over one runbook's state
    location    = path == f"skills/{name}/SKILL.md" or path == f"agents/{name}.md"
    frontmatter = name and description are present      # a Skill's or an Agent definition's; no type key
    rooted      = every edge in chain is declared in this file's own body   # no file describes another's behavior


class Edge:
    operation: read | write | do | override | never | args | report
    target:    Node | Bucket            # Bucket = git | GitHub | local file | scratch, for writes and targetless reads
    condition: str | None               # what must hold for the edge to fire; None fires always


class Node:
    name: str
    type: Standard | Agent | Skill | Script | None   # None is imported: named where the edge touches it
    data: dict                          # permission expression, model pin, verbatim
```

## Nodes

A node is an abstraction; every edge lands on one. Provenance
([System Legibility](/docs/system-legibility.md))
decides what the drawing shows. A declared abstraction is typed —
rendered `[name] Type` — and the type is a link to its own
declaration, per the table below. An imported abstraction — GitHub,
a file path, `str` — is named where the edge touches it and nothing
more: its contract lives outside this corpus.

| Type     | What chains do with it | How it runs | Where its declaration lives |
| -------- | ---------------------- | ----------- | --------------------------- |
| Standard | read                   | —           | The Standard doc-type ([Doc-Type System](/doc-types/doc-type-system.md)) |
| Agent    | do                     | fresh context, its own permissions — a subprocess | Its own Reference chain |
| Skill    | do                     | the calling context, the caller's permissions — in-process | Its own Reference chain |
| Script   | do                     | deterministic code via the shell | The code itself |

A node may also carry its permission expression and model pin as node
data, quoted verbatim in the harness's own syntax —
`allowed-tools: Bash(git *)`, `model: sonnet`, `effort: low` — never
paraphrased into prose. A script's own reads and writes hang under
its node.

## Edges

An edge is one of Runbook's operations, applied: a base verb
connecting the runbook to a node. A rendered chain inflects the verb
to the third person (`reads`, `writes`), and the encoding's span
keywords are its imperative form.

Edges live at the definition site: an edge belongs to the file whose
text declares it, and a chain is stitched by following do-edges into
each target's own declarations — no file describes another file's
behavior.

| Operation | The action | Detail |
| --------- | ---------- | ------ |
| read | consult | — |
| write | change state | target is one of four buckets — `git(commit, push)` |
| do | run a runbook or a script | — |
| override … with … | substitute a previous clause | — |
| never … | prohibit | wraps one write and flips it from action to ban |
| args | take the caller's input | by name — `friction` |
| report | give a result back to the caller | by name and type — `outcome: str` |

A write's target is one of four **buckets** — git, GitHub, local
file, scratch — plus an optional parenthetical hint, as in
`git(commit, push)`. The bucket list is fixed; the hint is a memory
aid, never a type. A read's target is a file, or one of two read
buckets when no on-disk target exists — GitHub for remote state, the
launch prompt for material the caller assigns at dispatch. A never
wraps one write; a git-bucket ban may also name `merge`, a verb that
exists only inside a prohibition.

This vocabulary is closed: the tables above are all of it. A new
operation, node type, or bucket is an edit here before its first
use; its written form is an edit to
[encoding.md](/doc-types/runbook/encoding.md).

Any edge may carry a **condition** — what must hold for it to fire.
A conditional edge draws dashed; an unconditional edge draws solid.
The condition never changes the edge's operation.

## The view

Every runbook collapses to its chain drawn as text: the runbook's node
at the root, one line per edge, the verb inflected and the target
named. `scripts/chaingen` writes every runbook's chain to
`doc-types/runbook/chains.txt` and, with `--check`, fails on drift:

```
[adjudicator] Agent · tools: Read, Bash, model: opus, effort: xhigh
  ├─reads───► review contract
  ├─reads───► GitHub    every thread on the pull request
  ├─writes──► GitHub    one reply, then the resolve
```

Rows of the generated file, excerpted. A conditional edge draws
dashed. The prose an edge was cut from stays below the collapse, in
the runbook.

## Acronyms

- **CLOA** — Correct Level of Abstraction.
