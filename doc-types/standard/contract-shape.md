---
type: General-Sheet
title: Population and Rules
description: Standard's contract shape — one population and its rules, each a predicate with an id and a kind, under a condition or none — in prose and as code
---

# Population and Rules

One population and its rules are Standard's contract shape
([Doc-Type](/doc-types/doc-type.md)): the form every Standard's
contract takes. A Standard describes a state; the population is the
class of object held to it, and each rule is one predicate a member is
checked against.

## The shape

- **Population.** The one class of object the Standard binds, with its
  exclusions: `an authored document, except type: Mirror and the
  paths in .prose-lint-exempt`. Every rule is a predicate over a member
  of this class.
- **Rule.** An id, a kind, a predicate, a condition or none, and a
  why or none. The id, `<name>.<slug>`, is the rule's identity, the
  atom a detector claims the rule by. The kind is
  deterministic or stochastic. The predicate is the check whole: a
  reader with only that text can apply it, and for a stochastic rule
  it is the judge's prompt. The why is the argument for the rule,
  never itself a predicate.
- **Condition.** A part a rule sits under: a heading with no id and
  no trailer, whose first paragraph names which members the rules
  under it bind, written once and shared by them: `python`, for the
  rules that hold only in a repo with a `pyproject.toml`; `harness-loaded
  agent instructions`, for the rules over runbook and context files
  only. A rule under no condition binds every member. The word is shared with
  Runbook, where an edge's condition is what must hold for it to fire,
  and with Loop, where it is what must hold for an act or check to
  fire.

The composition rule: exactly one population, any number of rules,
each under one condition or none. A Standard carries no pointer to a
verifier or a gate; a detector claims a rule by its id, and the wiring
says where the detector runs
([Detectors](/standards/standard/detectors.md)). A rule's why, and
the Standard's own, sit beside what they argue for, not in a
separate file.

The shape as code, one module importing the base in
[Doc-Type](/doc-types/doc-type.md#the-base); the reference model holds
the same text whole and a test keeps them identical.

```python
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
        why:       str | None     # a block after the trailer, running to the next heading; never a predicate

    population: type[Target]      # frontmatter, one phrase naming the class and its exclusions
    rules: list[Rule]             # in file order
    why: str | None               # a block after the lead, before the first rule; the Standard's own reason, not any one rule's


class Finding:                    # what a verifier returns for a member that fails a rule
    member: Target                # the thing that failed
    rule:   Standard.Rule         # the rule it failed
```

