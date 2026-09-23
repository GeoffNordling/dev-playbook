---
type: Standard
title: Guide Conventions
description: The form a document typed Guide takes — every ordered list a sequence of steps under its own heading, each step opening with its bold name, no trailer line, rules linked and never stated, and a description naming the work it is read before
population: "a document typed Guide"
---

# Guide Conventions

A document typed `Guide`, under `guides/`
([Document Types](/standards/knowledge-organization/document-types.md#guide-lives-under-guides)).
The [Guide doc-type](/doc-types/guide/index.md) declares what a guide
is and the encoding its file takes,
[Instruction Encoding](/doc-types/guide/encoding.md); a doc-type binds
nobody, so this Standard is what binds the file to that encoding.

> **Why.** The parse of a Guide shows its headings and its step names
> and nothing of the bodies beneath them, so those names are all a
> reader gets of the guide before opening it.

## A sequence is one list

In a file typed `Guide`, every ordered list starts at `1.` and has
no ordered list inside it. Between the heading above the list and the
list there is at most one paragraph, and that paragraph is one
sentence. After the list there is nothing until a heading at the
same level as that heading or higher.

`doc-type.a-sequence-is-one-list` · deterministic

## A step opens with its name

Each item of an ordered list in a document typed `Guide` opens with a
bold run ending in a period, followed by the item's text.

`doc-type.a-step-opens-with-its-name` · deterministic

## An ordered list is a sequence

Each ordered list in a document typed `Guide` is a run of actions a
reader performs in the order given, each item one action that its bold
run names; a ranking, an enumeration, or a set of alternatives is a
bulleted list.

`doc-type.an-ordered-list-is-a-sequence` · stochastic

## No trailer

No line of a document typed `Guide` is a rule trailer,
`` `<name>.<slug>` · deterministic `` or
`` `<name>.<slug>` · stochastic ``.

`doc-type.no-trailer` · deterministic

## Links rules, states none

A document typed `Guide` holds no sentence that holds a member of a
population to a state; where the work it instructs meets such a state,
the sentence links the rule that states it.

`doc-type.links-rules-states-none` · stochastic

## The description names the work

The `description` of a document typed `Guide` names the kind of work a
reader does after reading it.

`doc-type.the-description-names-the-work` · stochastic
