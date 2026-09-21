---
type: Standard
title: Explanation Conventions
description: The form a file typed Explanation takes — beside the Standard it explains and named for it, every section a Reason with a body and an explains trailer, and every id a rule of that Standard
population: "a file typed Explanation"
---

# Explanation Conventions

A file typed `Explanation`, under `standards/`
([Document Types](/standards/knowledge-organization/document-types.md#typed-explanation)):
the Reasons for one Standard. The
[Explanation doc-type](/doc-types/explanation/index.md) declares what
an explanation is and the encoding its file takes,
[Reasons Encoding](/doc-types/explanation/encoding.md); a doc-type
binds nobody, so this Standard is what binds the file to that encoding.

## Beside its subject

A file typed `Explanation` is named `<topic>-explanation.md` and sits
in a directory that holds a file typed `Standard` named `<topic>.md`.

`doc-type.beside-its-subject` · deterministic

## Level-two sections only

A file typed `Explanation` holds one H1, then level-two headings and
their sections, with no other heading and no text between the H1 and
the first level-two heading.

`doc-type.level-two-sections-only` · deterministic

## The reason shape

Each section of a file typed `Explanation` is a heading, a body, and
last a trailer line, the word `explains` and then one or more rule ids
in backticks separated by `, `; nothing follows the trailer before the
next heading.

`doc-type.the-reason-shape` · deterministic

## Ids resolve in the subject

Every id a trailer of a file typed `Explanation` names is the id of a
rule of the file typed `Standard` named `<topic>.md` beside it.

`doc-type.ids-resolve-in-the-subject` · deterministic

## One decision, argued

The body of each section of a file typed `Explanation` states one
design decision and the argument for it, and no sentence of it holds a
member of a population to a state.

`doc-type.one-decision-argued` · stochastic
