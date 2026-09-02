---
type: Standard
title: The Python Project
description: The root Python project — the name mapping, what a Python file in scripts/ carries, and when an entry point is declared
population: "a governed repo's root Python project: pyproject.toml, the package under src/, and the Python under scripts/"
---

# The Python Project

A governed repo has one Python project, at the root
([File Skeleton](/standards/build/skeleton.md#root-only-files)); this
Standard binds it. Its `pyproject.toml` is a canonical artifact
([Canonical Artifacts](/standards/build/canonical.md#pyprojecttoml)).
Code-level conventions are [Python Style](/standards/python/style.md);
pytest conventions are
[Testing Conventions](/standards/testing/conventions.md).

## Name mapping

The project `name` is the repo name lowercased, `My-Repo` → `my-repo`, and
the import package is the project name with each hyphen an underscore,
`my_repo`; further code nests inside that package as subpackages.

## Entry points

`[project.scripts]` is declared only when the project has a CLI, each
entry `<command> = "<package>.cli:main"`.

```toml
[project.scripts]
<command> = "<package>.cli:main"
```

## Scripts

A Python file under `scripts/`.

### Shebang and inline metadata

An executable Python file in `scripts/` opens with
`#!/usr/bin/env -S uv run --script` and carries a PEP 723 inline block
whose `requires-python` states the floor matching `.python-version`.

It then runs from a bare clone with nothing installed, which a pre-commit
hook `entry` requires.

### Package-backed scripts are shims

A script that imports the package is exposed as an entry point, and a file
for it exists in `scripts/` only when a checked-in path is required, a
pre-commit `entry`, as a thin shim that carries the shebang and block
above.
