---
type: Standard
title: Distribution
description: The distribution channel — the pre-commit hook repo, pinned revs, dogfooding, and the rev-bump release
---

# Distribution

dev-playbook publishes the canonical hook set as a **pre-commit hook
repository**: hook definitions live in
[`.pre-commit-hooks.yaml`](/.pre-commit-hooks.yaml), backed by executable
scripts in `scripts/`. Consumer repos reference them by URL and a pinned
revision, exactly as they reference any third-party hook. pre-commit clones
dev-playbook into its own cache at the pinned `rev` and runs the hooks from
there, so resolution is independent of where the consumer repo — or any of
its worktrees — sits on disk, and identical on CI. The clone carries the
[canonical artifacts](/standards/build/canonical.md) with it.

dev-playbook is a public repository — pre-commit clones it over
unauthenticated HTTPS.

## Dogfooding

dev-playbook consumes its own hooks from the working tree via a
`repo: local` block in its `.pre-commit-config.yaml`, so hook edits are
testable in place before release. The hook metadata appears twice *within*
dev-playbook — the published manifest serves consumers, the local block
dogfoods the working tree — and a hook change updates both. Consumers hold
only a pinned pointer.

## The rev bump is the release

A change to the standard — hook code, canonical artifact, version pin —
reaches a consumer only when the consumer's pinned `rev` moves
(`pre-commit autoupdate`). A stale pin is not an error: the consumer keeps
running the standard as of its pin and catches up when the pin is bumped.
Staleness is detected on demand — workspace-lint
([enforcement.md](/standards/build/enforcement.md)) compares each consumer's
pinned `rev` against dev-playbook's current `main` — never by a commit
hook.
