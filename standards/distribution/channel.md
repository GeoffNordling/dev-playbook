---
type: Standard
title: Distribution Channel
description: How the hook repository's checks reach the governed repos — a valid manifest, a publisher's local block, and a host's local hook and pinned dev dependency
population: "a governed repo's share of the distribution channel: its hook manifest, its local block, its local hook, and its dev dependency on the hook repository"
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

A consumer that writes its own Standards is a host: it runs its own
checks in a second hook, `playbook-check-local`, in its own environment,
because the environment pre-commit builds for the pinned hook holds
dev-playbook and nothing of the consumer's
([Consumer Checks Run in a Second, Local Hook](/docs/decisions/0031-consumer-checks-run-in-a-local-hook.md)).

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

## A host runs its own checks

A repo other than the hook repository whose `standards/` holds a
deterministic rule, or which tracks a `.py` file in
`src/<package>/checks/`, lists the hook `playbook-check-local` under a
`repo: local` block of its `.pre-commit-config.yaml`, with
`entry: uv run --locked playbook check --local` and
`language: system`.

`distribution.a-host-runs-its-own-checks` · deterministic

> **Why.** The pinned `playbook-check` hook runs dev-playbook's checks
> only. Without the local hook, a host's rules have no gate, and nothing
> goes red to say so. `--locked` makes a stale `uv.lock` fail the hook
> instead of the hook rewriting the lock mid-commit.

## A host's dev-playbook rides the pin

A repo that lists `playbook-check-local` names `dev-playbook` in its
`pyproject.toml` `[dependency-groups] dev`, and its
`[tool.uv.sources]` sources it as `git` at the hook repository's URL
with `rev` equal to the `rev` its `.pre-commit-config.yaml` pins for
the hook repository.

`distribution.a-hosts-dev-playbook-rides-the-pin` · deterministic

> **Why.** The local hook runs the dev-playbook its environment holds, so
> that copy must be the pinned one. A path source follows a live checkout
> that a CI runner does not have, and any other rev drifts from the
> Standards the pinned hook enforces. `bump-pin` and `update-pins` move
> the two revs together.

## The manifest validates

A `.pre-commit-hooks.yaml` at a governed repo's root passes
`pre-commit validate-manifest`.

`distribution.the-manifest-validates` · deterministic
