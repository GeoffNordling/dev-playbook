---
type: Standard
title: Detectors
description: The check contract — read-only, and the shim, git-root, hosting, and canonical-template rules a first-party script obeys
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

### The script holds no rule logic

The script holds no rule logic: apart from its shebang and inline
metadata block, its statements are at most one that puts the host repo's
package on `sys.path`, one import from that package, and one call of the
imported entry point.

`standard.the-script-holds-no-rule-logic` · deterministic

### Git runs against the given root

A first-party detector that runs git clears the variables
`git rev-parse --local-env-vars` lists from the child environment.

`standard.git-runs-against-the-given-root` · deterministic

> **Why.** Git exports `GIT_DIR` to a hook it runs, always when the
> hook fires in a linked worktree, and `GIT_DIR` outranks both the
> working directory and an explicit `git -C <root>`. The failure is
> silent: a detector told to audit one repository reads another and
> reports on it.

### Every detector is reachable and listed

A first-party detector is reachable from its repo's published hook,
named in the `playbook-lint` roster, wired as a `scripts/` hook its
`.pre-commit-config.yaml` and `.pre-commit-hooks.yaml` both carry, or
registered as an ungated audit, and has a row in a `scripts/README.md`
script table where the repo has that file.

`standard.every-detector-is-reachable-and-listed` · deterministic

### Offered by the canonical template

A first-party detector the repo carrying `standards/build/canonical/`
publishes in `.pre-commit-hooks.yaml` is a hook of that canonical
`.pre-commit-config.yaml`'s pinned dev-playbook block, which offers
exactly the ids that manifest publishes.

`standard.offered-by-the-canonical-template` · deterministic
