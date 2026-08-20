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
changed — none of it reaches that repo until the pin moves. The bump *is* the
release ([distribution.md](~/workspace/dev-playbook/standards/build/distribution.md)).

[bump-pins](~/workspace/dev-playbook/scripts/bump-pins) owns the mechanical
half. This skill owns the half it deliberately stops short of: deciding what
each finding means, and getting the result committed.

## 1. Confirm the release is on the remote

pre-commit installs a pin by fetching that object from GitHub, so a pin at a
commit that exists only on this disk is not stale — it is uninstallable. Run
each as its own top-level command and compare the two values yourself:

```
git rev-parse main
gh api repos/{owner}/{repo}/branches/main --jq .commit.sha
```

Unequal means the release is unpushed — escalate and stop. Commits push as
they land, so an unpushed main means something upstream went wrong; surface
it rather than pushing someone else's unreviewed work.

## 2. Run it

From the dev-playbook checkout, `scripts/bump-pins --dry-run` to see what would
move, then `scripts/bump-pins` to move it. The population is the `GOVERNED`
roster in
[workspace_lint.py](~/workspace/dev-playbook/src/dev_playbook/workspace_lint.py);
a repo absent from it is not governed and is neither audited nor bumped.

## 3. Read the report

One line per consumer:

| Line | Means |
|---|---|
| `green` | Bumped and verified. Nothing to do but commit. |
| `needs work` | Real findings at the new pin. Work them. |
| `skipped — uncommitted changes` / `not on main` | The repo is mid-work. Report it; never touch it. |
| `skipped — already red at its current pin` | Pre-existing breakage, unrelated to this release. Surface it separately. |
| `skipped — no dev-playbook pin` | Governed but unwired. An adoption question — /enable-repo-governance — not a bump. |

**An aborted run is an environment fault, not a finding.** If the script raises
`the gate could not run`, pre-commit died before judging anything and that
repo's pin is already restored — report it as the fault it is.

## 4. Work the findings, one repo at a time

Finish one repo before opening the next. A finding is sometimes not the
consumer's fault but a defect in the release itself, and then the fix goes back
into dev-playbook — a new commit, a new push, a new target sha.

That is not a disaster, because re-running is safe: a repo already at the
target reports `already current` and costs nothing, and a repo still on the
superseded sha simply bumps again. The one thing that does not survive a
re-run is a repo left **mid-fix** — preflight skips anything with a dirty
working tree, so commit or revert every repo already touched before re-running,
or the sweep passes it by in silence.

## 5. Trim retired content only after the bump is green

A requirement retired upstream is still enforced by the check that ships
**inside the pinned clone**. Delete what it demands before the pin moves and
the repo goes red against its own old pin. So: bump, verify green, then trim,
then commit both together.

## 6. Commit and push, one repo at a time

One commit per consumer carrying the pin move and any adaptation together —
they are one act, and the commit gate runs at the new pin, so a green commit is
a second verification. Push each repo as its commit lands: they are independent
repos, so each push gets its own attempt, and one failure never blocks the rest —
report per-repo results.

## 7. Collect the garbage

A bump is what creates it: pre-commit keeps one full clone of dev-playbook per
rev ever pinned, and the superseded ones accumulate silently. `pre-commit gc`
removes every cached clone no live config still references — after a bump, that
is exactly the revs just superseded. Safe by construction: anything still
pinned anywhere is kept, and anything removed is re-cloned on demand.
