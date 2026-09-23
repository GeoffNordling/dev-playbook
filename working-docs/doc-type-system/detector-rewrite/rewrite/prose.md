---
type: General-Sheet
title: Prose
description: The rewrite of the prose family's four deterministic rules and one new rule — five checks over the model, one Standard edited to the triage, and prose-lint retired
---

# Prose

The step built `src/dev_playbook/checks/prose.py` and
`tests/dev_playbook/checks/test_prose.py` from
[the prose triage](/working-docs/doc-type-system/detector-rewrite/triage/prose.md).
The three restated bodies in `standards/prose/conventions.md` are the
report's blockquotes, word for word. The `population` line gained "and,
for the two word rules, every tracked file", per Escalation 1. Every
check skips the population's exceptions: a `type: Mirror` document, a
path listed in `.prose-lint-exempt`, and the two declaration files.

## Built

- `prose.judgment-not-judgement`: function `judgment_spelling`, the
  port of `scan_text`. It reads the model's body lines outside fences,
  with inline code spans removed. The rule is kept as written.
- `prose.no-first-person`: function `no_first_person`, the port of
  `scan_voice` over `voice.VOICE_PATTERNS`. It reads the whole file,
  frontmatter included, of each `md.is_agent_instruction` path. The
  restated body replaced the old one.
- `prose.no-banned-word`: function `no_banned_word`, the port of
  `scan_banned` over the workspace layer. The word is the constant
  `WORKSPACE_WORD`. The Standard names the word in a new Why block
  under the rule, and `test_the_standard_names_the_banned_word` reads
  that section through `sources.BANNED_WORD` and asserts the two agree.
- `prose.no-word-the-repo-bans`: function `no_word_the_repo_bans`, the
  port of `scan_banned` over the repo layer. It reads the well-formed
  entries of `.prose-lint-vocabulary` only.
- `prose.the-vocabulary-file-is-well-formed`: function
  `vocabulary_well_formed`, the port of `vocabulary`'s exit-2 checks as
  findings. The new rule sits after `No word the repo bans`, with the
  report's proposed body and a new Why.

`repo_init.render_tree` refuses a repo name that carries the banned
word through `checks.prose.word_pattern(WORKSPACE_WORD)`. Its test
moved to `tests/dev_playbook/test_repo_init.py`.

## Deleted

None.

## Retired

- `scripts/prose-lint`, `src/dev_playbook/prose_lint.py`, and
  `tests/dev_playbook/test_prose_lint.py`. `repo_init.py` imported the
  module for the banned word only, and now imports it from the check
  module.
- The `"prose-lint"` entry in `DETECTORS` in
  `src/dev_playbook/playbook_lint.py`, and its two tuples in
  `tests/test_rule_registry.py`.
- The row and three mentions in `scripts/README.md`. The mentions in
  `scripts/repo-init`, `scripts/repo-lint`, `scripts/harness-files-lint`,
  `src/dev_playbook/voice.py`, `src/dev_playbook/repo_init.py`,
  `tests/test_repo_lint.py`, `tests/test_set_deslop_coverage.py`,
  `docs/decisions/0011`, and `docs/decisions/0019`.
- In `.prose-lint-exempt`, the two retired paths gave way to
  `src/dev_playbook/checks/prose.py`, which spells the word.

## Set aside

None. All five checks are clean on this repo.

## Measured

- `uv run playbook check .`: 0.39 s, fifteen checks over 447 files,
  zero findings.
- `scripts/playbook-lint .`: 0.24 s, clean.

## Acronyms

- **YAML** — YAML Ain't Markup Language, the data format of
  `.prose-lint-vocabulary`.
