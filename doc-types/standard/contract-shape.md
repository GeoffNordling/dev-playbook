---
type: General-Sheet
title: Population and Rules
description: Standard's contract shape — one population and its rules, each a name, a condition, and a predicate — and the two tables every Standard collapses to
---

# Population and Rules

One population and its rules are Standard's contract shape
([Doc-Type](/doc-types/doc-type.md)): the form every Standard's
contract takes. A Standard binds one class of object, and each of its
rules is a predicate a reviewer or a lint checks against one member's
state at one moment.

## The shape

- **Population.** The one class of object the Standard binds, with its
  exclusions: `an authored document, except type: Reference and the
  paths in .prose-lint-exempt`. Every rule is a predicate over a member
  of this class.
- **Rule.** A name, a condition, and a predicate. The name is the
  rule's identity inside its Standard, the atom later tables join on.
  The predicate is the check, in English or in a lint; a reviewer
  citing it satisfies the axis.
- **Condition.** What must hold of a member for the rule to bind it,
  named as a subset of the population: `python`, for a rule that holds
  only in a repo with a `pyproject.toml`; `harness-loaded agent
  instructions`, for a rule over runbook and context files only. A
  rule with no condition binds every member. The word is Runbook's,
  where an edge's condition is what must hold for it to fire.

The composition rule: exactly one population, any number of rules,
unordered. A Standard is a collection, so its shape is a relation,
and the grain is instance-level: every Standard owns a distinct rule
set. The shape in pseudocode:

```python
class Standard(Object):
    """One population and its rules. Binds state, never process."""

    population: ObjectClass         # one class, exclusions included
    rules: set[Rule]                # any number, unordered

    # rules: each a predicate over one Standard's state
    location    = path == f"standards/{card}/{name}.md"     # under its card's directory
    frontmatter = type == "Standard" and population is not None


class Rule:
    name:      str                  # unique within its Standard
    condition: Condition | None     # a named subset of the population; None binds every member
    predicate: str                  # English or a lint, checked against one member at one moment
```

A Standard carries no pointer to its card and no rationale field: the
path names the card, and rationale is another document's thing
([System Legibility](/docs/system-legibility.md#standing-principles)).

## The view

Every Standard in the tree collapses to rows of two relations,
`standards` and `rules`, in one file. `scripts/rulegen` writes the whole
tree to `doc-types/standard/standards.txt` and, with `--check`, fails on
drift:

```
standards
card   standard     population
build  skeleton     a repo's tracked tree
prose  conventions  an authored document, except type: Reference and the paths in .prose-lint-exempt

rules
card   standard     rule                           when
build  skeleton     pyproject-required             python
build  skeleton     readme-required                —
prose  conventions  declarative-present-tense      —
prose  conventions  imperative-and-second-person   harness-loaded-agent-instructions
```

Card and standard together key both tables, because a stem repeats
across cards: `standards/standard/consuming.md` and
`standards/semantic-validation/consuming.md`. The card column is the
path's first directory, never a pointer in the file. A rule with no
condition shows `—`. Rows sort by card, standard, then rule, so the
file diffs stably.

The view shows which rules exist, which Standard holds each, and which
card points at each Standard. Every other question is a grep. A third
table, rule to lint, joins on the rule column later, and drift is a set
difference.
