---
type: General-Sheet
title: Standard
description: What a standard is — a normative target a population is held to — its one verb, the file it is written in, the family it serves, how it is named and scoped, and where it lives
---

# Standard

A **standard** is a normative target: a state some class of object is
held to, that a reviewer or a lint could cite to reject work. A
standard has no notion of moving toward the state, only of being in or
out of it; driving toward it is [Loop](/doc-types/loop/definition.md)'s.

## The verb

One: **hold** — the standard holds every member of its population to
its rules. Who checks a rule and where the check runs are not the
standard's to say: a detector claims each rule by its id, and the
wiring says the gates that run it
([Detectors](/standards/standard/detectors.md)); what brings a
repository into the state the first time is a guide's or a runbook's.

## The file

A standard is one file, `standards/<name>/<topic>.md`, typed
`Standard` in the
[document-type registry](/standards/knowledge-organization/document-types.md):
one population and its rules, each rule a predicate over one member's
state. The state is described twice. The rule's predicate is the prose
form, what a writer reads to know what to make; the verifier the table
names for the rule's id, deterministic code or a model returning a
value, is the checkable form, what says whether one member is in the
state. The reasoning behind a rule sits beside it in the file, a block
after its trailer.

## The family

The directories under `standards/`, one per standard: `standards/prose/`
holds the Standards that bind an authored document, `standards/build/`
those that bind a repo's tracked tree. A standard does one thing
([System Legibility](/docs/system-legibility.md#standing-principles)):
its question, and the rules that answer it. Procedure and a writer's
heuristics are a guide's.

## Named by the question

A standard is named by the question it governs, not by the current
answer. "How knowledge is organized in markdown" is the question; the
OKF spec is today's answer, vendored at
[docs/mirrors/okf-spec.md](/docs/mirrors/okf-spec.md). The
litmus: if the implementation could be swapped while the name stays
true, the name is a standard's.

- **Membership is non-exclusive.** A file may be a member of more than
  one population. Standards are overlapping views over the repository,
  not a partition of it — populations, not directory placement, say
  what belongs to what.

## Scope

Every standard has a **scope** — the population it governs:

- **Workspace-scoped** — declared in dev-playbook, governing every repo
  in `~/workspace`. The bulk of the catalog is workspace-scoped: the
  cross-project standards every repo inherits through dev-playbook's
  published hooks.
- **Repo-scoped** — declared in one consumer repo, governing that repo
  alone. A repo stands one up when it has a convention no other repo
  shares; the recipe is
  [Adopting a Repo-Scoped Standard](/guides/consuming.md).

Exactly two levels: a standard governs the whole workspace or a single
repo, never an intermediate group.

**No shadowing.** A repo-scoped standard's directory name is one no
workspace-scoped standard carries, since a consumer's
`standards/<name>/` on an upstream name would silently override the
upstream standard of that name; the rule and its lint are
[No shadowing](/standards/standard/tree.md#no-shadowing).

## Where a standard lives

Under `standards/`, the one tree reserved for the type; nothing outside
it claims the label, and
`knowledge-organization.standard-lives-under-standards` checks it. Every
immediate subdirectory of `standards/` holds at least one file typed `Standard`.
The layout's rule and its lint are
[Every subdirectory a Standard directory](/standards/standard/tree.md#every-subdirectory-a-standard-directory); the
file forms are [the encoding](/doc-types/standard/encoding.md).
