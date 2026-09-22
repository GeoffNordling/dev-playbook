---
type: Standard
title: The Python Project
description: The root Python project — the name mapping, what a Python file in scripts/ carries, and when an entry point is declared
population: "a governed repo's root Python project: pyproject.toml, the package under src/, and the Python under scripts/"
---

# The Python Project

A governed repo has one Python project, at the root
([File Skeleton](/standards/build/skeleton.md#one-at-the-root-or-none)); this
Standard binds it.

## The repo directory names the project and package

The root `pyproject.toml` sets `project.name` to the repository's own
name lowercased, the directory holding the shared `.git` and so the same
from the main checkout and every worktree, `My-Repo` to `my-repo`, and
the import package is that name with each hyphen an underscore,
`my_repo`.

`build.the-repo-directory-names-the-project-and-package` · deterministic

## Every entry point resolves to a module's main

`[project.scripts]` in the root `pyproject.toml` is absent, or every
entry under it has the value `<module>:main`, where `<module>` is a
module inside the import package and that module defines `main`.

`build.every-entry-point-resolves-to-a-modules-main` · deterministic

## Scripts

A Python file under `scripts/`: a file whose name ends in `.py`, or a
file with no extension whose first line is a Python shebang.

### Executable scripts carry the uv shebang and inline metadata

An executable Python file under `scripts/` has
`#!/usr/bin/env -S uv run --script` as its first line and carries a
PEP 723 inline metadata block opened by a line reading `# /// script`;
where the repo has a root `.python-version`, that block's
`requires-python` value is `>=` followed by the contents of
`.python-version`, `>=3.13` for a `.python-version` of `3.13`.

`build.executable-scripts-carry-the-uv-shebang-and-inline-metadata` · deterministic

> **Why.** The shebang `#!/usr/bin/env -S uv run --script` is what
> lets the file run from a bare clone with nothing installed, which a
> pre-commit hook `entry` requires.
