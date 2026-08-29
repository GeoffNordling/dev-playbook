---
type: Standard
title: Working Documentation Sets
description: How the in-process Markdown files of one work stream are organized as a set — root plan, member links, single-home facts, worklists, and local terms
---

# Working Documentation Sets

A **working documentation set** is the group of Markdown files one stream of
in-process work accumulates — plans, design notes, records — committed to the
repo and drained into permanent homes or deleted when the work merges. This
standard governs the set level: how the files relate to each other. What goes
inside each file is governed by
[Knowledge Organization](/standards/knowledge-organization.md) and
[Prose](/standards/prose.md), which an agent reads before it writes one.
Members typically carry `type: General-Sheet`, the registry's genre for a
working document whose type is not yet settled.

The `/working-doc-set-deslop` skill sends a set through an agent that
audits it against this standard and then fixes what the audit finds,
leaving every edit uncommitted for the user's diff review.

## Speculative voice

A working set records work in progress, so it is exempt from the prose
conventions'
[declarative present tense](/standards/prose/conventions.md#declarative-present-tense)
and
[current state and next steps only](/standards/prose/conventions.md#current-state-and-next-steps-only):
a guess is written as a guess, an open question sits beside its topic, and
Completed keeps what is done. The root declares the set works this way;
members inherit it.

## Shape

A set is a tree: one root file, and every other member reached from it by a
path of links.

- The root is the document the work started from — the plan holding the goal.
- A member links what it depends on: its parent, its children, the sibling
  whose fact it defers to. The root need not link every member.
- A working file no path from the root reaches is an orphan.

Links take the form
[Cross-References](/standards/knowledge-organization/cross-references.md)
gives them.

## Worklist

Work is one list of items, each a bold name and a short body. An item's state
is which section it sits in — Planned or Completed — and a completed item
keeps its shape and moves.

Put the lists where they make sense: one pair for the whole set, or a pair
per strand where the work splits by level or by function. However it splits,
a strand has one Planned and one Completed, in one file.

## One home per fact

Each fact, rule, and decision lives in exactly one member; every other
member links. This extends the prose conventions'
[one rule, one place](/standards/prose/conventions.md#one-rule-one-place)
across the set.

## Buckets

A bucket is a named section role a fact type files under — the single home
above, made navigable. The list below is a menu: a set uses the buckets its
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
root's terms bucket with a one-line definition.

## Acronyms

Each member ends with an Acronyms appendix — bare `None.` where the member
uses none. An acronym is defined once in the set, in the appendix of the
highest member that uses it; members below use it undefined.
