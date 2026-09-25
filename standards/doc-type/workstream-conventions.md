---
type: Standard
title: Workstream Conventions
description: The form a Workstream's head file takes — its headings from one menu, Open holding questions only, each worklist item opening with its bold name, each stint entry in one form, and every child reached by links from its parent
population: "a document typed Workstream"
---

# Workstream Conventions

A document typed `Workstream`, the head file of one line of work. The
[Workstream doc-type](/doc-types/workstream/index.md) declares what a
workstream is and the encoding its head file takes,
[Headings and Stints Encoding](/doc-types/workstream/encoding.md); a
doc-type binds nobody, so this Standard is what binds the head file to
that encoding.

> **Why.** A workstream is read by the user, by an agent starting a
> stint, and by the scripts that list the work in flight. Each reads
> the head file by its headings, so the headings are one fixed menu,
> and the stints are one form a script can read.

## Headings from the menu

Every H2 of a document typed `Workstream` is a heading in the
[Workstream Heading Menu](/doc-types/workstream/heading-menu.md#headings),
and no two of its H2s have the same text.

`doc-type.headings-from-the-menu` · deterministic

> **Why.** Every heading is optional and all are peers, so a
> workstream picks the ones its work needs; a heading outside the menu
> is one no reader knows to look for.

## Open holds questions only

Every item under the `Open` heading of a document typed `Workstream`
is a question, and no item holds an answer to it, recommended or not.

`doc-type.open-holds-questions-only` · stochastic

> **Why.** An answer beside its question reads as settled. A question
> answered moves to Settled.

## A worklist item opens with its bold name

Each item directly under the `Planned` or the `Completed` heading of a
document typed `Workstream` starts with a bold name, such as
`- **Write the board script.**`.

`doc-type.a-worklist-item-opens-with-its-bold-name` · deterministic

> **Why.** An item's state is the heading it sits under, and an item
> moves from Planned to Completed by its name. The rules for the other
> files of a workstream are
> [Workstream Files](/standards/knowledge-organization/documentation-sets/workstream-files.md).

## A stint entry in form

Each item of the bulleted list under the `Stints` heading of a
document typed `Workstream` opens with `**Planned.**` or with a date,
`**YYYY-MM-DD.**`, and has exactly one link to a file typed `Loop`.
At most one item opens with `**Planned.**`, and it is the first; the
dated items follow it, newest first. An item that holds `Verdict:`
follows it with `advance`, `accept`, or `delete`.

`doc-type.a-stint-entry-in-form` · deterministic

> **Why.** Stints is the ledger of the loops that drove the workstream,
> the next spend and the past ones, and the board script reads it.

## Every child reached from its parent

A document typed `Workstream` with a document typed `Workstream` in a
directory above its own is a child of the nearest one, its parent. A
chain of links between the Markdown files in the parent's directory,
and the directories under it, leads from the parent to the child.

`doc-type.every-child-reached-from-its-parent` · deterministic

> **Why.** No head file lists its children: the directory is the one
> source. The links make sure a reader who starts at the parent finds
> every child.
