---
type: General-Sheet
title: Instruction Encoding
description: The layer below the shape — the headings, ordered lists, and bold runs that carry a Guide's sequences, steps, and references, the frontmatter, the trailer it never carries, and where the file sits
---

# Instruction Encoding

The layer below [the shape](/doc-types/guide/contract-shape.md): the
form a Guide takes so deterministic code reads every sequence, step,
and reference the same way, and where the file sits. The cut points
are three marks CommonMark already has, a heading, an ordered list,
and a bold run at the head of a list item; the extractor is a markdown
parser plus those cuts, and it reads nothing else. The Standard that
binds a Guide to this encoding is
[Guide Conventions](/standards/doc-type/guide-conventions.md).

## The frontmatter

`type: Guide`, `title`, and `description`. The description names the
work the guide is read before.

## The lead

The prose between the H1 and the first heading below it: what the
work is, and how the guide's sequences relate where it has more than
one. No part lives here and the parser skips it.

## Sequences

A sequence is a heading whose section is one ordered list. The
heading's text is the sequence's name; its slug is formed as a rule's
is
([Rules](/doc-types/standard/encoding.md#rules)). Before the list the
section holds at most one sentence, saying what the sequence does;
after the list, nothing, and no heading nests beneath it. The list is
numbered from `1.`, and a guide with two sequences numbers each from
one, since they are independent. A sequence holds no second ordered
list and no ordered list nests inside a step.

## Steps

A step is one item of a sequence's list. It opens with a bold run
ending in a period, the step's name, and the rest of the item is the
instruction:

```markdown
## The existing path

An existing repo is brought to green in this order:

1. **Read the layers.** Membership is inferred from facts on disk …
2. **Wire the pin.** No `.pre-commit-config.yaml` → copy …
```

Inside the item, after the name, anything goes: a fenced block, a
table, a bulleted list. The parser takes the bold run and skips the
rest.

## References

A reference is a heading whose section holds no ordered list. Its
text is the reference's name and its slug is formed as a rule's. Its
body is opaque: prose, a table, a Mermaid graph, a fenced block, a
bulleted list, in any mixture, and none of it reaches the parse.
Headings nested beneath a reference are references, or sequences, of
their own, and the parse nests them as the headings nest.

Because the body is opaque, the name is the whole of what the parse
shows of a reference, and the same holds of a sequence and a step. A
heading that names its section specifically, `Path-scoped
permissions do not work` rather than `Permissions`, is the encoding's
one demand on a writer beyond the marks.

## Bulleted lists

A bulleted list is body. A ranking, an enumeration, or a set of
alternatives is bulleted, never numbered, since the parser reads every
ordered list as a sequence of actions.

## No trailer

No line of a Guide is a rule trailer,
`` `<name>.<slug>` · deterministic `` or
`` `<name>.<slug>` · stochastic ``. A Guide that needs a rule links it:
`[No shadowing](/standards/standard/tree.md#no-shadowing)`.

## Where a Guide lives

A Guide is `guides/<work>.md`, or a draft in a workstream,
typed `Guide`, its filename kebab-case
naming the work as a noun or a gerund compound (`bootstrap.md`,
`linking-issues.md`). The registry's rule is
[Guide lives under `guides/`](/standards/knowledge-organization/document-types.md#guide-lives-under-guides).
