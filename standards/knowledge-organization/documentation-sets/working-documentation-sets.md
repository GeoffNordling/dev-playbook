---
type: Standard
title: Working Documentation Sets
description: What a working documentation set adds to Documentation Sets — a guess written as a guess, a link tree from ROOT.md, the branch directory, a worklist, buckets, terms held in ROOT.md, and an Acronyms appendix — each stated as the one difference against the general rule it qualifies
population: "a working documentation set, the Markdown files one stream of in-process work accumulates"
---

# Working Documentation Sets

A **working documentation set** is the
[documentation set](/standards/knowledge-organization/documentation-sets/documentation-sets.md)
one stream of in-process work accumulates on its branch, plans, design
notes, records, drained into permanent homes or deleted when the work
merges. Every rule of Documentation Sets and of
[Doc Conventions](/standards/prose/conventions.md) binds it; each section
below is the one difference the set adds, stated against the general rule
it qualifies, and a member is otherwise judged as any member is. A member
whose type is not yet settled carries `type: General-Sheet`
([Document Types](/standards/knowledge-organization/document-types.md#types)).

## Speculative voice

A member writes a guess as a guess and sets an open question beside its
topic; `ROOT.md` declares the set speculative, and the members inherit
it.

That is the whole exemption from
[declarative present tense](/standards/prose/conventions.md#declarative-present-tense).

## The link tree

Every member is reached from `ROOT.md`, the document the work started
from, by a path of links: a member links what it depends on, its parent,
its children, the sibling whose fact it defers to.

The tree a reader walks is the tree of sets
([an index in every directory](/standards/knowledge-organization/documentation-sets/documentation-sets.md#an-index-in-every-directory));
the link tree is the second structure, the one that says what depends on
what. `ROOT.md` need not link every member. A member no path from
`ROOT.md` reaches is an orphan, listed or not.

## Where a set lives

A set is one directory at the repo root, `<branch>-working-docs/`, named
for the branch the work runs on; it holds the set's `index.md`, its
`ROOT.md`, and its members under lowercase kebab-case names, and it
exists on that branch alone, drained into permanent homes or deleted
before the branch merges.

The directory is the one
[an index in every directory](/standards/knowledge-organization/documentation-sets/documentation-sets.md#an-index-in-every-directory)
makes a set, here named and placed. The branch `fix-index-drift` keeps
its set in `fix-index-drift-working-docs/`. `main` carries no such
directory, and a set under `docs/` is the defect: `docs/` holds
permanent documents.

## Worklist

Work is one list of items, each a bold name and a short body; an item's
state is which section it sits in, Planned or Completed, and a completed
item keeps its shape and moves.

Completed is the one past state a member records
([current state and next steps only](/standards/prose/conventions.md#current-state-and-next-steps-only)).
Put the pair where it makes sense: one for the whole set, or one per
strand where the work splits by level or by function. However it
splits, a strand has one Planned and one Completed, in one file.

## Buckets

A bucket is a named section role a fact type files under,
[one home](/standards/knowledge-organization/documentation-sets/documentation-sets.md#one-home)
made navigable; a set uses the buckets its work needs, skips the rest,
and coins its own where none fits.

An audit judges placement against the sections the set actually uses; a
bucket the set does not use is never a finding. The menu:

- **Goal** — what the work is for.
- **Principles** — the judgment calls that guide choices.
- **Constraints** — the hard bounds the work operates under, distinct from
  principles.
- **Terms** — see below.
- **Planned** and **Completed** — the worklist above.
- **Unfiled** — the escape valve: material fitting no bucket lands here
  explicitly, awaiting triage, instead of being force-fitted or scattered.

## Terms

A term coined by the work and used in more than one member is defined in
the Terms bucket of `ROOT.md`, in place of the entry
[terms defined once](/standards/knowledge-organization/documentation-sets/documentation-sets.md#terms-defined-once)
puts in the repo's `CONTEXT.md`.

`CONTEXT.md` holds the term that crosses sets
([project terms only](/standards/knowledge-organization/context-content.md#project-terms-only)),
and a term of the work crosses none until the set drains at merge; it
earns its entry when the member that carries it lands in a permanent
home and a second set uses it.

## Acronyms

Each member ends with an Acronyms appendix, bare `None.` where the
member uses none; an acronym is defined once in the set, in the appendix
of the highest member that uses it, and members below use it undefined.

The appendix is where a member declares its acronyms, in place of a
definition above first use
([declare before use](/standards/prose/conventions.md#declare-before-use)).
