---
name: update-standards-pin
description: Bump the dev-playbook standards pin of the consumer repo this session is standing in, landing it on main when the bump stays green and on a PR when it does not.
disable-model-invocation: true
model: opus
effort: xhigh
---

# Update Standards Pin

A consumer repo runs the standards as of the dev-playbook `rev` it pins, and
nothing else: a detector added upstream, a rule tightened, a canonical artifact
changed — none of it reaches that repo until the pin moves. {Read
[Distribution Channel](~/workspace/dev-playbook/standards/distribution/channel.md);
the bump *is* the release}.

The target is the repo this session stands in, and the bump comes back **green**
or **red**. Green lands one commit on `main`. Red moves to a worktree, works the
findings there, and ends in a PR. `bump-pin` decides which; everything past the
decision is judgment, and that is the half this skill owns.

## 1. Confirm the repo is governed

`git rev-parse --show-toplevel` names the target. {Read
[workspace_lint.py](~/workspace/dev-playbook/src/dev_playbook/workspace_lint.py)
for the `GOVERNED` roster}: governance is declared there, never inferred from a
repo sitting under the workspace root. {If the roster omits this repo, {Report
that it is ungoverned, and that /enable-repo-governance is what adopts it} and
stop} — bumping an unenrolled repo installs a standard nothing audits.

Done when the repo's name is in the roster.

## 2. Freshen main

The probe judges this checkout, and a branch, if one is needed, is cut from
`origin/main` — so the two have to be the same tree. Run `git fetch origin`, then
confirm `main` is checked out and clean, and fast-forward it if it is behind.
{If the working tree is dirty, {Report which files are uncommitted} and stop};
the bump's diff carries the pin and its fallout and nothing else.

Done when `main` is checked out, clean, and equal to `origin/main`.

## 3. Probe the bump

{Run [bump-pin](~/workspace/dev-playbook/scripts/bump-pin) `--check`}. It runs
the gate at the current pin, moves the pin to dev-playbook's published head,
runs the gate again, and restores the config whichever way that went — so this
checkout is left exactly as found and the probe commits the repo to nothing.

Its exit code picks the branch:

| Exit | Verdict | Continue at |
|---|---|---|
| 0 | green, or already current | §4 |
| 1 | red — the findings are on stdout | §5 |
| 2 | the probe reached no verdict | stop |

Exit 2 is an environment fault or a repo already red at its **current** pin —
breakage that predates this release either way. {If the probe exits 2, {Report
the refusal it printed, as the fault it is}} rather than as findings this
release caused.

Done when the exit code is read and the branch chosen.

## 4. Green: one commit on main

{Run [bump-pin](~/workspace/dev-playbook/scripts/bump-pin) `--write`} to move the
pin for real, then commit that one changed line to `main` and push. The commit
gate runs at the new pin, so a green commit is the second verification.

Then `pre-commit gc`. A bump is what creates the garbage — pre-commit keeps one
full clone of dev-playbook per rev ever pinned — and gc drops every cached clone
no live config still references, which after this commit is the rev just
superseded. It is safe by construction: anything still pinned anywhere is kept,
and anything removed is re-cloned on demand.

{Report the sha the pin moved from and to, and that the commit is pushed}.

Done when the commit is on `origin/main` and the cache is collected.

## 5. Red: cut a worktree

Use the `EnterWorktree` tool, naming the worktree `bump-pin-` followed by the
first twelve characters of the target sha, so the branch says which release it
carries. The worktree is cut from `origin/main`, which §2 made identical to the
tree the probe judged, so the findings reproduce there exactly.

Then {Run [bump-pin](~/workspace/dev-playbook/scripts/bump-pin) `--write`} inside
the worktree to move the pin, and re-run the gate with
`uvx pre-commit run --all-files` to put the worklist on screen.

Done when the worktree holds the moved pin and the gate's findings are in hand.

## 6. Work the findings

Commit freely with `--no-verify` while the work is in flight; the gate is the
worklist, not the judge, until §7 takes its verdict. Work to an empty gate.

**Each finding names its own authority.** A finding's rule id reads
`<name>.<rule>`, and the name half is a directory, `standards/<name>/` in
the dev-playbook checkout, whose Standard files hold the rule under the
heading the slug names. {Read
[the standards index](~/workspace/dev-playbook/standards/index.md); it
lists every directory} to reach it. Take the fix from that rule rather
than from the detector's message, which states the symptom.

Three shapes account for most of what a bump reddens:

- **A canonical artifact drifted.** The pinned clone carries
  `standards/build/canonical/`, so a canonical block changed upstream is a
  finding the moment the pin moves. Re-seed the block from
  `~/workspace/dev-playbook/standards/build/canonical/` — confirm that checkout
  sits at the target sha first — and merge it into the repo's file. The
  canonical copy wins; never edit the repo's copy to satisfy the detector by
  hand.
- **A detector reaching this repo for the first time.** Enrollment rides the
  pin, so a detector added upstream runs here with no config edit anywhere. Adapt
  the repo to the rule, authority as above.
- **A requirement retired upstream.** This one shows up as silence, not as a
  finding: the rule is gone from the new pin, so the adaptation the repo still
  carries for it — a suppression, a shim, a note — is dead weight nothing asks
  for any more. {Write the retired requirement's adaptation out of the repo}.

**Escalate rather than decide** where a fix changes what the repo *does* instead
of how it conforms — deleting a file whose content has no obvious new home,
renaming something other tooling may reference. Finish everything decidable
first, then {Report the remainder as one list of concrete choices} and wait.

Done when `uvx pre-commit run --all-files` is green in the worktree.

## 7. Land the PR

Make the last commit without `--no-verify`, so the commit gate runs at the new
pin and its green result is the verification. Push the branch and open a PR whose
body names the sha the pin moved from and to, and what each adaptation was for.

{Report the PR's URL, the sha move, and every escalation still open}. The merge
is the user's.

Done when the PR is open and its URL is on screen.
