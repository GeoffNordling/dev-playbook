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

## Format hand-off commands as single paste-safe lines

When you hand the user a command to run in **their own** terminal, copying from
this chat is lossy: a paste can split one line into several, or merge several
into one. So:

- **Make each command one line.** Chain the steps with `&&` (and pipes as
  needed) so the whole thing pastes and runs as a single line, even when it
  soft-wraps on screen.
- **State the line count.** Say "this is one line" so a soft-wrap isn't mistaken
  for several commands.
- **If it genuinely must be multiple lines** (independent commands where a
  mid-way failure should not stop the rest, or a heredoc), number them and say
  "run these N separately, in order."
- One `&&`-chained line beats a stack of lines the user selects and pastes one
  at a time — prefer it even for multi-step setup.

This is about commands the **user** runs; it does not relax the `cd` rule below,
which governs **your own** Bash tool calls.

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

## Keep sandbox-excluded commands leading and top-level

A sandbox-excluded command (`gh`, `git`) only escapes the bwrap jail to reach
its out-of-jail resource — the keyring holding `gh`'s PAT, the SSH remote for
`git` — when it is the **leading, top-level** command; nested inside a `$(…)`
capture, a `for`/`while` loop, a `bash -c '…'`, or behind a prefix
(`env`/`timeout`/`xargs`) it runs *inside* the jail and fails auth. So never
nest it. Chaining with `&&`/`;` and piping keep it leading and are fine.

When you need a value from the command, run it on its own line writing to a file
and read the file back — never capture it in `$(gh …)`. A long or multi-line
query belongs in a quoted `-f query='…'` argument on the top-level call, never a
heredoc piped into `bash -c`.

Wrong (jailed — no token, GraphQL fails every time):

    id=$(gh api graphql -f query='query { repository(owner:"o", name:"r") { id } }' --jq '.data.repository.id')

Right (`gh` runs leading/top-level; the non-`gh` `$(cat …)` does the capture):

    gh api graphql -f query='query { repository(owner:"o", name:"r") { id } }' --jq '.data.repository.id' > "$TMPDIR/id"
    id=$(cat "$TMPDIR/id")

## SSH-bound git operations

If the remote is `git@github.com:...`, then `git fetch`, `git pull`, and
`git push` all require the user's SSH key — hardware-token taps in this
workspace. Treat them like any other interactive command:

- For read-only checks (e.g. "does local `main` match `origin/main`?"), use
  `gh api` instead — it goes over HTTPS with a PAT and needs no tap.
  Example: `gh api repos/{owner}/{repo}/branches/main --jq .commit.sha`
- For pushes, hand the command back to the user.
