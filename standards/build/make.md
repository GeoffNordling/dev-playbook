---
type: Standard
title: Make
description: The Make contract — the universal check target plus per-layer targets, identical recipes in every repo
---

# Make

Make is the task runner; every repo has a `Makefile`. `check` is the
universal target and means the same thing everywhere: **green `check` = the
repo passes everything it can settle locally on its own** — every
deterministic check whose remedy is in the repo's own hands. Its recipe is
identical in every repo — run the full hook suite — and layers add
prerequisites. `check-judgments` is `check` plus the semantic
[cache gate](/standards/judgments/cache-gate.md) armed; it is what the
pre-push hook runs, because that gate's only remedy is the `run-judgments`
skill at the main loop:

| Target | Layer | Recipe |
|---|---|---|
| `check` | base | `uvx pre-commit run --all-files`, after the layer prerequisites below |
| `check-judgments` | base / python | base: `check-judgments: check` (no pytest, nothing to arm); python: `$(MAKE) check SKIP_JUDGMENTS=$(if $(NO_JUDGMENT_CACHE),1,0)` — `check` with the judgment cache gate armed |
| `format` (mutating) | python | `uv run ruff format .` |
| `format-check` | python | `uv run ruff format --check .` |
| `lint` | python | `uv run ruff check .` |
| `typecheck` | python | `uv run mypy <code-roots>` — whichever of `src tests scripts` hold `.py` files |
| `test` | python | `uv run pytest` |
| `synth` / `diff` / `deploy` | aws | `npx cdk synth` / `npx cdk diff` / `npx cdk deploy` |

In a python repo, `check: format-check lint typecheck test`. All targets
are `.PHONY`. Repos `MAY` add targets; the canonical ones are enforced
verbatim ([canonical.md](/standards/build/canonical.md)). Because `check` is
a strict superset of [thin CI](/standards/build/ci.md), a green local `check`
guarantees a green cloud run.

The `test` target carries the judgments cache gate — a deterministic pytest,
no LLM ([cache-gate.md](/standards/judgments/cache-gate.md)) — but `make test`
and `make check` **skip** it by default (they export `SKIP_JUDGMENTS=1`), so a
subagent never hits a miss it cannot fill. `make check-judgments` arms it and is
the pre-push hook's entry; a bare `uv run pytest` arms it too (fail-safe).

The judgment cache exists only on the Fedora primary. Every other machine sets
`NO_JUDGMENT_CACHE=1`, and `check-judgments` skips that one check there. The
rest of the push gate — mypy, pytest, the hook suite — runs everywhere
([machines.md](/docs/machines.md)).
