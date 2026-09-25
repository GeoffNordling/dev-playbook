---
type: Registry
title: Doc-Type Registry
description: Every built doc-type, each with the OKF type or the harness members its instances are, and the Standard that holds them
---

# Doc-Type Registry

A **doc-type** is a contract for one kind of file: a directory
`doc-types/<name>/` holding its definition, contract shape, encoding,
and residual ledger ([Reference Model](/doc-types/reference-model.md)).
Each row joins a doc-type to the kinds of file that are its instances:
an OKF type from the [OKF Type Registry](/registries/okf-types.md), or
members from the [Harness File Registry](/registries/harness-files.md).
Those two registries name no doc-type; this table is the only join.

Read from here, three relations hold:

- an OKF type a row names has a doc-type, such as `Loop`;
- an OKF type no row names is a label only, such as `Log`;
- a row whose instances are harness members has no OKF type, such as
  Runbook.

The rule [Registered](/standards/doc-type/doc-type.md#registered) holds
each `doc-types/<name>/` to a row here.

## Doc-types

| Doc-type | OKF type | Harness members | Conventions |
|---|---|---|---|
| [Guide](/doc-types/guide/definition.md) | `Guide` | — | [Guide Conventions](/standards/doc-type/guide-conventions.md) |
| [Loop](/doc-types/loop/definition.md) | `Loop` | — | [Loop Conventions](/standards/doc-type/loop-conventions.md) |
| [Runbook](/doc-types/runbook/definition.md) | — | skill bundles; `agents/*.md` | [Runbook Conventions](/standards/doc-type/runbook-conventions.md) |
| [Standard](/doc-types/standard/definition.md) | `Standard` | — | [Standard Conventions](/standards/doc-type/standard-conventions.md) |
| [Workstream](/doc-types/workstream/definition.md) | `Workstream` | — | [Workstream Conventions](/standards/doc-type/workstream-conventions.md) |
