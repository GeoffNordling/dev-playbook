---
type: Standard
title: Workstream Files
description: What the files of a workstream add to Documentation Sets — a guess written as a guess, every file reached from its head file, one directory per workstream under `workstreams/`, the worklist in the head file only, buckets, menu headings as names, terms and acronyms each held in the nearest head file that holds their uses — each stated as the one difference against the general rule it qualifies
population: "a Markdown file of a workstream, under `workstreams/`"
---

# Workstream Files

A **workstream** is one line of work: its
[head file](/doc-types/workstream/definition.md), typed `Workstream`,
and the
[documentation set](/standards/knowledge-organization/documentation-sets/documentation-sets.md)
the work accumulates beside it, plans, design notes, records, kept as
long as the work runs and drained into permanent homes or deleted when
it ends. Every rule of Documentation Sets and of
[Doc Conventions](/standards/prose/conventions.md) binds a file of a
workstream; each section below is the one difference a workstream adds,
stated against the general rule it qualifies, and a file is otherwise
judged as any file is. The form of the head file itself is
[Workstream Conventions](/standards/doc-type/workstream-conventions.md).
A file whose type is not yet settled carries `type: General-Sheet`
([OKF Frontmatter](/standards/knowledge-organization/okf-frontmatter.md#type-is-a-registered-okf-type)).
A file may also carry a type whose home is elsewhere, such as `Guide`,
before it moves there
([Guide lives under `guides/`](/standards/knowledge-organization/okf-frontmatter.md#guide-lives-under-guides));
the form rules of that type do not bind it while it is under
`workstreams/`.

A workstream may have **child workstreams**, each a directory below it
with its own `WORKSTREAM.md`. Below, the head file of a file is the
`WORKSTREAM.md` in its own directory or the nearest directory above,
and the workstream is the whole tree, child workstreams included.

> **Why.** The buckets are a menu,
> [one home per fact](/standards/knowledge-organization/documentation-sets/documentation-sets.md#one-home-per-fact)
> made navigable: a file uses the buckets its work needs, skips the
> rest, and `Unfiled` catches what fits none of them. A term or an
> acronym of the work is defined in a head file rather than in the
> repo's `CONTEXT.md` while no file outside the work uses it, and in the
> head file nearest its uses, so that the definition sits as low in
> the tree as the rule allows and every other use links to it.

## A guess written as a guess

Every file of a workstream writes a guess as a guess, and every head
file declares its workstream speculative in one sentence. This
is the whole exemption from
[every sentence in the present tense](/standards/prose/conventions.md#every-sentence-in-the-present-tense).

`knowledge-organization.a-guess-written-as-a-guess` · stochastic

## Every file reached from its head file

Every `.md` file of a workstream other than an `index.md` and a
`WORKSTREAM.md` is reached from its head file by a chain of links
between files of the workstream. A link in an `index.md` is not part of
a chain. A head file is reached from its parent's by
[Every child reached from its parent](/standards/doc-type/workstream-conventions.md#every-child-reached-from-its-parent).

`knowledge-organization.every-file-reached-from-its-head-file` · deterministic

> **Why.** The chain is a second structure over
> [an index in every directory](/standards/knowledge-organization/documentation-sets/documentation-sets.md#an-index-in-every-directory)'s
> tree of sets: an index lists a file, and only a link from the work's
> own files says where it sits in the work.

## One directory under `workstreams/`

Every directory directly under `workstreams/` has an `index.md` and a
`WORKSTREAM.md`. Every Markdown file under it has a lowercase
kebab-case name, such as `check-fixes.md`, except `index.md`,
`WORKSTREAM.md`, `README.md`, `PROMPT.md`, `SKILL.md`, and `CLAUDE.md`.

`knowledge-organization.one-directory-under-workstreams` · deterministic

> **Why.** The workstream is the one directory
> [an index in every directory](/standards/knowledge-organization/documentation-sets/documentation-sets.md#an-index-in-every-directory)
> makes, here named and placed.

## `workstreams/` holds only workstreams

`workstreams/` directly has `index.md`, directories, and no other file.

`knowledge-organization.workstreams-holds-only-workstreams` · deterministic

> **Why.** `workstreams/` is a plain parent to the sets
> [an index in every directory](/standards/knowledge-organization/documentation-sets/documentation-sets.md#an-index-in-every-directory)
> makes.

## The worklist in the head file only

No file of a workstream other than a `WORKSTREAM.md` has a `## Planned`
or a `## Completed` section.

`knowledge-organization.the-worklist-in-the-head-file-only` · deterministic

> **Why.** An item's state is the section it sits in, and `Completed`,
> `Settled`, and `Stints` are the past state a head file records
> ([current state and next steps only](/standards/prose/conventions.md#current-state-and-next-steps-only)).
> One worklist per workstream is one place to look.

## Every fact under a named bucket

Every fact in a file of a workstream sits under a named section, its
bucket, the
[one home per fact](/standards/knowledge-organization/documentation-sets/documentation-sets.md#one-home-per-fact)
inside the file, and a bucket holds facts of its own type only; the
section under the file's H1, which says what the file is and what it is
for, is exempt. A head file's buckets are the headings of
[its menu](/standards/doc-type/workstream-conventions.md#headings-from-the-registry);
any other file uses those names where they fit, coins its own where
none does, and puts material awaiting triage under `Unfiled`.

`knowledge-organization.every-fact-under-a-named-bucket` · stochastic

## Menu headings are names

An H2 of a head file, and a heading another file of a workstream takes
from the same menu, names its bucket and is not a proposition. This is
the whole exemption from
[headings are propositions](/standards/prose/conventions.md#headings-are-propositions).

`knowledge-organization.menu-headings-are-names` · stochastic

> **Why.** A reader and a script find a bucket by its menu name, such
> as `Open`, so a proposition in its place is a heading no reader knows
> to look for.

## A term in the nearest head file that holds its uses

A term coined by the work is defined once: in the `Terms` heading of
the head file of the nearest workstream that holds every file using
it, or, where a file outside `workstreams/` also uses it, in the repo's
`CONTEXT.md`, per
[crossing terms in CONTEXT.md](/standards/knowledge-organization/documentation-sets/documentation-sets.md#crossing-terms-in-contextmd).
Every other file of the workstream that uses the term links to that
definition.

`knowledge-organization.a-term-in-the-nearest-head-file-that-holds-its-uses` · stochastic

## An acronym in the nearest head file that holds its uses

Only a head file has an `Acronyms` heading. An acronym a file of a
workstream uses is defined once, in the `Acronyms` heading of the head
file of the nearest workstream that holds every file using it, in
place of a definition above first use
([definition before first use](/standards/prose/conventions.md#definition-before-first-use)).

`knowledge-organization.an-acronym-in-the-nearest-head-file-that-holds-its-uses` · stochastic
