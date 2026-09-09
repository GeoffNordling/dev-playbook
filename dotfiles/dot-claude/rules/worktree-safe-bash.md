# Worktree-safe Bash

In a worktree session the harness refuses any Bash call in which a
command's name is computed where it cannot read the value, whether or
not `git` appears in the call. The refused shapes:

- a loop variable as the command: `for l in …; do scripts/$l; done`,
  `… | while read l; do scripts/$l; done`
- command substitution as the command: `$(echo scripts/okf-lint)`
- `eval`
- `xargs` building a command: `… | xargs -I{} scripts/{}`

Everything else runs, in a worktree as anywhere: literal commands chained
with `&&` or `;`, `git` included; a variable whose assignment is in the
same call; a loop or subshell whose body names its commands literally.

Wrong:

    for l in okf-lint ref-lint repo-lint; do scripts/$l; done

Right:

    scripts/okf-lint; scripts/ref-lint; scripts/repo-lint

The loop saves nothing: the literal chain is the same length and runs.
Where a repo has one entry point for the whole set, dev-playbook's
`scripts/playbook-lint` for every commit-gate detector, call that.
