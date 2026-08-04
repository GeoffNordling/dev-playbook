---
type: Guide
title: Git Authority
description: The layers deciding which git operations an agent may run, the push and commit rule families, and the canonical command set
---

# Git Authority

Every remote is HTTPS and git authenticates with the same keyring PAT `gh`
uses, reached through the credential helper. Nothing in this workspace needs a
hardware token, so pushing is an agent's own act — which makes the question
"may this agent run this git command?" one the machine has to answer, every
time, on its own.

Five layers answer it: three decide (the deny block, the hook, the allowlist),
one says the same thing in prose to the hands-off classifier, and one is
GitHub's own last backstop. The binding rule across all of them is one
sentence:

> **A denied operation is refused, never re-spelled.**

An agent that hits a denial reports what it tried and why it was refused. It
does not search for a wording that gets past the rule, and it does not ask
another agent to run it. The push family has no override marker and no grant
lane — its escape hatch is the human's own terminal. The commit family has
exactly one grant lane, the human-typed `/commit-on` marker (below), and
nothing an agent writes can mint it.

## The layers

| Layer | Where it lives | What it decides |
|---|---|---|
| Server-side ruleset | GitHub, per [repo settings](/standards/tracking/repo-settings.md) | The last backstop: main rejects force-pushes and deletion whatever the client did |
| Deny block | `permissions.deny` in `dotfiles/settings/base.json` | Refuses the forbidden push spellings before anything else is consulted |
| `git-authority` hook | `dotfiles/dot-claude/hooks/git-authority`, wired as a `PreToolUse` hook on `Bash` in `base.json` | Parses every `git push` and `git commit` in the command: refuses the forbidden push spellings, in *any* spelling, and every commit no lane opens |
| Allowlist | `permissions.allow` in `base.json` | Lets the routine commands run without a prompt |
| Auto-mode entry | `autoMode.allow` in `base.json` | Tells the hands-off classifier the same thing in prose |

Deny is evaluated before allow, so the broad allow rows are safe: a row like
`Bash(git push origin *)` cannot resurrect a spelling the deny block already
refused. The hook sits above both — a `PreToolUse` deny overrides a permission
allow — so it is the layer that actually makes the rulings complete.

