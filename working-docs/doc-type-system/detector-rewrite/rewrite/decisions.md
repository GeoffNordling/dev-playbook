---
type: General-Sheet
title: Decisions
description: The rewrite of the decisions family's six deterministic rules — six checks over the model, two ported and four new, one Standard edited to the triage, and decisions-lint retired
---

# Decisions

The step built `src/dev_playbook/checks/decisions.py` and
`tests/dev_playbook/checks/test_decisions.py` from
[the decisions triage](/working-docs/doc-type-system/detector-rewrite/triage/decisions.md).
Each report blockquote replaced its rule's body in
`standards/decisions/records.md`; the template block and both Why
blocks are unchanged.

## Built

- `decisions.numbered-records-index-readme-nothing-else`: function
  `records_index_readme_only`, a new check. It reports a missing
  `index.md` or `README.md` against `docs/decisions`, and each
  subdirectory entry or other file by its path.
- `decisions.four-digits-from-0001-no-gaps-or-repeats`: function
  `sequential_numbering`, the port of `check_sequential_numbering`.
- `decisions.four-frontmatter-keys-title-repeated-as-h1`: function
  `frontmatter_keys_and_h1`, a new check. It reports a `type` other
  than `Decision-Record`, each missing key, and a first body line
  other than `# <title>`.
- `decisions.yyyy-mm-dd-date-or-null`: function `date_or_null`, a new
  check. It accepts a parsed `datetime.date` and `None` only.
- `decisions.proposed-accepted-deprecated-superseded-or-absent`:
  function `status_vocabulary`, the port of `check_status_vocabulary`
  and `_is_valid_status`.
- `decisions.superseded-by-a-record-that-exists`: function
  `superseded_by_existing`, a new check.

`UnclassifiedRecordsFile` in `scripts/ref-lint` still stops a run on
an unexpected `.md` file under `docs/decisions/`. The triage says the
new check replaces that stop, but `ref-lint` retires in Step 11, so
the stop stays until then.

## Deleted

None.

## Retired

- `scripts/decisions-lint`, `src/dev_playbook/decisions_lint.py`, and
  `tests/dev_playbook/test_decisions_lint.py`.
- The `"decisions-lint"` entry in `DETECTORS` in
  `src/dev_playbook/playbook_lint.py`, and its two tuples in
  `tests/test_rule_registry.py`.
- The row and one mention in `scripts/README.md`, the mention in the
  `CannotRun` docstring of `src/dev_playbook/prose_lint.py`, and the
  mention in `doc-types/standard/residual-ledger.md`.

## Set aside

None. All six checks are clean on this repo's 30 records.

## Measured

- `uv run playbook check .`: 0.31 s, ten checks over 445 files, zero
  findings.
- `scripts/playbook-lint .`: 0.33 s, clean.

## Acronyms

None.
