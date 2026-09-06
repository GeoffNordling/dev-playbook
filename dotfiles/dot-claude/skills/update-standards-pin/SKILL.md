---
name: update-standards-pin
description: Roll a dev-playbook standards release out to the governed consumer repos, working whatever the bump reddens.
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

`bump-pins` owns the mechanical half; this skill owns the half it
deliberately stops short of — deciding what each finding means, and getting
the result committed.

## 1. Confirm the release is on the remote

pre-commit installs a pin by fetching that object from GitHub, so a pin at a
commit that exists only on this disk is uninstallable. Run each as its own
top-level command and compare the two values yourself — {Read from GitHub
main's head sha} against the local `git rev-parse main`:

```
git rev-parse main
gh api repos/{owner}/{repo}/branches/main --jq .commit.sha
```

{If the two values are unequal, {report that the release is unpushed} and
stop} — commits push as they land, so an unpushed main means something
upstream went wrong; surface it rather than pushing someone else's
unreviewed work.

## 2. Run it

{Read [workspace_lint.py](~/workspace/dev-playbook/src/dev_playbook/workspace_lint.py)
for the `GOVERNED` roster}: the population this skill audits and bumps; a
repo absent from it is not governed and is neither audited nor bumped. From
the dev-playbook checkout, {Run
[bump-pins](~/workspace/dev-playbook/scripts/bump-pins) `--dry-run` first to
see what would move, then run it again for real}.

## 3. Read the report

One line per consumer:

| Line | Means |
|---|---|
| `green` | Bumped and verified. Nothing to do but commit. |
| `needs work` | Real findings at the new pin. Work them. |
| `skipped — uncommitted changes` / `not on main` | The repo is mid-work. Report it; never touch it. |
| `skipped — already red at its current pin` | Pre-existing breakage, unrelated to this release. Surface it separately. |
| `skipped — no dev-playbook pin` | Governed but unwired. An adoption question — /enable-repo-governance. |

**An aborted run is an environment fault**: pre-commit died before judging
anything and that repo's pin is already restored. {If the script raises
`the gate could not run`, {report the abort as the fault it is}}.

## 4. Work the findings, one repo at a time

Finish one repo before opening the next. A finding is sometimes a defect in
the release itself, and then the fix goes back into dev-playbook — a new
commit, a new push, a new target sha.

Re-running is safe: a repo already at the target reports `already current`
and costs nothing, and a repo still on the superseded sha bumps again. A repo
left **mid-fix** does not survive a re-run — preflight skips anything with a
dirty working tree, so commit or revert every repo already touched before
re-running, or the sweep silently skips it.

## 5. Trim retired content only after the bump is green

A requirement retired upstream is still enforced by the check that ships
**inside the pinned clone**, so a repo left untrimmed goes red against its
own old pin the moment the bump lands. {If the bump already reports green,
{Write the retired requirement's adaptation and deletions out of the
consumer repo}} — carry both into the same commit.

## 6. Commit and push, one repo at a time

One commit per consumer carries the pin move and any adaptation together;
the commit gate runs at the new pin, so a green commit is a second
verification. Push each repo as its commit lands — they are independent, so
one failure never blocks the rest. {Report per-repo results — bumped, needs
work, skipped, or faulted}.

## 7. Collect the garbage

A bump is what creates it: pre-commit keeps one full clone of dev-playbook per
rev ever pinned, and the superseded ones accumulate silently. `pre-commit gc`
removes every cached clone no live config still references — after a bump, that
is exactly the revs just superseded. Safe by construction: anything still
pinned anywhere is kept, and anything removed is re-cloned on demand.
