---
type: General-Sheet
title: Reference Model
description: The doc-type system's target state as a reference model — three DocTypes, ten verbs, the parts each composes, and how they fit, in pseudocode
---

# Reference Model

The target state of the doc-type system, drawn as a reference model:
one picture of the system as it should be, in pseudocode. It is
speculative, per
[ROOT.md](/worktree-loop-document-type-working-docs/ROOT.md).
[Specification](/worktree-loop-document-type-working-docs/specification.md)
holds the predicates that define the set this is one member of.

A markdown file is code in a fuzzy form, and the model that reads it
is its stochastic compiler. A doc-type gives such a file what code
has: structure, a contract, an API, and a type. The CLOA, the
correct level of abstraction, is a view of the system derived deterministically
from structure embedded in the files.

## The system

The doc-types are the language; the toolchain is the code that
parses, verifies, gates, and views them. Both halves are the system.

### The language

```python
Verb   = NewType("Verb", str)    # a verb is a string; the type says which strings
RuleId = NewType("RuleId", str)  # build.tests-present


class DocType:
    """The base of the doc-type system. A class extends it when its instance is one markdown file of that type.
    A part is a class nested inside its DocType: it does not extend DocType and has no verbs."""
    operations:  set[Verb]       # the doc-type's verbs
    location:    str             # the path rule
    frontmatter: dict            # the keys


class Runbook(DocType):          # skills/<name>/SKILL.md, agents/<name>.md
    """One invocable command. Invoked."""
    operations = {read, write, do, override, accept, report}

    class Edge:                  # a part: lives only inside a Runbook
        operation: Verb          # one of the six above
        target:    Target | None # None for accept and report: the signature, drawn at the root
        condition: str | None    # None fires always
        banned:    bool = False  # a write the runbook must never make

    chain: list[Edge]            # any number, coarsely ordered, rooted here


class Standard(DocType):         # standards/<name>/<topic>.md
    """One population held to its rules. Held to."""
    operations = {hold}

    class Rule:                  # a part: an H2, or an H3 under a condition
        id:        RuleId
        kind:      deterministic | stochastic
        predicate: str           # first paragraph, the check whole; a stochastic rule's judge prompt
        condition: "Rule | None" # the rule this one is under; None binds every member

    population: type[Target]     # frontmatter, one phrase naming the class and its exclusions
    rules: list[Rule]            # in file order


class Loop(DocType):             # loops/<name>.md
    """Acts, checks, and yields, iterated. Drives."""
    operations = {act, check, yield}

    class Act:
        runbook:   Runbook
        condition: str | None    # None fires every iteration
    class Check:
        standard:  Standard
        condition: str | None
    class Yield:
        receiver:  "Loop | User"
        condition: str | None    # "yields when …"

    steps: list[Act | Check | Yield]   # in iteration order; a step whose condition holds fires


class Finding:                   # what a check returns; what an act and a yield read
    member: Target               # the thing that failed
    rule:   Standard.Rule        # the rule it failed


Target = DocType | File | Issue | PullRequest | External   # what an edge lands on
# File        a path in the repo with no doc-type: a script, an untyped document, data
# Issue       a GitHub issue; Issue Shapes holds a population of them
# PullRequest a GitHub pull request; the factory's contract is issue in, PR out
# External    the catch-all for whatever the doc-type system does not define:
#             git history, scratch, the launch prompt, the rest of GitHub
```

### The toolchain

```python
verifiers: dict[RuleId, Script | Judge]      # the one sync point: every rule id has a verifier
def audit(standard, state) -> list[Finding]  # parse the file, route each id, skip where the condition fails, collect failures
boundary: commit hook | make check | CI | a loop's check     # each names the rule ids it runs
views: chains.txt (runbook edges), rules.txt (rule id, kind, verifier, boundaries), a loop's own graph
```

Runbook is invoked, Standard is held to, Loop drives. Ten verbs
across three DocTypes. A verb belongs to a DocType only; a part has
none.

## How they fit

```
Loop ─act───▶ Runbook ─do────▶ Runbook | Script
  │                   ─read──▶ Standard
  │                   ─write─▶ state
  ├─check─▶ audit(Standard) ─▶ Findings ─▶ the next act, or a yield
  └─yield─▶ User | Loop

Gate = a boundary that runs audit on its rule ids and blocks on findings
```

A loop points at the other two and contains neither. Nothing points
at a loop except another loop's yield. A stochastic rule certifies at
a loop's check the same way a deterministic one does: zero findings.
Which rule ids run at a repo boundary is that boundary's wiring, not
the standard's.

## What goes where

What the picture has no place for, and where each thing goes:

- **Standard-Card and its four cells.** Define is the ruleset files
  themselves, listed by the directory index. Audit is the verifier
  table. Enforce is the boundary column of the rules view, read from
  config. Adopt is not a primitive; its pointers today are build's
  bootstrap guide and skill, a runbook that stays where it is and is
  reached from the directory index; harness's and modules's pointers,
  runbooks that were never adoptions and stay runbooks with no pointer
  from the standard; and `consuming.md`, a guide that stays a guide,
  listed by its directory index.
- **Ruleset as a second object.** The Standard file is the ruleset.
- **Condition as its own type.** A rule another rule is under.
- **`args` and `never` as verbs.** `accept` is the verb for args; a
  ban is a polarity on a write edge, drawn in the chain view as it is
  today.
- **`Object`.** Renamed `DocType`, which is what it was.
- **Spec, Deviation, Predicate as objects.** A standard written for
  one run, a finding an act left standing, and the first paragraph of
  a rule.

## Acronyms

- **CLOA** — Correct Level of Abstraction.
