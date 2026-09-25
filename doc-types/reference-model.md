---
type: General-Sheet
title: Reference Model
description: The doc-type system's target state as a reference model — five DocTypes, twelve verbs, the parts each composes, and how they fit, in pseudocode, then where each thing the picture has no place for goes
---

# Reference Model

The target state of the doc-type system, drawn as a reference model:
one picture of the system as it should be, in pseudocode. The
Standard [Doc-Type](/standards/doc-type/doc-type.md) holds the
predicates that define the set this is one member of. Where a choice
in the model is open, the one that keeps the doc-types parallel is
taken.

A markdown file is code in a fuzzy form, and the model that reads it
is its stochastic compiler. A doc-type gives such a file what code
has: structure, a contract, an API, and a type. The CLOA is a view of
the system derived deterministically from structure embedded in the
files.

## The system

The doc-types are the language; the toolchain is the code that
parses, verifies, and gates them. Both halves are the system.

### The language

```python
Verb = NewType("Verb", str)      # a verb is a string; the type says which strings
Id   = NewType("Id", str)        # the id of a part of a DocType, in the written form its DocType fixes


class DocType:
    """The base of the doc-type system. A class extends it when its instance is one markdown file of that type.
    A part is a class nested inside its DocType: it does not extend DocType and has no verbs."""
    operations:  set[Verb]        # the doc-type's verbs
    frontmatter = {description}   # the keys every instance carries; a subclass adds its own


Target = DocType | File | Issue | PullRequest | External   # what an edge lands on
# File        a path in the repo with no doc-type: a script, an untyped document, data
# Issue       a GitHub issue; Issue Shapes holds a population of them
# PullRequest a GitHub pull request; the factory's contract is issue in, PR out
# External    the catch-all for whatever the doc-type system does not define:
#             git history, scratch, the launch prompt, the rest of GitHub,
#             the user, a stint's principal, a loop's driver


from doc_type import DocType, Target, Verb


class Runbook(DocType):
    """One invocable command. Invoked."""
    operations  = {read, write, do, override, accept, report}
    frontmatter = DocType.frontmatter | {name, model, effort}   # a skill also carries disable-model-invocation

    class Edge:                   # a part: lives only inside a Runbook
        operation: Verb           # one of the six above
        target:    Target | None  # None for accept and report: the signature, drawn at the root
        condition: str | None     # None fires always
        banned:    bool = False   # a write the runbook must never make

    chain: list[Edge]             # any number, coarsely ordered, rooted here


from doc_type import DocType, Id, Target

RuleId = NewType("RuleId", Id)   # build.tests-present


class Standard(DocType):
    """One population held to its rules. Held to."""
    operations  = {hold}
    frontmatter = DocType.frontmatter | {type, title, population}

    class Condition:              # a part: an H2 with no id and no trailer, written once and shared by the H3 rules under it
        scope: str                # its first paragraph: which members those rules bind

    class Rule:                   # a part: an H2, or an H3 under a condition
        id:        RuleId
        kind:      deterministic | stochastic
        predicate: str            # everything between the heading and the trailer, the rule whole; a stochastic rule's judge prompt
        condition: Condition | None   # None binds every member
        why:       str | None     # a block after the trailer, running to the next heading; never a predicate

    population: type[Target]      # frontmatter, one phrase naming the class and its exclusions
    rules: list[Rule]             # in file order
    why: str | None               # a block after the lead, before the first rule; the Standard's own reason, not any one rule's


class Finding:                    # what a verifier returns for a member that fails a rule
    member: Target                # the thing that failed
    rule:   Standard.Rule         # the rule it failed


from doc_type import DocType


class Guide(DocType):
    """What a reader needs before one kind of work: sequences of steps, and references. Instructs.
    It links a Standard's rules as any document does and states none, so it carries no trailer."""
    operations  = {instruct}
    frontmatter = DocType.frontmatter | {type, title}

    class Step:                   # a part: one item of a sequence's ordered list
        name: str                 # the item's leading bold run; the instruction after it is the body's

    class Sequence:               # a part: a heading whose section is one ordered list, numbered from one
        name:  str                # the heading's text
        steps: list[Step]         # in list order, one or more

    class Reference:              # a part: a heading whose section holds no ordered list; its body is opaque
        name:  str                # the heading's text, the whole of what the contract shows
        parts: list["Sequence | Reference"]   # the headings nested beneath it, in file order

    parts: list[Sequence | Reference]   # in file order; the names, read down, are the gist of the guide


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


from doc_type import DocType
from loop import Loop


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

    headings: list[Heading]       # in file order, each name at most once
    stints:   list[Stint]         # the planned stint first, if any, then the recorded ones, newest first

    # parent and children are derived from the directory, never written;
    # its Standard requires each child's head file be reached by links from its parent's
    @property
    def parent(self) -> "Workstream | None":
        """The head file in the nearest directory above; None at the top."""

    @property
    def children(self) -> list["Workstream"]:
        """The head files in the directories below, with no head file between."""
```

