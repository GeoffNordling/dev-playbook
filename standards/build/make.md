---
type: Standard
title: Make
description: The Make contract — the universal check target plus per-layer targets, identical recipes in every repo
---

# Make

Make is the task runner; every repo has a `Makefile`. `check` is the
universal target and means the same thing everywhere: **green `check` =
every deterministic check whose remedy is in the repo's own hands passes.**
Its recipe is identical in every repo — run the full hook suite — and
layers add prerequisites. `check-judgments-cache` is `check` plus the
semantic [cache gate](/standards/semantic-validation/cache-gate.md) armed; it is what
the pre-push hook runs, because that gate's only remedy is a
[`judgments-sweep`](/dotfiles/dot-claude/skills/judgments-sweep/SKILL.md)
run:

| Target | Layer | Recipe |
|---|---|---|
| `check` | base | `uvx pre-commit run --all-files`, after the layer prerequisites below |
| `check-judgments-cache` | base / python | base: `check-judgments-cache: check` (no pytest, nothing to arm); python: `$(MAKE) check SKIP_JUDGMENTS=$(if $(NO_JUDGMENT_CACHE),1,0)` — `check` with the judgment cache gate armed |
| `format` (mutating) | python | `uv run ruff format .` |
| `format-check` | python | `uv run ruff format --check .` |
| `lint` | python | `uv run ruff check .` |
| `typecheck` | python | `uv run mypy <code-roots>` — whichever of `src tests scripts` hold `.py` files |
| `test` | python | `uv run pytest` |

In a python repo, `check: format-check lint typecheck test`. All targets
are `.PHONY`. Repos `MAY` add targets; the canonical ones are enforced
verbatim ([canonical.md](/standards/build/canonical.md)). Because `check` is
a strict superset of [thin CI](/standards/build/ci.md), a green local `check`
guarantees a green cloud run.

The `test` target carries whatever judgment cache tripwires the repo has
wired via pytest — deterministic checks, no LLM
([cache-gate.md](/standards/semantic-validation/cache-gate.md)) — but `make test`
and `make check` **skip** them by default (they export `SKIP_JUDGMENTS=1`), so
a subagent never hits a miss it cannot fill. `make check-judgments-cache` arms
them and is the pre-push hook's entry — a repo with none wired passes it
vacuously; a bare `uv run pytest` arms them too (fail-safe).

The judgment cache exists only on the Fedora primary. Every other machine sets
`NO_JUDGMENT_CACHE=1`, and `check-judgments-cache` skips that one check there.
The rest of the push gate — mypy, pytest, the hook suite — runs everywhere
([machines.md](/docs/machines.md)).
