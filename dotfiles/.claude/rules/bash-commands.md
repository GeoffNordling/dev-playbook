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
