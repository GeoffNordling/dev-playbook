# Never chain `cd` with another command

`cd` may only appear as a **standalone** Bash call. Never combine it with
`&&`, `;`, `|`, or a newline-separated follow-up in the same Bash
invocation — not with relative paths, not with absolute paths, not with
read-only follow-ups like `pwd`/`git status`/`ls`. The harness treats
chained `cd` as a path-resolution bypass and prompts the user; even when
it doesn't, it violates this rule.

The pattern is two Bash calls:

1. `cd /abs/path` on its own to anchor the cwd.
2. A separate Bash call (or several, in parallel where independent) for
   the actual work — using paths relative to the anchored cwd, or
   absolute paths.

Wrong (all of these):

    cd /abs/path && pwd
    cd /abs/path && git status && git log
    cd worktree && ls

Right:

    # call 1
    cd /abs/path
    # call 2
    git status

If you catch yourself typing `cd … && …`, stop and split it.