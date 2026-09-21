---
type: Standard-Ruleset
title: Canonical Artifacts
description: The files that live once under standards/build/canonical/ and how each governed repo's copy is compared
population: "a canonical artifact: its source under standards/build/canonical/ and each governed repo's copy"
---

# Canonical Artifacts

The build standard's machine-checkable content lives once, as files under
`standards/build/canonical/` in dev-playbook, and each governed repo
carries a working copy of every artifact its layers require, because the
consuming tools demand real files in place. The directory is quoted
material, outside every tree rule
([File Skeleton](/standards/build/skeleton.md)); its `pyproject.toml` is a
template.

The reasoning behind the rules is the
[Build Explanation](/standards/build/explanation.md).

## ci.yml

`.github/workflows/ci.yml` is byte-identical to the canonical
[ci.yml](/standards/build/canonical/ci.yml).

`build.ciyml` · deterministic

## .python-version

`.python-version` is byte-identical to the canonical
[.python-version](/standards/build/canonical/.python-version).

`build.python-version` · deterministic

## .pre-commit-config.yaml

`.pre-commit-config.yaml` holds every block of the canonical
[.pre-commit-config.yaml](/standards/build/canonical/.pre-commit-config.yaml)
verbatim and in order; hooks may follow inside a block, further `repo:`
blocks may sit between blocks, and the line pinning the dev-playbook `rev`
carries the consumer's own value. The repo that carries
`standards/build/canonical/` is exempt from the block holding that `rev`.

`build.pre-commit-configyaml` · deterministic

## Makefile

`Makefile` holds the targets of its layer's fragment verbatim and
unbroken, [Makefile.base](/standards/build/canonical/Makefile.base) in a
repo with no root `pyproject.toml` or
[Makefile.python](/standards/build/canonical/Makefile.python) in a repo
with one, with `<code-roots>` replaced by whichever of `src`, `tests`,
and `scripts` hold a `.py` file, in that order; further targets may
follow.

`build.makefile` · deterministic

## artifacts.mk

`artifacts.mk`, where it exists at the root, sets `ARTIFACTS` to a list
of files and gives each one a rule whose target is that file's path.

`build.artifactsmk` · deterministic

## pyproject.toml

`pyproject.toml` parses as TOML and matches every value the canonical
[pyproject.toml](/standards/build/canonical/pyproject.toml) pins:
`project.requires-python`, `tool.pytest.ini_options.testpaths`,
`tool.ruff.target-version`, `tool.ruff.line-length`,
`tool.ruff.lint.select`, `tool.ruff.lint.ignore`,
`tool.ruff.lint.pydocstyle.convention`, and every `[tool.mypy]` key.
Where the canonical file writes a placeholder, the copy writes its own
name: `project.name` is the project name of the
[name mapping](/standards/build/python.md#name-mapping), and
`tool.ruff.lint.isort.known-first-party` is the one-item list holding the
import package. `[dependency-groups] dev` carries every floor the
canonical file lists. In a repo with `src/`, every `[build-system]` key
matches the canonical one; a repo without `src/` omits `[build-system]`
and sets `[tool.uv] package = false`. Every other value is free.

`build.pyprojecttoml` · deterministic

## .gitignore

`.gitignore` holds every pattern of the canonical
[.gitignore](/standards/build/canonical/.gitignore); comments and order
are free, and further patterns may follow.

`build.gitignore` · deterministic

## One version set

Every version the canonical artifacts pin, the Python interpreter, ruff,
mypy, pytest, and each hook `rev`, is the latest stable release.

`build.one-version-set` · deterministic

## The source directory

Every file directly under `standards/build/canonical/` is one a rule of
this Standard names, and every file a rule of this Standard names is
directly under `standards/build/canonical/`.

`build.the-source-directory` · deterministic
