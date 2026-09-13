---
type: Standard-Ruleset
title: Type Registry
description: The document-type vocabulary — dev-playbook's Types table and the additive okf_types a consumer declares in its root index
population: "a document-type declaration: dev-playbook's `## Types` table, or a consumer's root-index `okf_types` mapping"
---

# Type Registry

Where a document type is declared. The global registry is the `## Types`
table of
[Document Types](/standards/knowledge-organization/document-types.md) in
dev-playbook, the vocabulary every repo inherits. A consumer repo that
carries a document type no other repo shares declares it in the
frontmatter of its own root `index.md`, an `okf_types` mapping beside
`okf_version`; okf-lint resolves a document's `type` against the union of
the two, and against the global table alone when the repo declares no
`okf_types`. Declaring a local type is one step of
[Adopting a Repo-Scoped Standard](/standards/standard/consuming.md). okf-lint is the
authority ([Knowledge Organization](/standards/knowledge-organization/card.md)).

## Row shape

Each row's first cell is one backticked type name in Title Case,
hyphen-joined for a multi-word name with acronyms upper,
`Decision-Record`, `Standard-Card`, `README`, and its second cell says
what the type is.

## Alphabetical order

Rows are in alphabetical order by type name.

## Local declaration

The `okf_types` mapping in a consumer's root `index.md` frontmatter, one
entry per local type: the key its name, the value its description.

```yaml
---
okf_version: "0.1"
okf_types:
  Resume: A resume markdown source, master or batch variant
  Story: One work-experience story in SPAR form
---
```

Frontmatter, not a document under the repo's own `standards/` tree. That
tree is the meta-standard's population — standards-lint wants a card in
every subdirectory of it
([Directory layout](/standards/standard/cards.md#directory-layout))
and forbids a card named for a dev-playbook one
([No shadowing](/standards/standard/cards.md#no-shadowing)) — so a
registry document at `standards/knowledge-organization/` could not pass,
and a path that mirrors dev-playbook's own folder name breaks the moment
that folder is renamed upstream.

### Entry shape

Each key has the [Row shape](#row-shape)'s name, and each value is a
non-empty one-line description.

### Alphabetical keys

The keys are in alphabetical order by type name.

### Add, never shadow

Every key names a new type: no key equals an upstream name, or an earlier
key of the same mapping, compared case-insensitively.

Membership stays exact-case; the case-insensitive test stops a consumer
aliasing upstream `Guide` as a distinct `GUIDE`. A consumer never edits
the global table, so it can neither loosen nor drop an upstream type. A
local type is legal only in the repo that declares it and any repo
downstream of it, invisible uphill to dev-playbook and sideways to
sibling consumers.

### Name and description only

An entry carries the type's name and its description, and nothing else:
the per-type constraints upstream types impose, `resource` on
`Recipe-Description` for one, stay hardcoded upstream, and a local type
declares none.
