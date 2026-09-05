---
type: Standard
title: Canonical Artifacts
description: The files that live once under standards/build/canonical/ — how each governed repo's copy is compared, what the Makefile targets mean, and the one version set
population: "a canonical artifact: its source under standards/build/canonical/ and each governed repo's copy"
---

# Canonical Artifacts

The build standard's machine-checkable content lives once, as files under
`standards/build/canonical/` in dev-playbook, and each governed repo
carries a working copy of every artifact its layers require, because the
consuming tools demand real files in place. The files are the standard:
`repo-lint` compares each copy to its source at the strength its rule
names, and the source directory ships inside every hook clone
([Distribution Channel](/standards/distribution/channel.md)). The
directory is quoted material, outside every tree rule
([File Skeleton](/standards/build/skeleton.md)); its `pyproject.toml` is a
template.

## ci.yml

`.github/workflows/ci.yml` is byte-identical to the canonical
[ci.yml](/standards/build/canonical/ci.yml).

The workflow is one job with one real step, `pre-commit run --all-files`
with `SKIP: ref-lint`, on every push and pull request to `main`. It runs
the hook suite and nothing else; tests run at the
[push gate](/standards/standard/gates.md#three-rungs).

Tests stay local: the workspace is local-first, and a test suite depends
on dev-playbook as a local path dependency that does not exist on a
cloud runner. The pre-push hook does not fire under `pre-commit run`,
so CI stays test-free without a rule of its own.

## .python-version

`.python-version` is byte-identical to the canonical
[.python-version](/standards/build/canonical/.python-version).

## .pre-commit-config.yaml

`.pre-commit-config.yaml` holds every block of the canonical
[.pre-commit-config.yaml](/standards/build/canonical/.pre-commit-config.yaml)
verbatim and in order; hooks may follow inside a block and further `repo:`
blocks may sit between blocks, and the dev-playbook `rev` is the
consumer's own pin.

The canonical config carries the pinned `playbook-lint` hook, dev-playbook's
whole detector set behind one id, the ruff, shellcheck, and shfmt hooks at
canonical revs, and the pre-push `make check-judgments-cache` hook,
installing both the commit and push stages. In dev-playbook the pinned
block is absent, replaced by the dogfood block
([Distribution Channel](/standards/distribution/channel.md#dogfood-in-place-of-the-pin)).

## Makefile

`Makefile` holds the targets of its layer's fragment verbatim,
[Makefile.base](/standards/build/canonical/Makefile.base) in a base repo or
[Makefile.python](/standards/build/canonical/Makefile.python) in a Python
repo with `<code-roots>` replaced by whichever of `src`, `tests`, and
`scripts` hold `.py` files; further targets may follow.

`check` is the universal target and means the same thing everywhere: green
`check` = every deterministic check whose remedy is in the repo's own
hands passes. Its recipe is the full hook suite, and layers add
prerequisites; in a Python repo `check: format-check lint typecheck test`.
`check-judgments-cache` is `check` with the semantic
[cache gate](/standards/semantic-validation/cache-gate.md) armed and is
the pre-push hook's entry; a machine without the cache sets
`NO_JUDGMENT_CACHE=1` ([Machines](/docs/machines.md)). Every canonical
target is `.PHONY`. `check` is a strict superset of the CI gate, so a
green local `check` guarantees a green cloud run.

## pyproject.toml

`pyproject.toml` matches every value the canonical
[pyproject.toml](/standards/build/canonical/pyproject.toml) pins, parsed
from TOML; `[dependency-groups] dev` carries each floor the canonical file
lists; in a repo with `src/`, `[build-system]` matches the canonical one,
and a repo without `src/` sets `[tool.uv] package = false` and omits
`[build-system]`; additions are free.

The pinned values: `project.name`, the project name of the
[name mapping](/standards/build/python.md#name-mapping);
`requires-python`, the floor matching `.python-version`; pytest
`testpaths`; the ruff `target-version`, `line-length`, `select`, and
`ignore`; the pydocstyle `convention`; isort `known-first-party`, the
repo's own import package; and every `[tool.mypy]` key. The floors are
mypy, pytest, and ruff. The canonical file writes `<repo>` and `<package>`
where a copy writes its own names.

The reasons behind the pins, each a choice that looks reversible until
the reason is read:

- **`uv_build`** over other backends: it is bundled inside the uv binary,
  so building the package, including editable installs by consumers,
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
  distinct defect class: `I` import order, `UP` outdated syntax, `B`
  bug-prone patterns, `SIM` needless complexity, `SLF` private-member
  access from outside the defining class, and `D` docstring presence and
  format (pydocstyle), enforcing the docstring conventions in
  [python/style.md](/standards/python/style.md).
- **`[tool.ruff.lint.pydocstyle] convention = "pep257"`**: `D` on its own
  turns on mutually-exclusive members (`D203` vs `D211`, `D212` vs `D213`),
  so `ruff check` is unsatisfiable until a `convention` selects between
  them. Per-file ignores then drop all of `D` for `tests/**` (test
  functions carry no docstrings by convention) and `D104` for
  `__init__.py` (an empty init has none).
- **`ignore = ["E501", "D401"]`**: `ruff format` owns line length, so the
  `E501` lint rule would report the same overruns a second time; `D401`
  (imperative-mood summaries) is dropped to keep the workspace's
  noun-phrase docstring voice.

## .gitignore

`.gitignore` holds every pattern of the canonical
[.gitignore](/standards/build/canonical/.gitignore); comments and order
are free, and further patterns may follow.

## The source directory

Every file under `standards/build/canonical/` is one `repo-lint` compares,
and every artifact `repo-lint` compares is there (`build.self-audit`).

## One version set

The Python interpreter, ruff, mypy, pytest, and every hook `rev` are
pinned once, in the canonical artifacts, at the latest stable release, and
every copy carries the same value; a standalone script's PEP 723
`requires-python` states the same floor as `.python-version`.

Exact resolutions live in each repo's `uv.lock`.
