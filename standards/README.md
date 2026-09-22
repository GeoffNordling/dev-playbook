---
type: README
title: Standards
description: Cross-project engineering standards that apply to every repository in the workspace
---

# Standards

Cross-project engineering standards that apply to all repositories in the
workspace.

## How this directory reads

Every directory here is one standard: the files typed `Standard` that
state its rules, one population each (`build/skeleton.md`,
`build/canonical.md`, `build/python.md`), each rule carrying its own
why, and an `index.md` whose opening sentence is
the standard's remit. Which check decides each rule is
[the verifier table](/standards/verifiers.yaml), and where each check
runs is [the boundary table](/standards/boundaries.yaml). The rule is
the tree: **one directory, one standard**. The contract behind a
Standard file is the Standard doc-type
([doc-types/standard/](/doc-types/standard/index.md)).

## Rules live here; their subjects live elsewhere

Each standard files its *rules* in this directory; the population it
governs lives wherever that population naturally lives:

| Rules | Governed population |
|---|---|
| `build/` | every repo tree in the workspace |
| `harness/` | the harness files in every repo |
| `standard/` | the `standards/` tree itself |

The last row is the one loop: the meta-standard's population is the tree
itself, which tempts a reader to mistake this directory for a
governance hierarchy. It is not — everything here is under the
meta-standard **in form only** (the file and tree shape), while each standard's
substance governs its own population, one rung down. A rejection always
cites exactly one rung up: a bad Makefile is rejected by `build/`, never by
`standard/`.

The full catalog is [`index.md`](/standards/index.md).
