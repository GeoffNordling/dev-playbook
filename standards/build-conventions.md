# Build Conventions

Conventions for the build-and-check surface that Python projects in this
workspace expose to humans, agents, and CI.

Scope: applies to every Python sub-project in the workspace, including
script collections (e.g. `dev-playbook/tools/`). The `package = false`
exemption in `python-project-conventions.md` covers packaging only — it
does not exempt a sub-project from `make check`. Meta repos that are not
themselves Python projects (e.g. `dev-playbook` root) do not need a
Makefile.

## Task runner

Make is the task runner. Every Python sub-project `SHALL` have a `Makefile`
at its root with the standard targets defined below.

Rationale: Make is universal and stable. A standard surface across every
project means humans and agents do not have to learn each project's
ergonomic-of-the-month — `make check` is `make check` everywhere.

## Standard targets

A project's `Makefile` defines these targets. Each leaf target is a
one-liner around `uv run <tool>`; no logic lives in the Makefile.

| Target | Effect | Definition |
|---|---|---|
| `format` | **Mutating.** Apply formatting fixes. | `uv run ruff format .` |
| `format-check` | Read-only. Verify files are already formatted. | `uv run ruff format --check .` |
| `lint` | Read-only. Style and bug-class checks. | `uv run ruff check .` |
| `typecheck` | Read-only. Static type checks. | `uv run mypy <code-roots>` |
| `test` | Read-only. Run the full test suite. | `uv run pytest` |
| `check` | Read-only compound: "is this branch ready?" | Depends on `format-check lint typecheck test` |

`check` `SHALL` aggregate via prerequisite dependencies, not by inlining the
leaf commands. Inlining means a change to `lint`'s body silently diverges
from `check`'s copy of it; the dependency form makes each leaf the single
source of truth.

`check` uses `format-check` (read-only) rather than the mutating `format`.
`check` is grammatically a read-only verb; running it should never modify the
working tree. Running `make format` separately is the way to apply formatter
fixes.

The literal target body for `check` is:

    check: format-check lint typecheck test

`<code-roots>` in the `typecheck` target is every first-party Python
directory in the repo: `src/`, `tests/`, and `scripts/` when present.

PEP 723 standalone scripts under `bin/` are explicitly **out of scope** for
the project-level `typecheck` target. Their dependencies live in per-script
inline metadata, not in the project venv, so mypy cannot resolve their
imports. They are exercised by tests in `tests/`, which `typecheck` does
cover.

Every target above is declared `.PHONY` (no on-disk file by that name).

Rationale: a single named entry point for "all checks" is the contract that
issues, CI, and pre-push hooks reference. Without it, every consumer has to
list the individual targets and stay in sync as the set evolves. The
dependency form additionally enables `make -j check` to run independent
leaves in parallel.

## Pre-commit Config: Consumer Repo Opt-in

Workspace repos opt into the shared pre-commit hook set by symlinking their
`.pre-commit-config.yaml` to dev-playbook's, using a **relative** symlink:

```bash
ln -s ../dev-playbook/.pre-commit-config.yaml .pre-commit-config.yaml
```

The symlink `SHALL` be relative, not absolute. Absolute symlinks bake an
absolute path into the working tree on disk and break the moment the repo
is cloned on any machine that does not share the author's exact home
directory layout — which includes every CI runner. The relative form
resolves correctly anywhere both repos sit as siblings, which is the
workspace convention (`~/workspace/<repo>/`).

Rationale: one source of truth for hooks across the workspace. Updates to
dev-playbook's config propagate to every consumer repo without per-repo
maintenance. The shared config's hook entries resolve dev-playbook's path
via `realpath` on the symlink, so the same `.pre-commit-config.yaml` works
in dev-playbook itself, in symlinked consumers, and on the GitHub Actions
runner (see the header comment in `.pre-commit-config.yaml` for the
pattern). The relative-symlink rule extends that property to CI by letting
the consumer's runner check out dev-playbook as a sibling and have the
symlink resolve there too.

Meta repos that author the config (e.g. `dev-playbook` itself) keep the
real file; everything else symlinks.

## Pre-commit vs. `make check`

