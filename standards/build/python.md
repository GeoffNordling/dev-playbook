---
type: Standard
title: The Python Project
description: The root Python project — the name mapping, what a Python file in scripts/ carries, and when an entry point is declared
population: "a governed repo's root Python project: pyproject.toml, the package under src/, and the Python under scripts/"
---

# The Python Project

A governed repo has one Python project, at the root
([File Skeleton](/standards/build/skeleton.md#root-only-files)); this
Standard binds it.

## Name mapping

The root `pyproject.toml` sets `project.name` to the repo directory's
name lowercased, `My-Repo` → `my-repo`, and the import package is that
name with each hyphen an underscore, `my_repo`.

`build.name-mapping` · deterministic

## Entry points

`[project.scripts]` in the root `pyproject.toml` is absent, or every
entry under it has the value `<package>.cli:main`, where `<package>` is
the import package and `src/<package>/cli.py` defines `main`.

`build.entry-points` · deterministic

## Scripts

A Python file under `scripts/`: a file whose name ends in `.py`, or a
file with no extension whose first line is a Python shebang.

`build.scripts` · deterministic

### Shebang and inline metadata

An executable Python file under `scripts/` has
`#!/usr/bin/env -S uv run --script` as its first line and carries a
PEP 723 inline metadata block opened by a line reading `# /// script`;
where the repo has a root `.python-version`, that block's
`requires-python` value is `>=` followed by the contents of
`.python-version`, `>=3.13` for a `.python-version` of `3.13`.

`build.shebang-and-inline-metadata` · deterministic

> **Why.** The shebang `#!/usr/bin/env -S uv run --script` is what
> lets the file run from a bare clone with nothing installed, which a
> pre-commit hook `entry` requires.
