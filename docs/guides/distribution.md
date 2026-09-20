---
type: Guide
title: Distribution Guide
description: The thinking behind the distribution rules — one published hook id, why enrollment rides the pin, the roster, why dev-playbook dogfoods its manifest instead of pinning, and why a stale pin is advisory
---

# Distribution Guide

The guide behind
[Distribution Channel](/standards/distribution/channel.md), the ruleset
that binds a governed repo's share of the channel: its hook manifest,
its local block, and its pin on the hook repository. This guide carries
the reasoning; nothing here is enforced.

## One published id

The manifest `.pre-commit-hooks.yaml` publishes exactly one hook,
`playbook-lint`, backed by `scripts/playbook-lint`, which dispatches to
every detector in its roster, `src/dev_playbook/playbook_lint.py`, and
runs `uvx pre-commit validate-manifest` where the audited repo
publishes a manifest of its own.

A consumer never enumerates detectors, so enrollment rides the pin: a
detector added upstream reaches every consumer at its next pin bump
with no config edit anywhere. dev-playbook is a public repository, so
pre-commit clones it over unauthenticated HTTPS.

## The roster

workspace-lint's `GOVERNED` roster names every governed repo and
nothing else; inclusion is declared there, never inferred from the
directory listing under the workspace root, since repos land there for
reasons the standard has no say in.

A repo the roster omits is not audited and draws no output. A roster
entry with no such repo under the workspace root is a false claim, and
the audit refuses to run rather than pass a quietly shorter sweep.

## Dogfood in place of the pin

dev-playbook's `.pre-commit-config.yaml` carries no pinned dev-playbook
block; it runs the published hook from its working tree through its
`repo: local` block, so an edit to a detector is testable in place
before release, and it is the one governed repo exempt from the pin
rule ([A pinned rev](/standards/distribution/channel.md#a-pinned-rev)).

The hook metadata therefore appears twice within dev-playbook, the
manifest for consumers and the local block for the working tree, and a
hook change updates both
([A publisher dogfoods its manifest](/standards/distribution/channel.md#a-publisher-dogfoods-its-manifest)).
The exemption follows which repo it is, not what it publishes: a
consumer that publishes a manifest of its own still pins dev-playbook.

## A stale pin is advisory

The pin block is a canonical block of the config
([.pre-commit-config.yaml](/standards/build/canonical.md#pre-commit-configyaml)).
A consumer runs the standard as of its pin and catches up when the pin
is bumped, so staleness is reported by workspace-lint on demand, each
pin compared against dev-playbook's current `main`, never by a commit
hook. No pin at all is a failure: being governed is what makes the
absence wrong. pre-commit installs a pin by fetching it, so a
local-only sha is uninstallable.
