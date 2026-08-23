---
type: Standard
title: Layers
description: The layered model — the base layer, inferred membership, what each layer adds, and the additions-are-free rule
---

# Layers

Every workspace repository conforms to one layered standard: a **base layer**
that applies to every repo, plus each further layer the repo is in. Layer
membership is inferred from facts on disk, never declared. Conformance is
machine-checked — this prose describes the rules; the `repo-lint` hook is
the authority ([enforcement.md](/standards/build/enforcement.md)).

| Layer | A repo is in it when | It adds |
|---|---|---|
| base | always | the docs skeleton, `Makefile`, pre-commit, thin CI |
| python | `pyproject.toml` exists | the root Python project — [python.md](/standards/build/python.md) |
| python · src | `src/` exists | the importable package |
| python · scripts | `scripts/` holds Python | tested, runnable Python scripts |
| python · aws | `cdk.json` exists | the CDK shape and deploy targets — [aws.md](/standards/build/aws.md); requires src |
| js | `package.json` exists | a committed lockfile alongside `package.json`; nothing more yet |

`tests/` is not a layer: it is required the moment `src/` exists or
`scripts/` holds Python.

Each layer's concrete file requirements are the
[skeleton tables](/standards/build/skeleton.md).

## Additions are free; conflicts are not

A repo `MAY` contain anything beyond its layers' requirements, provided
required files stay present and canonical, and forbidden files stay absent.
A deviation from a requirement is an amendment to this standard in
dev-playbook.

## Deferred

Licensing: the standard takes no position on `LICENSE` files.
