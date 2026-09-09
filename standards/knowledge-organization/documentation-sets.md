---
type: Standard
title: Documentation Sets
description: How the concept documents one index.md owns relate as a set — a body inside its declared concern, a child set inside its parent, one home for every fact, distinct concerns, and terms defined once
population: "a documentation set, the concept documents one index.md owns"
---

# Documentation Sets

A **documentation set** is the concept documents one `index.md` owns: the
documents in its directory, and in every subdirectory with no `index.md`
of its own, which the nearest index above absorbs. A directory with its
own `index.md` is a set of its own, nested in the parent's. The index is
the set's root and its listing is the set's membership
([Indexes](/standards/knowledge-organization/indexes.md)); a link never
makes a file a member, since a link reaches any file in any set or repo
in the forms
[Cross-References](/standards/knowledge-organization/cross-references.md)
gives. A member's **concern** is the one line its frontmatter
`description` states
([Document Types](/standards/knowledge-organization/document-types.md#description));
a set's concern is the sentence its index's introduction opens with
([Indexes](/standards/knowledge-organization/indexes.md#the-introduction)).
The rules bind the set level, how the members relate to each other and
to their concerns; what one member holds is [Prose](/standards/prose.md)'s.

## Body inside its concern

A member's body stays inside its concern: every section answers the one
question the description names.

A member that has accumulated several concerns, distinct questions a
reader might arrive with, splits into one member per concern, or into a
directory of members with an `index.md` where the concerns nest. A reader
crawling for one answer then loads one small file. A subject with layers
may split by layer, each file named for the layer it holds.

## Child inside its parent

A nested set's concern lies inside its parent's: the child index's
introduction narrows what the parent's names.

`standards/knowledge-organization/` holds *the Standards on how knowledge
is organized in markdown*, one part of `standards/`, *the catalog*.

## One home

A fact, rule, or decision is stated in one member, the one whose concern
is the most general where the fact still holds; every other document
links there, whether it sits in the same set, another set, or another
repo.

The specific document links the general one: File Skeleton names
`docs/decisions/` and links Decision Record Conventions for what a record
holds, and story-forge links Doc Conventions for how its prose is written
instead of restating it. Inside one document the same rule is Doc
Conventions'
[one rule, one place](/standards/prose/conventions.md#one-rule-one-place).

## Distinct concerns

No two members of a set declare overlapping concerns: each question a
reader arrives with has one member that answers it.

Two members whose descriptions overlap are one concern written twice;
they merge, or the boundary between them is redrawn into both
descriptions.

## Terms defined once

A term a set coins and uses in more than one member is defined once, in
the repo's `CONTEXT.md`
([CONTEXT.md Content](/standards/knowledge-organization/context-content.md)).
