---
type: General-Sheet
title: Headings and Stints
description: Workstream's contract shape — a head file of peer headings picked from one menu, a ledger of stints, and a parent and children derived from the directory — in prose and as code
---

# Headings and Stints

Headings and stints are Workstream's contract shape
([Reference Model](/doc-types/reference-model.md)): the form every Workstream's
contract takes. A workstream holds one line of work
([Workstream](/doc-types/workstream/definition.md)), and what a reader
needs of it is the job as it stands: its ideas, its target state, and
its context, each under a heading of its own, and a ledger of the
stints that drove it.

## The shape

- **Heading.** One section of the head file, its name picked from one
  menu, [Headings from the registry](/standards/doc-type/workstream-conventions.md#headings-from-the-registry). Every heading is
  optional and all are peers; a workstream picks the ones its work
  needs. A heading's body is opaque to the contract, except Stints.
- **Stint.** One entry under Stints, a unit of accounting: one bounded
  spend of effort on this workstream, with the loop that drove it. The
  next stint is written before it runs, with its loop and its budget;
  a past stint is recorded with what it spent, its branch, and the
  user's verdict. A stint may name the rules it targets, rules of the
  workstream's [draft Standards](/CONTEXT.md#governance). Only a leaf
  workstream has stints. Stints does for spend what Planned and
  Completed do for work.
- **Parent and children.** Derived from the directory and never
  written. A workstream's parent is the head file in the nearest
  directory above; its children are the head files below with no head
  file between.
- **Pointers.** A heading's body points at any Target, any number of
  times. A stint points at one Loop, and at the rules it targets.

The composition rule: any number of headings in file order, each name
at most once; under Stints, the planned stint first, if any, then the
recorded ones, newest first. A workstream is driven: a loop drives it,
and it adds no verb of its own.

The shape as code, one module importing the base drawn in
[Reference Model](/doc-types/reference-model.md#the-language), which
holds the same text whole; a test keeps them identical.

```python
from doc_type import DocType
from loop import Loop
from standard import RuleId


class Workstream(DocType):
    """One line of work: the ideas, the target state, and the context of one job. Driven.
    Its instance is the head file WORKSTREAM.md; the rest of its directory is its material,
    and a subdirectory with a head file of its own is a child workstream."""
    operations  = set()           # driven, as a Standard is held to; it adds no verb
    frontmatter = DocType.frontmatter | {type, title}

    class Heading:                # a part: one H2, picked from the menu; every heading optional, all peers
        name: Goal | DoneWhen | Principles | Constraints | Terms | Settled | Open \
              | Planned | Completed | Stints | Unfiled | Acronyms
        body: str                 # opaque, but for Stints

    class Stint:                  # a part: one entry under Stints, a unit of accounting
        loop:    Loop             # the loop that drives, or will drive, the workstream
        budget:  str              # checkpoints × iterations, plus slack, to a hard limit
        spent:   str | None       # None for the planned stint
        branch:  str | None
        verdict: advance | accept | delete | None   # None until the user rules
        targets: list[RuleId]     # rules of the workstream's draft Standards; empty for a stint with none

    headings: list[Heading]       # in file order, each name at most once
    stints:   list[Stint]         # the planned stint first, if any, then the recorded ones, newest first;
                                  # a leaf only, since a loop advances a leaf workstream only

    # parent and children are derived from the directory, never written;
    # its Standard requires each child's head file be reached by links from its parent's
    @property
    def parent(self) -> "Workstream | None":
        """The head file in the nearest directory above; None at the top."""

    @property
    def children(self) -> list["Workstream"]:
        """The head files in the directories below, with no head file between."""
```

## Material and children

A workstream is its head file; the rest of its directory is its
material, documentation sets included, and no doc-type spans more than
one file. A subdirectory with a head file of its own is a child
workstream, with its own headings and its own stints. Nothing lists a
child: the directory is the one source, and the Standard over the head
file requires every child to be reached by links from its parent's
head file, so a reader following links finds each one.
