---
type: Standard
title: Detectors
description: The check contract behind the verifier and boundary tables — the two tables, read-only, clean on an absent surface, and the shim, git-root, hosting, rule-id, output, and exit-code rules a first-party script obeys
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

## Read-only

A detector leaves everything git tracks as it found it.

`standard.read-only` · deterministic

## An absent surface is clean

A detector whose surface is optional, a `skills/`, `standards/`, or
`loops/` tree, exits 0 and reports no finding in a repo that has no such
surface.

`standard.an-absent-surface-is-clean` · deterministic

> **Why.** The alternative, dropping the detector from repos that
> lack the surface, would make the hook set differ from repo to repo
> and would leave a repo unpoliced the day it grows the surface. The
> gap closes inside the detector, so the wiring stays the same
> everywhere.

## The verifier table

A repo that declares a rule under `standards/` carries
`standards/verifiers.yaml`, byte-identical to what `scripts/verifier-table`
writes: one row per declared rule id, sorted, each carrying the address of
the one check that decides it or null.

`standard.the-verifier-table` · deterministic

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

## The boundary table

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

`standard.the-boundary-table` · deterministic

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

`standard.a-first-party-detector` · deterministic

### Thin shims

The script holds no rule logic of its own: it puts the host repo's
package on the import path and calls that package's entry point.

`standard.thin-shims` · deterministic

### Git runs against the given root

A first-party detector that runs git addresses the repository it was
given even when its environment carries an absolute `GIT_DIR` that names
another repository.

`standard.git-runs-against-the-given-root` · deterministic

> **Why.** Git exports `GIT_DIR` to a hook it runs, always when the
> hook fires in a linked worktree, and `GIT_DIR` outranks both the
> working directory and an explicit `git -C <root>`. The failure is
> silent: a detector told to audit one repository reads another and
> reports on it.

### The hosting pattern

A first-party detector is published as a hook in its repo's
`.pre-commit-hooks.yaml` and has a row in the validation table of
`scripts/README.md` where the repo has that file.

`standard.the-hosting-pattern` · deterministic

### Offered by the canonical template

A first-party detector in the repo that carries
`standards/build/canonical/` is a hook of that canonical
`.pre-commit-config.yaml`'s pinned block.

`standard.offered-by-the-canonical-template` · deterministic

### List rules

A first-party detector answers `--list-rules` by printing every rule id
it can emit, one per line, and exiting 0.

`standard.list-rules` · deterministic

### Finding format

A finding is one line, `location:line: <rule id> message`: a colon after
the location, single spaces, the location a repo-relative path, or the
member's name where the member is not a file, and `:line` omitted for a
finding on the whole member.

`standard.finding-format` · deterministic

### Exit codes

A first-party detector exits 0 when clean, 1 when it has findings, and 2
when it cannot run.

`standard.exit-codes` · deterministic
