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
