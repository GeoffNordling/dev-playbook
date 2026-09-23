---
type: Standard
title: Detectors
description: The check contract — read-only, skipped only for machine state, and the canonical template offering the hooks the manifest publishes
population: "a check that decides a rule under standards/, first-party at scripts/<name> or a dependency by its pinned hook id or pyproject.toml name"
---

# Detectors

A **detector** is a read-only check that decides one or more rules under
`standards/`: it inspects the repository against those Standards and emits
findings, and by itself it blocks nothing; its run at a gate is the audit
stationed there, which is Enforcement ([Vocabulary](/CONTEXT.md#governance)).
A detector is a first-party script by its path, `scripts/repo-lint`; a
dependency by its pinned pre-commit hook id, `ruff-format`; or a dependency
by its `pyproject.toml` name and the subcommand it runs, `mypy`,
`pre-commit validate-manifest`.

## Read-only without a write flag

A first-party detector run without an explicit write flag leaves
everything git tracks as it found it; a dependency may write at its gate,
`ruff-format` and `shfmt -w`.

`standard.read-only-without-a-write-flag` · stochastic

## A skip is machine state

A detector is skipped at a gate only where its input is machine-local
rather than held in the repository.

`standard.a-skip-is-machine-state` · stochastic

## A first-party detector

The detector is a script the audited repo hosts at `scripts/<name>`.

### Offered by the canonical template

The hook ids in the dev-playbook `repo:` block of
`standards/build/canonical/.pre-commit-config.yaml` are the same
set as the hook ids in `.pre-commit-hooks.yaml`.

`standard.offered-by-the-canonical-template` · deterministic
