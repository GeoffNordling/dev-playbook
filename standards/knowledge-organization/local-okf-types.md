---
type: Standard
title: Local OKF Types
description: The table a consumer repo declares its own OKF types in — where it sits, each row's shape, the order of its rows, and no row that shadows a registered OKF type
population: "a local OKF type declaration: the table under `## OKF types` in a consumer repo's `registries/okf-types.md`"
---

# Local OKF Types

Where a consumer repo declares an OKF type that no other repo shares:
its own `registries/okf-types.md`, a table in the same shape as
dev-playbook's
[OKF Type Registry](/registries/okf-types.md#okf-types), the OKF types
every repo inherits. These rules govern the consumer's table and only
read dev-playbook's. A check resolves a document's `type` against the
union of the two, and against dev-playbook's alone when the repo has no
`registries/okf-types.md`
([`type` is a registered OKF type](/standards/knowledge-organization/okf-frontmatter.md#type-is-a-registered-okf-type)).
Declaring a local OKF type is one step of
[Adopting a Repo-Scoped Standard](/guides/consuming.md).

## Local declaration

The declaration is the table under `## OKF types` in
`registries/okf-types.md` of a repo that does not carry
`standards/build/canonical/`, one row per OKF type the repo declares
for itself.

```markdown
## OKF types

| OKF type | What it is |
|----------|------------|
| `Resume` | A resume markdown source, master or batch variant |
| `Story` | One work-experience story in SPAR form |
```

### OKF type name to description

Each row's first cell is an OKF type name in backticks, in Title Case,
hyphen-joined for a multi-word name, and its second cell is non-empty.

`knowledge-organization.okf-type-name-to-description` · deterministic

> **Why.** The description is what a reader picks the OKF type by.

### Rows in alphabetical order

The rows of the table are in alphabetical order by OKF type name,
compared case-insensitively.

`knowledge-organization.rows-in-alphabetical-order` · deterministic

### Add, never shadow

No row of the table names an OKF type equal, ignoring case, to one in
dev-playbook's OKF Type Registry, or to an earlier row's.

`knowledge-organization.add-never-shadow` · deterministic

> **Why.** The test compares case-insensitively so a consumer cannot
> alias an upstream `Guide` as a distinct `GUIDE`.
