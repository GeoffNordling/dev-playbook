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
prerequisites. `check-judgements` is `check` plus the semantic
[cache gate](/standards/judgements/cache-gate.md) armed; it is what the
pre-push hook runs, because that gate's only remedy is the `run-judgements`
skill at the main loop:

| Target | Layer | Recipe |
|---|---|---|
| `check` | base | `uvx pre-commit run --all-files`, after the layer prerequisites below |
| `check-judgements` | base / python | base: `check-judgements: check` (no pytest, nothing to arm); python: `$(MAKE) check SKIP_JUDGEMENTS=0` — `check` with the judgement cache gate armed |
| `format` (mutating) | python | `uv run ruff format .` |
| `format-check` | python | `uv run ruff format --check .` |
| `lint` | python | `uv run ruff check .` |
| `typecheck` | python | `uv run mypy <code-roots>` — whichever of `src tests scripts` hold `.py` files |
| `test` | python | `uv run pytest` |
| `synth` / `diff` / `deploy` | aws | `npx cdk synth` / `npx cdk diff` / `npx cdk deploy` |
| `validate` | sdd | `uv run spec-tools validate .` — the spec-graph gate |

In a python repo, `check: format-check lint typecheck test`. In an sdd repo
(`specs/` present), the `Makefile.sdd` fragment appends `validate` to
`check`'s prerequisites via a recipe-less `check: validate` line. All targets
are `.PHONY`. Repos `MAY` add targets; the canonical ones are enforced
verbatim ([canonical.md](/standards/build/canonical.md)). Because `check` is
a strict superset of [thin CI](/standards/build/ci.md), a green local `check`
guarantees a green cloud run.

The `test` target carries the judgements cache gate — a deterministic pytest,
no LLM ([cache-gate.md](/standards/judgements/cache-gate.md)) — but `make test`
and `make check` **skip** it by default (they export `SKIP_JUDGEMENTS=1`), so a
subagent never hits a miss it cannot fill. `make check-judgements` arms it
(`SKIP_JUDGEMENTS=0`) and is the pre-push hook's entry; a bare `uv run pytest`
arms it too (fail-safe).
