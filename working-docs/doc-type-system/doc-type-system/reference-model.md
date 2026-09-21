---
type: General-Sheet
title: Reference Model
description: The doc-type system's target state as a reference model — five DocTypes, twelve verbs, the parts each composes, and how they fit, in pseudocode, then where each thing the picture has no place for goes
---

# Reference Model

The target state of the doc-type system, drawn as a reference model:
one picture of the system as it should be, in pseudocode. It is
speculative, per
[Doc-Type System](/working-docs/doc-type-system/doc-type-system/ROOT.md).
The Standard [Doc-Type](/standards/doc-type/doc-type.md) holds the
predicates that define the set this is one member of.

A markdown file is code in a fuzzy form, and the model that reads it
is its stochastic compiler. A doc-type gives such a file what code
has: structure, a contract, an API, and a type. The CLOA, the
correct level of abstraction, is a view of the system derived deterministically
from structure embedded in the files.

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
#             git history, scratch, the launch prompt, the rest of GitHub


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
        predicate: str            # everything between the heading and the trailer, the check whole; a stochastic rule's judge prompt
        condition: Condition | None   # None binds every member

    population: type[Target]      # frontmatter, one phrase naming the class and its exclusions
    rules: list[Rule]             # in file order


class Finding:                    # what a verifier returns for a member that fails a rule
    member: Target                # the thing that failed
    rule:   Standard.Rule         # the rule it failed


from doc_type import DocType, Id


class Explanation(DocType):
    """The Reasons for one document. Explains.
    In code, Reasons might sit inside the document they explain, but markdown is more rigid;
    in order to ensure a markdown file holds only one concern, we split Reasons into a 
    distinct Explanation object that gets its own file."""
    operations  = {explain}
    frontmatter = DocType.frontmatter | {type, title}

    class Reason:                 # a part: an H2; one design decision and the argument for it
        explains: set[Id]         # the trailer line; each id resolves to a part of `subject`, and a part may have no Reason
        why:      str             # everything between the heading and the trailer; never a predicate

    subject: DocType              # the document this explains, the file beside it, found by name
    reasons: list[Reason]         # in file order, and nothing else under the H1


from doc_type import DocType


class Guide(DocType):
    """What a reader needs before one kind of work: steps, calls, a checklist, a catalogue. Instructs.
    It links a Standard's rules as any document does and states none, so it carries no trailer."""
    operations  = {instruct}
    frontmatter = DocType.frontmatter | {type, title}


from doc_type import DocType
from runbook import Runbook
from standard import Finding, Standard


class Loop(DocType):
    """Acts, checks, and yields, iterated. Drives."""
    operations  = {act, check, yield}
    frontmatter = DocType.frontmatter | {type, title}

    class Act:
        runbook:   Runbook
        condition: str | None     # None fires every iteration
    class Check:
        standard:  Standard
        condition: str | None
        findings:  list[Finding]  # what the check returns; the next act and a yield read them
    class Yield:
        receiver:  "Loop | User"
        condition: str | None     # "yields when …"

    steps: list[Act | Check | Yield]   # in iteration order; a step whose condition holds fires
```

### The toolchain

```python
verifiers: dict[RuleId, Script | Judge]      # the one sync point: every rule id has a verifier
extractors: dict[type[DocType], Extractor]   # each encoding defines one: written form to rows
def audit(standard, state) -> list[Finding]  # parse the file, route each id, skip where the condition fails, collect failures
boundary: commit hook | make check | CI | a loop's check     # each names the rule ids it runs
```

Runbook is invoked, Standard is held to, Explanation explains, Guide
instructs, Loop drives. Twelve verbs across five DocTypes. A verb
belongs to a DocType only; a part has none.

## How they fit

```
Loop ─act───▶ Runbook ─do────▶ Runbook | Script
  │                   ─read──▶ Standard
  │                   ─write─▶ state
  ├─check─▶ audit(Standard) ─▶ Findings ─▶ the next act, or a yield
  └─yield─▶ User | Loop

Explanation ─explain──▶ Standard      the Reasons for its rules, in the file beside it
Guide       ─instruct─▶ User | Runbook   links a Standard's rules and states none

Gate = a boundary on the path to main that blocks on the findings of its audit
```

Audit and gate are the words of [CONTEXT.md](/CONTEXT.md#governance);
a loop's check audits and never gates.

A loop points at the other two and contains neither. Nothing points
at a loop except another loop's yield. A stochastic rule certifies at
a loop's check the same way a deterministic one does: zero findings.
Which rule ids run at a repo boundary is that boundary's wiring, not
the standard's.

## What goes where

What the picture has no place for, and where each thing goes:

- **Standard-Card and its four cells.** Define is the Standard files
  themselves, listed by the directory index. Audit is the verifier
  table. Enforce is each boundary's list of rule ids, read from
  config. Adopt is not a primitive; its pointers today are build's
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
- **Spec, Deviation, Predicate as objects.** A standard written for
  one run, a finding an act left standing, and the first paragraph of
  a rule.

## Acronyms

None.
