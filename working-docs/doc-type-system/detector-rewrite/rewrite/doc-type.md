---
type: General-Sheet
title: Doc-Type
description: The rewrite of the doc-type family's twenty-eight deterministic rules — twenty-one checks over the model, five registered to loop-lint, one deleted per its escalation, one set aside, five Standards edited to the triage, and harness-files-lint and standards-lint retired
---

# Doc-Type

The step built `src/dev_playbook/checks/doc_type.py` and
`tests/dev_playbook/checks/test_doc_type.py` from
[the doc-type triage](/working-docs/doc-type-system/detector-rewrite/triage/doc-type.md).
The module holds twenty-one functions and five `loop-lint`
registrations. `loop_lint.py` stays as it is, per the plan's loop
family, so the five Loop rules it decides are registered to it by
name and their gaps stay open there.

## Built

### doc-type.md

- `doc-type.registered`: function `registered`, new. The body is the
  triage blockquote. The table is `sources.REGISTRY_RULINGS`; the
  check reads the `Ruling` column's links. 4 of 4 directories pass.

### guide-conventions.md

- `doc-type.a-sequence-is-one-list`: function `a_sequence_is_one_list`,
  new. The body is the triage blockquote. 11 of 11 lists pass.
- `doc-type.a-step-opens-with-its-name`: function
  `a_step_opens_with_its_name`, new; body kept.
- `doc-type.no-trailer`: function `no_trailer`, new; body kept. Fenced
  lines are read too.

### loop-conventions.md

- `doc-type.one-paragraph-then-one-graph`,
  `doc-type.acts-checks-and-yields-in-that-order`,
  `doc-type.nodes-and-entries-agree`,
  `doc-type.every-entry-states-its-condition`: hook `loop-lint`. Each
  body is its triage blockquote. The gaps the triage names stay open
  in `loop_lint.py`.
- `doc-type.edges-lead-to-steps`: hook `loop-lint`; body kept.
- `doc-type.an-act-links-a-runbook`: function `an_act_links_a_runbook`,
  new. The body is the triage blockquote. No file is typed `Loop`.

### runbook-conventions.md

- `doc-type.front-matter-holds-its-kinds-vocabulary`: function
  `front_matter_holds_its_kinds_vocabulary`, ported from
  `parse_runbook`, `check_required_fields`, and
  `check_unknown_fields`. The body is the triage blockquote; the two
  example YAML blocks and their two paragraphs are gone.
- `doc-type.name-matches-its-home`, `doc-type.kebab-case-name`,
  `doc-type.description-two-sentences-or-one`,
  `doc-type.model-and-effort-from-closed-sets`,
  `doc-type.body-opens-with-an-h1`,
  `doc-type.boolean-disable-model-invocation`,
  `doc-type.arguments-bare-kebab-case-names`: one function each, named
  for the slug, ported from `harness-files-lint`; bodies kept.
- `doc-type.every-bundle-file-reached-from-skillmd`: function
  `every_bundle_file_reached_from_skillmd`, new, the linked form of
  escalation 3. The body is the triage blockquote. 8 bundle files
  pass.
- `doc-type.no-argument-placeholder`: function
  `no_argument_placeholder`, new. The body is the triage blockquote.
- `doc-type.references-one-level-deep`: function
  `references_one_level_deep`, ported from `check_references_depth`
  with the three gaps closed: root-absolute and `~/` targets,
  subdirectories of `references/`, and reference-style links.
- `doc-type.skillmd-at-most-500-lines`: function
  `skillmd_at_most_500_lines`, new, from the old stderr advisory.
- `doc-type.tools-comma-separated-tool-names`: function
  `tools_comma_separated_tool_names`, ported from `check_tools` with
  each part tested as a tool name.

### standard-conventions.md

- `doc-type.the-frontmatter-names-the-population`: function
  `the_frontmatter_names_the_population`, ported from
  `check_directory_layout`. The body is the triage blockquote; the Why
  no longer names the retired detector.
- `doc-type.a-rule-heading-predicate-trailer`: function
  `a_rule_heading_predicate_trailer`, new, escalation 2. The body is
  the triage blockquote with the block limit relaxed to the ruling's
  shape, tables included. 30 of 30 Standards pass.
- `doc-type.the-files-why-ends-the-opening-prose`: function
  `the_files_why_ends_the_opening_prose`, new. The body is the triage
  blockquote. 30 of 30 pass.

`doc-type.md`'s `description`, its file Why, and its row in
`standards/doc-type/index.md` no longer name one base class or an
index row.

## Deleted

- `doc-type.one-base-class`, escalation 1, with its Why. No link
  pointed at it.

## Retired

- `scripts/harness-files-lint` and `tests/test_harness_files_lint.py`.
- `scripts/standards-lint`, `src/dev_playbook/standards_lint.py`, and
  `tests/dev_playbook/test_standards_lint.py`.
- Both roster lines in `DETECTORS`, both tuples each in
  `tests/test_rule_registry.py`, and both rows of the table in
  `scripts/README.md`.
- Mentions repointed in `guides/consuming.md` steps 5 and 6,
  `doc-types/doc-type-system.md`, `doc-types/runbook/residual-ledger.md`,
  `docs/decisions/0012-one-published-hook.md`,
  `docs/writing-improvement-process/writing-improvement-problems.md`,
  `dotfiles/dot-claude/skills/runbook-creator/SKILL.md`, the opening
  of `runbook-conventions.md`, and comments in `scripts/okf-lint`,
  `scripts/repo-lint`, `tests/test_okf_lint.py`, and
  `tests/test_repo_lint.py`.

## Set aside

- `doc-type.tool-fields-space-separated-specs`, kept by the triage,
  which found the three `allowed-tools` values passing. Two do not:
  `dotfiles/dot-claude/skills/commit/SKILL.md` and
  `dotfiles/dot-claude/skills/commit-inherit/SKILL.md` carry
  `Bash(git *), Read, Edit`, comma-separated, and the check reports
  `'Bash(git *),'` and `'Read,'` as parts that are not tool specs. The
  rule left `runbook-conventions.md`:

  > A skill's `allowed-tools` and `disallowed-tools`, when present, are
  > space-separated tool specs, as in `Bash(git *) Bash(gh *)`.

  The check split the value at spaces outside parentheses and matched
  each part to a tool name, alone or with `(<pattern>)`.

## Measured

- `uv run playbook check .`: 0.41 s, 67 checks over 465 files, zero
  findings.
- `scripts/playbook-lint .`: 0.20 s, clean.

## Acronyms

None.
