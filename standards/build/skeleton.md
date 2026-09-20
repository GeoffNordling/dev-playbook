---
type: Standard-Ruleset
title: File Skeleton
description: The tree a governed repo carries — the entries every repo requires, keeps at the root, and forbids, and the entries each layer adds
population: "a governed repo's tree, except standards/build/canonical/ in dev-playbook"
---

# File Skeleton

The entries a governed repo's tree requires, permits, and forbids. Every
governed repo is bound. A rule under no condition binds every repo, the
base layer; each
condition is a further layer, and a repo is in every layer whose test its
tree meets, inferred from facts on disk, never declared. An entry no rule
names is free. `standards/build/canonical/` in dev-playbook is quoted
material, the source of the
[canonical artifacts](/standards/build/canonical.md), and no tree rule
reads it.

The reasoning behind the rules is the
[Build Guide](/docs/guides/build.md).

## Required files

`README.md`, `CLAUDE.md`, `index.md`, `.gitignore`,
`.pre-commit-config.yaml`, and `Makefile` exist at the root, and
`.github/workflows/ci.yml` exists.

`build.required-files` · deterministic

## Root-only files

`pyproject.toml`, `CONTEXT.md`, and `CANDIDATES.md` appear at the root or
not at all, one of each.

`build.root-only-files` · deterministic

## No other future-work file

No file named `ROADMAP.md`, `TODO.md`, `BACKLOG.md`, or `IDEAS.md` exists
at any depth in the tree.

`build.no-other-future-work-file` · deterministic

## Runnables live in scripts/

No `bin/` directory and no `tools/` directory exists at the root.

`build.runnables-live-in-scripts` · deterministic

## Dependencies live in pyproject.toml

No file named `requirements.txt` exists anywhere in the tree.

`build.dependencies-live-in-pyprojecttoml` · deterministic

## Python

A repo in which `pyproject.toml` exists at the root.

`build.python` · deterministic

### uv.lock and .python-version

`uv.lock` is tracked and `.python-version` exists, both at the root.

`build.uvlock-and-python-version` · deterministic

## Python package

A Python repo in which `src/` exists.

`build.python-package` · deterministic

### One package under src/

`src/` holds exactly one entry: a directory whose name is the import
package the [name mapping](/standards/build/python.md#name-mapping)
names.

`build.one-package-under-src` · deterministic

## Python source

A repo in which `src/` exists beside a root `pyproject.toml`, or
`scripts/` holds a [Python file](/standards/build/python.md#scripts).

`build.python-source` · deterministic

### tests/ present

`tests/` exists and is not empty.

`build.tests-present` · deterministic

## JavaScript

A repo in which `package.json` exists at the root.

`build.javascript` · deterministic

### Lockfile committed

A lockfile, `package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, `bun.lock`,
or `bun.lockb`, is tracked beside `package.json`.

`build.lockfile-committed` · deterministic
