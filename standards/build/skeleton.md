---
type: Standard
title: File Skeleton
description: The per-layer file skeleton — required, optional, and forbidden entries, with worked example trees
---

# File Skeleton

The files each [layer](/standards/build/layers.md) requires, permits, and
forbids.

## Base layer — every repo

| Entry | Presence | Rule |
|---|---|---|
| `README.md` | Required | content per [readme-content.md](/standards/knowledge-organization/readme-content.md) |
| `CLAUDE.md` | Required | content per [claude-content.md](/standards/harness/claude-content.md) |
| `index.md` | Required | at the root; further indexes wherever concept docs live; content per [indexes.md](/standards/knowledge-organization/indexes.md) |
| `.gitignore` | Required | contains the canonical baseline lines; `MAY` extend |
| `.pre-commit-config.yaml` | Required | contains the canonical blocks; `MAY` append further hooks |
| `Makefile` | Required | contains the canonical targets for the repo's layers |
| `.github/workflows/ci.yml` | Required | byte-identical to the canonical thin CI |
| `scripts/` | Optional | sole home for checked-in runnables, any language; `bin/` and `tools/` are forbidden at the root |
| `CONTEXT.md` | Optional | root only; content per [context-content.md](/standards/knowledge-organization/context-content.md) |
| `CANDIDATES.md` | Optional | root only, one per repo; the register of uncommitted future work, content per [tracking/candidates.md](/standards/tracking/candidates.md) |
| `docs/` | Optional | guides and surveys that outgrow the README, each an OKF concept doc |
| `docs/decisions/` | Optional | Decision Records per [decisions/records.md](/standards/decisions/records.md) |
| `readings/` | Optional | instrument output artifacts, one subdirectory per instrument, per [the instrument standard](/standards/instrument/format.md); regenerated manually on demand, never hand-edited, may lag what it describes |
| `.claude/` | Optional | Claude Code files per [the harness-files standard](/standards/harness/index.md); `worktrees/` gitignored |
| `requirements.txt` | Forbidden | anywhere in the tree; dependencies live in `pyproject.toml` + `uv.lock` |
| `ROADMAP.md`, `TODO.md`, `BACKLOG.md`, `IDEAS.md` | Forbidden | anywhere in the tree; uncommitted work lives in `CANDIDATES.md` and committed work in issues, per [tracking/candidates.md](/standards/tracking/candidates.md) |

## python layer

| Entry | Presence | Rule |
|---|---|---|
| `pyproject.toml` | Required | at the root, the only one in the tree; canonical blocks — see [pyproject.toml](/standards/build/python.md#pyprojecttoml) |
| `uv.lock` | Required | committed |
| `.python-version` | Required | byte-identical to the canonical pin |
| `tests/` | Required | non-empty (every Python repo has `src/` or Python `scripts/`) |

## python · src

| Entry | Presence | Rule |
|---|---|---|
| `src/<package>/` | Required | exactly one package, named per the [name mapping](/standards/build/python.md#name-mapping) |

## python · scripts

| Entry | Presence | Rule |
|---|---|---|
| `scripts/*.py` | — | executable, tested; shape per [Scripts](/standards/build/python.md#scripts) |

## Worked trees

Base only:

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

Full stack (python · src · scripts):

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
