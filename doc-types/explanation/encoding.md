---
type: General-Sheet
title: Reasons Encoding
description: The layer below the shape — how an Explanation names its subject, writes each Reason, and lists the ids it explains so a lint reads them, and where the file sits
---

# Reasons Encoding

The layer below [the shape](/doc-types/explanation/contract-shape.md):
the form an Explanation takes so deterministic code reads the subject
and every Reason the same way, and where the file sits. The cut points
are the filename, the heading levels, and the trailer line.

## The subject

The filename. The Explanation of the Standard `<topic>.md` is
`<topic>-explanation.md` in the same directory; the subject is found
by name and the file carries no key for it. Nothing sits between the
H1 and the first H2.

## Reasons

A Reason is an H2; its section is the Reason. There is no H3.

- **The name.** The heading's text, in sentence case, naming the
  decision.
- **The why.** Everything between the heading and the trailer: the
  decision and the argument for it.
- **The trailer.** The section's last line, `explains` and then the
  rule ids, each in backticks, separated by `, `:
  `` explains `doc-type.the-rule-shape`, `doc-type.decidable-predicates` ``.
  Every id is a rule of the subject. Nothing follows it before the
  next heading.

## Where an Explanation lives

Beside its subject, in the same directory. The registry's rule is
[Typed Explanation](/standards/knowledge-organization/document-types.md#typed-explanation).
