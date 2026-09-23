---
type: General-Sheet
title: Prose
description: The triage of the prose family's four deterministic rules — one kept, two restated plain with the meaning held, one restated to name its word and escalated, and one new rule for the vocabulary file
---

# Prose

Four deterministic rules in one Standard, `standards/prose/conventions.md`.
The other fourteen rules in the file are stochastic and are not triaged
here. Today one detector decides all four: `scripts/prose-lint`, a shim
over `audit` in `src/dev_playbook/prose_lint.py:347`. On this worktree
it reports 0 findings.

## conventions.md

Kept as written, the check matching the sentence:
`judgment-not-judgement`. The check is `scan_text`,
`src/dev_playbook/prose_lint.py:197`: `.md` files only, body only, fenced
blocks and inline code spans removed, `\bjudgements?\b` in any case.

- **`no-first-person`**, `standards/prose/conventions.md:110`. Rewrite,
  wording only.

  > The document does not contain the word `I`, `me`, or `my`, in its
  > frontmatter or its body. Exempt: `I` in `I/O`, and a word inside
  > double quotes, an inline code span, or a fenced block.

  `wording only`. The member stays the document of the condition
  `Harness-loaded agent instructions` (`conventions.md:104`): a Markdown
  file named `CLAUDE.md`, or one with a path segment `skills`, `rules`,
  or `agents` (`md.is_agent_instruction`, `src/dev_playbook/md.py:230`).
  The check is `scan_voice`, `src/dev_playbook/prose_lint.py:244`, with
  the three patterns in `src/dev_playbook/voice.py:23`; it stays. The
  survey in Detector Fixes names two gaps. The first, non-`.md` files
  under `skills/` never scanned, is not a gap: the Standard's
  population is "an authored document" and its H1 says Markdown. 10
  such files are tracked (8 `agents/openai.yaml`, 2 `.sh`), and 0 of
  them has a first-person word, so neither reading moves the repo. The
  second, the `md.classify` "excluded" skip at `prose_lint.py:365`,
  goes: the model lists tracked files only, and 0 tracked files are
  `PLAN.md`, `PROGRESS.md`, or under `tmp/`.
- **`no-banned-word`**, `standards/prose/conventions.md:156`. Rewrite,
  meaning changed. Escalation 1.

  > The file does not contain the workspace's banned word, singular
  > or plural, in any case, frontmatter, code spans, and fenced blocks
  > included. The match is a whole word: the word joined to another
  > by a hyphen or a space fails, the word inside a longer word passes.

  The Standard spells the word; this report does not.

  `meaning changed`. The check is `scan_banned`,
  `src/dev_playbook/prose_lint.py:216`, over `WORKSPACE_VOCABULARY`,
  `prose_lint.py:157`, with the pattern `\bhumans?\b` in any case
  (`Word.pattern`, `prose_lint.py:121`). It stays.
- **`no-word-the-repo-bans`**, `standards/prose/conventions.md:162`.
  Rewrite, wording only.

  > For each word in the repo's `.prose-lint-vocabulary`, no tracked
  > file under a directory listed for that word contains the word, bare
  > or plural, in any case, frontmatter, code spans, and fenced blocks
  > included. A word with no directory listed is banned in every
  > tracked file.

  `wording only`. The check is `scan_banned` again, over the repo's
  words that `vocabulary`, `src/dev_playbook/prose_lint.py:291`, reads.
  The survey names three skips in `audit` with no exception behind
  them: the `md.classify` "excluded" path (`prose_lint.py:365`), a
  symlink (`:367`), and a file with a zero byte (`:370`). None decides a
  file today: 0 tracked excluded paths and 0 tracked symlinks (mode
  `120000` in `git ls-files -s`). The model lists tracked files only,
  so the first skip goes and the untracked files `md.find_files` adds
  today (`--others`) go with it. A symlink and a binary file have no
  text in the model, so the check reads nothing there.

## Escalations

Ruled 2026-09-23 under the general rulings in
[Triage](/working-docs/doc-type-system/detector-rewrite/triage.md#rulings-that-calibrate-the-rest).
The number is the one the rows above cite.

1. `no-banned-word`, `standards/prose/conventions.md:156`: built; the
   Standard names the word, the code keeps it as a constant, a test
   asserts the two agree, and the `population` line gains "and, for
   the two word rules, every tracked file". This report does not spell
   the word, so the gate passes.

The new rule below is accepted.

## New rules

- **The vocabulary file is well formed.** Under
  `no-word-the-repo-bans`. Proposed body:

  > `.prose-lint-vocabulary`, where the repo has one, is a YAML
  > mapping. Each key is a word the workspace does not already ban. Each
  > value has a `say` string and, optionally, a `where` list of
  > directories that exist in the repo, and no other key.

  Today `vocabulary`, `src/dev_playbook/prose_lint.py:291`, enforces
  exactly this and stops the run with exit 2, under no rule id. The
  rewrite's exit state is that every check decides a stated rule, so
  the check needs this rule or goes. The one declaration today, the
  word `guard` over `doc-types` and `standards/doc-type`, passes. The
  heading is new and needs the user's approval.

## Acronyms

- **YAML** — YAML Ain't Markup Language, the data format of
  `.prose-lint-vocabulary`.
