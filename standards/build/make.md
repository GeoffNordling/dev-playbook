---
type: Standard
title: Make
description: The Make contract — the universal check target plus per-layer targets, identical recipes in every repo
---

# Make

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

The `test` target includes the judgments stage-1 cache gate — a
deterministic pytest, no LLM ([cache-gate.md](/standards/judgments/cache-gate.md)).
