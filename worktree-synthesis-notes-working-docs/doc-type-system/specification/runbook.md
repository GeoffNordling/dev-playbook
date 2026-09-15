---
type: General-Sheet
title: Runbook Specification
description: What the Runbook doc-type satisfies beyond Doc-Type Specification — its six verbs, and every edge landing on a Target
population: "the Runbook doc-type: its directory doc-types/runbook/ in dev-playbook, every Runbook in a governed repo, and the toolchain entries that read them"
---

# Runbook Specification

What the Runbook doc-type satisfies beyond
[Doc-Type Specification](/worktree-synthesis-notes-working-docs/doc-type-system/specification/doc-type.md),
which every doc-type satisfies. Speculative, per
[Doc-Type System](/worktree-synthesis-notes-working-docs/doc-type-system/ROOT.md).

## Six verbs

The operations are read, write, do, override, accept, report.

`doc-type-system.runbook.verbs` · deterministic

## Every edge lands

Every edge carries one of the six and lands on a
[Target](/worktree-synthesis-notes-working-docs/doc-type-system/reference-model.md#the-language);
a ban is a polarity on a write; accept and report carry no target and sit at the
root.

`doc-type-system.runbook.edges` · deterministic

## Acronyms

None.
