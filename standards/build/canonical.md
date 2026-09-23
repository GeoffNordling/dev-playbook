---
type: Standard
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

> **Why.** The source directory ships inside every hook clone, so a
> copy is compared against its source with no network.

## ci.yml byte-identical to canonical

`.github/workflows/ci.yml` is byte-identical to the canonical
[ci.yml](/standards/build/canonical/ci.yml).

`build.ciyml-byte-identical-to-canonical` · deterministic

> **Why.** The canonical workflow runs the hook suite and no tests,
> because a test suite depends on dev-playbook as a local path
> dependency a cloud runner does not have. It sets `SKIP: workspace` for
> the same reason: the checks tagged `workspace` resolve a cross-repo
> citation at its absolute path under `~/workspace/`, a tree the runner
> does not have.

## .python-version byte-identical to canonical

`.python-version` is byte-identical to the canonical
[.python-version](/standards/build/canonical/.python-version).

`build.python-version-byte-identical-to-canonical` · deterministic

## .pre-commit-config.yaml holds every canonical block

`.pre-commit-config.yaml` holds every block of the canonical
[.pre-commit-config.yaml](/standards/build/canonical/.pre-commit-config.yaml)
verbatim and in order; hooks may follow inside a block, further `repo:`
blocks may sit between blocks, and the line pinning the dev-playbook `rev`
carries the consumer's own value. The repo that carries
`standards/build/canonical/` is exempt from the block holding that `rev`.

`build.pre-commit-configyaml-holds-every-canonical-block` · deterministic

## Makefile holds its layer's targets

`Makefile` holds the targets of its layer's fragment verbatim and
unbroken, [Makefile.base](/standards/build/canonical/Makefile.base) in a
repo with no root `pyproject.toml` or
[Makefile.python](/standards/build/canonical/Makefile.python) in a repo
with one, with `<code-roots>` replaced by whichever of `src`, `tests`,
and `scripts` hold a `.py` file, in that order; further targets may
follow.

`build.makefile-holds-its-layers-targets` · deterministic

## pyproject.toml matches every pinned value

`pyproject.toml` parses as TOML and matches every value the canonical
[pyproject.toml](/standards/build/canonical/pyproject.toml) pins:
`project.requires-python`, `tool.pytest.ini_options.testpaths`,
`tool.ruff.target-version`, `tool.ruff.line-length`,
`tool.ruff.lint.select`, `tool.ruff.lint.ignore`,
`tool.ruff.lint.pydocstyle.convention`, and every `[tool.mypy]` key.
Where the canonical file writes a placeholder, the copy writes its own
name: `project.name` is the project name
[The Python Project](/standards/build/python.md#the-repo-directory-names-the-project-and-package) fixes, and
`tool.ruff.lint.isort.known-first-party` is the one-item list holding the
import package. `[dependency-groups] dev` carries every floor the
canonical file lists. In a repo with `src/`, every `[build-system]` key
matches the canonical one; a repo without `src/` omits `[build-system]`
and sets `[tool.uv] package = false`. Every other value is free.

`build.pyprojecttoml-matches-every-pinned-value` · deterministic

> **Why.** Each pinned value is a choice that looks reversible without
> its reason. `uv_build` is bundled inside the uv binary, so building
> the package, an editable install by a consumer included, needs no
> network and no PyPI, and its default layout is this standard's,
> `src/<package>` named from the project name. The pair
> `disallow_untyped_defs` and `disallow_incomplete_defs` stands in for
> `strict = true`, which also turns on `disallow_untyped_calls`,
> choking on every untyped third-party library, and
> `disallow_any_generics`, noisy about every bare `list` and `dict`.
> `tool.ruff.lint.pydocstyle.convention` is not a preference: `D` on
> its own turns on mutually exclusive members, `D203` against `D211`
> and `D212` against `D213`, so `ruff check` is unsatisfiable unless a
> convention selects between them. `E501` is ignored because
> `ruff format` owns line length and the lint would report the same
> overruns a second time, and `D401`, imperative-mood summaries,
> because the workspace writes noun-phrase docstrings.

## .gitignore holds every canonical pattern

`.gitignore` holds every pattern of the canonical
[.gitignore](/standards/build/canonical/.gitignore); comments and order
are free, and further patterns may follow.

`build.gitignore-holds-every-canonical-pattern` · deterministic

## One version set

**The Python version is written once.** `.python-version` holds
the version. `requires-python` is `>=` that version,
`tool.ruff.target-version` is `py` plus that version with the dot
removed, and `tool.mypy.python_version` equals it.

**The ruff version is written once.** The ruff `rev` in the
canonical `.pre-commit-config.yaml` and the `ruff>=` floor in the
canonical `pyproject.toml` carry the same version.

`build.one-version-set` · deterministic

> **Why.** The pins are meant to be the latest stable releases, bumped
> together; that is why a version pinned in two files must agree.
