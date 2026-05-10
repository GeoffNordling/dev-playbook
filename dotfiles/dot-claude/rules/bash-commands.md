# Running Bash Commands

## The `!` prefix does not work

Claude's training sometimes suggests "type `! <command>` in the prompt to run
it in the session." This is false — the Claude Code harness has never
implemented this. Do not tell the user to use `!`.

## Handing off interactive commands

The Bash tool runs non-interactively and cannot capture tty prompts
(PIN dialogs, `sudo`, hardware-key taps, GUI pinentry, etc.). When a command
needs that kind of interaction:

1. Present the command in a fenced code block.
2. Ask the user to run it in their terminal and paste the output back.

Do not try to run interactive commands yourself with the Bash tool in these
cases, and do not suggest `!` as a workaround.

## Never chain `cd` with another command

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

If you catch yourself typing `cd … && …`, stop and split it. No
exceptions for "just a quick check."

## Quote regex patterns with single quotes

Backticks, `$`, `!`, and `\` inside `"..."` are interpreted by bash. A lone
backtick in double quotes hangs with `unexpected EOF`. Use single quotes for
any pattern argument:

    grep -n '^`' file       # right
    grep -n "^`" file       # wrong — bash waits for closing backtick

When a `&&`-chained or parallel `Bash` call fails this way, siblings get
cancelled too. Prefer single quotes by default for regex/pattern data.

## SSH-bound git operations

If the remote is `git@github.com:...`, then `git fetch`, `git pull`, and
`git push` all require the user's SSH key — hardware-token taps in this
workspace. Treat them like any other interactive command:

- For read-only checks (e.g. "does local `main` match `origin/main`?"), use
  `gh api` instead — it goes over HTTPS with a PAT and needs no tap.
  Example: `gh api repos/{owner}/{repo}/branches/main --jq .commit.sha`
- For pushes, hand the command back to the user.
