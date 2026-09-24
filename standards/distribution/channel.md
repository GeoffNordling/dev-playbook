---
type: Standard
title: Distribution Channel
description: How the hook repository's checks reach the governed repos — a valid manifest and a publisher's local block
population: "a governed repo's share of the distribution channel: its hook manifest and its local block"
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
consumer only when its pinned `rev` moves; the release is the bump.

## A publisher dogfoods its manifest

A repo whose root holds `.pre-commit-hooks.yaml` lists every hook id that
file publishes under a `repo: local` block of its `.pre-commit-config.yaml`.

`distribution.a-publisher-dogfoods-its-manifest` · deterministic

## A consumer pins the published head

A governed repo other than the hook repository pins the hook repository,
in its `.pre-commit-config.yaml` on its default branch, at the sha of the
hook repository's published `main` head, and lists under that block
exactly the hook ids the hook repository's `.pre-commit-hooks.yaml`
publishes at that sha. Behind the head, the repo runs a standard that is
no longer the standard; at a stale id, pre-commit fails before any check
runs.

`distribution.a-consumer-pins-the-published-head` · deterministic

## The manifest validates

A `.pre-commit-hooks.yaml` at a governed repo's root passes
`pre-commit validate-manifest`.

`distribution.the-manifest-validates` · deterministic
