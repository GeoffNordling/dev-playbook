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
The number is the one the rows above cite.

1. `every-harness-file-matches-a-member-row`,
   `standards/harness/files.md:18`: built, with the table brought to
   the repo as it stands, a `statusline.sh` row and the workflows row
   over both roots.
2. `every-runbook-at-a-fixed-path`, `standards/harness/files.md:39`:
   built, the tree read as a closed list.

The new rule below is accepted.

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
