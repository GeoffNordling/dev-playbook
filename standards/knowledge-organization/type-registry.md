---
type: Standard
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
[Adopting a Repo-Scoped Standard](/guides/consuming.md).

## Global table

The declaration is the `## Types` table of
`standards/knowledge-organization/document-types.md`, in the repo that
carries `standards/build/canonical/`.

`knowledge-organization.global-table` · deterministic

### Row shape

Every row of the `## Types` table below its header holds, in its first
cell, one backticked type name in Title Case, hyphen-joined for a
multi-word name: `Decision-Record`, `Candidate-List`, `README`.

`knowledge-organization.row-shape` · deterministic

### Row description

Every row of the `## Types` table below its header holds, in its second
cell, a non-empty one-line description of what the type is.

`knowledge-organization.row-description` · deterministic

### Alphabetical order

The rows of the `## Types` table are in alphabetical order by type name,
compared case-insensitively.

`knowledge-organization.alphabetical-order` · deterministic

## Local declaration

The declaration is the `okf_types` mapping in the frontmatter of the
root `index.md` of a repo that does not carry
`standards/build/canonical/`, one entry per document type the repo
declares for itself.

```yaml
okf_version: "0.1"
okf_types:
  Resume: A resume markdown source, master or batch variant
  Story: One work-experience story in SPAR form
```

`knowledge-organization.local-declaration` · deterministic

> **Why.** Frontmatter, not a document under the consumer's own
> `standards/` tree: that tree is the meta-standard's population, so a
> registry document there could not pass, and a path that mirrors
> dev-playbook's own folder name breaks the moment that folder is
> renamed upstream.

### Mapping entry shape

Each entry's key is a type name in Title Case, hyphen-joined for a
multi-word name, and its value is a non-empty one-line description of
the type.

`knowledge-organization.mapping-entry-shape` · deterministic

### Alphabetical keys

The keys of the `okf_types` mapping are in alphabetical order by type
name, compared case-insensitively.

`knowledge-organization.alphabetical-keys` · deterministic

### Add, never shadow

No key of the `okf_types` mapping equals a type name of the `## Types`
table, or an earlier key of the same mapping, compared
case-insensitively.

`knowledge-organization.add-never-shadow` · deterministic

> **Why.** The test compares case-insensitively so a consumer cannot
> alias an upstream `Guide` as a distinct `GUIDE`.
