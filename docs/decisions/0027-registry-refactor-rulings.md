---
type: Decision-Record
title: Registry Refactor Rulings
description: The four rulings of the registry refactor — a Standard is what a reviewer or lint can cite to reject work, it governs object state and never process, the software factory card is deleted, and Spec-Item leaves the registry, partially reversing 0021
date: 2026-09-05
status: accepted
---

# Registry Refactor Rulings

The `no-more-slop` branch built the Standard doc-type
([definition](/doc-types/standard/definition.md)) and ported every
card's Standards onto its encoding. The port needed a rule for what a
Standard is, and applying that rule reorganized the document-type
registry ([Document Types](/standards/knowledge-organization/document-types.md)).
Four rulings shaped the result; each is hard to reverse, because the
ported files, the deleted card, and the rulings table in
[Doc-Type System](/doc-types/doc-type-system.md) all rest on them.

**The axis.** Can a reviewer or a lint cite the document to reject work?
Yes is a Standard. No is not.

**State, never process.** A Standard governs the state of an object at
one moment, never a process. A process is checked through the objects
it produces, never through its trace: rejecting work because an agent
deviated from documented steps is the wrong audit.

**The software factory card is deleted.** The factory's documentation is
due for a rewrite, so reorganizing around its current form would be
wasted work. It stays typed `Guide` for now, a known imprecision, and the
factory needs no card until its rules exist: the card `standards/software-factory.md` is
deleted, since every file its Define cell pointed at was a Guide, and a
card returns when a Standard exists to point at.

**Spec-Item leaves the registry.** Its one tooled population is
spec-tools, which is not a priority. A consumer repo may break during
this refactor; its pinned `rev` keeps it on the prior revision until it
catches up.

## Consequences

- The Spec-Item ruling reverses the second half of
  [0021](/docs/decisions/0021-scope-directories-and-spec-item-return.md);
  its first half, the `unit` and `integration` scope directories,
  stands.
- Log and Survey stay as rows of the pass, first class, the user's to
  rule on.
- The split the factory's rewrite will make — object-state rules into a
  Standard under `standards/software-factory/`, the two regions into a
  Guide, the `gh` mechanics into the review runbooks — is a Candidate
  ([Candidates](/CANDIDATES.md)), not a commitment.
