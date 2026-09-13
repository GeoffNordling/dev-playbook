---
type: General-Sheet
title: Doc-Type
description: The doc-type kind — operations plus a composition rule, fixing a contract shape — and the doc-type build loop that produces one from a documentation family
---

# Doc-Type

A **doc-type** hands one documentation family a contract shape. A
repository's doc-types make up its documentation type system; doc-types
are built when their benefits justify the costs. Serves
[System Legibility](/docs/system-legibility.md).

## The kind

A doc-type is **operations** plus a **composition rule**. An
**instance** is one member of the family (one runbook, one standard,
one loop).

- An **operation** is an action instances of the family support
  (define, audit, enforce, adopt; read, write, do; etc.).
- The **composition rule** says how many operations an instance may
  carry and in what arrangement.

Those two fix a **shape**: the form every contract in the family
takes. A **contract** is the shape filled with instance detail.

```
family ──doc-type build loop──► doc-type = operations + composition rule
                                  │
                                  └──► shape ──filled per instance──► contract
```

An instance *has* a contract; it is not one. A doc-type may serve
more than one file kind of the
[document-type registry](/standards/knowledge-organization/document-types.md):
Runbook serves Skill and Agent definition, Standard serves
Standard-Card and Standard-Ruleset. The doc-type is the object; a kind
is a file the object is written across.

## Contract

A contract is the shape filled with one instance's detail: everything
about the instance that its shape carries, and so everything that can
be known of it without reading its body. Whatever the shape drops stays
in the body. For a runbook the contract is its chain, args in, results
out, effects in coarse order; for a standard, its four cells; for a
loop, its graph. A contract is a parsimonious collapse of the instance,
the instance's important functionality at the CLOA.

## Object

Every contract shape is written once as pseudocode, one screen, and
every class in that pseudocode extends `Object`, the base class of the
doc-type system. `Object` carries what every instance of every doc-type
has, its operations and a file at a path with frontmatter, and nothing
more:

```python
class Object:
    """The base of the doc-type system. Any class extending it is pseudocode of this system."""

    operations:  set[str]       # the doc-type's verbs; the composition rule says how each appears below
    location:    str            # the path rule its doc-type declares
    frontmatter: dict           # the keys its doc-type declares
```

Every subclass fills `operations` on its first line, so the verb list
is a literal line of each contract shape and the two views of a
doc-type, its verbs and its pseudocode, agree by construction.

The name marks scope. A class that extends `Object` is one view of this
system and must agree with every other class that does, across every
bundle; a class that does not is some other system's.

## Composition rule and machinery

The freer the composition rule, the deeper the machinery a shape
needs. For example, a rule of "one of each operation" yields a struct, and
headings suffice to hold it; a rule of "any number, coarsely
ordered" yields a chain, and the chain needs a grammar, a parser,
and a drift check.

## The doc-type build loop

The **doc-type build loop** produces a doc-type. Its **target** is what
one run makes predictable — a family, a corpus, a single artifact — and
the loop is an expectation-maximization procedure over that target:

- **E-step.** An agent re-expresses the target entirely in the
  current primitives. Whatever forces a drop to file-level detail is
  the **residual**.
- **M-step.** Propose a primitive refactor that shrink the residual. The user filters candidates on
  intuition; the model's job is to challenge the filter. The burden
  of proof sits with the model: the user's accept or reject needs no
  justification, and the model validates every accepted candidate
  for feasibility against the corpus.
- **Convergence** is the pandas standard
  ([System Legibility](/docs/system-legibility.md)): the primitives allow
  the user to efficiently predict the target's behavior while staying at
  the CLOA; the primitive count is minimal — good primitives are a
  simple codebook.

Before running the build loop on a target, interview the user on what they want to
understand about it: the CLOA is relative to the repository's purpose
and the user's preferences. Residuals are recorded in the doc-type's
residual ledger; the primitive set is refactored only when the
reduction is worth the change cost.

The build loop's first move on a repo is the **registry pass**:
enumerate every document kind from the repo's registries and rule each
one important to the type system or not. Unimportant kinds are declared
so and ignored; build-loop targets come from the important ones. The
registries make "every family accounted for" a checkable claim.

On a greenfield repo the build loop runs the same way, with conversation in
place of a corpus: the user and the AI talk through the repository's
intended functionality and the primitives come from the user's
imagination and intuition.

### Practices

What has worked while running the loop:

- **Pseudocode is a muscle, not a target.** Writing a kind as
  pseudocode forces precision where prose blurs: the fields, what they
  may hold, the rules over the object's own state. Stop one screen
  above the content; pseudocode that holds the markdown's rows has gone
  too deep.
- **Name the primitive first.** A kind that resists expression is made
  of one primitive it has not named yet. Name it, and the CLOA object
  follows.
- **Greenfield mindset.** The agent's tendency is to keep what it finds:
  today's headings, tables, and file boundaries. None of that is a
  constraint. What is preserved is what the rules mean and what the
  existing lints check; everything else is open. This needs saying
  repeatedly, because the tendency returns.
- **Borrow the abstraction that fits.** Some computer-science
  abstraction matches every family: a sequence, a relation, a tree, a
  graph. Which one is decided per kind, never by what worked last time.

## Layers and the primitive map

A **layer** is a rung where one run of the doc-type build loop
happened, and the build loop is layer-invariant: the same algorithm
runs at any rung, on whatever target that rung holds.

Adjacent runs join through the **primitive map**: one lower
expression per higher primitive, written to a stateful location.
One-to-one is the ideal and may not always be possible; the map is
what matters, because it lets the next run start from structure
that connects the levels.

```
layer N:    target artifact ──doc-type build loop──► primitives
                                                         ▲
                                                         │ the primitive map:
                                                         │ one lower expression
                                                         │ per higher primitive
layer N−1:  target artifact ──doc-type build loop──► primitives
```

The stack descends until a target stops being stochastic: the
bedrock of determinism
([System Legibility](/docs/system-legibility.md)). Below that
boundary the work is mostly choosing pre-existing tools.

## Acronyms

- **CLOA** — Correct Level of Abstraction.
- **EM** — Expectation-Maximization: the two-step statistical
  procedure that inspired the doc-type build loop.