Pre-commit and `make check` are complementary, not duplicative.

| | Pre-commit | `make check` |
|---|---|---|
| Scope | Staged files only | Whole repo |
| Mutates | Yes (`ruff --fix`, `ruff-format`) | No |
| Speed | Sub-second to a few seconds | Scales with test suite |
| Role | Fast feedback at commit time | "Is this ready to share?" gate |

`make check` `SHALL NOT` be invoked from a `pre-commit` hook. Test suites grow
linearly; once a commit blocks for 30 seconds, contributors reach for
`--no-verify` and the hook stops protecting anything. The right home for
`make check` as an automatic gate is `pre-push` or CI, not `pre-commit`.

## Continuous Integration

Every repo containing one or more Python sub-projects `SHALL` have a GitHub
Actions workflow at `.github/workflows/ci.yml` that runs on every PR and on
pushes to `main`. The workflow runs two gates:

1. **Pre-commit** — `pre-commit/action@v3.0.1` against the canonical
   `.pre-commit-config.yaml` (symlinked from dev-playbook in consumer
   repos). This catches lint, format, and the workspace validators on the
   diff.
2. **`make check`** — invoked inside each Python sub-project's root. This
   runs the full leaf set (format-check, lint, typecheck, test) against
   the whole sub-project.

Pre-commit and `make check` are complementary (see [Pre-commit vs. `make
check`](#pre-commit-vs-make-check)). CI runs both. Pre-commit gives fast,
diff-scoped signal; `make check` gives whole-repo signal including the
test suite.

### Python version pin

CI's `actions/setup-python` `python-version` `SHALL` match the
`requires-python` floor declared in the sub-project's `pyproject.toml`. CI
is the contract enforcer — it must run against the same Python the project
declares it supports. If a repo contains multiple Python sub-projects with
divergent floors, pin to the lowest floor.

### Two templates

There are two CI shapes, depending on where the repo sits relative to
dev-playbook.

**Meta repo (owns `.pre-commit-config.yaml`).** Currently only `dev-playbook`
itself. Its workflow checks out one repo and runs both gates from there:

```yaml
name: CI
on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.14'      # match requires-python floor
      - uses: astral-sh/setup-uv@v3
      - uses: pre-commit/action@v3.0.1
      - run: make check
        working-directory: tools         # or repo root if Python lives there
```

**Consumer repo (symlinks the config).** Every other workspace repo.
Because the `.pre-commit-config.yaml` is a relative symlink to
`../dev-playbook/.pre-commit-config.yaml`, the workflow must check out
dev-playbook as a sibling so the symlink resolves:

```yaml
name: CI
on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          path: <repo>                   # this repo into ./<repo>/
      - uses: actions/checkout@v4
        with:
          repository: <owner>/dev-playbook
          path: dev-playbook             # sibling, for the symlink target
      - uses: actions/setup-python@v5
        with:
          python-version: '3.14'      # match requires-python floor
      - uses: astral-sh/setup-uv@v3
      - uses: pre-commit/action@v3.0.1
        with:
          working-directory: <repo>
      - run: make check
        working-directory: <repo>
```

After both checkouts, the runner has `<repo>/` and `dev-playbook/` as
siblings — the same layout as `~/workspace/` locally. The relative symlink
inside `<repo>` resolves to `dev-playbook/.pre-commit-config.yaml`, and
every hook entry's `realpath` walk lands inside the checked-out
dev-playbook tree exactly as it does locally.

Rationale: the orphaned-test failure mode is real. A repo with tests that
nothing runs is a repo whose tests are decoration, not coverage. CI calling
`make check` is the mechanism that prevents the drift. The sibling-checkout
pattern is the price of keeping `.pre-commit-config.yaml` as a single
source of truth across the workspace — the alternative is per-repo copies
that silently drift.

## Adding a new check tool

When a project adopts a new check (e.g. a security scanner, a custom
validator):

1. Add a dedicated `.PHONY` target for it (e.g. `security`).
2. Append it to `check`'s prerequisite list so a single `make check` covers
   everything.
3. If the tool produces auto-fixes, expose them through `format` or a sibling
   `fix` target — never inside `check`.
