---
type: Standard
title: File Skeleton
description: The tree a governed repo carries — the entries every repo requires, keeps at the root, and forbids, and the entries each layer adds, with worked trees
population: "a governed repo's tree, except standards/build/canonical/ in dev-playbook"
---

# File Skeleton

The entries a governed repo's tree requires, permits, and forbids. Every
repo on the [roster](/standards/distribution/channel.md#the-roster) is
bound. A rule under no condition binds every repo, the base layer; each
condition is a further layer, and a repo is in every layer whose test its
tree meets, inferred from facts on disk, never declared.
`standards/build/canonical/` in dev-playbook is quoted material, the source
of the [canonical artifacts](/standards/build/canonical.md), and no tree
rule reads it. `repo-lint` is the authority on conformance
([Build](/standards/build.md)).

## Required files

`README.md`, `CLAUDE.md`, `index.md`, `.gitignore`,
`.pre-commit-config.yaml`, and `Makefile` exist at the root, and
`.github/workflows/ci.yml` exists.

What each holds is another Standard's rule:

- `README.md` —
  [README Content](/standards/knowledge-organization/readme-content.md).
- `CLAUDE.md` —
  [CLAUDE.md Content](/standards/harness/claude-content.md).
- `index.md` — [Indexes](/standards/knowledge-organization/indexes.md),
  which also places the further indexes wherever concept documents live.
- `.gitignore`, `.pre-commit-config.yaml`, `Makefile`, and `ci.yml` —
  [Canonical Artifacts](/standards/build/canonical.md), one rule per file.

## Root-only files

`pyproject.toml`, `CONTEXT.md`, and `CANDIDATES.md` appear at the root or
not at all, one of each.

`CONTEXT.md` is the vocabulary center
([CONTEXT.md Content](/standards/knowledge-organization/context-content.md));
`CANDIDATES.md` is the register of uncommitted future work
([Candidates](/standards/tracking/candidates.md)); `pyproject.toml` is the
one Python project ([The Python Project](/standards/build/python.md)).

## Runnables live in scripts/

Checked-in runnables, in any language, live in `scripts/`; no `bin/` or
`tools/` directory exists at the root.

Shell in `scripts/` is gated by shellcheck and shfmt
([Shell](/standards/shell.md)); Python in `scripts/` is bound by
[The Python Project](/standards/build/python.md#scripts).

## Dependencies live in pyproject.toml

Dependencies are declared in `pyproject.toml` and locked in `uv.lock`; no
`requirements.txt` exists anywhere in the tree.

## Python

A repo in which `pyproject.toml` exists at the root.

### uv.lock and .python-version

`uv.lock` is tracked and `.python-version` exists, both at the root.

`.python-version` is a
[canonical artifact](/standards/build/canonical.md#python-version).

## Python package

A Python repo in which `src/` exists.

### One package under src/

`src/` holds exactly one directory, the import package the
[name mapping](/standards/build/python.md#name-mapping) names.

## Python source

A repo in which `src/` exists beside a root `pyproject.toml`, or `scripts/`
holds a `.py` file.

### tests/ present

`tests/` exists and is not empty.

Its content is [Testing Conventions](/standards/testing/conventions.md)'.

## JavaScript

A repo in which `package.json` exists at the root.

### Lockfile committed

A lockfile, `package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, `bun.lock`,
or `bun.lockb`, is tracked beside `package.json`.

## Additions are free

An entry no rule names is free: a tree is rejected only for a required
entry absent, a root-only entry elsewhere, a forbidden entry present, or a
canonical copy drifted.

Entries a repo carries when it has the content, each governed by the
Standard that owns the content:

- `docs/` — guides and surveys that outgrow the README, each an OKF concept
  document.
- `docs/decisions/` — Decision Records
  ([Decision Record Conventions](/standards/decisions/records.md)).
- `readings/` — instrument output, one subdirectory per instrument
  ([Instruments and Instrument Specs](/standards/instrument/format.md)).
- `.claude/` — Claude Code files ([Harness Files](/standards/harness/index.md));
  `worktrees/` under it is gitignored.

A base tree:

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

A full stack, Python with a package and scripts:

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
