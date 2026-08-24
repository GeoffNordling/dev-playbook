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
| python · src | `pyproject.toml` and `src/` both exist | the importable package |
| python · scripts | `scripts/` holds Python | tested, runnable Python scripts |
| js | `package.json` exists | a committed lockfile alongside `package.json`; nothing more yet |

`tests/` is not a layer: it is required the moment a repo is in
`python · src` or `python · scripts`.

`src/` is the default source root of most JavaScript build tools as well, so
the `python · src` trigger is a conjunction: a repo without `pyproject.toml`
is not in the python layer, and therefore not in `python · src`, whatever it
keeps in `src/`.

Each layer's concrete file requirements are the
[skeleton tables](/standards/build/skeleton.md).

## Additions are free; conflicts are not

A repo `MAY` contain anything beyond its layers' requirements, provided
required files stay present and canonical, and forbidden files stay absent.
A deviation from a requirement is an amendment to this standard in
dev-playbook.

## Deferred

Licensing: the standard takes no position on `LICENSE` files.
