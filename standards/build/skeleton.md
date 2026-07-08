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
| `README.md` | Required | content per [readme-content.md](/standards/docs/readme-content.md) |
| `CLAUDE.md` | Required | content per [claude-content.md](/standards/claude-code/claude-content.md) |
| `index.md` | Required | at the root; further indexes wherever concept docs live; content per [indexes.md](/standards/docs/indexes.md) |
| `.gitignore` | Required | contains the canonical baseline lines; `MAY` extend |
| `.pre-commit-config.yaml` | Required | contains the canonical blocks; `MAY` append further hooks |
| `Makefile` | Required | contains the canonical targets for the repo's layers |
| `.github/workflows/ci.yml` | Required | byte-identical to the canonical thin CI |
| `scripts/` | Optional | sole home for checked-in runnables, any language; `bin/` and `tools/` are forbidden at the root |
| `CONTEXT.md` | Optional | root only; content per [context-content.md](/standards/docs/context-content.md) |
| `docs/` | Optional | guides and surveys that outgrow the README, each an OKF concept doc |
| `docs/adr/` | Optional | ADRs per [adr-conventions.md](/standards/adr-conventions.md) |
| `readings/` | Optional | instrument output artifacts, one subdirectory per instrument, per [the instrument standard](/standards/instrument/format.md); regenerated, never hand-edited |
| `specs/` | Optional | governed by the [SDD standards](~/workspace/spec-tools/sdd-standards/README.md), not the OKF profile |
| `.claude/` | Optional | Claude Code files per [the harness-files standard](/standards/claude-code/index.md); `worktrees/` gitignored |

## python layer

| Entry | Presence | Rule |
|---|---|---|
| `pyproject.toml` | Required | at the root, the only one in the tree; canonical blocks — see [pyproject.toml](/standards/build/python.md#pyprojecttoml) |
| `uv.lock` | Required | committed |
| `.python-version` | Required | byte-identical to the canonical pin |
| `tests/` | Required | non-empty (every Python repo has `src/` or Python `scripts/`) |
| `requirements.txt` | Forbidden | anywhere in the tree |

## python · src

| Entry | Presence | Rule |
|---|---|---|
| `src/<package>/` | Required | exactly one package, named per the [name mapping](/standards/build/python.md#name-mapping) |

## python · scripts

| Entry | Presence | Rule |
|---|---|---|
| `scripts/*.py` | — | executable, tested; shape per [Scripts](/standards/build/python.md#scripts) |

## python · aws

| Entry | Presence | Rule |
|---|---|---|
| `cdk.json` | Required | at the root; `src/` must exist |
| `src/<package>/app.py` | Required | the CDK entry; a root `app.py` is forbidden |
| `synth`, `diff`, `deploy` | Required | Make targets |
| `cdk.out/` | Forbidden in git | gitignored |

## Worked trees

Base only:

```
<repo>/
├── .github/workflows/ci.yml
├── .gitignore
├── .pre-commit-config.yaml
├── CLAUDE.md
├── Makefile
├── README.md
├── index.md
└── scripts/            # optional — shell here, gated by shellcheck
```

Full stack (python · src · scripts · aws):

```
<repo>/
├── .github/workflows/ci.yml
├── .gitignore
├── .pre-commit-config.yaml
├── .python-version
├── CLAUDE.md
├── CONTEXT.md          # optional
├── Makefile
├── README.md
├── cdk.json
├── docs/adr/           # optional
├── index.md
├── pyproject.toml
├── uv.lock
├── scripts/
├── src/<package>/
│   ├── __init__.py     # empty
│   └── app.py          # CDK entry
└── tests/
```
