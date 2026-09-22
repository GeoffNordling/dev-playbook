---
type: Standard
title: Detectors
description: The check contract behind the verifier and boundary tables — the two tables, read-only, and the shim, git-root, hosting, and canonical-template rules a first-party script obeys
population: "a check the verifier table names, first-party at scripts/<name> or a dependency by its address, and the two tables at standards/verifiers.yaml and standards/boundaries.yaml"
---

# Detectors

A **detector** is a read-only check the verifier table names: it inspects
the repository against one or more Standards and emits findings, and by
itself it blocks nothing; its run at a gate is the audit stationed there,
which is Enforcement ([Vocabulary](/CONTEXT.md#governance)). The
**verifier table**,
`standards/verifiers.yaml`, maps every rule id declared under `standards/`
to the address of the one check that decides it, or to null where no check
does: a first-party detector by its path, `scripts/repo-lint`; a
dependency by its pinned pre-commit hook id, `ruff-format`; or a dependency
by its `pyproject.toml` name and the subcommand it runs, `mypy`,
`pre-commit validate-manifest`. `scripts/verifier-table` writes the table
and is its lint. The **boundary table**, `standards/boundaries.yaml`, maps
every address the verifier table names to the gates that run it;
`scripts/boundary-table` writes it from the wiring and is its lint. No
Standard says where it runs; the boundary table does.

## Read-only without a write flag

A first-party detector run without an explicit write flag leaves
everything git tracks as it found it; `verifier-table --write` and
`boundary-table --write` are enforcement, and a dependency the verifier
table names may write at its gate, `ruff-format` and `shfmt -w`.

`standard.read-only-without-a-write-flag` · stochastic

## A declaring repo carries the generated verifier table

A repo that declares a rule under `standards/` carries
`standards/verifiers.yaml`, byte-identical to what `scripts/verifier-table`
writes: one row per declared rule id, sorted, each carrying the address of
the one check that decides it or null.

`standard.a-declaring-repo-carries-the-generated-verifier-table` · deterministic

> **Why.** Question and mechanism cross-cut: several detectors check
> one Standard, and one detector checks for several Standards, so the
> one-to-one fact sits at the rule id rather than at the check. A
> null row is an honest one: the rule is stated and no check decides
> it.

### An emitted id is a rule heading

Every id a check claims, a first-party detector under `--list-rules` or a
dependency in the generator's dependency map, is the id of a rule
declared deterministic under `standards/`, and no two checks claim the
same id.

`standard.an-emitted-id-is-a-rule-heading` · deterministic

### An address exists

Every dependency address the table names resolves in the repo: a hook id
of its `.pre-commit-config.yaml`, or a dependency its `pyproject.toml`
declares, or `pre-commit` itself where that config file exists.

`standard.an-address-exists` · deterministic

### A consumer adds only its own rules

In a repo other than dev-playbook, no row of the table names a rule
dev-playbook's shipped table carries; the two tables union at read time.

`standard.a-consumer-adds-only-its-own-rules` · deterministic

## The boundary table, generated from the wiring

A repo that asks any check, dev-playbook or a consumer whose
`.pre-commit-config.yaml` wires a `scripts/` hook, carries
`standards/boundaries.yaml`, byte-identical to what
`scripts/boundary-table` writes: one row per address the verifier table
names, sorted, each carrying the gates that run it in a fixed order drawn
from `commit`, the pre-commit stage at `git commit`; `push`, the pre-push
stage at `git push`, which runs `make check`; `ci`, a workflow under
`.github/workflows/`; and `on-demand`, no gate. The rows are read from
the wiring: the hooks of `.pre-commit-config.yaml` by their stages, with
`playbook-lint` expanded to its roster, the recipe of `make check`, and
each workflow's `run` steps less their `SKIP`.

`standard.the-boundary-table-generated-from-the-wiring` · deterministic

> **Why.** A Standard that stated its own enforcement could be wrong
> about it and nothing would notice, so where a check runs is read
> from the wiring instead.

### Every address runs somewhere

Every address the verifier table names runs at a gate or is a registered
ungated audit, and no registered ungated audit runs at a gate.

`standard.every-address-runs-somewhere` · deterministic

### A skip is machine state

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
