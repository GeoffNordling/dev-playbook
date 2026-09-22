---
type: Standard
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
consumer only when its pinned `rev` moves; the release is the bump.

> **Why.** The publisher gains nothing from pinning itself: a pin would
> run the last released detector, while a local block runs the one
> being edited, so a change is testable before release. The exemption
> follows which repo it is, not what it publishes.

## One published id

The hook repository's `.pre-commit-hooks.yaml` publishes exactly one
hook, `playbook-lint`.

`distribution.one-published-id` · deterministic

> **Why.** One id spares a consumer the detector list, so enrollment
> rides the pin: a detector added upstream reaches every consumer at
> its next pin bump with no config edit anywhere.

## A publisher dogfoods its manifest

A repo whose root holds `.pre-commit-hooks.yaml` lists every hook id that
file publishes under a `repo: local` block of its `.pre-commit-config.yaml`.

`distribution.a-publisher-dogfoods-its-manifest` · deterministic

## A valid manifest

A `.pre-commit-hooks.yaml` at a governed repo's root passes
`pre-commit validate-manifest`.

`distribution.a-valid-manifest` · deterministic

## A pinned rev

A governed repo's `.pre-commit-config.yaml` pins the hook repository to a
`rev`, unless the repo is the hook repository itself.

`distribution.a-pinned-rev` · deterministic

> **Why.** A consumer runs the standard as of its pin and catches up
> when the pin is bumped, so staleness is advisory rather than a
> commit-time failure. The absence of a pin is the failure: being
> governed is what makes it wrong.

## The roster

A governed repo is named in workspace-lint's `GOVERNED` roster, and
every name in the roster is a repo under the workspace root.

`distribution.the-roster` · deterministic

> **Why.** Repos land under the workspace root for reasons the standard
> has no say in, so the directory listing cannot tell a governed repo
> from a neighbour and inclusion is declared instead. A name with no
> repo behind it is a false claim, and a sweep that quietly covers less
> is worse than one that stops.