All of it lives in `base.json`, never in `fedora.json` or `wsl.json`: the
authority over a push is a fact about the work, not about the machine doing it.
`fedora.json` keeps its wholesale `git` sandbox exclusion, which answers a
different question — *can git run correctly here* — not *is this operation
allowed*. git is excluded because the harness's protection of `.git/config` and
`.git/hooks` is not user-overridable and broke sandboxed `git status` and
`git commit`, per [sandboxing](/docs/sandboxing.md). Narrowing that exemption
is [#261](https://github.com/GeoffNordling/dev-playbook/issues/261)'s subject,
and nothing here depends on how it lands.

## What both families read

Both families walk the same command first, so a chained, wrapped or substituted
command hides nothing from either.

The hook splits a command on `&&`, `||`, `;`, `|`, `&` and newlines — respecting
quoting, so a `;` inside a commit message separates nothing — and judges each
segment on its own lexed argv, so chaining hides nothing. A segment that will
not lex at all is refused only where its text resolves to a `git … push` or a
`git … commit`: an ordinary command carrying the word is not the operation, and
refusing it would stop work this hook has no authority over.

**Text the shell would never run is read as a command anyway, and that is an
accepted false deny.** Newlines split segments and comments are not stripped, so
a `#` line and a heredoc body both arrive as ordinary commands: `# remember to
git commit later` is refused, and so is the body of a `gh pr comment … <<'EOF'`
that names a git verb. This workspace writes about its own git rules constantly,
so it is hit often. The way through is to stop making the text a shell argument
— write the body to a file and pass `--body-file`, or `git commit -F` — never a
re-spelling of the git command itself.

It is a false deny by choice. One attempt to read those two shapes the way bash
reads them was reverted after it opened three fail-opens, each a partial parser
disagreeing with another about a shape neither had been written for; a herestring
and an arithmetic shift both blinded the hook for the rest of the command. A loud
refusal is recoverable in seconds and a silent hole is not, so the trade goes to
the refusal. The measurements are on
[#348](https://github.com/GeoffNordling/dev-playbook/issues/348), and the real
fix — one tokenizing pass in place of the hand-rolled walkers — is
[#355](https://github.com/GeoffNordling/dev-playbook/issues/355).

**Both families fail closed on a fault in the hook's own machinery**, bounded by
what the hook has authority over: a fault denies where the command reads as a
push or a commit, and draws no opinion on anything else, because this hook runs
on every Bash call and one fault must not take out `ls` and `make check`
everywhere at once. The one fault it cannot scope that way is an event that will
not parse off stdin — there is no command to read, so that denies whole. The
residual harness-level fail-open (interpreter missing, script unreadable) is
accepted.

## The push rule family

Three families are refused outright, in every spelling:

- **Main-targeting.** main is written by merging a pull request, never by
  pushing at it. `origin main`, `HEAD:main`, `issue-9:main`,
  `HEAD:refs/heads/main` and `+main` are all the same act.
- **Forcing.** A forced push rewrites published history. `--force-with-lease`
  is refused with the rest: it is safer, not safe, and history repair is
  discussed with the top-level session and typed by the human. `-f`, `-fu`,
  `--force-if-includes` and a `+refspec` are all forcing.
- **Deleting a remote ref.** The only remote-branch deletion is GitHub's
  delete-on-merge. `--delete`, `-d` and the empty-source refspec `:branch` all
  delete.

Three further rules protect the first three:

- **A push must name both a remote and a refspec.** Bare `git push`, and
  `git push origin` with no ref, leave the target to configuration — invisible
  state, and unreviewable.
- **A push must name the branch it writes.** `HEAD` and its `@` synonym are
  whatever branch the checkout is standing on, which on a main checkout is
  main. Write the branch, or the `HEAD:issue-9` form.
- **A push the hook cannot read is refused unread.** Behind `bash -c`, inside a
  command substitution, or with a variable expansion where the remote or the
  refspec belongs, the hook cannot see what would run. It fails closed.

## The commit rule family

`git commit` is deny-by-default: the hook refuses it unless exactly one of
two lanes allows, and the lanes never mix.

- **Lane 1 — factory agent types.** A subagent session's hook payload carries
  an `agent_type` key; when its value is on the allowlist (`builder`,
  `judgment-facilitator`) the commit runs. The value comes from the
  human-authored agent definition the subagent was spawned as — no prompt,
  brief, or skill can write it. A payload carrying `agent_type` is judged by
  this lane *only*.
- **Lane 2 — the human's marker.** A main session (no `agent_type` key)
  commits when its transcript holds a `/commit-on` command marker in a
  genuine user turn — harness-written when the human types the command, and
  never read from tool results or assistant turns. `/commit-off` revokes; the
  later marker wins. The grant survives a `--continue` resume and does not
  survive `/clear`, which starts a new transcript.

Lane exclusivity is load-bearing: subagents inherit the parent session's
transcript path, so honoring a parent's grant inside a subagent would extend
one typed `/commit-on` to every node under a factory manager. It never does.

A transcript the hook cannot open holds no grant it can see, so that is the
ungranted state and not a fault: the denial names the missing grant, because
telling its reader the hook needs repair would send them to fix working
machinery instead of typing the grant.

**A commit inside a `$(…)` or a backtick body is judged by its lane like any
other, which is deliberately not what the push family does there.** The two
families answer different questions. The push family asks *is this push
watched*, because a push is irreversible publication into shared history, and a
substituted push is one whose output nobody sees — so it fails closed wherever
it sits. The commit family asks *who is committing*, and the lane answers that
identically wherever the command sits; refusing a substituted commit would deny
a granted user's own scripted commit and buy nothing, since the lane already
said who was asking. The asymmetry is this ruling, not an artifact of where the
check happens to sit.

One authoring rule protects lane 2: no authored content anywhere in the repo may
contain the literal marker wrapper string; the hook, the tests, and the
`claude-code.command-marker` check that enforces it all assemble it from pieces.
The rule itself is stated for every governed repo in
[files.md](/standards/claude-code/files.md); this file is the mechanism's home,
not the rule's.

That check exempts the vendored tree, and it is an **accepted gap** rather than
a clean boundary. Vendored skills are published under the skills root by symlink
and stowed into `~/.claude/skills/`, so they are live skill text, and the hook
reads a marker without reading its provenance — reachability is what makes a
file dangerous here, not ownership. The tree is carried verbatim from upstream
and cannot be edited, so enforcing there would mean a permanently red gate on
something nobody can fix. The exemption is recorded here and pinned by a test
rather than left to be inferred from the code.

Two limits are stated rather than fixed, each with an issue:

- **The family reads `git commit` and nothing else.** `git revert`, `merge`,
  `cherry-pick`, `am`, `rebase --continue` and `commit-tree` all write commit
  objects and draw no opinion here, so "a commit needs a lane" is true of
  `git commit` specifically, not of every way a commit can be made. Which verbs
  belong, and at what false-deny cost, is
  [#353](https://github.com/GeoffNordling/dev-playbook/issues/353).
- **Lane 2 rests on `disable-model-invocation` being a hard refusal.** The
  marker skills carry that flag so only a typed command can plant a marker. If
  the harness treats it as a listing omission rather than a refusal at the Skill
  tool, a model could mint its own grant and the lane is forgeable. That is an
  assumption, not a measured fact;
  [#354](https://github.com/GeoffNordling/dev-playbook/issues/354) settles it.

Commit authorization never rides a delegation prompt or brief — the
auto-mode classifier kills a node whose prompt asserts authority it
structurally lacks. That is enforcement, not etiquette: authorization lives
only in what the human authored — the definitions, and the typed marker.

## The canonical commands

These are the spellings the allowlist grants and the skills issue. Write them
this way; a variant that means the same thing may still prompt.

    git push -u origin <branch>
    git push origin <branch>
    git push --no-verify -u origin <branch>
    git push --no-verify origin <branch>
    git fetch --prune origin
    git pull --ff-only origin main

Each also has a `git -C <path> …` form, granted for the same six, because a
session working one repo often has to push another.

`--no-verify` is granted broadly on purpose: intermediary pushes skip the
pre-push gate by standing ruling, because the judgments phase is the
verification act. The canonical pull is `--ff-only` against an explicit
`origin main`, so it can never quietly merge.

## What the pattern engine actually does

The deny and allow rows are matched by Claude Code's own pattern engine, whose
behavior was measured on 2.1.221 rather than taken from the documentation —
the two disagree. What was observed:

- `*` matches any run of characters, including spaces, at any position.
- **A trailing ` *` needs a following space, so it cannot match the end of a
  command.** `Bash(echo * main *)` refuses `echo alpha main beta` but not
  `echo alpha main`. The published docs state the opposite. This is why every
  `… X *` row has a `… X` sibling: without it, `Bash(git push * main *)` would
  have missed `git push origin main`.
- **Nothing normalizes `git -C <path> push` into `git push`.** Rows bind to the
  literal command text, so every row has a `git -C * push …` mirror.
- A rule with no wildcard matches exactly, which is what makes `Bash(git push)`
  refuse the bare push and nothing else.
- Shell operators split the command and each segment is matched on its own.

Rows are therefore a coarse first net, and deliberately so: spellings like
`git push origin main:main` or `env git push …` slip past them. The hook is the
net that catches those, which is why the rulings above are stated as the hook's
behavior and not as a list of rows.

## Where to change things

| To change | Edit |
|---|---|
| Which spellings are refused or granted | `dotfiles/settings/base.json` — `permissions.deny`, `permissions.allow` |
| What the rulings actually mean | `dotfiles/dot-claude/hooks/git-authority` |
| How the hands-off classifier reads them | `autoMode.allow` in `base.json` |
| The guard on all of it | `tests/test_git_authority.py` |

The rows are asserted character-for-character by the test, because pytest
cannot invoke the pattern engine and a row that quietly changes spelling stops
binding with nothing to notice. Change a row and the test changes with it,
deliberately.
