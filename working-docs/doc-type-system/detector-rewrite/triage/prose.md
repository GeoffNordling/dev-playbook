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
Item 1: built; the Standard names the word, the code keeps it as a
constant, a test asserts the two agree, and the population line
gains the two word rules over every tracked file. This report does
not spell the word, so the gate passes. The new rule is accepted.

1. **`no-banned-word`**, `standards/prose/conventions.md:156`.
   - **What it means.** No tracked file, of any type, contains the
     banned word or its plural, in any case, anywhere in the file.
   - **Proposal.** The body in the row above. It names the word, and it
     says "whole word" with four examples in place of "alone or in a
     compound".
   - **Against today's sentence.** Today's body names no word. It
     points at the constant `WORKSPACE_VOCABULARY` in
     `src/dev_playbook/prose_lint.py`, a file the rewrite deletes, so
     the pointer goes stale on exit. The proposal writes the word in the
     Standard. `standards/prose/conventions.md` is already in
     `.prose-lint-exempt`, under the comment "The three files that must
     name the banned word in order to ban it"; today the file has 0
     occurrences, so the proposal makes that comment true again. "In a
     compound" read wide also bans a closed compound such as
     `superhuman`; the proposal passes it. This is the meaning change.
     An earlier amendment chose the pointer over the word, so the user
     rules on it.
   - **Against today's enforcement.** None. `Word.pattern`,
     `prose_lint.py:121`, is `\bhumans?\b` in any case: a hyphen or a
     space ends the word, a letter does not. An underscore does not
     either, so `human_review` passes today; the proposal keeps that.
   - **Measured.** 0 findings today. 1 occurrence of the word inside
     a longer word in the tracked files outside `.prose-lint-exempt`,
     `docs/decisions/0022-prose-lint-exempt-file.md:18`. It passes
     under both readings.
   - **One more gap, for the same ruling.** The Standard's `population`
     is "an authored document, except type: Mirror and the paths in
     .prose-lint-exempt" (`conventions.md:5`). This rule and
     `no-word-the-repo-bans` bind every tracked file: 97 `.py`, 13
     `.yaml`, 27 extensionless files, and more. The proposal adds to the
     `population` line: "and, for the two word rules, every tracked
     file". The check already reads every file, so the repo does not
     move.

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
