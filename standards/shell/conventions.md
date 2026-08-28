---
type: Standard
title: Shell Conventions
description: How shell is written — glue-only boundary, strict mode, declared bash, shellcheck-clean
---

# Shell Conventions

Shell here is glue. These rules say where shell is allowed, how an executable
script opens, which dialect it speaks, and the one requirement every shell
file meets. shellcheck and shfmt enforce the mechanical parts at the commit
gate; rules 1–3 are prose by choice — a reviewer's call.

## Boundary — shell is glue only

Shell exists to wire tools together, nothing more. The moment an **executable
script** reaches for a function, an array, or argument parsing, it has outgrown
shell: rewrite it as a Python `scripts/` shim over `src/`, where it is testable
and typed.

**Sourced interactive fragments** (`.bashrc.d/*`) are exempt from the rewrite
rule — their whole job is to mutate the parent shell (cd, aliases, completion),
which a child Python process cannot do. They stay bounded to small
shell-integration helpers all the same; any logic beyond wiring the interactive
shell moves to Python too.

## Strict mode — every executable script opens the same way

Every executable script starts the same way:

```bash
#!/usr/bin/env bash
set -euo pipefail
```

Sourced fragments (`.bashrc.d/*`) carry **neither**: `set -euo pipefail` in a
sourced file kills the parent shell on the first error, and the fragment has no
shebang of its own because it is never executed directly. A sourced fragment
declares its dialect with a `# shellcheck shell=bash` directive at the top
instead, so shellcheck knows how to read it.

## Bash, declared

The declared dialect is bash. Bashisms — arrays, `[[ ]]`, `mapfile`, process
substitution — are fine and expected. POSIX-sh portability is a non-goal:
nothing here has to run under `dash` or `sh`, so do not contort a script to
dodge a bashism.

## shellcheck-clean

Every shell file passes shellcheck with no findings. A `# shellcheck disable=`
directive is a last resort, and each one carries a same-line comment giving the
reason it is safe:

```bash
# shellcheck disable=SC2016  # the $VAR is meant to be literal, not expanded
```

A disable with no reason is itself a defect.
