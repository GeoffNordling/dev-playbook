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

The reasoning behind the rules is the
[Shell Explanation](/standards/shell/explanation.md).

## Bash, declared

Every shell file declares bash as its dialect, in a shebang that names
bash or in a `# shellcheck shell=bash` directive.

`shell.bash-declared` · deterministic

## shellcheck-clean

Every shell file passes shellcheck with no findings.

`shell.shellcheck-clean` · deterministic

## Disable carries a reason

Every `# shellcheck disable=` directive in a shell file carries a
same-line comment giving the reason the suppression is safe.

`shell.disable-carries-a-reason` · stochastic

## Formatting

A shell file's bytes are what `shfmt` writes from that file with its
default options.

`shell.formatting` · deterministic

## Executable scripts

The shell file has the executable bit set.

`shell.executable-scripts` · deterministic

### Glue only

An executable script wires tools together and nothing more: it defines no
function, declares no array, and reads no positional parameter.

`shell.glue-only` · deterministic

### Strict mode

An executable script opens with the shebang `#!/usr/bin/env bash`, and its
first command is `set -euo pipefail`.

`shell.strict-mode` · deterministic

## Sourced fragments

The shell file is under `.bashrc.d/`.

`shell.sourced-fragments` · deterministic

### No shebang, no strict mode

A sourced fragment carries neither a shebang nor `set -euo pipefail`.

`shell.no-shebang-no-strict-mode` · deterministic

### Dialect directive

A sourced fragment opens with a `# shellcheck shell=bash` directive.

`shell.dialect-directive` · deterministic

### Bounded to shell integration

A sourced fragment holds only what mutates the parent shell: directory
changes, aliases, and completions.

`shell.bounded-to-shell-integration` · stochastic
