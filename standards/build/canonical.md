---
type: Standard
title: Canonical Artifacts
description: The canonical artifacts — the single-source files under standards/canonical/ and how each repo copy is compared
---

# Canonical Artifacts

The standard's machine-checkable content lives **once**, as files in
dev-playbook under [`standards/canonical/`](/standards/canonical/index.md),
shipped inside every hook clone
([distribution.md](/standards/build/distribution.md)). Prose points at them
and does not restate their contents — the files are the standard. Each
repo's working copies exist because the consuming tools demand real files in
place, and `repo-audit` enforces them equal to the canonical source:

| Artifact | Compared how |
|---|---|
| [ci.yml](/standards/canonical/ci.yml) | whole file, byte-identical |
| [.python-version](/standards/canonical/.python-version) | whole file, byte-identical |
| [.pre-commit-config.yaml](/standards/canonical/.pre-commit-config.yaml) | canonical blocks present verbatim; extra hooks may follow |
| [Makefile.base](/standards/canonical/Makefile.base) / [Makefile.python](/standards/canonical/Makefile.python) / [Makefile.aws](/standards/canonical/Makefile.aws) | the repo's layer-matching targets present verbatim; extra targets may follow |
| [pyproject.toml](/standards/canonical/pyproject.toml) | canonical blocks present verbatim |
| [.gitignore](/standards/canonical/.gitignore) | baseline lines present |

`standards/canonical/` is quoted material: hooks and tree rules skip it —
its `pyproject.toml` is a template, not a second project. The directory also
holds the documentation baselines ([CLAUDE.md](/standards/canonical/CLAUDE.md),
[CONTEXT.md](/standards/canonical/CONTEXT.md)), which are floors per
[repo-documentation.md](/standards/repo-documentation.md), not byte-compared
artifacts.

## One config serves every repo

The canonical [.pre-commit-config.yaml](/standards/canonical/.pre-commit-config.yaml)
carries the dev-playbook hook set, the ruff and shellcheck hooks at canonical
revs, and the pre-push `make check` hook, installing both the commit and
push stages. It serves every repo unchanged: a hook with no matching files
skips itself, and `judgments-lint` passes where no `[tool.judgments]` table
exists. Repos that author skills append `internal-skill-audit`; dev-playbook
replaces the published block with its dogfood block
([distribution.md](/standards/build/distribution.md#dogfooding)).

## Versions

One version set for the whole workspace: the Python interpreter
(`.python-version`), ruff, mypy, pytest, and every hook `rev` are defined
once, in the canonical artifacts — latest stable, identical in all repos,
bumped deliberately. Exact resolutions live in each repo's `uv.lock`.
