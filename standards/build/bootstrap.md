---
type: Guide
title: Bootstrap
description: How a repository joins the workspace — repo-init scaffolds a fresh tree, adoption brings an existing one to green; the GitHub tail and roster enrollment complete both
---

# Bootstrap

How a repository joins the workspace conforming. Entry paths — a
**fresh** repo is scaffolded, an **existing** repo is adopted — converge
on the same GitHub tail and roster enrollment.

## The fresh path: scaffold

[`scripts/repo-init`](/scripts/repo-init) creates the repo locally:

```bash
scripts/repo-init <name> --description '<one-line purpose>' [--python]
```

It renders the [skeleton](/standards/build/skeleton.md) from the
[canonical artifacts](/standards/build/canonical.md), pinning the hook
`rev` at dev-playbook's `origin/main` as of init time, then runs
`git init -b main` and `uv lock`, stages everything, installs both
pre-commit stages, and self-checks the result with `repo-lint`. It fails
loud when the target directory already exists or the self-check reports
findings.

The first commit is yours to make after review; the commit gate runs on it.

## The existing path: adoption

An existing repo joins by being brought to green against the pinned
standard, in this order:

1. **Read the layers.** Membership is inferred from facts on disk; what
   the repo must contain is the [skeleton](/standards/build/skeleton.md)
   for exactly those layers.
2. **Wire the pin.** No `.pre-commit-config.yaml` → copy the
   [canonical one](/standards/build/canonical.md), substituting
   `<pinned-sha>` with dev-playbook's `origin/main`. An existing config →
   add the canonical blocks and keep the repo's own hooks (additions are
   free). Either way the sha `MUST` be one already on GitHub — pre-commit
   installs the pin by fetching it, so a local-only sha is uninstallable.
3. **Seed the canonicals.** Copy each missing byte-identical artifact
   (`ci.yml`, `.python-version`); merge the canonical blocks into files the
   repo already has (`Makefile`, `pyproject.toml`, `.gitignore`), preserving
   repo-specific content beyond them.
4. **Install the gate.** `uvx pre-commit install` — the canonical config
   declares both stages.
5. **Lint to green.** Run dev-playbook's [`repo-lint`](/scripts/repo-lint)
   over the repo; the findings are the worklist, and each rule's define doc
   is the fix's authority. Forbidden files get explicit dispositions —
   `ROADMAP.md` and kin become `CANDIDATES.md` entries or issues
   ([tracking/candidates.md](/standards/tracking/candidates.md)),
   `requirements.txt` moves into `pyproject.toml`.

The adoption lands as one reviewable unit — a small diff as a single
commit straight to main, a large one as a branch and PR; either way the
commit gate at the new pin is the verification.

## The GitHub tail

Both paths finish on GitHub, in order:

1. Fresh repo only: `gh repo create <owner>/<name> --source=. --push` —
   pick the visibility flag deliberately.
2. `~/workspace/dev-playbook/scripts/bootstrap-labels` — enforce the
   canonical label scheme.
3. Set the merge settings and the default-branch protection ruleset by hand,
   per [repo-settings.md](/standards/tracking/repo-settings.md) — both sit
   behind GitHub's Administration permission, so no script does this.

## Enrollment

Add the repo to workspace-lint's `GOVERNED` roster — a dev-playbook edit,
made only once the repo is green. Inclusion is declared, never inferred from
the directory listing
([Distribution Channel](/standards/distribution/channel.md#the-roster));
until enrolled, the repo is not audited and its pin drift never reported.
