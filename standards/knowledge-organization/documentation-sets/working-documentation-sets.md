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
([Document Types](/standards/knowledge-organization/document-types.md#type-names-a-registered-type)).
A member may also carry a type whose home is elsewhere, such as
`Guide`, before it moves there
([Guide lives under `guides/`](/standards/knowledge-organization/document-types.md#guide-lives-under-guides));
the form rules of that type do not bind it while it is in the set.

The work may split into **strands**, each one line of it with its own
worklist, held in one member or in one subdirectory with its own
`ROOT.md`. Below, `ROOT.md` is the nearest root above the member, and
the set is the whole tree, strands included.

> **Why.** The buckets are a menu,
> [one home per fact](/standards/knowledge-organization/documentation-sets/documentation-sets.md#one-home-per-fact)
> made navigable: a set uses the buckets its work needs, skips the
> rest, and coins its own where none fits, so a bucket a set does not
> use is no finding, and `Unfiled` catches what fits none of them. A
> term of the work is defined in a `ROOT.md` rather than in the repo's
> `CONTEXT.md` because it crosses no set while the work runs.

## A guess written as a guess

Every member of a working documentation set writes a guess as a guess,
and the set's `ROOT.md` declares the set speculative. This is the whole
exemption from
[every sentence in the present tense](/standards/prose/conventions.md#every-sentence-in-the-present-tense).

`knowledge-organization.a-guess-written-as-a-guess` · stochastic

## Every member reached from `ROOT.md`

Every `.md` file of a working documentation set other than an
`index.md` is reached from its `ROOT.md` by a chain of links between
files of the set. A link in an `index.md` is not part of a chain. The
`ROOT.md` of a file is the one in its own directory or the nearest
directory above; the `ROOT.md` of a strand is reached from the next
`ROOT.md` above it.

`knowledge-organization.every-member-reached-from-rootmd` · deterministic

> **Why.** The chain is a second structure over
> [an index in every directory](/standards/knowledge-organization/documentation-sets/documentation-sets.md#an-index-in-every-directory)'s
> tree of sets: an index lists a member, and only a link from the
> work's own members says where it sits in the work.

## One directory under `working-docs/`

Every directory directly under `working-docs/` has an `index.md` and a
`ROOT.md`. Every Markdown file under it has a lowercase kebab-case
name, such as `check-fixes.md`, except `index.md`, `ROOT.md`,
`README.md`, `PROMPT.md`, `SKILL.md`, and `CLAUDE.md`.

`knowledge-organization.one-directory-under-working-docs` · deterministic

> **Why.** The set is the one directory
> [an index in every directory](/standards/knowledge-organization/documentation-sets/documentation-sets.md#an-index-in-every-directory)
> makes, here named and placed.

## `working-docs/` holds only sets

`working-docs/` directly has `index.md`, directories, and no other
file.

`knowledge-organization.working-docs-holds-only-sets` · deterministic

> **Why.** `working-docs/` is a plain parent to the sets
> [an index in every directory](/standards/knowledge-organization/documentation-sets/documentation-sets.md#an-index-in-every-directory)
> makes.

## One list of items, state by section

In a working documentation set, every `ROOT.md` with no `ROOT.md` in
a directory below it has exactly one `## Planned` and one
`## Completed` section, and no other file of the set has either. Each
bullet directly under them starts with a bold name.

`knowledge-organization.one-list-of-items-state-by-section` · deterministic

> **Why.** An item's state is the section it sits in, and `Completed`
> is the one past state a member records
> ([current state and next steps only](/standards/prose/conventions.md#current-state-and-next-steps-only)).

## Every fact under a named bucket

Every fact in a member of a working documentation set sits under a named
section, its bucket, the
[one home per fact](/standards/knowledge-organization/documentation-sets/documentation-sets.md#one-home-per-fact)
inside the member, and a bucket holds facts of its own type
only; the section under the member's H1, which says what the member is
and what it is for, is exempt.

A bucket is one of the buckets below, or one the member coins where none
of them fits; material awaiting triage sits under `Unfiled`. The named
buckets:

- **Goal** — what the work is for.
- **Principles** — the judgment calls that guide choices.
- **Constraints** — the hard bounds the work operates under, distinct from
  principles.
- **Terms** — the terms the work coins
  ([A shared term in one `ROOT.md`](#a-shared-term-in-one-rootmd)).
- **Planned** and **Completed** — the worklist
  ([One list of items, state by section](#one-list-of-items-state-by-section)).
- **Unfiled** — material awaiting triage.

`knowledge-organization.every-fact-under-a-named-bucket` · stochastic

## A shared term in one `ROOT.md`

A term coined by the work and used in more than one member of a working
documentation set is defined in the `Terms` bucket of one `ROOT.md`: the
root of the smallest strand that holds every member using the term, and
the set's own root where the term crosses strands, in place of the entry
[crossing terms in CONTEXT.md](/standards/knowledge-organization/documentation-sets/documentation-sets.md#crossing-terms-in-contextmd)
puts in the repo's `CONTEXT.md`.

`knowledge-organization.a-shared-term-in-one-rootmd` · stochastic

## An `Acronyms` appendix in every member

Every member of a working documentation set ends with an `Acronyms`
appendix, holding a bare `None.` where the member uses no acronym, and
an acronym is defined in the appendix of the highest member that uses
it and in no other member's, in place of a definition above first use
([definition before first use](/standards/prose/conventions.md#definition-before-first-use)).

`knowledge-organization.an-acronyms-appendix-in-every-member` · stochastic
