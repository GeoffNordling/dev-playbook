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
The number is the one the rows above cite.

1. `glue-only`, `standards/shell/conventions.md:57`: deleted. The
   user's reason: it micromanages how code is written and shapes no
   high-level guidance or comprehension.

## New rules

None.

## Acronyms

None.
