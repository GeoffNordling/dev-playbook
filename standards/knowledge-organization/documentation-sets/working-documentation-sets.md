---
type: Standard
title: Working Documentation Sets
description: The further rules the in-process Markdown files of one work stream obey as a set — speculative voice, the branch directory, the root plan every member is reached from, worklists, buckets, terms in the root, and acronyms
population: "a working documentation set, the Markdown files one stream of in-process work accumulates"
---

# Working Documentation Sets

A **working documentation set** is the group of Markdown files one stream of
in-process work accumulates, plans, design notes, records, committed to the
repo and drained into permanent homes or deleted when the work merges. It
is a
[documentation set](/standards/knowledge-organization/documentation-sets/documentation-sets.md),
so every rule there binds it; the rules below are the further rules of
in-process work. What goes inside each file is
[Knowledge Organization](/standards/knowledge-organization/card.md)'s and
[Prose](/standards/prose/card.md)'s, which an agent reads before it writes one.
Members typically carry `type: General-Sheet`, the registry's genre for a
working document whose type is not yet settled. The doc-set-deslop
skill enforces the rules on demand
([Knowledge Organization](/standards/knowledge-organization/card.md#enforce)).

## Speculative voice

The root declares the set speculative, and members inherit it: a guess
is written as a guess, and an open question sits beside its topic.

That is the whole exemption from the prose conventions'
[declarative present tense](/standards/prose/conventions.md#declarative-present-tense).
[Current state and next steps only](/standards/prose/conventions.md#current-state-and-next-steps-only)
still binds.

## Reached from the root

Every member is reached from the root, `ROOT.md`, by a path of links; the
root is the document the work started from, the plan holding the goal.

The index still lists every member
([Documentation Sets](/standards/knowledge-organization/documentation-sets/documentation-sets.md));
the link tree is the second structure, the one that says what depends on
what. A member links what it depends on: its parent, its children, the
sibling whose fact it defers to. The root need not link every member. A
member no path from the root reaches is an orphan, listed or not.

Links take the form
[Cross-References](/standards/knowledge-organization/cross-references.md)
gives them.

## Where a set lives

A set is one directory at the repo root, `<branch>-working-docs/`, named
for the branch the work runs on; it holds the set's `index.md`, its root
file `ROOT.md`, and its members under lowercase kebab-case names, and it
exists on that branch alone, drained into permanent homes or deleted
before the branch merges.

The branch `fix-index-drift` keeps its set in
`fix-index-drift-working-docs/`. `main` carries no such directory, and a
set under `docs/` is the defect: `docs/` holds permanent documents.

## Worklist

Work is one list of items, each a bold name and a short body. An item's state
is which section it sits in — Planned or Completed — and a completed item
keeps its shape and moves.

Put the lists where they make sense: one pair for the whole set, or a pair
per strand where the work splits by level or by function. However it splits,
a strand has one Planned and one Completed, in one file.

## Buckets

A bucket is a named section role a fact type files under —
[one home](/standards/knowledge-organization/documentation-sets/documentation-sets.md#one-home),
made navigable. The list below is a menu: a set uses the buckets its
work needs, skips the rest, and coins its own where none fits. An audit
judges placement against the sections the set actually uses; a bucket the set
does not use is never a finding.

- **Goal** — what the work is for.
- **Principles** — the judgment calls that guide choices.
- **Constraints** — the hard bounds the work operates under, distinct from
  principles.
- **Terms** — see below.
- **Planned** and **Completed** — the worklist above.
- **Unfiled** — the escape valve: material fitting no bucket lands here
  explicitly, awaiting triage, instead of being force-fitted or scattered.

## Terms

A term coined by the work and used in more than one member appears in the
root's Terms bucket with a one-line definition, in place of `CONTEXT.md`.

The set is drained at merge, so a term of the work is not yet the repo's
vocabulary; it reaches `CONTEXT.md` when the member that carries it lands
in a permanent home
([Terms defined once](/standards/knowledge-organization/documentation-sets/documentation-sets.md#terms-defined-once)).

## Acronyms

Each member ends with an Acronyms appendix — bare `None.` where the member
uses none. An acronym is defined once in the set, in the appendix of the
highest member that uses it; members below use it undefined.
