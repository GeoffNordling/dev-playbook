---
type: Guide
title: Build Guide
description: The thinking behind the build rules — layers inferred from the tree, what each required file is for, the four strengths of a canonical compare, what a green check means, why CI runs no tests, and the reasons behind the pyproject pins
---

# Build Guide

The guide behind the three build rulesets,
[File Skeleton](/standards/build/skeleton.md),
[Canonical Artifacts](/standards/build/canonical.md), and
[The Python Project](/standards/build/python.md). Each states its rules
as predicates `repo-lint` or a reviewer can decide; this guide carries
the vocabulary, the worked trees, and the reasoning that make the rules
intelligible. Nothing here is enforced; every rule is in its Standard.

## Layers are inferred, never declared

A rule under no condition binds every governed repo: that is the base
layer. Each further layer is a condition the tree meets, read from
facts on disk. A repo is Python because `pyproject.toml` exists at its
root ([Python](/standards/build/skeleton.md#python)), a Python package
because `src/` exists beside it
([Python package](/standards/build/skeleton.md#python-package)), and
JavaScript because `package.json` exists
([JavaScript](/standards/build/skeleton.md#javascript)). The package
condition is a conjunction on purpose: `src/` is the default source
root of most JavaScript build tools as well, so a repo without
`pyproject.toml` is not Python, whatever it keeps in `src/`. No file
declares a layer, so no declaration can drift from the tree.

`standards/build/canonical/` in dev-playbook is quoted material, the
source of the canonical artifacts, and no tree rule reads it.

## What each required file is for

The skeleton names the files
([Required files](/standards/build/skeleton.md#required-files)); what
each holds is another Standard's rule.

- `README.md` —
  [README Content](/standards/knowledge-organization/readme-content.md).
- `CLAUDE.md` —
  [CLAUDE.md Content](/standards/harness/claude-content.md).
- `index.md` — [Indexes](/standards/knowledge-organization/indexes.md),
  which also places the further indexes wherever concept documents
  live.
- `.gitignore`, `.pre-commit-config.yaml`, `Makefile`, and `ci.yml` —
  [Canonical Artifacts](/standards/build/canonical.md), one rule per
  file.
- `CONTEXT.md` — the vocabulary center
  ([CONTEXT.md Content](/standards/knowledge-organization/context-content.md)).
- `CANDIDATES.md` — the register of uncommitted future work
  ([Tracking Guide](/docs/guides/tracking.md#candidates)).
- `pyproject.toml` — the one Python project
  ([The Python Project](/standards/build/python.md)).

Checked-in runnables, in any language, live in `scripts/`. Shell there
is gated by shellcheck and shfmt
([Shell Conventions](/standards/shell/conventions.md)); Python there is
bound by the shebang rule
([Shebang and inline metadata](/standards/build/python.md#shebang-and-inline-metadata)).
Dependencies are declared in `pyproject.toml` and locked in `uv.lock`,
which is why no `requirements.txt` exists anywhere in the tree.

## Additions are free

An entry no rule names is free. A tree is rejected only for a required
entry absent, a root-only entry elsewhere, a forbidden entry present,
or a canonical copy drifted. Entries a repo carries when it has the
content, each governed by the Standard that owns the content:

- `artifacts.mk` — the build products the gate needs that git does not
  carry ([artifacts.mk](/standards/build/canonical.md#artifactsmk)).
- `docs/` — guides and surveys that outgrow the README, each an OKF
  concept document.
- `docs/decisions/` — Decision Records
  ([Decision Record Conventions](/standards/decisions/records.md)).
- `working-docs/` — the working documentation sets, one directory per
  line of work, each kept as long as its work runs
  ([Working Documentation Sets](/standards/knowledge-organization/documentation-sets/working-documentation-sets.md#where-a-set-lives)).
- `.claude/` — Claude Code files; `worktrees/` under it is gitignored.

A base tree:

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

A full stack, Python with a package and scripts:

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

## The files are the standard

The canonical artifacts live once, under `standards/build/canonical/`,
and the consuming tools demand real files in place, so each governed
repo carries a copy. The files are the standard: `repo-lint` compares
each copy to its source at the strength its rule names, and the source
directory ships inside every hook clone, so the compare needs no
network. The four strengths:

- **Byte-identical** — `ci.yml` and `.python-version`.
- **Verbatim line blocks** — `.pre-commit-config.yaml` and the
  `Makefile`; extra lines may surround a block, and the dev-playbook
  `rev` pin is the consumer's own value.
- **Baseline patterns** — `.gitignore`; comments and order are free.
- **Parsed values** — `pyproject.toml`; the settings the canonical file
  pins must match, and additions are free.

## What a green check means

`check` is the universal Makefile target and means the same thing in
every repo: green `check` means every deterministic check whose remedy
is in the repo's own hands passes. Its recipe is the full hook suite,
and layers add prerequisites; in a Python repo
`check: format-check lint typecheck test`. `check` is also the pre-push
hook's entry, and it is a strict superset of the CI gate, so a green
local `check` guarantees a green cloud run. Every canonical target is
`.PHONY`.

## CI runs no tests

The workflow is one job with one real step, `pre-commit run --all-files`
with `SKIP: ref-lint`, on every push and pull request to `main`
([ci.yml](/standards/build/canonical.md#ciyml)). Tests stay local: the
workspace is local-first, and a test suite depends on dev-playbook as a
local path dependency that does not exist on a cloud runner. The
pre-push hook does not fire under `pre-commit run`, so CI stays
test-free without a rule of its own. `ref-lint` is skipped because it
resolves a cross-repo citation at its absolute path under
`~/workspace/`, a tree the runner does not have.

## Why artifacts.mk exists

A repo whose gate needs a build product git does not carry, generated
code, a compiled page, a fetched fixture, writes `artifacts.mk` at the
root. The fragment's `-include artifacts.mk` reads it where present and
is silent where absent, so a repo with no build product writes no file.

The gate's remedy is in the repo's own hands, so the gate applies it: a
gitignored build product is absent in every fresh checkout and every
fresh worktree, and a `check` that only reports it missing turns the
pre-push hook into an obstacle to bypass. `ARTIFACTS` is a prerequisite
of `test` in a Python repo, whose tests are what drive the product, and
of `check` in a base repo, which has no `test` target.

Each rule names a real file, never a `.PHONY` target: `make` then
compares timestamps and rebuilds only what is stale, so the gate pays
the build cost once per checkout and nothing on later runs.
dev-playbook's own `artifacts.mk` builds the cloa-viewer page its
end-to-end tests drive.

## The reasons behind the pyproject pins

The pinned values are listed in the rule
([pyproject.toml](/standards/build/canonical.md#pyprojecttoml)). Each
pin is a choice that looks reversible until its reason is read.

- **`uv_build`** over other backends: it is bundled inside the uv
  binary, so building the package, including editable installs by
  consumers, needs no network and no PyPI, and its default layout is
  exactly this standard's, `src/<package>` named from the project name.
- **`disallow_untyped_defs` and `disallow_incomplete_defs`** instead of
  `strict = true`: the pair guarantees every function signature is
  fully annotated, while full strict also turns on
  `disallow_untyped_calls`, which chokes on every untyped third-party
  library, and `disallow_any_generics`, which is noisy about every bare
  `list` and `dict`.
- **`disable_error_code = ["import-untyped"]`**: importing a library
  that ships no type stubs works without `# type: ignore` at each
  import site; `types-*` stub packages join `dev` when a specific
  library warrants them.
- **The ruff families** beyond the `E`, `W`, and `F` core each catch a
  distinct defect class: `I` import order, `UP` outdated syntax, `B`
  bug-prone patterns, `SIM` needless complexity, `SLF` private-member
  access from outside the defining class, and `D` docstring presence
  and format, which enforces
  [Docstrings](/standards/python/style.md#docstrings).
- **`[tool.ruff.lint.pydocstyle] convention = "pep257"`**: `D` on its
  own turns on mutually exclusive members, `D203` against `D211` and
  `D212` against `D213`, so `ruff check` is unsatisfiable until a
  `convention` selects between them. Per-file ignores then drop all of
  `D` for `tests/**`, since test functions carry no docstrings, and
  `D104` for `__init__.py`, since an empty init has none.
- **`ignore = ["E501", "D401"]`**: `ruff format` owns line length, so
  the `E501` lint rule would report the same overruns a second time;
  `D401`, imperative-mood summaries, is dropped to keep the workspace's
  noun-phrase docstring voice.

## One version set

The Python interpreter, ruff, mypy, pytest, and every hook `rev` are
pinned once, in the canonical artifacts, at the latest stable release,
and every copy carries the same value; a standalone script's PEP 723
`requires-python` states the same floor as `.python-version`. Exact
resolutions live in each repo's `uv.lock`.

## Package-backed scripts are shims

A script that imports the package is exposed as an entry point
([Entry points](/standards/build/python.md#entry-points)), and a file
for it exists in `scripts/` only when a checked-in path is required, a
pre-commit `entry`, as a thin shim that carries the shebang and the
inline metadata block. The shebang `#!/usr/bin/env -S uv run --script`
is what lets the file run from a bare clone with nothing installed,
which a pre-commit hook `entry` requires.
