---
type: Standard
title: Local Types
description: The okf_types mapping a consumer repo declares its own document types in — where it sits, each entry's shape, the order of its keys, and no key that shadows a registered type
population: "a local type declaration: the `okf_types` mapping in the frontmatter of a consumer repo's root `index.md`"
---

# Local Types

Where a consumer repo declares a document type that no other repo
shares: an `okf_types` mapping in the frontmatter of its own root
`index.md`, beside `okf_version`. The types every repo inherits are the
[OKF Type Registry](/registries/okf-types.md#okf-types), which lives in
dev-playbook; these rules read that table and never govern it. A check
resolves a document's `type` against the union of the two, and against
the registry alone when the repo declares no `okf_types`
([`type` names a registered type](/standards/knowledge-organization/document-types.md#type-names-a-registered-type)).
The declaration is frontmatter and not a document under the consumer's
own `standards/` tree, since that tree is the meta-standard's
population, and a registry document there could not pass. Declaring a
local type is one step of
[Adopting a Repo-Scoped Standard](/guides/consuming.md).

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

### Type name to description

Each entry's key is a type name in Title Case, hyphen-joined for a
multi-word name, and its value is non-empty text on one line.

`knowledge-organization.type-name-to-description` · deterministic

> **Why.** The value is a description a reader picks the type by.

### Keys in alphabetical order

The keys of the `okf_types` mapping are in alphabetical order by type
name, compared case-insensitively.

`knowledge-organization.keys-in-alphabetical-order` · deterministic

### Add, never shadow

No key of the `okf_types` mapping is equal, ignoring case, to a type
name in the table of `registries/okf-types.md`, or to an earlier key of
the same mapping.

`knowledge-organization.add-never-shadow` · deterministic

> **Why.** The test compares case-insensitively so a consumer cannot
> alias an upstream `Guide` as a distinct `GUIDE`.
