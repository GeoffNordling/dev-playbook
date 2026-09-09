---
type: Standard
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
[terms defined once](#terms-defined-once) into the repo's `CONTEXT.md`;
a set is otherwise judged with no neighbour's body open.

## An index in every directory

A set's members sit in the directory of its index: a subdirectory
holding concept documents carries an `index.md` of its own and is a
child set, never absorbed into the parent's listing; okf-lint reports a
directory without one (`knowledge-organization.index-present`).

A set is then exactly one directory, so the tree a reader walks is the
tree of sets, and every directory declares its concern in an
introduction sentence of its own.

## Body inside its concern

A member serves one purpose, the one its description states, so a reader
who chose it from the index finds nothing in the body they did not
expect.

A section that reader would not have predicted is a second purpose: it
splits into a member of its own, or into a directory of members with an
`index.md` where the purposes nest, or the description was wrong and is
rewritten. A reader crawling for one answer then loads one small file.
What a description says, and how, is Document Types'
([description](/standards/knowledge-organization/document-types.md#description)).

## Rows inside the set

Every row of an index, member or child set, lies inside the concern the
introduction names: a reader who chose the set from its parent's index
expects each row they find.

A row that reader would not expect sits in the wrong set, or the
introduction is too narrow and is rewritten.

## One home

A fact, rule, or decision has one home, the member whose concern is the
thing the fact binds and the most general such member where the fact
still holds; every other document links there, whether it sits in the
same set, another set, or another repo, and states the fact without its
reason.

The reason is what drifts, so it is written once, at the home. A second
place that argues the fact is a duplicate; a place that names it and
links the home is not. The same rule applies inside one document via
Doc Conventions'
[one rule, one place](/standards/prose/conventions.md#one-rule-one-place).

## Distinct concerns

No two rows of an index, member or child set, answer the same question:
a reader at the index picks one.

Two neighbouring concerns draw their boundary where there is room, in
each lead paragraph, each linking the other. Two whose descriptions
cannot be told apart are one concern written twice, and merge. A child
set whose introduction cannot be told apart from its parent's is the
parent's concern written twice, and its members merge upwards.

## Terms defined once

A term is defined once, in the member whose concern it is, and every
other use links the definition. A term used beyond the set that coins it
also has an entry in the repo's `CONTEXT.md`
([CONTEXT.md Content](/standards/knowledge-organization/context-content.md)),
a one-sentence gloss that links the definition the way an index row
links a member; what the gloss says is CONTEXT.md Content's
([Tight definitions](/standards/knowledge-organization/context-content.md#tight-definitions)).

A definition is a fact like any other, so its home follows
[one home](#one-home).
