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
  exclusions: `an authored document, except type: Reference and the
  paths in .prose-lint-exempt`. Every rule is a predicate over a member
  of this class.
- **Rule.** An id, a kind, a predicate, and a condition. The id,
  `<name>.<slug>`, is the rule's identity, the atom the verifier and
  boundary tables join on. The kind is deterministic or stochastic. The
  predicate is the check whole: a reader with only that text can apply
  it, and for a stochastic rule it is the judge's prompt.
- **Condition.** What must hold of a member for the rule to bind it,
  named as a subset of the population: `python`, for a rule that holds
  only in a repo with a `pyproject.toml`; `harness-loaded agent
  instructions`, for a rule over runbook and context files only. A
  rule with no condition binds every member. The word is shared with
  Runbook, where an edge's condition is what must hold for it to fire,
  and with Loop, where it is what must hold for an act or check to
  fire.

The composition rule: exactly one population, any number of rules. A
Standard carries no pointer to a verifier or a gate, since the
verifier table and the boundary table hold those, keyed by rule id
([Detectors](/standards/standard/detectors.md)), and no rationale,
since the reasoning is the explanation beside it
([System Legibility](/docs/system-legibility.md#standing-principles)).

The shape as code, one module importing the base in
[Doc-Type](/doc-types/doc-type.md#the-base); the reference model holds
the same text whole and a test keeps them identical.

```python
from doc_type import DocType, Target

RuleId = NewType("RuleId", str)  # build.tests-present


class Standard(DocType):
    """One population held to its rules. Held to."""
    operations  = {hold}
    frontmatter = DocType.frontmatter | {type, title, population}

    class Rule:                   # a part: an H2, or an H3 under a condition
        id:        RuleId
        kind:      deterministic | stochastic
        predicate: str            # everything between the heading and the trailer, the check whole; a stochastic rule's judge prompt
        condition: "Rule | None"  # the rule this one is under; None binds every member

    population: type[Target]      # frontmatter, one phrase naming the class and its exclusions
    rules: list[Rule]             # in file order


class Finding:                    # what a verifier returns for a member that fails a rule
    member: Target                # the thing that failed
    rule:   Standard.Rule         # the rule it failed
```

