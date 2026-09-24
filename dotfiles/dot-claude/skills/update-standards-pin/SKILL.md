---
name: update-standards-pin
description: Bump the dev-playbook standards pin of the consumer repo this session is standing in, landing it on main when the bump stays green and on a PR when it does not; also the runbook the pin cascade hands its headless agent for a red repo.
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
or **red**. Green lands one commit on `main`. Red moves to a worktree, works the
findings there, and ends in a PR. `bump-pin` decides which; everything past the
decision is judgment, and that is the half this skill owns.

## Two callers

**By hand.** `/update-standards-pin` in a consumer session runs §1 to §6 in
order, and a user is present to take every escalation.

**By the cascade.** [cascade](~/workspace/dev-playbook/scripts/cascade), the
timer job that moves every governed repo's pin when dev-playbook `main` moves,
found this repo red and launched a headless agent in a worktree it had already
cut and committed the bump into. That agent starts at §5; the prompt it holds
names the worktree, the branch, the sha move, and the gate output. No user is
present, so nothing the agent prints is read: where a section below says to
report and wait, the cascade-launched run writes the same content into the PR
body instead (§6 names where), and its result is the PR, which the cascade
reads back with `gh pr list --head`.

Both callers use the branch name `bump-pin-` followed by the first twelve
characters of the target sha, and that is what keeps them from colliding: at
its next tick the cascade reads a pin already at the release head as `current`
and an open PR on that branch as `pending`, and runs nothing.

## 1. Confirm the repo is governed

`git rev-parse --show-toplevel` names the target. {Read
[workspace_lint.py](~/workspace/dev-playbook/src/dev_playbook/workspace_lint.py)
for the `GOVERNED` roster}: governance is declared there, never inferred from a
repo sitting under the workspace root. {If the roster omits this repo, {Report
that it is ungoverned, and that /enable-repo-governance is what adopts it} and
stop} — bumping an unenrolled repo installs a standard nothing checks.

Done when the repo's name is in the roster.

## 2. Probe the bump

{Run [bump-pin](~/workspace/dev-playbook/scripts/bump-pin) `--check`}. It
fetches `origin/main`, cuts a throwaway worktree of it, runs the gate at the
current pin there, moves the pin and its hook ids to dev-playbook's release
head, runs the gate again, and removes the worktree. This checkout is never
read or written — it may sit on any branch, dirty or clean — and the probe
commits the repo to nothing.

Its exit code picks the branch:

| Exit | Verdict | Continue at |
|---|---|---|
| 0 | green, or already current | §3 |
| 1 | red — the findings are on stdout | §4 |
| 2 | the probe reached no verdict | stop |

Exit 2 is an environment fault or a repo already red at its **current** pin —
breakage that predates this release either way. {If the probe exits 2, {Report
the refusal it printed, as the fault it is}} rather than as findings this
release caused.

Done when the exit code is read and the branch chosen.

## 3. Green: one commit on main

The probe judged `origin/main`, and `--write` edits this checkout, so the two
have to be the same tree before the edit is made. Run `git fetch origin`, then
confirm `main` is checked out and clean, and fast-forward it if it is behind.
{If a branch is checked out or the tree is dirty, {Report the branch and the
uncommitted files} and stop}; the bump's commit carries the pin and nothing
else.

Then {Run [bump-pin](~/workspace/dev-playbook/scripts/bump-pin) `--write`} to
move the pin for real, commit that one changed file to `main`, and push. The
commit gate runs at the new pin, so a green commit is the second verification.

Then `pre-commit gc`. A bump is what creates the garbage — pre-commit keeps one
full clone of dev-playbook per rev ever pinned — and gc drops every cached clone
no live config still references, which after this commit is the rev just
superseded. It is safe by construction: anything still pinned anywhere is kept,
and anything removed is re-cloned on demand.

{Report the sha the pin moved from and to, and that the commit is pushed}.

Done when the commit is on `origin/main` and the cache is collected.

## 4. Red: cut a worktree

