---
type: Standard
title: Distribution
description: The distribution channel — the pre-commit hook repo, pinned revs, dogfooding, and the rev-bump release
---

# Distribution

dev-playbook publishes the canonical hook set as a **pre-commit hook
repository** with exactly one published hook: the manifest
[`.pre-commit-hooks.yaml`](/.pre-commit-hooks.yaml) carries the single id
`playbook-lint`, backed by [`scripts/playbook-lint`](/scripts/playbook-lint),
which dispatches to every detector in its roster
([`src/dev_playbook/playbook_lint.py`](/src/dev_playbook/playbook_lint.py)) —
and runs manifest validation via `uvx pre-commit validate-manifest` where the
audited repo publishes a manifest of its own. Consumer repos reference that
one id by URL and a pinned revision, exactly as they reference any
third-party hook. pre-commit clones dev-playbook into its own cache at the
pinned `rev` and runs the hook from there, so resolution is independent of
where the consumer repo — or any of its worktrees — sits on disk, and
identical on CI. The clone carries the
[canonical artifacts](/standards/build/canonical.md) with it.

dev-playbook is a public repository — pre-commit clones it over
unauthenticated HTTPS.

## Enrollment rides the pin

The consumer config never enumerates detectors — the roster inside the clone
does. That is what makes enrollment automatic: a detector added upstream
reaches every consumer at its next pin bump with no config edit anywhere.

An enumerated consumer block cannot do this, which is why the manifest
publishes one id and `MUST` keep publishing one. `pre-commit autoupdate`
moves `rev` and nothing else, and pre-commit accepts no wildcard in place of
a literal hook id, so any list a consumer writes is frozen at the revision
that wrote it — and the canonical-block compare that would flag the gap
ships inside the pinned clone, so it reads that same frozen list and passes.
Enrollment must therefore ride something the pin carries, not something the
consumer restates.

Per-detector skipping still exists where it must: the dispatcher honors the
ordinary `SKIP` environment variable by detector name (the canonical CI
workflow skips `ref-lint` this way).

## Dogfooding

dev-playbook consumes its own hook from the working tree via a
`repo: local` block in its `.pre-commit-config.yaml`, so detector edits are
testable in place before release. The hook metadata appears twice *within*
dev-playbook — the published manifest serves consumers, the local block
dogfoods the working tree — and a hook change updates both. Consumers hold
only a pinned pointer.

Dogfooding is the hosting-pattern invariant, not a dev-playbook privilege:
any repo that publishes a `.pre-commit-hooks.yaml` must run what it ships
from its own local block. repo-lint's `build.self-audit` rule checks the
mirror wherever it finds a manifest.

## The rev bump is the release

A change to the standard — hook code, canonical artifact, version pin —
reaches a consumer only when the consumer's pinned `rev` moves
(`pre-commit autoupdate`). A stale pin is not an error: the consumer keeps
running the standard as of its pin and catches up when the pin is bumped.
Staleness is detected on demand — workspace-lint
([enforcement.md](/standards/build/enforcement.md)) compares each consumer's
pinned `rev` against dev-playbook's current `main` — never by a commit
hook.
