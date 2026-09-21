---
type: Standard
title: Guide Conventions
description: The form a document typed Guide takes — no trailer line, rules linked and never stated, and a description naming the work it is read before
population: "a document typed Guide"
---

# Guide Conventions

A document typed `Guide`, under `guides/`
([Document Types](/standards/knowledge-organization/document-types.md#typed-guide)).
The [Guide doc-type](/doc-types/guide/index.md) declares what a guide
is and the encoding its file takes,
[Instruction Encoding](/doc-types/guide/encoding.md); a doc-type binds
nobody, so this Standard is what binds the file to that encoding.

## No trailer

No line of a document typed `Guide` is a rule trailer,
`` `<name>.<slug>` · deterministic `` or
`` `<name>.<slug>` · stochastic ``, or a Reason trailer, a line opening
with the word `explains`.

`doc-type.no-trailer` · deterministic

## Links rules, states none

A document typed `Guide` holds no sentence that holds a member of a
population to a state; where the work it instructs meets such a state,
the sentence links the rule that states it.

`doc-type.links-rules-states-none` · stochastic

## Names its work

The `description` of a document typed `Guide` names the kind of work a
reader does after reading it.

`doc-type.names-its-work` · stochastic
