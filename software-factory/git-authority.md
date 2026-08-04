---
type: Guide
title: Git Authority
description: The layers deciding which git operations an agent may run, the push rule family, and the canonical command set
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
| `git-authority` hook | `dotfiles/dot-claude/hooks/git-authority`, wired as a `PreToolUse` hook on `Bash` in `base.json` | Parses every `git push` and `git commit` in the command: refuses the forbidden push spellings, in *any* spelling, and every commit but the two lanes allow |
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

The hook splits a command on `&&`, `||`, `;`, `|`, `&` and newlines — respecting
quoting, so a `;` inside a commit message separates nothing — and judges each
segment on its own lexed argv, so chaining hides nothing. A segment that will
not lex at all is refused only where its text resolves to a `git … push`: an
ordinary command carrying the word "push" is not a push, and refusing it would
stop work this hook has no authority over.

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

The commit family fails **closed**: an internal hook error — including an
event that will not parse off stdin — denies with the error named, rather
than passing silently. The residual harness-level fail-open (interpreter
missing, script unreadable) is accepted. One authoring rule protects lane 2:
no authored content anywhere in the repo may contain the literal marker
wrapper string; the hook and the tests assemble it from pieces.

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
