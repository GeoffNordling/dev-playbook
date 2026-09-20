---
type: Guide
title: Shell Guide
description: The thinking behind the shell rules — bash and not POSIX sh, shellcheck and the cost of a disable, shfmt's defaults as the bar, when a script has outgrown shell, what strict mode fixes, and why a sourced fragment is different
---

# Shell Guide

The guide behind [Shell Conventions](/standards/shell/conventions.md),
the ruleset that binds a shell file in a governed repo. This guide
carries the reasoning and the examples; nothing here is enforced.

## Bash, not POSIX sh

Bashisms are fine and expected: arrays, `[[ ]]`, `mapfile`, process
substitution. Nothing in a governed repo runs under `dash` or `sh`, so
a script contorted to dodge a bashism is rejected on that ground alone.
An executable script declares the dialect in its shebang and a sourced
fragment in a directive
([Bash, declared](/standards/shell/conventions.md#bash-declared)).

## shellcheck and the cost of a disable

shellcheck is pinned in the canonical
[.pre-commit-config.yaml](/standards/build/canonical/.pre-commit-config.yaml),
which stations it at the commit gate. A `# shellcheck disable=`
directive suppresses a finding rather than fixing it, so it is a last
resort and carries its reason on the same line:

```bash
# shellcheck disable=SC2016  # the $VAR is meant to be literal, not expanded
```

shellcheck cannot check this rule: a disable directive is how a file
tells shellcheck to stop looking, so the reason is a reviewer's to read
([Disable carries a reason](/standards/shell/conventions.md#disable-carries-a-reason)).

## shfmt's defaults are the bar

shfmt is pinned in the same canonical config with no `args:` override,
so its defaults, tab indentation and its own spacing and line breaks,
are the bar ([Formatting](/standards/shell/conventions.md#formatting)).
The commit gate stations `shfmt -w`, so a file that differs is
rewritten and the hook fails; `shfmt -d` gives a reviewer the same
answer without the rewrite.

## When a script has outgrown shell

An executable script, a file the repo runs rather than reads, wires
tools together and nothing more. The moment it reaches for a function,
an array, or argument parsing, it has outgrown shell and is rewritten
as a Python `scripts/` shim over `src/`, where it is testable and typed
([Glue only](/standards/shell/conventions.md#glue-only),
[Runnables live in scripts/](/standards/build/skeleton.md#runnables-live-in-scripts)).

## What strict mode fixes

```bash
#!/usr/bin/env bash
set -euo pipefail
```

A header comment between the two lines satisfies the rule. What the
rule fixes is the state the shell is in once the script starts working:
it dies on the first failing command, on an unset variable, and on a
failure anywhere in a pipeline
([Strict mode](/standards/shell/conventions.md#strict-mode)).

## Why a sourced fragment is different

A file under `.bashrc.d/` is sourced into an interactive shell rather
than executed. `set -euo pipefail` in a sourced file kills the parent
shell on the first error, and a file nothing executes directly has no
use for a shebang
([No shebang, no strict mode](/standards/shell/conventions.md#no-shebang-no-strict-mode)).
The `# shellcheck shell=bash` directive is the fragment's declaration
of dialect, holding the place a shebang holds in an executable script.

A fragment holds only what mutates the parent shell, because that is
the one job a child Python process cannot do: it cannot change the
parent's directory, define its aliases, or register its completions
([Bounded to shell integration](/standards/shell/conventions.md#bounded-to-shell-integration)).
`dotfiles/.bashrc.d/worktree.sh` is the shape: the command `cdwt()`,
its completion function `_cdwt()`, and nothing else. A fragment that
parses arguments or implements an algorithm is rejected, the same as an
executable script that does.
