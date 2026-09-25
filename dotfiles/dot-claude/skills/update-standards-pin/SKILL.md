---
name: update-standards-pin
description: Bump the dev-playbook standards pin of the consumer repo this session is standing in — probe the bump, land it on main when it stays green, cut a bump-pin worktree when it does not and hand the worktree to the user for /finish-pin-bump.
disable-model-invocation: true
model: inherit
effort: xhigh
---

# Update Standards Pin

A consumer repo runs the standards as of the dev-playbook `rev` it pins, and
nothing else: a check added upstream, a rule tightened, a canonical artifact
changed — none of it reaches that repo until the pin moves. {Read
[Distribution Channel](~/workspace/dev-playbook/standards/distribution/channel.md);
the bump *is* the release}.

The target is the repo this session stands in, and the bump comes back **green**
or **red**. Green lands one commit on `main`. Red moves to a worktree, and
[finish-pin-bump](~/workspace/dev-playbook/dotfiles/dot-claude/skills/finish-pin-bump/SKILL.md) takes it from
there. `bump-pin` decides which; this skill owns the decision and the landing,
and nothing past the worktree.

This is the hand form of what
[update-pins](~/workspace/dev-playbook/scripts/update-pins) does for every
governed repo on a timer. The two use the same branch name, `bump-pin-` plus
the first twelve characters of the target sha, so a bump landed or a PR opened
by hand is what the timer finds already done at its next tick, and it runs
nothing for that repo.

## 1. Confirm the repo is governed

`git rev-parse --show-toplevel` names the target. {Read
[workspace_lint.py](~/workspace/dev-playbook/src/dev_playbook/workspace_lint.py)
for the `GOVERNED` roster}: governance is declared there, never inferred from a
repo sitting under the workspace root. {If the roster omits this repo, {Report
that it is ungoverned and must be enrolled in the roster first} and
stop} — bumping an unenrolled repo installs a standard nothing checks.

Done when the repo's name is in the roster.

## 2. Probe the bump

{Run [bump-pin](~/workspace/dev-playbook/scripts/bump-pin) `--check`}. It
fetches `origin/main`, cuts a throwaway worktree of it, moves the pin and its
hook ids there to dev-playbook's release head, runs the gate once, and removes
the worktree. This checkout is never read or written — it may sit on any
branch, dirty or clean — and the probe commits the repo to nothing. There is
no run at the current pin: a repo red before the bump is red with more
findings, and every finding at the new pin is worked whichever release brought
it.

Its exit code picks the branch:

| Exit | Verdict | Continue at |
|---|---|---|
| 0 | green, or already current | §3 |
| 1 | red — the findings are on stdout | §4 |
| 2 | the probe reached no verdict | stop |

Exit 2 is an environment fault: the gate crashed, the network was gone, `gh`
had no credential. {If the probe exits 2, {Report the refusal it printed, as
the fault it is}} rather than as findings this release caused.

Done when the exit code is read and the branch chosen.

## 3. Green: one commit on main

The probe judged `origin/main`, and `--write` edits this checkout, so the two
have to be the same tree before the edit is made. Run `git fetch origin`, then
confirm `main` is checked out and clean, and fast-forward it if it is behind.
{If a branch is checked out or the tree is dirty, {Report the branch and the
uncommitted files} and stop}; the bump's commit carries the pin and nothing
else.

Then {Run [bump-pin](~/workspace/dev-playbook/scripts/bump-pin) `--write`} to
move the pin for real, commit the files it names to `main` — the config, and in
a host `pyproject.toml` and `uv.lock` too — and push. The
commit gate runs at the new pin, so a green commit is the second verification.

Then `pre-commit gc`. A bump is what creates the garbage — pre-commit keeps one
full clone of dev-playbook per rev ever pinned — and gc drops every cached clone
no live config still references, which after this commit is the rev just
superseded. It is safe by construction: anything still pinned anywhere is kept,
and anything removed is re-cloned on demand.

{Report the sha the pin moved from and to, and that the commit is pushed}.

Done when the commit is on `origin/main` and the cache is collected.

## 4. Red: cut the worktree

The findings belong on a branch cut from the tree the probe judged. Run
`git fetch origin`, then

    git worktree add -b bump-pin-<sha12> .claude/worktrees/bump-pin-<sha12> origin/main

with `<sha12>` the first twelve characters of the target sha `bump-pin`
printed. {If that path already exists, {Report it as an `update-pins`
worktree, and that the
[Pin Updates Ledger](~/workspace/dev-playbook/docs/pin-updates.md) says how
that run ended} and stop}: it belongs to a run that did not finish, and two
runs working one branch is the one thing worse than an unworked bump.

`cd` into the worktree, then {Run
[bump-pin](~/workspace/dev-playbook/scripts/bump-pin) `--write`} to move the
pin, and commit it `--no-verify` as the branch's first commit. The worktree
and branch need no cleanup afterwards: once their PR is merged or closed, the
next `update-pins` run removes both, and the remote branch with them.

Done when the worktree holds the committed bump.

## 5. Hand off

`/finish-pin-bump` works the findings to an empty gate and lands the PR, and
it is user-invoked: this skill never starts it. {Report the worktree path, the
sha move, the finding count, and that the next step is the user typing
`/finish-pin-bump` in a session whose working directory is the worktree} and
stop.

Done when the report is on screen.
