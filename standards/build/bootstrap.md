---
type: Standard
title: Bootstrap
description: The fresh-repo procedure — repo-init scaffolds the conforming tree; GitHub creation, labels, settings, and roster enrollment complete adoption
---

# Bootstrap

How a fresh repository joins the workspace conforming from its first
commit. The local scaffold is scripted; the GitHub side is a short manual
tail.

## The scaffold

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

## The GitHub tail

From the new repo, in order:

1. `gh repo create <owner>/<name> --source=. --push` — pick the visibility
   flag deliberately.
2. `~/workspace/dev-playbook/scripts/bootstrap-labels` — mint the canonical
   label scheme.
3. Set the merge settings and the default-branch protection ruleset by hand,
   per [repo-settings.md](/standards/tracking/repo-settings.md) — both sit
   behind GitHub's Administration permission, so no script does this.

## Enrollment

Add the repo to workspace-lint's `GOVERNED` roster — a dev-playbook edit.
Inclusion is declared, never inferred from the directory listing
([distribution.md](/standards/build/distribution.md#which-repos-are-consumers));
until enrolled, the repo is not audited and its pin drift never reported.
