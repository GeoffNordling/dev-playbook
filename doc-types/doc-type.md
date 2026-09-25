---
type: General-Sheet
title: Doc-Type
description: What a doc-type is in one sentence, where the theory of the doc-type system now lives, and the residual every built doc-type records
---

# Doc-Type

A **doc-type** hands one documentation family a contract shape: the
form every member of the family is read against, so a caller learns
what it needs without reading the body. An **instance** is one member
of the family, one runbook, one standard, one guide, one loop, one workstream. This repo's built doc-types, and what each directory holds,
are
[Doc-Type System](/doc-types/doc-type-system.md).

The whole system, what a doc-type is made of, its verbs, and its
parts, is drawn in [Reference Model](/doc-types/reference-model.md),
with its words in [CONTEXT.md](/CONTEXT.md#doc-types). The rules
every doc-type is held to are the Standard
[Doc-Type](/standards/doc-type/doc-type.md).

## The base

The pseudocode of the system is split the way code is: this block is
the base module, what more than one doc-type uses, and each doc-type's
`contract-shape.md` holds its own class and opens with the imports it
needs. The reference model holds the six blocks whole, in this order,
Runbook, Standard, Guide, Loop, Workstream, and
`tests/test_pseudocode_sync.py` fails when the texts differ
([Reference Model](/doc-types/reference-model.md#the-language)).

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
```

## The doc-type build loop

The procedure that produces a doc-type from a family: an agent
re-expresses the family in the current primitives, and whatever forces
a drop to file-level detail is the **residual**; the primitives are
refactored only when the reduction is worth the change cost. Residuals
are recorded in the doc-type's residual ledger, one entry per instance
that has one. The fact base child workstream plans to run it as a
Loop
([Planned](/workstreams/system/see/fact-base/WORKSTREAM.md#planned)).
