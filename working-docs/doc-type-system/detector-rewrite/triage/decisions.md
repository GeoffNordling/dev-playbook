---
type: General-Sheet
title: Decisions
description: The triage of the decisions family's six deterministic rules — all six restated plain with their meaning held, two keeping today's check and four gaining one, none deleted, none escalated
---

# Decisions

Six deterministic rules in one Standard, `standards/decisions/records.md`,
per
[Triage](/working-docs/doc-type-system/detector-rewrite/triage.md).
The three stochastic rules are skipped:
`hard-to-reverse-surprising-a-real-trade-off`,
`context-decision-and-reason`, `source-named-sha-or-version-pinned`.
Today one detector, `decisions_lint` (`src/dev_playbook/decisions_lint.py`,
run by the shim `scripts/decisions-lint`), decides two of the six;
the other four are `null` in `standards/verifiers.yaml:25-33`.
[Detector Fixes](/working-docs/doc-type-system/detector-rewrite/detector-fixes.md)
has no row for this family.

Measured on this repo, read-only: `docs/decisions/` tracks 32 files,
30 records `0001`–`0030`, `index.md`, and `README.md`. All 30 records
have `type`, `title`, `description`, `date`; 9 also have
`status: accepted`; 27 dates are `YYYY-MM-DD`, 3 are `null`; every
record's first body line is `# ` plus its `title`. No record is
superseded. So every rule below passes today, and no row moves the
repo out of compliance.

## records.md

Kept as written: none. Each body uses "holds", "carries", or
"belongs to" where "is" or "has" will do.

- **`numbered-records-index-readme-nothing-else`**,
  `standards/decisions/records.md:37`. Rewrite, the check added.

  > When `docs/decisions/` has a record, it also has `index.md` and
  > `README.md`, and every other entry in it is a file named
  > `<digits>-<slug>.md`. It has no other file and no subdirectory.

  `wording only`. The old sentence lists "one `index.md`, and one
  `README.md`" as held; a directory cannot hold two files of one name,
  so "one" can only mean the file is there, and the restatement keeps
  that. The name shape is `<digits>-<slug>.md`, not `NNNN-slug.md`, so
  a badly padded `12-x.md` fails `four-digits-from-0001-no-gaps-or-repeats`
  alone and not both rules. Check: list the model's tracked paths
  under `docs/decisions/`; report a path in a subdirectory, a name
  that is not `index.md`, `README.md`, or `^\d+-.+\.md$`, and a missing
  `index.md` or `README.md`. Today nothing reports under this id;
  `source_files` in `scripts/ref-lint:95` stops the run with
  `UnclassifiedRecordsFile` (`scripts/ref-lint:114`) on an unexpected
  `.md` file only, never on another extension or a missing file. The
  new check replaces that stop.

- **`four-digits-from-0001-no-gaps-or-repeats`**,
  `standards/decisions/records.md:44`. Rewrite, check unchanged.

  > A record's filename is `NNNN-slug.md`, where `NNNN` is its number
  > in exactly four digits. Sorted, the numbers in `docs/decisions/`
  > are `0001`, `0002`, and on up by one to the highest, each once.

  `wording only`: "starts at `0001`, up by one, each once" is the old
  "`0001` or higher, no repeat, no gap" in one comparison. Check:
  `check_sequential_numbering` (`src/dev_playbook/decisions_lint.py:108`)
  matches `^(\d+)-.+\.md$` and reports a prefix not four characters
  long, a number below 1, a repeated number, and each run of missing
  numbers against the directory. It decides the sentence as restated.

- **`four-frontmatter-keys-title-repeated-as-h1`**,
  `standards/decisions/records.md:54`. Rewrite, the check added.

  > A record's frontmatter has `type: Decision-Record` and the keys
  > `title`, `description`, and `date`. The first non-blank line after
  > the frontmatter is `# ` followed by the `title` value exactly.

  `wording only`. The template block under the sentence stays. Other
  keys, `status` among them, are allowed, as the old "holds" allowed
  them. Check: read the record's parsed frontmatter and first body
  line from the model. Today no check reads the `type` value, the
  `date` key, or the H1; `check_types` in `scripts/okf-lint:424`
  reports an empty `title` or `description` under the two
  `knowledge-organization.` ids, and this check reports only a missing
  key, so one fault gets one finding.

- **`yyyy-mm-dd-date-or-null`**, `standards/decisions/records.md:82`.
  Rewrite, the check added.

  > A record's `date` is a `YYYY-MM-DD` date or `null`.

  `wording only`. Check: PyYAML reads an unquoted `2026-09-22` as a
  `datetime.date` and `null` as `None`; accept those two, and reject a
  `datetime.datetime` (a time was written), a string, and any other
  value. An absent `date` is `four-frontmatter-keys-title-repeated-as-h1`'s
  finding, not this one's.

- **`proposed-accepted-deprecated-superseded-or-absent`**,
  `standards/decisions/records.md:92`. Rewrite, check unchanged.

  > A record's `status`, if it has one, is `proposed`, `accepted`,
  > `deprecated`, or `superseded by NNNN` with `NNNN` four digits.

  `wording only`. Check: `check_status_vocabulary`
  (`src/dev_playbook/decisions_lint.py:185`) skips a record with no
  `status` key and reports any other value `_is_valid_status`
  (`src/dev_playbook/decisions_lint.py:212`) rejects: not a string,
  or not one of the three words or `^superseded by \d{4}$`. A
  `status: null` is reported, as the old sentence requires.

- **`superseded-by-a-record-that-exists`**,
  `standards/decisions/records.md:100`. Rewrite, the check added.

  > If a record's `status` is `superseded by NNNN`, `docs/decisions/`
  > has a record whose filename starts `NNNN-`.

  `wording only`. Check: take the four digits from each `superseded by
  NNNN` status and look for a record path `docs/decisions/NNNN-*.md`
  in the model. No record in this repo is superseded, so it passes
  with nothing to check.

## Escalations

None.

## New rules

None.

## Acronyms

None.
