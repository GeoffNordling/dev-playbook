---
type: General-Sheet
title: Harness
description: The triage of the harness family's five deterministic rules — one kept, two restated plain with their meaning held, two null rules restated to gain a check and escalated
---

# Harness

Five deterministic rules over two Standards under `standards/harness/`.
Three stochastic rules are skipped: `operational-content-only`,
`one-rule-one-scope`, `one-rule-per-heading`. Today's check for the
two rules that have one is `check_global_claude` in
`scripts/harness-files-lint:517`. Three rules are `null` in
`standards/verifiers.yaml:80-82`. The survey in Detector Fixes has no
`harness.*` row. Triaged per
[Triage](/working-docs/doc-type-system/detector-rewrite/triage.md).

## claude-content.md

Kept as written, the check matching the sentence:
`behaviors-then-principles`. `scripts/harness-files-lint:534-547`
collects the `## ` lines outside fences through `md.content_lines` and
compares the tuple to `("## Behaviors", "## Principles")`. The check
runs only when `dotfiles/dot-claude/CLAUDE.md` exists (`:531-533`),
which is the rule's population. It passes today: the file has
`## Behaviors` at line 3 and `## Principles` at line 60.

- **`no-frontmatter`**, `standards/harness/claude-content.md:28`.
  Rewrite, gaining a check.

  > The first line of a `CLAUDE.md` is not `---`.

  `wording only`. Check: for every tracked file named `CLAUDE.md` at
  any depth, compare line 1 to `---`. No check exists today
  (`verifiers.yaml:82` is `null`). `okf-lint` does not see the file
  either, because `classify()` at `src/dev_playbook/md.py:289` makes
  every `CLAUDE.md` a harness file. The 2 tracked files, `CLAUDE.md`
  and `dotfiles/dot-claude/CLAUDE.md`, both open on `# `, so 0 fail.
- **`two-required-rules`**, `standards/harness/claude-content.md:69`.
  Rewrite.

  > The global source has the headings `### Read the standards` and
  > `### Navigate docs by index`, both outside fenced code blocks.

  `wording only`: "carries" becomes "has". The check does not change:
  `scripts/harness-files-lint:548-552` reports each of the two lines
  that is not among the file's heading lines outside fences. It
  passes today (lines 5 and 10).

## files.md

- **`every-harness-file-matches-a-member-row`**,
  `standards/harness/files.md:18`. Rewrite, gaining a check. Meaning
  changed. Escalation 1.

  > Every tracked file under `.claude/` or `dotfiles/dot-claude/` has
  > one of these paths below that directory: `CLAUDE.md`,
  > `skills/<name>/` and any file under it, `agents/<name>.md`,
  > `rules/<name>.md`, `settings.json`, `settings.local.json`,
  > `hooks/` and any file under it, `workflows/<name>.js`,
  > `statusline.sh`.

  The table keeps its columns. The `.claude/workflows/*.js` row becomes
  `workflows/*.js`, and a `statusline.sh` row is added. Check: match
  each tracked path under the two roots against the nine patterns. No
  check exists today (`verifiers.yaml:80` is `null`).
- **`every-runbook-at-a-fixed-path`**, `standards/harness/files.md:39`.
  Rewrite, gaining a check. Meaning changed. Escalation 2.

  > Every directory directly under `.claude/skills/` or
  > `dotfiles/dot-claude/skills/` has a `SKILL.md`, and has nothing
  > else in it but `references/`, `scripts/`, and `agents/`. Every
  > file under `.claude/agents/` or `dotfiles/dot-claude/agents/` is
  > a `.md` file directly in that directory.

  The tree block stays as the illustration. Check: group the tracked
  paths under each skills root by their first segment, then test each
  group for `SKILL.md` and for other entries. Test each tracked path
  under an agents root for depth 1 and the `.md` suffix. Today
  (`verifiers.yaml:81` is `null`) only part of this is enforced, and
  under no id. `audit_skill` at `scripts/harness-files-lint:454-462`
  raises `ToolError` and exits 2 when a directory under a skills root
  has no `SKILL.md`. `main` at `:631` globs `*.md` under an agents
  root, so it does not see a non-`.md` file or a subdirectory.

