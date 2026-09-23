---
type: General-Sheet
title: Testing
description: The triage of the testing family's three deterministic rules — none kept as written, two restated plain with their meaning held, one of them gaining its check, and the fixture rule rewritten with its meaning changed and escalated
---

# Testing

Three deterministic rules in one Standard,
`standards/testing/conventions.md`. The fourth rule,
`fakes-live-in-the-test-tree` at `standards/testing/conventions.md:48`,
has the trailer `stochastic` and is skipped. Triaged per
[Triage](/working-docs/doc-type-system/detector-rewrite/triage.md).

Today one check covers the family: `check_mirror_layout` at
`src/dev_playbook/testing_lint.py:114`, run by `scripts/testing-lint`.
`standards/verifiers.yaml:193-196` gives `null` for the other two.
[Detector Fixes](/working-docs/doc-type-system/detector-rewrite/detector-fixes.md)
has one testing row, at `detector-fixes.md:56`. It names
`testing.access-only-public-names`, a rule the Standard no longer has.
That row has nothing to triage.

## conventions.md

Kept as written, the check matching the sentence: none.

- **`test-files-carry-the-test-prefix`**,
  `standards/testing/conventions.md:18`. Rewrite, `null` gains a
  check. The old body says "every test file" but does not say what a
  test file is. The frontmatter's `population` defines the suite as
  "the `test_*.py` files", so read literally the rule is always true.
  The restatement uses pytest's default collection rule as the meaning
  of "test file".

  > Every `.py` file that defines, at module level, a function whose
  > name begins `test_` or a class whose name begins `Test` is named
  > `test_*.py`.

  `wording only`. Check: for each tracked `.py` file whose name does
  not begin `test_`, look at the top-level `def` and `class` nodes in
  its `ast` tree and report any that have the prefix. Measured today:
  47 files define tests, and all 47 are named `test_*.py`. No file
  fails. Without this rule, pytest never collects a test in a file
  named, for example, `tests/check_login.py`, and does not report it.

- **`test-tree-mirrors-the-source-tree`**,
  `standards/testing/conventions.md:24`. Rewrite. The check already
  decides the sentence, but the body is a single 90-word sentence.

  > Take a file `tests/**/test_<name>.py` where at least one module
  > `src/<dir>/<name>.py` exists, other than `__init__.py`. The file is
  > at `tests/<dir>/test_<name>.py`,
  > `tests/unit/<dir>/test_<name>.py`, or
  > `tests/integration/<dir>/test_<name>.py`. Example:
  > `src/auth/login.py` is tested at `tests/auth/test_login.py`. When
  > more than one module has the name `<name>.py`, the mirror of any
  > one of them passes.

  `wording only`. Check: `check_mirror_layout`,
  `src/dev_playbook/testing_lint.py:114`, with the mirror paths from
  `_mirrors_of` at `:84` and `MIRROR_SCOPES` at `:81`. It decides the
  whole sentence. The rewrite drops the `_CACHES` directory filter at
  `:47` and the untracked files that `pyast.find_python_files` adds
  (`src/dev_playbook/pyast.py:44`), because the model reads only
  tracked files. Measured today: `scripts/testing-lint` is clean over
  120 files.

- **`fixture-lives-in-the-narrowest-conftest`**,
  `standards/testing/conventions.md:41`. Rewrite, `null` gains a
  check. `meaning changed`. Escalation 1.

  > A fixture defined in `<dir>/conftest.py` is named as a parameter,
  > or in `pytest.mark.usefixtures`, by a test or fixture in at least
  > one file under `<dir>`. `<dir>` is the deepest directory that
  > contains all of those files. An `autouse=True` fixture is exempt.
  > A fixture defined in a `test_*.py` file is outside this rule.

## Escalations

Ruled 2026-09-23 under the general rulings in
[Triage](/working-docs/doc-type-system/detector-rewrite/triage.md#rulings-that-calibrate-the-rest).
The number is the one the rows above cite.

1. `fixture-lives-in-the-narrowest-conftest`,
   `standards/testing/conventions.md:41`: deleted. The user's reason:
   it micromanages how a conftest is written.

## New rules

None.

## Acronyms

None.
