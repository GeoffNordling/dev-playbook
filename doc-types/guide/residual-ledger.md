---
type: General-Sheet
title: Guide Residual Ledger
description: Guide's residual record — what Instruction cannot express, one entry per Guide that has one
---

# Guide Residual Ledger

Guide's residual record: what
[Instruction](/doc-types/guide/contract-shape.md) cannot express. That
is all an entry is — a record.

## Guides

Per Guide checked against the encoding: what the shape could not
express, recognized and written down at the moment of checking.
Entries name the sequences, steps, and references in the vocabulary
[encoding.md](/doc-types/guide/encoding.md) declares.

An entry is a couple of sentences, hard limit: name each specific thing
the file could not express and why the shape cannot say it, nothing
else. A Guide with nothing to record has no entry.

- **[Bootstrap](/guides/bootstrap.md).** The fresh-path and adoption
  sequences are alternatives, and both run into the GitHub-tail and
  enrollment sequences after them. The shape lists sequences in file
  order and says nothing of how they relate.
- **[Adopting a Repo-Scoped Standard](/guides/consuming.md).** The last
  step binds only a repo that registers a document type; the condition
  sits in the step's name because a step has no condition of its own.
- **[Linking Issues](/guides/linking-issues.md).** The first reference,
  the database id, is a prerequisite of the two write references after
  it. A reference's name is all the shape shows, so the dependency is
  in the bodies alone.
- **[Slop Tics](/guides/slop-tics.md).** Every reference has the same
  body, a definition, one action, and examples, and `tics-remover`
  relies on finding the action in whichever entry it matched. A
  reference's body is opaque to the shape, so the uniformity is
  unstated.
- **[Writing for Agents](/guides/writing-for-agents.md).** The
  information hierarchy is a ladder ranked by immediacy, in-file step
  first. An ordered list is a sequence, so the ranking is a bulleted
  list and its order is in the prose alone.
