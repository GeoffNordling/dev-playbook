---
type: Standard
title: Adopting a Repo-Scoped Standard
description: The consumer-repo recipe for a first repo-scoped standard — grow the standards/ tree, write and publish a conforming detector, mirror it, and gate it
---

# Adopting a Repo-Scoped Standard

Most standards a repo runs are workspace-scoped — inherited from dev-playbook
through its published hooks, governing every repo alike. A repo with a
convention no other repo shares declares its own **repo-scoped** standard: the
same card-and-detector machinery the
[meta-standard](/standards/standard/format.md) defines, hosted in the consumer
repo instead of dev-playbook. The recipe below is end-to-end; the card format,
the detector contract, and the hosting pattern it points at are all defined in
[format.md](/standards/standard/format.md).

## 1. Grow the `standards/` tree

If the repo has no `standards/` tree yet, create its landing doc first:
`standards/README.md` (`type: README`) and `standards/index.md`, with the README
listed **first** in the index. The catalog-order rule `standard.catalog-order`
requires that leading `standards/README.md` entry, so an index without it fails
the commit.

Add the standard's **card** at `standards/<name>.md` (`type: Standard-Card`, the
four cells) and the **define doc** it points at — the contract prose. Register
the card in the repo's own `standards/index.md` so the catalog stays complete.
Pick a name no workspace-scoped card already uses: reusing a dev-playbook card
stem shadows the upstream standard and the rule
`standard.card-shadows-upstream` fails the commit (see step 6).

## 2. Write a contract-conforming detector

Back the card's Audit cell with a detector — a `scripts/<name>` shim over the
repo's own reusable modules. It obeys the detector contract in
[format.md](/standards/standard/format.md): read-only, one finding per line in
GNU format (`file:line: card.rule message`) with card-namespaced rule ids,
answering `--list-rules`, exit 0 clean / 1 findings / 2 tool error.

One contract clause is invisible until a hook runs and is easy to miss: the
explicit-root rule — a git-shelling detector scrubs the repository-locating
variables `git rev-parse --local-env-vars` names from its subprocess
environment, and its test suite clears the same set per test. The commit gate is
a git hook, and a hook inherits an absolute `GIT_DIR` whenever discovery would
otherwise find the wrong repository — always from a linked worktree, so anyone
working the way this workspace does meets it immediately, even though a plain
clone shows nothing.

## 3. Publish it in the repo's own manifest

Add the hook to the consumer repo's own `.pre-commit-hooks.yaml`, backed by the
`scripts/<name>` entry — the same way dev-playbook publishes its hooks. The
repo is now the topmost instance of the hosting pattern for its own standard.

## 4. Mirror it in the local block

Add the same hook id to the repo's `repo: local` block in
`.pre-commit-config.yaml`, so the repo runs from its working tree what it
publishes. This is the dogfooding invariant every manifest-shipping repo owes
([distribution.md](/standards/build/distribution.md)); repo-lint's
`build.self-audit` rule checks the mirror.

## 5. Station it at a gate

The local-block wiring runs the detector at the **commit gate**. Record that
rung in the card's Enforce cell, exactly as
[enforcement.md](/standards/build/enforcement.md) prescribes, so the card names
where nonconformance blocks the path to main.

## 6. Turn the meta-standard's own policing on

The meta-standard's detector, `standards-lint`, is a published dev-playbook
hook. Pin-bumping to a dev-playbook `rev` that carries it wires it over the
consumer's `standards/` tree in consumer mode: from that rev it runs the
consumer-mode `standards-lint` rules over the tree (`standards-lint
--list-rules` is the registry). Until the pin moves, the tree is unpoliced by
the meta-standard; the bump is what turns policing on.

## 7. Register a local document type (only if the standard needs one)

Skip this step unless the new standard governs a **document type** the global
OKF registry does not carry. If it does, declare that type in a **local
extension**: the repo's own `standards/docs/document-types.md`, a `## Types`
table of the same shape as the [global registry](/standards/docs/document-types.md),
listing only the repo's local types. okf-lint unions its valid names onto the
upstream registry (upstream ∪ local); it never replaces the global set. The
hierarchy law — additive, downhill only, no shadowing — is defined in the
[registry doc](/standards/docs/document-types.md#local-extensions).

The extension file is itself a **concept document**, so it obeys the same rules
as any doc in the bundle:

- `type: Standard` frontmatter, with a `description` that byte-matches its entry
  in the nearest `index.md` — where it must be listed, like every concept doc.
- Type names in Title Case, hyphen-joined for multi-word names; the `## Types`
  table alphabetical by name.
- Declare a type only when a population of documents actually carries it — a
  vocabulary word earns its place by the documents that use it, and it stays as
  local as that population.

A local type carries name and description only. The per-type constraints upstream
types impose (a required `resource`, an `## Employed by` section) stay upstream;
a local extension cannot declare its own.