### The toolchain

```python
verifiers: dict[RuleId, Check | Judge]       # the one sync point: every rule id has a verifier
extractors: dict[type[DocType], Extractor]   # each encoding defines one: written form to rows
def verify(standard, state) -> list[Finding] # parse the file, route each id to its verifier, skip where the condition fails, collect failures
gate: pre-commit | pre-push | CI             # each runs the checks, never a judge
```

Runbook is invoked, Standard is held to, Guide instructs, Loop drives,
Workstream is driven. Twelve verbs across five DocTypes. A verb belongs to a DocType only; a
part has none.

## How they fit

```
Loop ─drive──▶ Workstream   each drive logged as a Stint under the workstream's Stints
  ├─act────▶ Runbook ─do────▶ Runbook | Script
  │                  ─read──▶ Standard
  │                  ─write─▶ state
  ├─verify─▶ verify(Standards) ─▶ Findings ─▶ the next act, or a yield
  └─yield──▶ Loop | External

Guide ─instruct─▶ User | Runbook   links a Standard's rules and states none

Gate = pre-commit, pre-push, or CI: blocks on the findings of the checks it runs
```

Verifier, check, judge, and gate are the words of
[CONTEXT.md](/CONTEXT.md#governance); a loop's verification runs
verifiers and never gates.

A loop points at Runbooks and Standards and contains neither. It
names no workstream, since one loop drives many; a workstream's Stints
names the loop of each stint, planned or recorded, and that link has
no verb. Another loop's yield is the other thing that points at a
loop. A stochastic rule certifies at
a loop's verification the same way a deterministic one does: zero
findings. Which checks run at a gate is that gate's wiring, not the
standard's.

## What goes where

What the picture has no place for, and where each thing goes:

- **Standard-Card and its four cells.** Define is the Standard files
  themselves, listed by the directory index. Audit is the verifiers,
  one per rule id. Enforce is the gates, each running the checks.
  Adopt is not a primitive; its pointers today are build's
  bootstrap guide and skill, a runbook that stays where it is and is
  reached from the directory index; harness's and modules's pointers,
  runbooks that were never adoptions and stay runbooks with no pointer
  from the standard; and `consuming.md`, a guide that stays a guide,
  listed by its directory index.
- **Ruleset as a second object.** There is one object; the Standard
  file holds the rules.
- **`args` and `never` as verbs.** `accept` is the verb for args; a
  ban is a polarity on a write edge.
- **`Object`.** Renamed `DocType`, which is what it was.
- **Working documentation set.** A workstream: a documentation set in
  a workstream's directory is its material.
- **`PLAN.md` and `PROGRESS.md`.** A stint's material, on its branch.
- **Spec, Deviation, Predicate as objects.** A standard written for
  one run, a finding an act left standing, and the first paragraph of
  a rule.

## Acronyms

- **CI** — Continuous Integration.
- **CLOA** — Correct Level Of Abstraction.
- **PR** — Pull Request.
