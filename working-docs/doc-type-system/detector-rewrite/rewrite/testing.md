---
type: General-Sheet
title: Testing
description: The rewrite of the testing family's three deterministic rules — two checks over the model, the fixture rule deleted per its escalation, one Standard edited to the triage, and testing-lint retired
---

# Testing

The step built `src/dev_playbook/checks/testing.py` and
`tests/dev_playbook/checks/test_testing.py` from
[the testing triage](/working-docs/doc-type-system/detector-rewrite/triage/testing.md).

## Built

- `testing.test-files-carry-the-test-prefix`: function
  `carries_test_prefix`, a new check. The report's blockquote replaced
  the body in `standards/testing/conventions.md`.
- `testing.test-tree-mirrors-the-source-tree`: function
  `mirrors_source_tree`, the port of `check_mirror_layout` over tracked
  files only. The report's blockquote replaced the body; the Why is
  unchanged.

Neither function name is the slug: a module-level name that begins
`test_` is a test by the first rule, so each takes a shorter name.

## Deleted

- `testing.fixture-lives-in-the-narrowest-conftest`, per Escalation 1:
  heading, body, and trailer removed. No link pointed at the heading.
  The Standard's `description`, its row in `standards/testing/index.md`,
  that index's intro, and the directory's row in `standards/index.md`
  no longer name the conftest hierarchy.

## Retired

- `scripts/testing-lint`, `src/dev_playbook/testing_lint.py`, and
  `tests/dev_playbook/test_testing_lint.py`.
- The `"testing-lint"` entry in `DETECTORS` in
  `src/dev_playbook/playbook_lint.py`, and its two tuples in
  `tests/test_rule_registry.py`.
- The row, the module line, and two mentions in `scripts/README.md`,
  and the mentions in
  `docs/decisions/0011-one-registry-for-non-authored-content.md` and
  `docs/decisions/0021-scope-directories-and-spec-item-return.md`.
  `src/dev_playbook/pyast.py` stays, since `repo-lint` imports it.

## Set aside

None. Both checks are clean on this repo: 49 files define tests, all
named `test_*.py`.

## Measured

- `uv run playbook check .`: 0.30 s, four checks over 447 files, zero
  findings.
- `scripts/playbook-lint .`: 0.33 s, clean.

## Acronyms

None.
