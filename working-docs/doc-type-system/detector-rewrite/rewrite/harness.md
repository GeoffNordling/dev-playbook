---
type: General-Sheet
title: Harness
description: The rewrite of the harness family's five deterministic rules and one new rule — six checks over the model, two ported, three that were null gaining a check, one new, two Standards edited to the triage, and nothing retired
---

# Harness

The step built `src/dev_playbook/checks/harness.py` and
`tests/dev_playbook/checks/test_harness.py` from
[the harness triage](/working-docs/doc-type-system/detector-rewrite/triage/harness.md).
`scripts/harness-files-lint` still runs `check_global_claude` and its
`ToolError` for a skill directory with no `SKILL.md`; both retire with
`harness-files-lint` in Step 10.

## Built

- `harness.no-frontmatter`: function `no_frontmatter`, gaining a
  check. Reads line 1 of every tracked file named `CLAUDE.md` at any
  depth. The body in `standards/harness/claude-content.md` is the
  triage blockquote. 0 findings on the 2 tracked files.
- `harness.behaviors-then-principles`: function
  `behaviors_then_principles`, kept as written, ported from
  `check_global_claude`. Compares the global source's level-2 heading
  texts from the model to `Behaviors`, `Principles`.
- `harness.two-required-rules`: function `two_required_rules`, ported
  from `check_global_claude`. The body in `claude-content.md` is the
  triage blockquote ("carries" becomes "has").
- `harness.read-the-standards-first`: function
  `read_the_standards_first`, the new rule, added under Global file
  after Two required rules with the triage's proposed body. It reports
  nothing when the heading is absent, which is the required-rules
  check's finding. Passes today (line 5).
- `harness.every-harness-file-matches-a-member-row`: function
  `matches_a_member_row`, gaining a check. The body in
  `standards/harness/files.md` is the triage blockquote; the table's
  workflows row is `workflows/*.js` and a `statusline.sh` row is added.
  Nine patterns over the paths below `.claude/` and
  `dotfiles/dot-claude/` at the repo root.
- `harness.every-runbook-at-a-fixed-path`: function
  `runbook_at_a_fixed_path`, gaining a check. The body in `files.md` is
  the triage blockquote; the tree block stays. The skill directory
  missing `SKILL.md` is reported on the directory path, each other
  entry on its file path, each misplaced agent on its file path.

`claude-content.md`'s `description` and its row in
`standards/harness/index.md` now name the first rule of the global
source.

## Deleted

None.

## Retired

None.

## Set aside

None.

## Measured

- `uv run playbook check .`: 0.87 s, 41 checks over 457 files, zero
  findings.
- `scripts/playbook-lint .`: 0.60 s, clean.

## Acronyms

None.
