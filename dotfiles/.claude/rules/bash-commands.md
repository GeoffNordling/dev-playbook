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

## Use absolute paths, not `cd`

Pass an absolute path to the command, or use a path flag: `git -C <dir>`,
`ls <dir>`, `make -C <dir>`. Keep the shell's working directory stable
across the session.

`cd` in compound commands is enforced against: `cd <relative> && … <redirect>`
is flagged as "path resolution bypass" and prompts for manual approval. The
prompt is correct — rewrite the command, don't ask the user to approve.

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
