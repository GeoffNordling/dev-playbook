---
type: Guide
title: Adopting a Repo-Scoped Standard
description: The consumer-repo recipe for a first repo-scoped standard — grow the standards/ tree, write and publish a conforming detector, mirror it, and gate it
---

# Adopting a Repo-Scoped Standard

Most standards a repo runs are workspace-scoped: inherited from
dev-playbook through its published hooks, governing every repo alike. A
repo with a convention no other repo shares declares its own
**repo-scoped** standard, the same card-and-detector machinery the
[Meta-Standard](/standards/standard.md) card defines, hosted in the
consumer repo instead of dev-playbook. The recipe below is the order of
operations; every rule a step meets is stated once, in the Standard the
step links.

## 1. Grow the `standards/` tree

If the repo has no `standards/` tree yet, create its landing doc first:
`standards/README.md` (`type: README`) and `standards/index.md`, with
the README listed first. Add the standard's **card** at
`standards/<name>.md`, the four cells, and the **Standard** it points
at under `standards/<name>/`, and register both in the index. The
layout, the stem, and the index order are
[Card Catalog](/standards/standard/cards.md): a stem no dev-playbook card
carries ([No shadowing](/standards/standard/cards.md#no-shadowing)), and
the README-first catalog
([The catalog](/standards/standard/cards.md#the-catalog)).

## 2. Write a contract-conforming detector

Back the card's Audit cell with a detector, a `scripts/<name>` shim over
the repo's own reusable modules, obeying the first-party rules in
[Detectors](/standards/standard/detectors.md#a-first-party-detector):
read-only, one finding per line in GNU format with card-namespaced rule
ids, answering `--list-rules`, exit 0 clean, 1 findings, 2 cannot run.
The one clause invisible until a hook runs is
[Explicit roots outrank the hook environment](/standards/standard/detectors.md#explicit-roots-outrank-the-hook-environment):
the commit gate is a git hook, and from a linked worktree it exports an
absolute `GIT_DIR`, so anyone working the way this workspace does meets
the clause immediately.

## 3. Publish it in the repo's own manifest

Add the hook to the consumer repo's own `.pre-commit-hooks.yaml`, backed
by the `scripts/<name>` entry, the same way dev-playbook publishes its
hooks
([The hosting pattern](/standards/standard/detectors.md#the-hosting-pattern)).
The repo is now the topmost instance of the hosting pattern for its own
standard.

## 4. Mirror it in the local block

Add the same hook id to the repo's `repo: local` block in
`.pre-commit-config.yaml`, so the repo runs from its working tree what it
publishes
([The local block covers the manifest](/standards/distribution/channel.md#the-local-block-covers-the-manifest));
repo-lint's `distribution.dogfood` checks the mirror.

## 5. Station it at a gate

The local-block wiring runs the detector at the **commit gate**. Record
that rung in the card's Enforce cell
([Cells](/doc-types/standard-card/encoding.md#cells)), so the card names
where nonconformance blocks the path to main
([Gates](/standards/standard/gates.md#three-rungs)).

## 6. Turn the meta-standard's own policing on

The meta-standard's detector, `standards-lint`, is a published
dev-playbook hook. Bump the pin to a dev-playbook `rev` that carries it
([A pinned rev](/standards/distribution/channel.md#a-pinned-rev)): from
that rev it runs the consumer-mode rules over the repo's `standards/`
tree (`standards-lint --list-rules` is the registry). Until the pin
moves, the tree is unpoliced by the meta-standard.

## 7. Register a local document type (only if the standard needs one)

Skip this step unless the new standard governs a **document type** the
global OKF registry does not carry. If it does, declare the type in a
local extension, the repo's own
`standards/knowledge-organization/document-types.md` holding a
`## Types` table of the same shape as the
[global registry](/standards/knowledge-organization/document-types.md);
okf-lint unions its valid names onto the upstream registry. The table's
rules, the row shape, alphabetical order, add-never-shadow, and name and
description only, are
[Type Registry](/standards/knowledge-organization/type-registry.md#local-extension),
and the extension file is itself a concept document bound by
[Document Types](/standards/knowledge-organization/document-types.md).