The findings belong on a branch cut from the tree the probe judged. Run
`git fetch origin`, then

    git worktree add -b bump-pin-<sha12> .claude/worktrees/bump-pin-<sha12> origin/main

with `<sha12>` the first twelve characters of the target sha `bump-pin`
printed, so the branch says which release it carries and matches the name the
cascade would have chosen. {If that path already exists, {Report it as a
cascade run's worktree, and that
[Pin Cascade Ledger](~/workspace/dev-playbook/docs/pin-cascade.md) says how
that run ended} and stop}: it belongs to a run that did not finish, and two
runs working one branch is the one thing worse than an unworked bump.

`cd` into the worktree, then {Run
[bump-pin](~/workspace/dev-playbook/scripts/bump-pin) `--write`} to move the
pin, commit it `--no-verify` as the branch's first commit, and re-run the gate
with `uvx pre-commit run --all-files` to put the worklist on screen.

Done when the worktree holds the committed bump and the gate's findings are in
hand.

## 5. Work the findings

Commit freely with `--no-verify` while the work is in flight; the gate is the
worklist, not the judge, until §6 takes its verdict. Work to an empty gate.

**Each finding names its own authority.** A finding's rule id reads
`<name>.<rule>`, and the name half is a directory, `standards/<name>/` in
the dev-playbook checkout, whose Standard files hold the rule under the
heading the slug names. {Read
[the standards index](~/workspace/dev-playbook/standards/index.md); it
lists every directory} to reach it. Take the fix from that rule rather
than from the check's message, which states the symptom.

Three shapes account for most of what a bump reddens:

- **A canonical artifact drifted.** The pinned clone carries
  `standards/build/canonical/`, so a canonical block changed upstream is a
  finding the moment the pin moves. Re-seed the block from
  `~/workspace/dev-playbook/standards/build/canonical/` — confirm that checkout
  sits at the target sha first — and merge it into the repo's file. The
  canonical copy wins; never edit the repo's copy to satisfy the check by
  hand.
- **A check reaching this repo for the first time.** Enrollment rides the
  pin, so a check added upstream runs here with no config edit anywhere. Adapt
  the repo to the rule, authority as above.
- **A requirement retired upstream.** This one shows up as silence, not as a
  finding: the rule is gone from the new pin, so the adaptation the repo still
  carries for it — a suppression, a shim, a note — is dead weight nothing asks
  for any more. {Write the retired requirement's adaptation out of the repo}.

**Escalate rather than decide** where a fix changes what the repo *does* instead
of how it conforms — deleting a file whose content has no obvious new home,
renaming something other tooling may reference. Finish everything decidable
first. By hand, {Report the remainder as one list of concrete choices} and
wait. Launched by the cascade, go on to §6 with the gate still red for those
findings alone, and carry the list into the PR body under the heading
`Escalations`.

Done when `uvx pre-commit run --all-files` is green in the worktree, or red
only on findings listed as escalations.

## 6. Land the PR

Make the last commit without `--no-verify`, so the commit gate runs at the new
pin and its green result is the verification; a commit the gate refuses over an
escalated finding goes in with `--no-verify` and the refusal quoted in the PR
body. Push the branch with `git push -u origin bump-pin-<sha12>`. {If the push
is rejected because the token cannot write `.github/workflows`, {Report the
rejection verbatim} and stop}: the fine-grained PAT needs Workflows read/write,
which the user grants by hand.

Open the PR with `gh pr create --base main --head bump-pin-<sha12>`, titled
`Pin dev-playbook at <sha12>`. The body names:

- the sha the pin moved from and to;
- each adaptation and the rule it serves;
- whether `.github/workflows/ci.yml` changed;
- every open escalation, under the heading `Escalations`;
- launched by the cascade, the list of remote branches not merged to `main`
  that the prompt handed over, so the user can spot a live branch that will
  meet this pin when it rebases.

**Never merge the PR, approve it, or enable auto-merge.** The merge is the
user's, whichever caller opened it.

{Report the PR's URL, the sha move, and every escalation still open}.

Done when the PR is open and its URL is on screen.
