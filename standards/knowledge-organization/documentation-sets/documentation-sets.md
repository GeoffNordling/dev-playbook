---
type: Standard-Ruleset
title: Documentation Sets
description: How the concept documents one index.md owns relate as a set — an index in every directory, a body inside its declared concern, every row inside the set, one home for every fact, distinct concerns, and terms defined once
population: "a documentation set, the concept documents one index.md owns, except a numbered Decision Record or a type: Reference mirror among them"
---

# Documentation Sets

A **documentation set** is the concept documents one `index.md` owns: the
documents in its directory. A subdirectory carries an `index.md` of its
own and is a set of its own, nested in the parent's. The index is
the set's root and its listing is the set's membership
([Indexes](/standards/knowledge-organization/indexes.md)); a link never
makes a file a member, since a link reaches any file in any set or repo
in the forms
[Cross-References](/standards/knowledge-organization/cross-references.md)
gives. A numbered
[Decision Record](/standards/decisions/records.md) is outside every rule
here, as it is outside Cross-References: a record frozen at merge
restates the context of its day and is never rewritten; so is a
`type: Reference` mirror, upstream text vendored verbatim and never
edited here. A member's **concern** is the one purpose its frontmatter
`description` states
([Document Types](/standards/knowledge-organization/document-types.md#description));
a set's concern is its index's introduction
([Indexes](/standards/knowledge-organization/indexes.md#the-introduction)).
The rules bind the set level, how the members relate to each other and
to their concerns; what one member holds is [Prose](/standards/prose/card.md)'s.
Every rule here reads one set: its index, its members, and the index one
level up and one level down. Two reach farther by their own text,
[one home](#one-home) into any set or repo and
[terms that cross sets](#terms-that-cross-sets) into the repo's
`CONTEXT.md`; a set is otherwise judged with no neighbour's body open.

## An index in every directory

A set's members sit in the directory of its `index.md`; every
subdirectory that holds a concept document, a numbered Decision Record
or a `type: Reference` mirror included, carries an `index.md` of its own
and is a child set.

`knowledge-organization.an-index-in-every-directory` · deterministic

## Body inside its concern

A member serves one purpose, the one its description states, so a reader
who chose it from the index finds nothing in the body they did not
expect.

`knowledge-organization.body-inside-its-concern` · stochastic

## Rows inside the set

Every row of an index, member or child set, lies inside the concern the
introduction names: a reader who chose the set from its parent's index
expects each row they find.

`knowledge-organization.rows-inside-the-set` · stochastic

## One home

A fact, rule, or decision has one home, the member whose concern is the
thing the fact binds and the most general such member where the fact
still holds; every other document links there, whether it sits in the
same set, another set, or another repo, and states the fact without its
reason.

`knowledge-organization.one-home` · stochastic

## Distinct concerns

No two rows of an index, member or child set, answer the same question:
a reader at the index picks one.

`knowledge-organization.distinct-concerns` · stochastic

## Distinct from the parent

A child set's introduction names a concern its parent's introduction
does not.

`knowledge-organization.distinct-from-the-parent` · stochastic

## Terms defined once

A term is defined once, in the member whose concern it is, and every
other use links that definition.

`knowledge-organization.terms-defined-once` · stochastic

## Terms that cross sets

A term the set coins and a document outside the set uses has an entry in
the repo's `CONTEXT.md`.

`knowledge-organization.terms-that-cross-sets` · stochastic
