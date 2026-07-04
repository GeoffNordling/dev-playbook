---
type: Standard
title: Build Conventions
description: The layered repo standard — layer skeletons, the Python project shape, universal make check, the hook-repo rollout, thin CI, and repo-audit
---

# Build Conventions

Every workspace repository conforms to one layered standard: a **base layer**
that applies to every repo, plus each further layer the repo is in. Layer
membership is inferred from facts on disk, never declared. Conformance is
machine-checked by the `repo-audit` hook, so every rule below is enforced
deterministically — this prose describes the rules; the hook is the authority.
This document defines which files a repo must have, what `make check`
means, where each rule is enforced, and how a change to this standard
reaches every repo.

## Layers

| Layer | A repo is in it when | It adds |
|---|---|---|
| base | always | the docs skeleton, `Makefile`, pre-commit, thin CI |
| python | `pyproject.toml` exists | the root Python project — see [The Python project](/standards/build-conventions.md#the-python-project) |
| python · src | `src/` exists | the importable package |
| python · scripts | `scripts/` holds Python | tested, runnable Python scripts |
| python · aws | `cdk.json` exists | the CDK shape and deploy targets; requires src |
| js | `package.json` exists | a committed lockfile alongside `package.json`; nothing more yet |

`tests/` is not a layer: it is required the moment `src/` exists or `scripts/`
holds Python.

**Additions are free; conflicts are not.** A repo `MAY` contain anything
beyond its layers' requirements — extra directories (a `standards/` of concept
docs, `dotfiles/`, `secrets/`), extra Make targets, extra hooks — provided
nothing conflicts with the standard: required files stay present and
canonical, forbidden files stay absent. Deviating from a requirement is done
by amending this standard in dev-playbook, never inside the consuming repo.

## File skeleton

### Base layer — every repo

| Entry | Presence | Rule |
|---|---|---|
| `README.md` | Required | scope and baseline per [repo-documentation.md](/standards/repo-documentation.md) |
| `CLAUDE.md` | Required | scope and baseline per repo-documentation.md |
| `index.md` | Required | at the root; further indexes wherever concept docs live; content per repo-documentation.md |
| `.gitignore` | Required | contains the canonical baseline lines; `MAY` extend |
| `.pre-commit-config.yaml` | Required | contains the canonical blocks; `MAY` append further hooks |
| `Makefile` | Required | contains the canonical targets for the repo's layers |
| `.github/workflows/ci.yml` | Required | byte-identical to the canonical thin CI |
| `scripts/` | Optional | sole home for checked-in runnables, any language; `bin/` and `tools/` are forbidden at the root |
| `CONTEXT.md` | Optional | root only; format per repo-documentation.md |
| `docs/`, `docs/adr/`, `specs/` | Optional | scope per repo-documentation.md |
| `.claude/` | Optional | harness-owned; `worktrees/` gitignored |

### python layer

