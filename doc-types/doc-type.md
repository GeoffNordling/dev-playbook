---
type: General-Sheet
title: Doc-Type
description: What a doc-type is in one sentence, where the theory of the doc-type system now lives, and the residual every built doc-type records
---

# Doc-Type

A **doc-type** hands one documentation family a contract shape: the
form every member of the family is read against, so a caller learns
what it needs without reading the body. An **instance** is one member
of the family, one runbook, one standard, one loop. This repo's built
doc-types, and what each directory holds, are
[Doc-Type System](/doc-types/doc-type-system.md).

The theory of the system, what a doc-type is made of, its verbs, its
rules as predicates, and the pseudocode of the target state, is
in-process work and lives in the working set, not here:
[Doc-Type System](/working-docs/doc-type-system/doc-type-system/ROOT.md),
with the pseudocode in
[Reference Model](/working-docs/doc-type-system/doc-type-system/reference-model.md),
the predicates in
[Doc-Type Specification](/working-docs/doc-type-system/doc-type-system/specification/doc-type.md),
and the words in the set's
[Terms](/working-docs/doc-type-system/ROOT.md#terms).

## The doc-type build loop

The procedure that produces a doc-type from a family: an agent
re-expresses the family in the current primitives, and whatever forces
a drop to file-level detail is the **residual**; the primitives are
refactored only when the reduction is worth the change cost. Residuals
are recorded in the doc-type's residual ledger, one entry per instance
that has one. The loop's current design is
[Specifying a Loop](/working-docs/doc-type-system/loop/specifying-a-loop.md#the-loop-that-proposes),
and the fact base strand plans to run it as a Loop
([Planned](/working-docs/doc-type-system/fact-base/ROOT.md#planned)).
