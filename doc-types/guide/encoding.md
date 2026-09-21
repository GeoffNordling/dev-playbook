---
type: General-Sheet
title: Instruction Encoding
description: The layer below the shape — the frontmatter a Guide carries, the trailer it never carries, and where the file sits
---

# Instruction Encoding

The layer below [the shape](/doc-types/guide/contract-shape.md): the
form a Guide takes so deterministic code tells it from a Standard, and
where the file sits. The cut points are the frontmatter `type` and the
absence of a trailer line.

## The frontmatter

`type: Guide`, `title`, and `description`. The description names the
work the guide is read before.

## No trailer

No line of a Guide is a rule trailer,
`` `<name>.<slug>` · deterministic `` or
`` `<name>.<slug>` · stochastic ``, and no line is a Reason trailer, a
line opening `explains`. A Guide that needs a rule links it:
`[No shadowing](/standards/standard/tree.md#no-shadowing)`.

## Where a Guide lives

A Guide is `guides/<work>.md`, typed `Guide`, its filename kebab-case
naming the work as a noun or a gerund compound (`bootstrap.md`,
`linking-issues.md`). The registry's rule is
[Typed Guide](/standards/knowledge-organization/document-types.md#typed-guide).
