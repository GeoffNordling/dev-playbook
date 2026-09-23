---
type: General-Sheet
title: Shell
description: The triage of the shell family's seven deterministic rules — three kept, three restated, one deleted, and one escalation, glue-only, whose new check fails two hook scripts today
---

# Shell

Seven deterministic rules in one Standard, `standards/shell/conventions.md`;
`shell.disable-carries-a-reason` is stochastic and skipped. Triaged
per [Triage](/working-docs/doc-type-system/detector-rewrite/triage.md).

The population is pre-commit's `types: [shell]`. On this repo that is
nine tracked files: three sourced fragments under
`dotfiles/.bashrc.d/`, five executable scripts (git mode `100755`:
three hooks under `dotfiles/dot-claude/hooks/`, `statusline.sh`,
`usage-report/scripts/report.sh`), and
`diagnosing-bugs/scripts/hitl-loop.template.sh`, mode `100644`, which
is neither kind. All nine reach both tool hooks. Today `shellcheck`
0.11.0 and `shfmt` 3.13.1 report nothing on them.
[Detector Fixes](/working-docs/doc-type-system/detector-rewrite/detector-fixes.md)
has no survey row for this family.

## conventions.md

Kept as written, the check matching the sentence: `formatted-by-shfmt`.
The `shfmt` hook of the canonical `.pre-commit-config.yaml`
(`maxwinterstein/shfmt-py` `v4.0.0`) passes only `-w`, and no
`.editorconfig` is tracked. This means the hook runs with shfmt's
default options, which is what the sentence says.

- **`bash-declared`**, `standards/shell/conventions.md:17`. Keep, add
  the check. The check passes a file when line 1 is a `#!` line whose
  interpreter is `bash` (`#!/usr/bin/env bash`, `#!/bin/bash`), or when
  a `# shellcheck shell=bash` comment comes before the first command.
  shellcheck reads a file-wide directive only in that position.
  `shellcheck` does not decide the rule: SC2148 fires when there is no
  shebang, but `#!/bin/sh` passes. No file fails today, 9 of 9.
- **`shellcheck-clean`**, `standards/shell/conventions.md:28`. Rewrite,
  `wording only`. Per the ruling that a tool's own configuration is
  the rule: the new body says which configuration.

  > `shellcheck` reports no finding on the file when it runs as the
  > `shellcheck` hook of the canonical `.pre-commit-config.yaml` runs
  > it: with no arguments, so every check at `style` severity and
  > above runs, and no optional check runs.

  Check: the `shellcheck` hook (`shellcheck-py/shellcheck-py`
  `v0.11.0.1`, `types: [shell]`), registered under the hook's name.
  It finds nothing on the 9 files today.
- **`glue-only`**, `standards/shell/conventions.md:57`. Rewrite,
  `wording only`. The check is new. Escalated (1): the check fails two
  hook scripts today.

  > An executable script has no function definition, no array, and no
  > read of a positional parameter. A function definition is `name()`
  > or `function name`. An array is made by `name=(…)`, `declare -a`,
  > `declare -A`, `local -a`, `read -a`, or `mapfile`. A positional
  > read is `$1` or `${1}` and up, `$@`, `$*`, `shift`, or `getopts`.

- **`strict-mode-first`**, `standards/shell/conventions.md:70`. Keep,
  add the check. The check passes a file when line 1 is exactly
  `#!/usr/bin/env bash` and the first line that is not blank and not a
  comment is exactly `set -euo pipefail`. The population is the
  tracked shell files with git mode `100755` in `git ls-files -s`. No
  file fails today, 5 of 5.
- **`no-shebang-no-strict-mode`**, `standards/shell/conventions.md:85`.
  Rewrite, `wording only`. The check is new.

  > Line 1 of a sourced fragment does not start with `#!`, and no line
  > of it is `set -euo pipefail`.

  Check: read line 1, and read each line with its whitespace trimmed,
  for each shell file under a `.bashrc.d/` directory. No file fails
  today, 3 of 3.
- **`dialect-by-directive`**, `standards/shell/conventions.md:96`.
  Delete, because it restates other rules. Under `.bashrc.d/`,
  `shell.no-shebang-no-strict-mode` forbids a shebang. This leaves the
  `# shellcheck shell=bash` directive as the only way to meet
  `shell.bash-declared`. The deletion removes one requirement: the
  directive must be on line 1. After the deletion, the directive can
  be on any line before the first command. All three fragments have
  it on line 1 today.

## Escalations

Ruled 2026-09-23 under the general rulings in
[Triage](/working-docs/doc-type-system/detector-rewrite/triage.md#rulings-that-calibrate-the-rest).
Item 1: parked on Later Checks, the rule leaves the Standard; the
two hooks are fixed first, later.

1. **`shell.glue-only`**, `standards/shell/conventions.md:57`.
   - **Meaning.** An executable shell script only calls other
     programs. When it needs a function, an array, or an argument, it
     must become Python.
   - **Proposal.** Use the restated body above, and add a check that
     sends the file to `shfmt --to-json` and walks the syntax tree:
     - `FuncDecl` nodes;
     - array assignments, and the `-a` and `-A` declare flags;
     - `ParamExp` nodes on `1`–`9`, `@`, or `*`;
     - calls to `shift`, `getopts`, `mapfile`, `readarray`, or
       `read -a`.

     A parser is necessary because a text search reads quoted text
     as shell. For example, the jq program in
     `dotfiles/dot-claude/skills/usage-report/scripts/report.sh:61`
     has `$t1` and `$d` in single quotes. The cost is that the check
     needs the `shfmt` binary in the package environment, from
     `shfmt-py` as a dependency. The rewrite decides between this and
     a hand-rolled lexer.

     Then make the two failing scripts compliant:
     - Split `play-sound` into one script per event. Update
       `dotfiles/dot-claude/settings.json:123` and `:187` to call each
       script by name, with no argument.
     - Move `session-start-stale-base` to Python, like the
       `measure-event` hook beside it. The other option is to write
       out `note` at each of its five call sites.
   - **Difference from today's sentence.** The meaning does not
     change. The restated body lists the forms that each of the three
     clauses covers, where the old body said only "defines", "declares",
     and "reads". Confirm the list. `$#` is not in it, because it
     counts the positional parameters and does not read one.
   - **Difference from today's enforcement.** No check exists today:
     `shell.glue-only: null` at `standards/verifiers.yaml:173`. The new
     check makes the commit gate fail on two files.
   - **Measured.** The repo has 5 executable shell files, and 2 fail:
     - `dotfiles/dot-claude/hooks/play-sound:13` reads `${1:-}` to
       select `stop` or `notification`.
     - `dotfiles/dot-claude/hooks/session-start-stale-base:27` defines
       `note()`, which reads `$1` at `:30`. Five lines call it.

     No executable script makes an array. The rule does not apply to
     `hitl-loop.template.sh`. Its mode is `100644`, and a user runs it
     as `bash hitl-loop.template.sh`. It defines `step()` and
     `capture()` and reads `$1` and `$2`.

## New rules

None.

## Acronyms

None.