## Escalations

Ruled 2026-09-23 under the general rulings in
[Triage](/working-docs/doc-type-system/detector-rewrite/triage.md#rulings-that-calibrate-the-rest).
Item 1: built, with the table brought to the repo as it stands, a
`statusline.sh` row and the workflows row over both roots. Item 2:
built, the tree read as a closed list. The new rule is accepted.

1. **`every-harness-file-matches-a-member-row`**,
   `standards/harness/files.md:18`.
   - Meaning: every tracked file under a harness root is one of the
     file kinds that the table lists.
   - Proposal: the path list above. Add a table row for
     `statusline.sh`: class code, role "run by the `statusLine`
     setting", content standard none yet. Change the workflows row
     from `.claude/workflows/*.js` to `workflows/*.js`, relative to
     either root like the other rows.
   - Difference from today's sentence: "matches a member row" becomes
     nine literal path patterns. "Skill bundles" becomes
     `skills/<name>/` and any file under it. The workflows row covers
     both roots, not `.claude/` only. The table gains one row.
     "Tracked" is added, because the repo model reads only
     `git ls-files` (Decided, Repo model). The untracked harness state
     under the roots, such as `.claude/worktrees/` and the
     `dotfiles/dot-claude/` runtime directories that `.gitignore:12-32`
     lists, is then out of scope.
   - Difference from today's enforcement: no check exists. The new
     check starts to run.
   - Measured: 59 tracked files under `dotfiles/dot-claude/`, none
     under `.claude/`. Under the proposal, 0 fail. Under today's
     sentence read literally, 3 fail:
     `dotfiles/dot-claude/statusline.sh`, which no row names (it is
     run from `dotfiles/dot-claude/settings.json:204`), and the two
     files in `dotfiles/dot-claude/workflows/`, which the
     `.claude/`-only row does not cover. If the rule gets a check with
     no change to its sentence, the repo goes out of compliance.
2. **`every-runbook-at-a-fixed-path`**, `standards/harness/files.md:39`.
   - Meaning: a skill is a directory under a skills root that has a
     `SKILL.md`, and an agent is a `.md` file directly under an agents
     root.
   - Proposal: the restatement above.
   - Difference from today's sentence: the sentence and its tree block
     say where a runbook sits. They do not say whether a bundle can
     have an entry that is not in the tree, such as `assets/`. The
     restatement reads the tree as a closed list. If the user reads it
     as open, remove "and has nothing else in it but `references/`,
     `scripts/`, and `agents/`", and the remaining restatement is
     `wording only`.
   - Difference from today's enforcement: a missing `SKILL.md` is an
     exit-2 error state today (`scripts/harness-files-lint:459`) and
     becomes a finding under this id. A bundle entry outside the three
     directories, and a non-`.md` file or a subdirectory under an
     agents root, are not reported today. With the proposal, they are
     reported. Today the detector skips a symlinked bundle and
     `synced/` (`discover_internal_skills`, `:556-579`). Git tracks a
     symlink as a file, not a directory, so the proposal does not
     select one. `synced/` is in `.gitignore:32`, so the model does not
     read it.
   - Measured: 27 directories under `dotfiles/dot-claude/skills/`,
     each with a tracked `SKILL.md`. The 16 other bundle files are all
     under `references/` (6), `scripts/` (2), or `agents/` (8,
     each `openai.yaml`). The 4 files under `dotfiles/dot-claude/agents/`
     are `.md` at depth 1. 0 tracked symlinks. So 0 fail.

## New rules

- **`### Read the standards` first**, for
  `standards/harness/claude-content.md` under Global file. The Why at
  `claude-content.md:22` says that `### Read the standards` "must be
  the first heading in the file", but no rule states that. Also the
  statement is not correct as written, because `# Global` at line 1 is
  the first heading. Proposed body: "`### Read the standards` is the
  first `###` heading of the global source, outside fenced code
  blocks." It passes today (line 5). The alternative is to correct the
  Why and add no rule.

## Acronyms

None.
