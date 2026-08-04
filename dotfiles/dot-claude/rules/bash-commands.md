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

`gh` and `git` are sandbox-excluded: each escapes the bwrap jail to reach the
same out-of-jail resource — the keyring holding the PAT, which `gh` reads
directly and `git` reaches through the credential helper. That escape works
**only when the command is the first, top-level thing on its line.** Every rule
below protects that.

**Do:**

- **Start the line with `gh`/`git`.** Chaining with `&&`/`;` and piping with
  `|` keep it leading — all fine.
- **Read the result from stdout, shaped with `--jq`.** Take the value out of
  the tool result yourself; don't route it through a temp file. This one habit
  sidesteps both traps below.

      gh api repos/{owner}/{repo}/branches/main --jq .commit.sha

- **One top-level call per item — never a loop.** Acting on several issues/PRs
  is several separate Bash calls (run them in parallel), not a `for`/`while`
  over a single call.
- **Keep a long query inline** as a quoted `-f query='…'` argument on the same
  line — never a heredoc piped into `bash -c`.

**Two traps this guards against** — both hit in real sessions:

- **Nesting jails the command.** Inside `$(…)`, a `for`/`while` loop,
  `bash -c '…'`, or behind `env`/`timeout`/`xargs`, it runs *inside* the jail
  and auth fails: the keyring is out of reach, so `gh` returns HTTP 401 and
  `git` push/pull fails with an invalid or missing PAT. To capture a value,
  write it to a file on its own top-level `gh` line, then `id=$(cat file)` on a
  separate line — `$(cat …)` is fine, `$(gh …)` is not.
- **`$TMPDIR` is empty on the escaped line.** The escape context drops session
  env vars, so `> "$TMPDIR/x"` (or `| tee "$TMPDIR/x"`) on a `gh`/`git` line
  writes to `/x` at the root and fails with `Permission denied` — even though
  `$TMPDIR` resolves fine for ordinary sandboxed commands. When a `gh`/`git`
  line must write a file, hardcode the literal path (it's the scratchpad path
  in your prompt, or run plain `echo "$TMPDIR"` first), never the `$TMPDIR`
  variable.

Right — capture a value for a follow-on command in the same call:

    gh api graphql -f query='query { repository(owner:"o", name:"r") { id } }' --jq '.data.repository.id' > /tmp/claude-1000/id
    id=$(cat /tmp/claude-1000/id)

## Remote git operations

Remotes are HTTPS, and git authenticates with the same keyring PAT `gh` uses,
reached through the credential helper. So `git fetch`, `git pull`, and
`git push` are ordinary non-interactive commands — run them yourself, subject
to the push rules below. No remote git operation in this workspace is
interactive, so none of them belong in the hand-off section above.

The canonical commands, each already granted in settings:

    git push -u origin <branch>
    git push --no-verify -u origin <branch>
    git fetch --prune origin
    git pull --ff-only origin main

Three push families are denied outright, by permission rule and by the
`git-authority` PreToolUse hook: anything targeting `main`, anything forcing
(including `--force-with-lease`), and anything deleting a remote ref. **A denied
operation is refused, never re-spelled** — do not look for a wording that gets
past the rule. Hand it to the user for their own terminal and say why. See
[git-authority](~/workspace/dev-playbook/software-factory/git-authority.md).

For a read-only check that needs no clone state (e.g. "does local `main` match
`origin/main`?"), `gh api` is still the cheapest route:
`gh api repos/{owner}/{repo}/branches/main --jq .commit.sha`
