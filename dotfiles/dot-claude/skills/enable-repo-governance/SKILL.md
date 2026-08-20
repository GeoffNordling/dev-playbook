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

Then, before touching a file, tell the user what their GitHub token will
need. A fine-grained PAT carries neither permission by default, and both
failures land late — one at the push, one at the CI check — so raising them
now lets the user grant them while you work instead of being stopped twice:

- **Workflows: Read and write** — the adoption diff creates
  `.github/workflows/ci.yml`, and without this the push is rejected outright
  (`refusing to allow a Personal Access Token to create or update workflow`).
- **Actions: Read** — without it `gh pr checks` and the Actions API return
  403, so you cannot confirm the CI gate went green before handing over the
  PR.

Both are granted per-token at `https://github.com/settings/personal-access-tokens`,
and the token's repository selection must include the target. Do not offer
`gh auth refresh -s workflow` — that is the OAuth path and does nothing for a
fine-grained token. Say that the grant can be narrowed again once the repo is
enrolled, so a temporary widening is not mistaken for a permanent one.

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
