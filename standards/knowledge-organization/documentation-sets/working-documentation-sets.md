---
type: Standard
title: Working Documentation Sets
description: What a working documentation set adds to Documentation Sets — a guess written as a guess, a link tree from ROOT.md, a directory per line of work under `working-docs/` and its strands, a worklist, buckets, terms held in ROOT.md, and an Acronyms appendix — each stated as the one difference against the general rule it qualifies
population: "a working documentation set, the Markdown files one stream of in-process work accumulates"
---

# Working Documentation Sets

A **working documentation set** is the
[documentation set](/standards/knowledge-organization/documentation-sets/documentation-sets.md)
one line of in-process work accumulates, plans, design notes, records,
kept as long as the work runs and drained into permanent homes or
deleted when it ends. Every rule of Documentation Sets and of
[Doc Conventions](/standards/prose/conventions.md) binds it; each section
below is the one difference the set adds, stated against the general rule
it qualifies, and a member is otherwise judged as any member is. A member
whose type is not yet settled carries `type: General-Sheet`
([Document Types](/standards/knowledge-organization/document-types.md#types)).

The work may split into **strands**, each one line of it with its own
worklist, held in one member or in one subdirectory with its own
`ROOT.md`. Below, `ROOT.md` is the nearest root above the member, and
the set is the whole tree, strands included.

> **Why.** The buckets are a menu,
> [one home](/standards/knowledge-organization/documentation-sets/documentation-sets.md#one-home)
> made navigable: a set uses the buckets its work needs, skips the
> rest, and coins its own where none fits, so a bucket a set does not
> use is no finding, and `Unfiled` catches what fits none of them. A
> term of the work is defined in a `ROOT.md` rather than in the repo's
> `CONTEXT.md` because it crosses no set while the work runs.

## Speculative voice

Every member of a working documentation set writes a guess as a guess,
and the set's `ROOT.md` declares the set speculative.

`knowledge-organization.speculative-voice` · stochastic

## The link tree

Every member of a working documentation set is reached from the set's
`ROOT.md` by a path of links, a second structure over
[an index in every directory](/standards/knowledge-organization/documentation-sets/documentation-sets.md#an-index-in-every-directory)'s
tree of sets. A row of an `index.md` that lists the member is not such a
link.

`knowledge-organization.the-link-tree` · deterministic

## Where a set lives

A working documentation set is one directory under `working-docs/` at
the repo root, `working-docs/<work>/`, holding the set's `index.md`, its
`ROOT.md`, and its members under lowercase kebab-case names, flat or in
subdirectories, except a member whose kind fixes its name (`README.md`,
`PROMPT.md`, `SKILL.md`, `CLAUDE.md`, a Python module).

`knowledge-organization.where-a-set-lives` · deterministic

## `working-docs/` holds only sets

`working-docs/` at the repo root, a plain parent to the sets
[an index in every directory](/standards/knowledge-organization/documentation-sets/documentation-sets.md#an-index-in-every-directory)
makes, holds its own `index.md` and the directories of the sets, and
nothing else.

`knowledge-organization.working-docs-holds-only-sets` · deterministic

## Worklist

The work of a working documentation set is one list of items, each item
a bold name and a body beneath it, and an item's state is the section it
sits in, `Planned` or `Completed`, the one past state a member records
([current state and next steps only](/standards/prose/conventions.md#current-state-and-next-steps-only)).
One `Planned` section and one `Completed` section sit together in one
file: the set's `ROOT.md`, or, where the work splits into strands, the
`ROOT.md` of each strand.

`knowledge-organization.worklist` · deterministic

## Buckets

Every fact in a member of a working documentation set sits under a named
section, its bucket, and a bucket holds facts of its own type only; the
section under the member's H1, which says what the member is and what it
is for, is exempt.

A bucket is one of the buckets below, or one the member coins where none
of them fits; material awaiting triage sits under `Unfiled`. The named
buckets:

- **Goal** — what the work is for.
- **Principles** — the judgment calls that guide choices.
- **Constraints** — the hard bounds the work operates under, distinct from
  principles.
- **Terms** — the terms the work coins ([Terms](#terms)).
- **Planned** and **Completed** — the worklist ([Worklist](#worklist)).
- **Unfiled** — material awaiting triage.

`knowledge-organization.buckets` · stochastic

## Terms

A term coined by the work and used in more than one member of a working
documentation set is defined in the `Terms` bucket of one `ROOT.md`: the
root of the smallest strand that holds every member using the term, and
the set's own root where the term crosses strands, in place of the entry
[terms that cross sets](/standards/knowledge-organization/documentation-sets/documentation-sets.md#terms-that-cross-sets)
puts in the repo's `CONTEXT.md`.

`knowledge-organization.terms` · stochastic

## Acronyms

Every member of a working documentation set ends with an `Acronyms`
appendix, holding a bare `None.` where the member uses no acronym, and
an acronym is defined in the appendix of the highest member that uses
it and in no other member's, in place of a definition above first use
([declare before use](/standards/prose/conventions.md#declare-before-use)).

`knowledge-organization.acronyms` · stochastic
