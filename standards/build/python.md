---
type: Standard
title: The Python Project
description: The root Python project — name mapping, the canonical pyproject.toml, scripts, entry points, and initial setup
---

# The Python Project

A repo has at most one Python project: `pyproject.toml` at the root, per the
[skeleton](/standards/build/skeleton.md). A repo that genuinely needs
multiple projects uses a
[uv workspace](https://docs.astral.sh/uv/concepts/workspaces/) — one root
`uv.lock`, members declared in the root `pyproject.toml` — and amends this
standard first. Code-level conventions live in
[python/style.md](/standards/python/style.md); pytest
conventions in [testing/conventions.md](/standards/testing/conventions.md).

## Name mapping

Repo name → project `name`: lowercased (`My-Repo` → `my-repo`). Project name
→ import package: hyphens become underscores (`my_repo`). Further code nests
inside that package as subpackages.

## pyproject.toml

The canonical shape is [/standards/build/canonical/pyproject.toml](/standards/build/canonical/pyproject.toml),
with `<repo>` and `<package>` placeholders. It pins: the `uv_build` backend,
pytest `testpaths`, the `dev` dependency group (mypy, pytest, ruff floors),
the ruff target/line-length/rule selection (including the pydocstyle
`convention` and the `tests/**` + `__init__.py` docstring per-file-ignores),
and the mypy strictness set. `requires-python` states the floor matching
`.python-version`.

A scripts-only repo (no `src/`) is not a package: it sets
`[tool.uv] package = false` and omits `[build-system]`; everything else is
unchanged.

### Rationale

The reasons behind the canonical file's pins:

- **`uv_build`** over other backends: it is bundled inside the uv binary,
  so building the package — including editable installs by consumers —
  needs no network and no PyPI, and its default layout is exactly this
  standard's (`src/<package>`, named from the project name).
- **`disallow_untyped_defs` + `disallow_incomplete_defs`** instead of
  `strict = true`: the pair guarantees every function signature is fully
  annotated, while full strict also turns on `disallow_untyped_calls`
  (chokes on every untyped third-party lib) and `disallow_any_generics`
  (noisy about every bare `list`/`dict`).
- **`disable_error_code = ["import-untyped"]`**: importing a library that
  ships no type stubs works without `# type: ignore` at each import site;
  `types-*` stub packages join `dev` when a specific library warrants them.
- **The ruff families** beyond the `E`/`W`/`F` core: each catches a
  distinct defect class — `I` import order, `UP` outdated syntax, `B`
  bug-prone patterns, `SIM` needless complexity, `SLF` private-member
  access from outside the defining class, and `D` docstring presence and
  format (pydocstyle), enforcing the docstring conventions in
  [python/style.md](/standards/python/style.md).
- **`[tool.ruff.lint.pydocstyle] convention = "pep257"`**: `D` on its own
  turns on mutually-exclusive members (`D203` vs `D211`, `D212` vs `D213`),
  so `ruff check` is unsatisfiable until a `convention` selects between
  them — pinning it is what keeps the family usable. Per-file ignores then
  drop all of `D` for `tests/**` (test functions carry no docstrings by
  convention) and `D104` for `__init__.py` (an empty init has none — see
  `python.empty-init`).
- **`ignore = ["E501", "D401"]`**: `ruff format` owns line length, so the
  `E501` lint rule would report the same overruns a second time; `D401`
  (imperative-mood summaries) is dropped to keep the workspace's
  noun-phrase docstring voice.

## Scripts

For Python files in `scripts/`:

- **Standalone script** (imports nothing from the repo): shebang
  `#!/usr/bin/env -S uv run --script`, dependencies declared in a PEP 723
  inline block whose `requires-python` states the floor matching
  `.python-version`. Runs from a bare clone with nothing installed — what
  pre-commit hook entries require.
- **Script backed by the package**: expose it as an entry point (below)
  instead of path-hacking imports. A file in `scripts/` then exists only
  when a checked-in path is required (a pre-commit `entry`), as a thin
  shim.
- **Workspace-wide utility**: `uv tool install -e .` puts the project's
  entry points on `PATH` machine-wide, editable — the tool tracks the
  checkout.

## Entry points

When the project exposes a CLI, declare it:

```toml
[project.scripts]
<command> = "<package>.cli:main"
```

Lazy — present only when a CLI actually exists.

## Initial setup

`uv init --package <repo>` generates the uv_build src layout; overwrite the
generated `pyproject.toml` with the canonical shape.
