---
type: Standard
title: Type Registry
description: The document-type registry's Types table — Title-Case names in alphabetical order, and the additive law a consumer's local extension obeys
population: "a document-type registry's Types table, the global one in dev-playbook or a consumer's local extension"
---

# Type Registry

The `## Types` table of a document-type registry. The global registry is
[Document Types](/standards/knowledge-organization/document-types.md) in
dev-playbook, the vocabulary every repo inherits. A consumer repo that
carries a document type no other repo shares declares it in a local
extension, its own `standards/knowledge-organization/document-types.md`
holding a `## Types` table of the same shape; okf-lint resolves a
document's `type` against the union of the two, and against the global
table alone when the repo carries no extension. Declaring a local
extension is one step of
[Consuming a Standard](/standards/standard/consuming.md). okf-lint is the
authority ([Knowledge Organization](/standards/knowledge-organization.md)).

## Row shape

Each row's first cell is one backticked type name in Title Case,
hyphen-joined for a multi-word name with acronyms upper,
`Decision-Record`, `Standard-Card`, `README`, and its second cell says
what the type is.

## Alphabetical order

Rows are in alphabetical order by type name.

## Local extension

The Types table in a consumer's own
`standards/knowledge-organization/document-types.md`.

### Add, never shadow

Every row names a new type: no row's name equals an upstream name, or
an earlier row's name in the same table, compared case-insensitively.

Membership stays exact-case; the case-insensitive test stops a consumer
aliasing upstream `Guide` as a distinct `GUIDE`. A consumer never edits
the global table, so it can neither loosen nor drop an upstream type. A
local type is legal only in the repo that declares it and any repo
downstream of it, invisible uphill to dev-playbook and sideways to
sibling consumers.

### Name and description only

A row carries the type's name and its cell, and nothing else: the
per-type constraints upstream types impose, `resource` on
`Recipe-Description` or `## Employed by` on `Instrument-Spec`, stay
hardcoded upstream, and a local type declares none.
