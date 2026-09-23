---
type: General-Sheet
title: Python
description: The rewrite of the python family's four deterministic rules — two checks over the model, two registered to their ruff hooks, one Standard edited to the triage, and python-lint retired
---

# Python

The step built `src/dev_playbook/checks/python.py` and
`tests/dev_playbook/checks/test_python.py` from
[the python triage](/working-docs/doc-type-system/detector-rewrite/triage/python.md).

## Built

- `python.empty-init`: function `empty_init`. Kept as written; no
  change to the Standard.
- `python.every-definition-carries-a-docstring`: hook `ruff-check`.
  The report's blockquote replaced the body of
  `standards/python/style.md`; the old sentence moved into the Why,
  ahead of the Why that was already there.
- `python.no-future-annotations`: function `no_future_annotations`.
  The `build`, `dist`, `deprecated` exception left the body; the
  model reads tracked files only.
- `python.formatted-by-ruff-format`: hook `ruff-format`. Kept; its gap
  fix is on the ROOT's Planned list, after the rewrite, so the body is
  unchanged.

## Deleted

None. No heading left `standards/python/`, so no link was repointed.

## Retired

- `scripts/python-lint` and `tests/test_python_lint.py`.
- The `"python-lint"` entry in `DETECTORS` in
  `src/dev_playbook/playbook_lint.py`, and its two tuples in
  `tests/test_rule_registry.py`.
- The row and two mentions in `scripts/README.md`, the mention in the
  docstring of `src/dev_playbook/pyast.py`, which stays since
  `testing-lint` and `repo-lint` import it, the stale mention in a
  docstring of `tests/test_rule_registry.py`, and the mention in the
  Consequences of `docs/decisions/0011-one-registry-for-non-authored-content.md`.

## Set aside

None.

## Measured

- `uv run playbook check .`: 0.30 s, two checks over 445 files, zero
  findings.
- `scripts/playbook-lint .`: 0.34 s, clean.

## Acronyms

None.
