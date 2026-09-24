---
name: finish-pin-bump
description: In a bump-pin worktree whose committed dev-playbook pin bump leaves the gate red, work every finding from the rule it names to an empty gate and open the PR — never merging it — whether run by hand from /update-standards-pin or headless by update-pins with the state in the arguments.
disable-model-invocation: true
model: inherit
effort: xhigh
---

# Finish Pin Bump

The situation this skill starts in, and nothing else: the working directory is
a worktree of a governed consumer repo on the branch `bump-pin-<sha12>`, cut
from `origin/main`, whose last commit moves the dev-playbook pin in
`.pre-commit-config.yaml` and its hook ids to release head `<sha12>`. At that
pin the gate, `uvx pre-commit run --all-files`, is red. The job is to make it
green and land the PR.

Two callers put a session here. `/update-standards-pin` §4 cuts the worktree by
hand and a user is present. `update-pins`, the timer job that moves every
governed repo's pin when dev-playbook `main` moves, cuts it headless and hands
this skill the state as its arguments: the repo, the worktree, the sha move,
the remote branches not merged to `main`, and the gate's output. Headless,
nothing printed is read; the pull request is the only output, and `update-pins`
reads it back from GitHub with `gh pr list --head`. The steps are the same for
both, because every decision a user would be asked for goes into the PR body
instead, where the user reads it before merging either way.

Confirm the state first: `git branch --show-current` is `bump-pin-<sha12>`, and
`git log --oneline origin/main..HEAD` opens with the pin commit. {If either is
not so, {Report the branch and the commits} and stop}: this skill does not cut
worktrees or move pins, and running it elsewhere works the wrong tree. Commits
above the pin commit are earlier work on this same bump — a run that stopped at
a rejected push, say — and the skill resumes from wherever the gate stands.

## 1. Work the findings

Run `uvx pre-commit run --all-files` to put the worklist on screen when the
arguments did not carry it. Commit freely with `--no-verify` while the work is
in flight; the gate is the worklist, not the judge, until §2 takes its verdict.
Work to an empty gate.

**Each finding names its own authority.** A finding's rule id reads
`<name>.<rule>`, and the name half is a directory, `standards/<name>/` in the
dev-playbook checkout, whose Standard files hold the rule under the heading the
slug names. {Read
[the standards index](~/workspace/dev-playbook/standards/index.md); it lists
every directory} to reach it. Take the fix from that rule rather than from the
check's message, which states the symptom.

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

**Escalate rather than decide** where a fix changes what the repo *does*
instead of how it conforms — deleting a file whose content has no obvious new
home, renaming something other tooling may reference. Do not make that change.
Finish everything decidable, then carry each open choice, as one concrete
question, into the PR body under the heading `Escalations` in §2. An
escalation is never a stop and never a wait: the PR is where the user answers
it.

Done when `uvx pre-commit run --all-files` is green in the worktree, or red
only on findings that are escalations.

## 2. Land the PR

Make the last commit without `--no-verify`, so the commit gate runs at the new
pin and its green result is the verification. A commit the gate refuses over an
escalated finding alone goes in with `--no-verify`, and the refusal is quoted
in the PR body next to its escalation.

Push the branch with `git push -u origin bump-pin-<sha12>`. {If the push is
rejected because the token cannot write `.github/workflows`, {Report the
rejection verbatim} and stop}: the fine-grained PAT needs Workflows read/write,
which the user grants by hand at github.com/settings/personal-access-tokens.

Open the PR with `gh pr create --base main --head bump-pin-<sha12>`, titled
`Pin dev-playbook at <sha12>`. The body names:

- the sha the pin moved from and to;
- each adaptation and the rule it serves;
- whether `.github/workflows/ci.yml` changed;
- every open escalation, under the heading `Escalations`, or the line
  `Escalations: none`;
- the remote branches not merged to `main` that the arguments carried, when
  they did, so the user can spot a live branch that will meet this pin when
  it rebases.

**Never merge the PR, approve it, or enable auto-merge.** The merge is the
user's, whichever caller opened the PR.

{Report the PR's URL, the sha move, and every escalation}.

Done when the PR is open and its URL is on screen.
