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
Item 1: parked on Later Checks, the rule leaves the Standard; two
fixtures fail today.

1. **`fixture-lives-in-the-narrowest-conftest`**,
   `standards/testing/conventions.md:41`.
   - **What it means.** Put a shared pytest fixture in the conftest
     closest to the tests that use it. Do not put it in a higher
     conftest, where tests that never use it can also see it.
   - **Proposal.** The quoted body in the row above. Check: collect
     every function decorated `@pytest.fixture` in a `conftest.py`.
     For each one, find the files that use its name as a parameter or
     in `usefixtures`. Take the deepest directory that contains all
     of those files and compare it with the conftest's directory.
     Report a fixture that no file uses as a finding too.
   - **How it differs from today's sentence.** The old sentence
     requires every fixture to be in a `conftest.py`, even one used by
     only one test module. The proposal lets a test module define its
     own fixtures, because pytest shows those fixtures only to that
     module, and a module is narrower than any directory. The old
     sentence does not say what happens to an `autouse` fixture, which
     no test names. The proposal exempts it: all tests below the
     conftest use it, so its conftest is already the narrowest. The
     old sentence also does not say what happens to a fixture that
     nothing uses. The proposal reports it, because it has no
     "narrowest directory whose tests use it".
   - **How it differs from today's enforcement.** No check today:
     `standards/verifiers.yaml:194` gives `null`. The check matches by
     name only. It does not follow a nested conftest that defines a
     fixture with the same name, `request.getfixturevalue`, or
     indirect parametrization. None of these occurs in this repo
     today.
   - **Measured.** 63 fixtures in the tracked `.py` files: 3 in
     `tests/conftest.py`, 60 in 13 `test_*.py` files, and none in
     `working-docs/software-factory/tests/conftest.py` that fails. Under
     the proposal, 2 fail:
     - `ambient_git_dir`, `tests/conftest.py:67`, is used only by five
       files under `tests/dev_playbook/`, so it belongs in
       `tests/dev_playbook/conftest.py`, which does not exist.
     - `make_repo`, `tests/conftest.py:94`, is used by no file.
       `tests/test_harness_files_lint.py:60` defines its own plain
       function with the same name.

     Under the old sentence read literally, all 60 fixtures defined in
     test modules also fail.

## New rules

None.

## Acronyms

None.
