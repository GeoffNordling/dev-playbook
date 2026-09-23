---
type: General-Sheet
title: Shell
description: The rewrite of the shell family's seven deterministic rules — three checks over the model, two registered to their tool hooks, two deleted, one per its escalation, one Standard edited to the triage, and nothing retired
---

# Shell

The step built the three functions of `src/dev_playbook/checks/shell.py`
and `tests/dev_playbook/checks/test_shell.py` from
[the shell triage](/working-docs/doc-type-system/detector-rewrite/triage/shell.md).
The two tool-decided rules were already registered and stay as they were.

## Built

- `shell.bash-declared`: function `bash_declared`. Kept as written; the
  check passes a shebang whose interpreter is bash, or a
  `# shellcheck shell=bash` directive before the first command.
- `shell.shellcheck-clean`: hook `shellcheck`. The report's blockquote
  replaced the body of `standards/shell/conventions.md`.
- `shell.formatted-by-shfmt`: hook `shfmt`. Kept as written.
- `shell.strict-mode-first`: function `strict_mode_first`. Kept as
  written; the check reads the tracked shell files with the executable
  bit.
- `shell.no-shebang-no-strict-mode`: function
  `no_shebang_no_strict_mode`. The report's blockquote replaced the
  body; the check reads each shell file under a `.bashrc.d/` directory.

The three functions share one population, the files pre-commit's
`types: [shell]` selects: a name or extension `identify` tags `shell`,
or, where the name tags nothing, an executable file whose shebang names
a shell. On this repo that is the nine files the triage counts.

## Deleted

- `shell.glue-only`, per escalation 1: heading, body, trailer, and Why.
  No link pointed at it. The opening paragraph, the `description`, the
  intro and row of `standards/shell/index.md`, and the row in
  `standards/index.md` no longer name the glue boundary.
- `shell.dialect-by-directive`, as a restatement of
  `shell.no-shebang-no-strict-mode` and `shell.bash-declared`. No link
  pointed at it.

## Retired

None.

## Set aside

None.

## Measured

- `uv run playbook check .`: 0.53 s, 105 checks over 467 files, zero
  findings.
- `scripts/playbook-lint .`: 0.15 s, clean.

## Acronyms

None.