| Entry | Presence | Rule |
|---|---|---|
| `pyproject.toml` | Required | at the root, the only one in the tree; canonical blocks — see [pyproject.toml](/standards/build-conventions.md#pyprojecttoml) |
| `uv.lock` | Required | committed |
| `.python-version` | Required | byte-identical to the canonical pin |
| `tests/` | Required | non-empty (every Python repo has `src/` or Python `scripts/`) |
| `requirements.txt` | Forbidden | anywhere in the tree |

### python · src

| Entry | Presence | Rule |
|---|---|---|
| `src/<package>/` | Required | exactly one package, named per the [name mapping](/standards/build-conventions.md#name-mapping) |

### python · scripts

| Entry | Presence | Rule |
|---|---|---|
| `scripts/*.py` | — | executable, tested; shape per [Scripts](/standards/build-conventions.md#scripts) |

### python · aws

| Entry | Presence | Rule |
|---|---|---|
| `cdk.json` | Required | at the root; `src/` must exist |
| `src/<package>/app.py` | Required | the CDK entry; a root `app.py` is forbidden |
| `synth`, `diff`, `deploy` | Required | Make targets |
| `cdk.out/` | Forbidden in git | gitignored |

### Worked trees

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

## The Python project

A repo has at most one Python project — `pyproject.toml` at the root, per
the skeleton. A repo that someday genuinely needs multiple projects uses a
[uv workspace](https://docs.astral.sh/uv/concepts/workspaces/) — one root
`uv.lock`, members declared in the root `pyproject.toml` — and amends this
standard first. Code-level conventions live in
[python-conventions.md](/standards/python-conventions.md); pytest
conventions in [testing-conventions.md](/standards/testing-conventions.md).

### Name mapping

Repo name → project `name`: lowercased (`My-Repo` → `my-repo`). Project name
→ import package: hyphens become underscores (`my_repo`). Further code nests
inside that package as subpackages.

### pyproject.toml

The canonical shape is [/standards/canonical/pyproject.toml](/standards/canonical/pyproject.toml),
with `<repo>` and `<package>` placeholders. It pins: the `uv_build` backend,
pytest `testpaths`, the `dev` dependency group (mypy, pytest, ruff floors),
the ruff target/line-length/rule selection, and the mypy strictness set.
`requires-python` states the floor matching `.python-version`.

A scripts-only repo (no `src/`) is not a package: it sets
`[tool.uv] package = false` and omits `[build-system]`; everything else is
unchanged.

### Rationale

- **`uv_build`.** uv's own build backend, bundled inside the uv binary —
  building the package (including editable installs by consumers) needs no
  network and no PyPI. Its default layout is exactly this standard's:
  `src/<package>` named from the project name.
- **`disallow_untyped_defs = true`.** Every function gets a signature.
  Lighter than full `strict = true`, which also turns on
  `disallow_untyped_calls` (chokes on every untyped third-party lib) and
  `disallow_any_generics` (noisy about every bare `list`/`dict`).
- **`disallow_incomplete_defs = true`.** Pairs with the above: a
  half-annotated signature errors instead of passing silently with no type
  information for the unannotated slots.
- **`disable_error_code = ["import-untyped"]`.** Allows imports from
  libraries without type stubs without `# type: ignore` at each import. Add
  `types-*` stub packages to `dev` when a specific library warrants them.
- **Ruff rule selection.** `E`/`W`/`F` are pycodestyle/pyflakes; `I` is
  isort; `UP` is pyupgrade; `B` is bugbear; `SIM` is simplification; `SLF`
  flags private-member access from outside the defining class. `E501` is
  ignored because line length is enforced by `ruff format`.

### Scripts

For Python files in `scripts/`:

- **Standalone script** (imports nothing from the repo): shebang
  `#!/usr/bin/env -S uv run --script`, dependencies declared in a PEP 723
  inline block. Runs from a bare clone with nothing installed — what
  pre-commit hook entries require.
- **Script backed by the package**: expose it as an entry point (below)
  instead of path-hacking imports. A file in `scripts/` then exists only
  when a checked-in path is required (a pre-commit `entry`), as a thin
  shim.
- **Workspace-wide utility**: `uv tool install -e .` puts the project's
  entry points on `PATH` machine-wide, editable — the tool tracks the
  checkout.

### Entry points

When the project exposes a CLI, declare it:

```toml
[project.scripts]
<command> = "<package>.cli:main"
```

Lazy — present only when a CLI actually exists.

### AWS

An AWS repo is one Python codebase, not a collection of per-function
mini-projects:

- `cdk.json` declares `"app": "uv run python -m <package>.app"`.
- Stacks and Lambda handlers live under `src/<package>/` as ordinary
  subpackages.
- Each Lambda's runtime dependencies are a uv dependency group; bundling
  exports the group from the lock at synth time (`uv export --group <fn>`).
  Docker bundling `MAY` be used where a group needs platform builds.

### Initial setup

`uv init --package <repo>` generates the uv_build src layout; overwrite the
generated `pyproject.toml` with the canonical shape.

## Make

Make is the task runner; every repo has a `Makefile`. `check` is the
universal target and means the same thing everywhere: **green `check` = the
repo passes everything it can verify locally**. Its recipe is identical in
every repo — run the full hook suite — and layers add prerequisites:

| Target | Layer | Recipe |
|---|---|---|
| `check` | base | `uvx pre-commit run --all-files`, after the layer prerequisites below |
| `format` (mutating) | python | `uv run ruff format .` |
| `format-check` | python | `uv run ruff format --check .` |
| `lint` | python | `uv run ruff check .` |
| `typecheck` | python | `uv run mypy <code-roots>` — whichever of `src tests scripts` exist |
| `test` | python | `uv run pytest` |
| `synth` / `diff` / `deploy` | aws | `npx cdk synth` / `npx cdk diff` / `npx cdk deploy` |

In a python repo, `check: format-check lint typecheck test`. All targets are
`.PHONY`. Repos `MAY` add targets; the canonical ones are byte-compared by
repo-audit. Because `check` is a strict superset of thin CI, a green local
`check` guarantees a green cloud run.

The `test` target includes the judgments stage-1 cache gate — a
deterministic pytest, no LLM ([judgments.md](/standards/judgments.md)).

## Venues

| Venue | Trigger | What runs |
|---|---|---|
| commit | `git commit` | the pre-commit hook suite, on staged files |
| push | `git push` | `make check`, via the pre-push-stage hook |
| agent | before every commit and before opening every PR | `make check` |
| CI | every push and PR on GitHub | thin CI — exactly `pre-commit run --all-files`, nothing else |
| sweep | on demand | GitHub settings per [repo-settings.md](/standards/repo-settings.md), via `gh api` |

`make check` runs **before push and before PR** — stated explicitly even
though a PR can only contain pushed commits, so the push gate already covered
them: an agent still re-runs `check` immediately before opening the PR.

**CI never runs tests.** Two hard reasons: this workspace is local-first (no
headless cloud agents, ever), and test suites depend on dev-playbook as a
local path dependency that does not exist on a cloud runner. The
pre-push-stage hook does not fire under `pre-commit run`, so CI stays
test-free automatically — nothing to configure, nothing to drift.

## The hook repo and rollout

dev-playbook publishes the canonical hook set as a **pre-commit hook
repository**: hook definitions live in
[`.pre-commit-hooks.yaml`](/.pre-commit-hooks.yaml), backed by executable
scripts in `scripts/`. Consumer repos reference them by URL and a pinned
revision, exactly as they reference any third-party hook. pre-commit clones
dev-playbook into its own cache at the pinned `rev` and runs the hooks from
there, so resolution is independent of where the consumer repo — or any of
its worktrees — sits on disk, and identical on CI.

Because pre-commit clones dev-playbook over HTTPS unauthenticated,
**dev-playbook must remain a public repository**.

dev-playbook consumes its own hooks from the working tree via a `repo: local`
block in its `.pre-commit-config.yaml`, so hook edits are testable in place
before release. The hook metadata appears twice *within* dev-playbook — the
published manifest serves consumers, the local block dogfoods the working
tree — and a hook change updates both. Consumers hold only a pinned pointer.

### Canonical artifacts

The standard's machine-checkable content lives **once**, as files in
dev-playbook under `standards/canonical/`, shipped inside every hook clone.
This document points at them and does not restate their contents — the files
are the standard. Each repo's working copies exist because the consuming
tools demand real files in place, and repo-audit enforces them equal to the
canonical source, so they cannot drift:

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

The canonical `.pre-commit-config.yaml` carries the dev-playbook hook set,
the ruff and shellcheck hooks at canonical revs, and the pre-push
`make check` hook, installing both the commit and push stages. One config
serves every repo: a hook with no matching files skips itself, and
`judgments-lint` passes where no `[tool.judgments]` table exists. Repos that
author skills append `internal-skill-audit`. dev-playbook itself replaces
the published block with its `repo: local` dogfood block.

### Versions

One version set for the whole workspace: the Python interpreter
(`.python-version`), ruff, mypy, pytest, and every hook `rev` are defined
once, in the canonical artifacts — latest stable, identical in all repos,
bumped deliberately. Exact resolutions live in each repo's `uv.lock`.

### The rev bump is the release

A change to the standard — hook code, canonical artifact, version pin —
reaches a consumer only when the consumer's pinned `rev` moves
(`pre-commit autoupdate`). **A standard change is complete only when every
repo's pin is current**: the sweep across all repos is part of the change,
same-day and agent-driven, not a someday follow-up. Staleness is
self-enforcing — repo-audit compares the `rev` in the consumer's config
against the revision of the clone it is running from, so a stale pin is red
at the next commit, in every `make check`, and in CI.

## Thin CI

Every repo carries the identical workflow, byte-for-byte the canonical
`ci.yml`: one job, one real step — `pre-commit run --all-files` with
`SKIP: ref-check` — on every push and PR to `main`. No tests, no
`make check`, ever.

`SKIP: ref-check` because: `ref-check` validates cross-repo Citations
(`~/workspace/<repo>/…`), and a CI runner checks out only the one repo, so
those citations can never resolve there. Local pre-commit remains the strict
reference gate. (`okf-lint` is not skipped — everything it checks is
in-repo.)

## Enforcement map

Where each tool's rules fire. Every pre-commit hook fires at **commit, in
CI, and inside every `make check`** (hence also at push, agent, and pre-PR);
the table lists only what falls outside that pattern.

| Tool | Owns | Venues |
|---|---|---|
| repo-audit | structure: presence, canonical bytes, forbidden files, layer shape, pin freshness | hook pattern |
| ruff-check / ruff-format | Python lint + formatting | hook pattern, plus `lint`/`format-check` targets |
| python-lint | workspace Python-source rules | hook pattern |
| okf-lint | concept-doc types, `index.md` freshness | hook pattern |
| ref-check | Links and Citations | hook pattern, except CI (skipped) |
| judgments-lint | judgment declarations | hook pattern |
| shellcheck | shell scripts | hook pattern |
| internal-skill-audit | skill bundles (skill-authoring repos) | hook pattern |
| mypy | types | `make check` only — never CI |
| pytest | tests + judgments stage-1 cache gate | `make check` only — never CI |
| `gh api` sweep | GitHub settings ([repo-settings.md](/standards/repo-settings.md)) | sweep |

## Deferred

Licensing: the standard takes no position on `LICENSE` files yet —
deliberately unaddressed.
