---
name: enable-repo-governance
description: Bring the repository the session is standing in into governance — wire the standards pin, work it to green, finish the GitHub tail, and enroll it.
disable-model-invocation: true
model: opus
effort: xhigh
---

# Enable Repo Governance

An existing repo joins the workspace by being brought to green against the
pinned standard, then enrolled. The procedure is the adoption path of
[bootstrap.md](~/workspace/dev-playbook/standards/build/bootstrap.md) — that
document is the authority on the steps and their order; this skill owns the
choreography around them: preflight, the findings loop, the hand-offs, and
the commits.

## 1. Preflight

The target is the repo the session is standing in —
`git rev-parse --show-toplevel` names it. Refuse to start unless its working
tree is clean and on `main` — the adoption diff must carry adoption and
nothing else. If the repo is already in
workspace-lint's `GOVERNED` roster, say so and stop: that repo's problem is
pin drift or findings, which is /update-standards-pin territory, not
adoption.

## 2. Wire and seed

Follow bootstrap.md's adoption steps 1–4: read the layers, wire the pin at a
**pushed** dev-playbook sha, seed and merge the canonical artifacts, install
the hook stages. The canonical artifacts live in
`~/workspace/dev-playbook/standards/build/canonical/`. Where a canonical
block must merge into a file the repo already has, show the user the merged
result before moving on when anything beyond mechanical insertion was
involved.

## 3. Lint to green

Run `~/workspace/dev-playbook/scripts/repo-lint`. The findings are the
worklist; work it to empty, taking each fix's authority from the rule's
define doc, reached through the card catalog at
[standards/index.md](~/workspace/dev-playbook/standards/index.md).

Escalate rather than decide when a finding needs a call only the user can
make — deleting a forbidden file with content that has no obvious new home,
renaming something other tooling may reference, or any fix that changes what
the repo does rather than how it conforms. Batch the escalations: finish
everything decidable first, then present the remainder as one list of
concrete choices.

## 4. The GitHub tail

Run `~/workspace/dev-playbook/scripts/bootstrap-labels`. The merge settings
and the protection ruleset sit behind GitHub's Administration permission —
hand those to the user per bootstrap.md's tail, pointing at
[repo-settings.md](~/workspace/dev-playbook/standards/tracking/repo-settings.md),
and wait for their confirmation before calling the tail done.

## 5. Land the target

The size of the diff picks the vehicle — judge it as soon as the worklist
makes the size clear:

- **Five or fewer changed files**: one commit carrying the pin wiring and
  every fix together, straight to `main` — /commit runs the gate at the new
  pin, which is the verification.
- **More**: a branch, commits as the work proceeds, and a PR handed to the
  user at the end — approval and merge are the user's.

## 6. Enroll

Enrollment follows the adoption onto `main`: add the target's name to the
`GOVERNED` roster in
[workspace_lint.py](~/workspace/dev-playbook/src/dev_playbook/workspace_lint.py),
run `scripts/workspace-lint` to confirm the newly enrolled repo reports
clean, and commit that dev-playbook edit separately. On the PR path this
waits for the user's merge — a repo enrolled while its pin sits on an
unmerged branch reports a `build.pin` finding against `main`.

Report per-repo results — a failure in one never blocks the other's
report.
