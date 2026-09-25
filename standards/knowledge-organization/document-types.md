---
type: Standard
title: Document Types
description: The frontmatter profile every concept document carries — a registered type, a title, a description, a resource where an asset backs the document, and the README type on a README.md alone
population: "a concept document"
---

# Document Types

The frontmatter a concept document carries, the prose `.md` file a
reader loads to understand something. The
boundary is drawn by exclusion from a repo's `.md` files: `index.md` is a
typeless listing ([Indexes](/standards/knowledge-organization/indexes.md));
the harness kinds of the
[Type Registry](/doc-types/registry.md#harness-kinds) are harness-owned, a
tool consumes them as configuration or runs them as code, and they carry
no frontmatter; and `classify()` in [md.py](/src/dev_playbook/md.py)
holds the boundary in code with its further exclusions, the transient
`PLAN.md` and `PROGRESS.md` pair, the root `tmp/` tree, and every
top-level `tests/` tree.

## Frontmatter, a YAML mapping

A concept document opens with a `---`-delimited frontmatter block whose
YAML is a mapping.

`knowledge-organization.frontmatter-a-yaml-mapping` · deterministic

## `type` names a registered type

A concept document's frontmatter has a `type` key whose value names one
row of the Document types table of the
[Type Registry](/doc-types/registry.md#document-types), or one entry of
the `okf_types` mapping in the frontmatter of the repo's own root
`index.md`
([Local Types](/standards/knowledge-organization/local-types.md#local-declaration)).

`knowledge-organization.type-names-a-registered-type` · deterministic

## Non-empty `title`

A concept document's frontmatter has a `title` key with a non-empty
value.

`knowledge-organization.non-empty-title` · deterministic

## Non-empty `description`, no closing period

A concept document's frontmatter has a `description` key whose value is
non-empty and does not end with a period.

`knowledge-organization.non-empty-description-no-closing-period` · deterministic

## The description names the document in the present tense

A concept document's `description` is a sentence fragment in the present
tense that names what the document is, what it governs, or, for a
`Decision-Record`, the decision it records.

`knowledge-organization.the-description-names-the-document-in-the-present-tense` · stochastic

> **Why.** The description is what a reader triages on and what every
> `index.md` listing carries verbatim, so it is read far more often,
> and far further from its document, than the document itself.

## `resource`, a repo-root path or a URI

A concept document's `resource`, where present, is a repo-root path
beginning with `/` or an external URI.

`knowledge-organization.resource-a-repo-root-path-or-a-uri` · deterministic

## resource names the asset

A concept document's `resource`, where present, names the asset the
document describes, never a companion file that only supports it.

`knowledge-organization.resource-names-the-asset` · stochastic

## Recipe-Description carries a `resource`

A concept document typed `Recipe-Description` has a `resource` key with
a non-empty value.

`knowledge-organization.recipe-description-carries-a-resource` · deterministic

## Standard lives under `standards/`

A concept document typed `Standard` lives under `standards/` or in a
workstream under `workstreams/`.

`knowledge-organization.standard-lives-under-standards` · deterministic

## Loop lives under `loops/`

A concept document typed `Loop` lives under `loops/` or in a
workstream under `workstreams/`.

`knowledge-organization.loop-lives-under-loops` · deterministic

## Guide lives under `guides/`

A concept document typed `Guide` lives under `guides/` or in a
workstream under `workstreams/`.

`knowledge-organization.guide-lives-under-guides` · deterministic

## `README.md` is typed `README`

A concept document named `README.md` has `type: README`, and a concept
document of any other name does not.

`knowledge-organization.readmemd-is-typed-readme` · deterministic
