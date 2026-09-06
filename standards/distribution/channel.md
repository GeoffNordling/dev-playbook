---
type: Standard
title: Distribution Channel
description: How dev-playbook's checks reach the governed repos — the one published hook, the roster, a publisher's local block, and a consumer's pinned rev
population: "a governed repo's share of the distribution channel: its hook manifest, its local block, its dev-playbook pin, and in dev-playbook the roster"
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
([Distribution](/standards/distribution.md)).

## dev-playbook

The hook repo itself, the one repo that carries
`standards/build/canonical/`.

### One published id

The manifest [.pre-commit-hooks.yaml](/.pre-commit-hooks.yaml) publishes
exactly one hook, `playbook-lint`, backed by
[scripts/playbook-lint](/scripts/playbook-lint), which dispatches to every
detector in its roster
([playbook_lint.py](/src/dev_playbook/playbook_lint.py)) and runs
`uvx pre-commit validate-manifest` where the audited repo publishes a
manifest of its own.

A consumer never enumerates detectors, so enrollment rides the pin: a
detector added upstream reaches every consumer at its next pin bump with
no config edit anywhere.

### Public

dev-playbook is a public repository; pre-commit clones it over
unauthenticated HTTPS.

### The roster

workspace-lint's `GOVERNED` roster names every governed repo and nothing
else; inclusion is declared there, never inferred from the directory
listing.

A repo the roster omits is not audited and draws no output. A roster entry
with no such repo under the workspace root is a false claim, and the audit
refuses to run rather than pass a quietly shorter sweep.

### Dogfood in place of the pin

dev-playbook's `.pre-commit-config.yaml` carries no pinned dev-playbook
block; it runs the published hook from its working tree through its
`repo: local` block, and it is the one governed repo exempt from the pin
rule.

The hook metadata appears twice within dev-playbook, the manifest for
consumers and the local block for the working tree, and a hook change
updates both. The exemption follows which repo it is, not what it
publishes: a consumer that publishes a manifest of its own still pins
dev-playbook.

## A publisher

A repo whose tree holds a `.pre-commit-hooks.yaml`.

### The local block covers the manifest

Every hook id the manifest publishes appears in the repo's `repo: local`
block, so the repo runs what it ships from its own tree
(`distribution.dogfood`); local-only hooks are free additions.

## A consumer

A governed repo other than dev-playbook.

### A pinned rev

`.pre-commit-config.yaml` pins dev-playbook by `rev`, a sha already on
GitHub (`distribution.pin`); a stale pin is advisory, since the consumer
runs the standard as of its pin and catches up when the pin is bumped.

The pin block is a canonical block of the config
([Canonical Artifacts](/standards/build/canonical.md#pre-commit-configyaml)).
Staleness is reported by workspace-lint on demand, each pin compared
against dev-playbook's current `main`, never by a commit hook. pre-commit
installs a pin by fetching it, so a local-only sha is uninstallable.
