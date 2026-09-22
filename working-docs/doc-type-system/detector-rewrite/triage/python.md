---
type: General-Sheet
title: Python
description: The triage of the python family's four deterministic rules — one kept, one kept with its cause fixed in the canonical files, one exception dropped, one replaced by ruff's own configuration, ruled 2026-09-22
---

# Python

Four rules in one Standard, `standards/python/style.md`. Done by hand
as the calibration sample, per
[Triage](/working-docs/doc-type-system/detector-rewrite/triage.md).

## style.md

Kept as written, the check matching the sentence: `empty-init`.

- **`every-definition-carries-a-docstring`**,
  `standards/python/style.md:35`. Rewrite, meaning changed: replaced
  by one rule, the old sentence its Why. Relaxes the sentence to
  public, top-level definitions, which is what ruff enforces today
  and what the repo practises: 7 private and 6 nested definitions
  under `src/` carry none. Ruled 2026-09-22.

  > **Ruff check reports nothing.** `ruff check` over the file reports
  > no finding under the canonical configuration: the nine families
  > `tool.ruff.lint.select` pins, `pep257` docstrings, line length and
  > imperative-mood summaries ignored, no docstrings required under
  > `tests/`.

- **`no-future-annotations`**, `standards/python/style.md:47`.
  Rewrite, meaning changed: drop the `build`, `dist`, `deprecated`
  exception; the model reads tracked files only.
- **`formatted-by-ruff-format`**, `standards/python/style.md:58`.
  Keep, and fix the cause of its gap: ruff never opened an
  extensionless script, since pre-commit tags one `executable` and
  not `python`, and `ruff check .` filters on `*.py`. The canonical
  `pyproject.toml` gains `extend-include = ["scripts/*"]`, and the two
  ruff hooks in the canonical `.pre-commit-config.yaml` gain
  `types_or: [python, pyi, executable]`. Today that reformats three
  scripts and raises 48 findings under `scripts/`, most in files the
  rewrite deletes. Ruled 2026-09-22.

## Escalations

Both ruled 2026-09-22 and folded into the rows above.

## New rules

None.

## Acronyms

None.
