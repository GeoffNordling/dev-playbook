---
type: Standard
title: Shell Conventions
description: How a shell file is written — the glue boundary, strict mode, declared bash, the shellcheck and shfmt bars, and what a sourced fragment carries
population: "a shell file in a governed repo"
---

# Shell Conventions

A shell file in a governed repo: the set pre-commit's `types: [shell]`
identifies, by extension or by shebang. Shell here is glue, and two kinds
of shell file carry rules of their own: the **executable script**, which
the repo runs, and the **sourced fragment**, which an interactive shell
reads into itself. Both also meet the dialect, shellcheck, and formatting
rules every shell file meets.

## Bash, declared

Every shell file declares bash as its dialect, in a shebang that names
bash or in a `# shellcheck shell=bash` directive.

`shell.bash-declared` · deterministic

> **Why.** Nothing in a governed repo runs under `dash` or `sh`, so
> bashisms are expected: arrays, `[[ ]]`, `mapfile`, process
> substitution. Contorting a script to dodge one buys nothing.

## shellcheck-clean

Every shell file passes shellcheck with no findings.

`shell.shellcheck-clean` · deterministic

## Disable carries a reason

Every `# shellcheck disable=` directive in a shell file carries a
same-line comment giving the reason the suppression is safe.

`shell.disable-carries-a-reason` · stochastic

> **Why.** A `# shellcheck disable=` directive suppresses a finding
> rather than fixing it, so it is a last resort. shellcheck cannot
> check this rule: a disable directive is how a file tells shellcheck
> to stop looking, so the reason is a reviewer's to read.

## Formatting

A shell file's bytes are what `shfmt` writes from that file with its
default options.

`shell.formatting` · deterministic

## Executable scripts

The shell file has the executable bit set.

### Glue only

An executable script wires tools together and nothing more: it defines no
function, declares no array, and reads no positional parameter.

`shell.glue-only` · deterministic

> **Why.** A script that reaches for a function, an array, or argument
> parsing has outgrown shell: the same work as a Python `scripts/` shim
> over `src/`
> ([Runnables live in scripts/](/standards/build/skeleton.md#runnables-live-in-scripts))
> is testable and typed.

### Strict mode

An executable script opens with the shebang `#!/usr/bin/env bash`, and its
first command is `set -euo pipefail`.

`shell.strict-mode` · deterministic

> **Why.** What the rule fixes is the state the shell is in once the
> script starts working: it dies on the first failing command, on an
> unset variable, and on a failure anywhere in a pipeline.

## Sourced fragments

The shell file is under `.bashrc.d/`.

### No shebang, no strict mode

A sourced fragment carries neither a shebang nor `set -euo pipefail`.

`shell.no-shebang-no-strict-mode` · deterministic

> **Why.** A fragment is sourced into an interactive shell rather than
> executed: `set -euo pipefail` in it kills the parent shell on the
> first error, and a file nothing executes directly has no use for a
> shebang.

### Dialect directive

A sourced fragment opens with a `# shellcheck shell=bash` directive.

`shell.dialect-directive` · deterministic
