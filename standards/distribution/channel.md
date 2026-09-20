---
type: Standard-Ruleset
title: Distribution Channel
description: How the hook repository's checks reach the governed repos — a publisher's local block and a consumer's pinned rev
population: "a governed repo's share of the distribution channel: its hook manifest, its local block, and its pin on the hook repository"
---

# Distribution Channel

dev-playbook publishes the canonical hook set as a pre-commit hook
repository. A consumer references it by URL and a pinned revision, as it
references any third-party hook; pre-commit clones dev-playbook into its
own cache at the pinned `rev` and runs the hook from there, so resolution
is independent of where the consumer or any of its worktrees sits on disk
and identical on CI, and the clone carries the
[canonical artifacts](/standards/build/canonical.md) with it. A change to
the standard, hook code, a canonical artifact, or a version pin, reaches a
consumer only when its pinned `rev` moves; the release is the bump
([Distribution](/standards/distribution/card.md)).

## A publisher dogfoods its manifest

A repo whose root holds `.pre-commit-hooks.yaml` lists every hook id that
file publishes under a `repo: local` block of its `.pre-commit-config.yaml`.

`distribution.a-publisher-dogfoods-its-manifest` · deterministic

## A pinned rev

A governed repo's `.pre-commit-config.yaml` pins the hook repository to a
`rev`, unless the repo is the hook repository itself.

`distribution.a-pinned-rev` · deterministic
