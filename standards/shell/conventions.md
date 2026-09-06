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

Every shell file declares bash as its dialect, and no shell file is
contorted for POSIX-sh portability.

Bashisms are fine and expected: arrays, `[[ ]]`, `mapfile`, process
substitution. Nothing in a governed repo runs under `dash` or `sh`, so a
script rewritten to dodge a bashism is rejected on that ground alone. An
executable script declares the dialect in its shebang
([Strict mode](#strict-mode)); a sourced fragment declares it in a
directive ([Dialect directive](#dialect-directive)).

## shellcheck-clean

Every shell file passes shellcheck with no findings. shellcheck is pinned
in the canonical
[.pre-commit-config.yaml](/standards/build/canonical/.pre-commit-config.yaml),
which stations it at the commit gate.

A `# shellcheck disable=` directive suppresses a finding rather than fixing
it, so it is a last resort and carries its reason
([Disable carries a reason](#disable-carries-a-reason)).

## Disable carries a reason

Every `# shellcheck disable=` directive carries a same-line comment giving
the reason the suppression is safe. A disable with no reason is itself a
defect.

```bash
# shellcheck disable=SC2016  # the $VAR is meant to be literal, not expanded
```

shellcheck cannot check this rule: a disable directive is how a file tells
shellcheck to stop looking, so the reason is a reviewer's to read.

## Formatting

A shell file's bytes are what `shfmt` writes: tab indentation, and shfmt's
default spacing and line breaks. The commit gate stations `shfmt -w`, so a
file that differs is rewritten and the hook fails; `shfmt -d` gives a
reviewer the same answer without the rewrite.

shfmt is pinned in the canonical
[.pre-commit-config.yaml](/standards/build/canonical/.pre-commit-config.yaml)
with no `args:` override, so shfmt's defaults are the bar.

## Executable scripts

A shell file with the executable bit set: a file the repo runs, rather than
one it reads.

### Glue only

An executable script wires tools together and nothing more. The moment it
reaches for a function, an array, or argument parsing, it has outgrown
shell and is rewritten as a Python `scripts/` shim over `src/`, where it is
testable and typed
([Runnables live in scripts/](/standards/build/skeleton.md#runnables-live-in-scripts)).

### Strict mode

An executable script opens with the shebang `#!/usr/bin/env bash` and
carries `set -euo pipefail` before its first command.

```bash
#!/usr/bin/env bash
set -euo pipefail
```

A header comment between the two lines satisfies the rule. What the rule
fixes is the state the shell is in once the script starts working: it dies
on the first failing command, on an unset variable, and on a failure
anywhere in a pipeline.

## Sourced fragments

A shell file under `.bashrc.d/`: a fragment an interactive shell sources
into itself rather than executes.

### No shebang, no strict mode

A sourced fragment carries neither a shebang nor `set -euo pipefail`.
`set -euo pipefail` in a sourced file kills the parent shell on the first
error, and a file nothing executes directly has no use for a shebang.

### Dialect directive

A sourced fragment opens with a `# shellcheck shell=bash` directive, so
shellcheck knows which dialect to read it as. The directive is the
fragment's declaration of dialect, holding the place a shebang holds in an
executable script ([Bash, declared](#bash-declared)).

### Bounded to shell integration

A sourced fragment holds only what mutates the parent shell: cd, aliases,
and completion. Logic beyond that moves to Python.

A child Python process cannot change the parent shell's directory, define
its aliases, or register its completions, which is the whole reason this
work stays in shell. `dotfiles/.bashrc.d/worktree.sh` is the shape: the
command `cdwt()`, its completion function `_cdwt()`, and nothing else. A
fragment that parses arguments or implements an algorithm is rejected, the
same as an executable script that does ([Glue only](#glue-only)).
