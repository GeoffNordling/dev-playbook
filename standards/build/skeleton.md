---
type: Standard
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

## Files every repo carries

`README.md`, `CLAUDE.md`, `index.md`, `.gitignore`,
`.pre-commit-config.yaml`, and `Makefile` exist at the root, and
`.github/workflows/ci.yml` exists.

```
<repo>/
├── .github/workflows/ci.yml
├── .gitignore
├── .pre-commit-config.yaml
├── CANDIDATES.md       # optional
├── CLAUDE.md
├── Makefile
├── README.md
├── index.md
└── scripts/            # optional — shell here, gated by shellcheck and shfmt
```

`build.files-every-repo-carries` · deterministic

## One at the root, or none

`pyproject.toml`, `CONTEXT.md`, and `CANDIDATES.md` appear at the root or
not at all, one of each.

`build.one-at-the-root-or-none` · deterministic

## No other future-work file

No file named `ROADMAP.md`, `TODO.md`, `BACKLOG.md`, or `IDEAS.md` exists
at any depth in the tree.

`build.no-other-future-work-file` · deterministic

## Runnables live in scripts/

No `bin/` directory and no `tools/` directory exists at the root.

`build.runnables-live-in-scripts` · deterministic

## scripts/ holds only scripts

Every file under `scripts/` has a name ending in `.py`, `.sh`, or `.md`,
or a name with no dot and `#!/usr/bin/env -S uv run --script` as its
first line.

`build.scripts-holds-only-scripts` · deterministic

> **Why.** The canonical
> [pyproject.toml](/standards/build/canonical/pyproject.toml) has ruff
> read every file under `scripts/` as Python except a `.sh` file and a
> `.md` file, so a name with no dot says the file is a uv Python script,
> and a file of any other kind lives elsewhere.

## Dependencies live in pyproject.toml

No file named `requirements.txt` exists anywhere in the tree.

`build.dependencies-live-in-pyprojecttoml` · deterministic

## Python

A repo in which `pyproject.toml` exists at the root.

### Lock file tracked, Python version pinned

`uv.lock` is tracked and `.python-version` exists, both at the root.

`build.lock-file-tracked-python-version-pinned` · deterministic

## Python package

A Python repo in which `src/` exists.

```
<repo>/
├── .github/workflows/ci.yml
├── .gitignore
├── .pre-commit-config.yaml
├── .python-version
├── CANDIDATES.md       # optional
├── CLAUDE.md
├── CONTEXT.md          # optional
├── Makefile
├── README.md
├── docs/decisions/     # optional
├── index.md
├── pyproject.toml
├── uv.lock
├── scripts/
├── src/<package>/
│   └── __init__.py     # empty
└── tests/
```

### One package under src/

`src/` holds exactly one entry: a directory whose name is the import
package [The Python Project](/standards/build/python.md#the-repo-directory-names-the-project-and-package) names.

`build.one-package-under-src` · deterministic

## Python source

A repo in which `src/` exists beside a root `pyproject.toml`, or
`scripts/` holds a [Python file](/standards/build/python.md#scripts).

### tests/ present

`tests/` exists and is not empty.

`build.tests-present` · deterministic
