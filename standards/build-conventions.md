# Build Conventions

Conventions for the build-and-check surface that Python projects in this
workspace expose to humans, agents, and CI.

Scope: applies to Python sub-projects (e.g. `spec-tools`, projects generated
from `project-template`). Meta repos that are not themselves Python projects
(e.g. `dev-playbook` itself) do not need a Makefile.

## Task runner

Make is the task runner. Every project has a `Makefile` at its root with the
standard targets defined below.

Rationale: Make is universal and stable. A standard surface across every
project means humans and agents do not have to learn each project's
ergonomic-of-the-month — `make check` is `make check` everywhere.

## Standard targets

A project's `Makefile` defines these targets. Each target is a one-liner
around `uv run <tool>`; no logic lives in the Makefile.

| Target | Effect | Definition |
|---|---|---|
| `format` | **Mutating.** Apply formatting fixes. | `uv run ruff format .` |
| `lint` | Read-only. Style and bug-class checks. | `uv run ruff check .` |
| `typecheck` | Read-only. Static type checks. | `uv run mypy <code-roots>` |
| `test` | Read-only. Run the full test suite. | `uv run pytest` |
| `check` | Read-only compound: "is this branch ready?" | `format --check && lint && typecheck && test` |

`check` uses `ruff format --check` (read-only) rather than the mutating
`format`. `check` is grammatically a read-only verb; running it should never
modify the working tree. Running `make format` separately is the way to apply
formatter fixes.

The literal target body for `check` is:

    check:
    	uv run ruff format --check .
    	uv run ruff check .
    	uv run mypy <code-roots>
    	uv run pytest

`<code-roots>` is the project's typed source directory or directories
(typically `src/`, plus `scripts/` when present).

Rationale: a single named entry point for "all checks" is the contract that
issues, CI, and pre-push hooks reference. Without it, every consumer has to
list the individual targets and stay in sync as the set evolves.

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

## Adding a new check tool

When a project adopts a new check (e.g. a security scanner, a custom
validator):

1. Add a dedicated target for it (e.g. `security`).
2. Append it to the `check` target's command list so a single `make check`
   covers everything.
3. If the tool produces auto-fixes, expose them through `format` or a sibling
   `fix` target — never inside `check`.
