---
type: General-Sheet
title: Standard Family Rule Audit
description: The test run of the rule-audit prompt over the standard/ family — every rule's kind, detector coverage, repo state, and overlap, with escalations for what breaks or is weakly checked
---

# Rule audit: standards/standard/

The family declares 21 rules across two Standards: 17 in
[Detectors](/standards/standard/detectors.md) and 4 in
[The Standards Tree](/standards/standard/tree.md). I propose 2
reclassifications, both deterministic to stochastic
(`standard.read-only`, `standard.an-absent-surface-is-clean`); none the
other way. Five rules break: `standard.read-only`, `standard.thin-shims`,
`standard.the-hosting-pattern`, `standard.offered-by-the-canonical-template`,
and `standard.directory-layout`. Three checks are weak
(`standard.the-hosting-pattern`, `standard.offered-by-the-canonical-template`,
`standard.directory-layout`), 8 are full, and 10 have no check at all. The
two hosting rules break because the family's words say each first-party
detector is a published hook while
[Distribution Channel](/standards/distribution/channel.md) says the manifest
publishes exactly one, `playbook-lint`; the detectors written for those two
rules test a different predicate and stay green.

| id | rule | kind | proposed | check | state | overlap | note |
|----|------|------|----------|-------|-------|---------|------|
| `standard.read-only` | A detector leaves everything git tracks as it found it. | deterministic | stochastic | none | breaks | none | Population holds third-party addresses whose code is not in the repo; `ruff-format` and `shfmt` (boundaries.yaml:10,25) run at `commit` as write-mode hooks. |
| `standard.an-absent-surface-is-clean` | A detector whose surface is optional, a `skills/`, `standards/`, or `loops/` tree, exits 0 and reports no finding in a repo that has no such surface. | deterministic | stochastic | none | holds | none | Which detector has an "optional surface" is a judgment; verifying exit 0 needs a run, not a file read. All five optional-surface detectors return clean. |
| `standard.the-verifier-table` | A repo that declares a rule under `standards/` carries `standards/verifiers.yaml`, byte-identical to what `scripts/verifier-table` writes: | deterministic | deterministic | full | holds | none | `verifier_table.audit` renders from the trailers and byte-compares the committed file; missing file and drift are both findings. |
| `standard.an-emitted-id-is-a-rule-heading` | Every id a check claims, a first-party detector under `--list-rules` or a dependency in the generator's dependency map, is the id of a rule declared deterministic under `standards/`, and no two checks claim the same id. | deterministic | deterministic | full | holds | none | `verifier_table.derive` flags an undeclared id, a stochastic id, and a second claimant, for detectors and `DEPENDENCY_RULES` alike. |
| `standard.an-address-exists` | Every dependency address the table names resolves in the repo: | deterministic | deterministic | full | holds | none | `derive` checks each dependency address against hook ids, `pyproject.toml` names, and `pre-commit`. `mypy` is in `dependency-groups.dev`. |
| `standard.a-consumer-adds-only-its-own-rules` | In a repo other than dev-playbook, no row of the table names a rule dev-playbook's shipped table carries; | deterministic | deterministic | full | holds | none | Vacuous here: dev-playbook is the repo the predicate excludes, and no consumer tree is visible. Code path is consumer-mode only. |
| `standard.the-boundary-table` | A repo that asks any check, dev-playbook or a consumer whose `.pre-commit-config.yaml` wires a `scripts/` hook, carries `standards/boundaries.yaml`, byte-identical to what `scripts/boundary-table` writes: | deterministic | deterministic | full | holds | none | `boundary_table.derive` reads hook stages, expands `playbook-lint` and `make -n check`, reads workflow `run` steps less `SKIP`, then byte-compares. |
| `standard.every-address-runs-somewhere` | Every address the verifier table names runs at a gate or is a registered ungated audit, and no registered ungated audit runs at a gate. | deterministic | deterministic | full | holds | none | `derive` flags an address at no gate that is unregistered, and a registered audit a gate runs. `scripts/workspace-lint` is the one `on-demand` row. |
| `standard.a-skip-is-machine-state` | A detector is skipped at a gate only where its input is machine-local rather than held in the repository. | stochastic | stochastic | none | holds | none | "Machine-local rather than held in the repository" is a judgment about a detector's inputs. The one skip, `SKIP: ref-lint` (ci.yml:16), qualifies. |
| `standard.a-first-party-detector` | The detector is a script the audited repo hosts at `scripts/<name>`. | deterministic | deterministic | none | holds | none | Test: every `scripts/<name>` address of verifiers.yaml is an executable file. All 13 exist. The heading is a condition, not a requirement. |
| `standard.thin-shims` | The script holds no rule logic of its own: | deterministic | deterministic | none | breaks | none | Test: the script's module body is only a `sys.path` insert, a `dev_playbook` import, and a `main` call. Five of 13 hold their logic inline. |
| `standard.git-runs-against-the-given-root` | A first-party detector that runs git addresses the repository it was given even when its environment carries an absolute `GIT_DIR` that names another repository. | deterministic | deterministic | none | holds | none | Test: every `git` subprocess passes `env=gitrepo.no_git_env()`. All 11 call sites in `src/` do; no `scripts/` file spawns git. |
| `standard.the-hosting-pattern` | A first-party detector is published as a hook in its repo's `.pre-commit-hooks.yaml` and has a row in the validation table of `scripts/README.md` where the repo has that file. | deterministic | deterministic | weak | breaks | `distribution.a-publisher-dogfoods-its-manifest` | Code compares manifest and local-block id sets and requires a README row; it never tests that a detector is itself a published hook. |
| `standard.offered-by-the-canonical-template` | A first-party detector in the repo that carries `standards/build/canonical/` is a hook of that canonical `.pre-commit-config.yaml`'s pinned block. | deterministic | deterministic | weak | breaks | `distribution.one-published-id` | Code compares the manifest's full id set with the canonical pinned block's; it never tests that a detector is a hook of that block. |
| `standard.list-rules` | A first-party detector answers `--list-rules` by printing every rule id it can emit, one per line, and exiting 0. | deterministic | deterministic | none | holds | none | Test: run each `scripts/<name> --list-rules`, compare its lines with the rule-id constants the module emits. All 13 answer. |
| `standard.finding-format` | A finding is one line, `location:line: | deterministic | deterministic | none | holds | none | Test: every finding is built through `dev_playbook.findings.render` (findings.py:14). All 13 detectors import and use it. |
| `standard.exit-codes` | A first-party detector exits 0 when clean, 1 when it has findings, and 2 when it cannot run. | deterministic | deterministic | none | holds | none | Test: each detector's `main` has a 0, a 1, and a 2 return or `sys.exit`. All 13 do; `harness-files-lint:640` is the exit 2. |
| `standard.directory-layout` | Every immediate subdirectory of `standards/` is a Standard directory: | deterministic | deterministic | weak | breaks | `knowledge-organization.typed-explanation` | `_flat_strays` filters to `.md`, so the flat `verifiers.yaml` and `boundaries.yaml` are neither flagged nor allowed by the predicate. |
| `standard.the-statement` | Every Standard directory's `index.md` opens with one sentence, `<Name> governs <what> — <the things>`: | deterministic | deterministic | none | holds | `knowledge-organization.the-opening-sentence` | The `<Name> governs <what> — <the things>` form is unchecked; the-catalog checks only that a sentence exists and that the row repeats it. All 13 obey. |
| `standard.the-catalog` | A repo carrying a `standards/` tree has a `standards/index.md` listing `README.md` first and then every directory, in dev-playbook the meta-standard's `standard/` next, the rest alphabetical by name, each row carrying its directory index's opening sentence verbatim less the period; | deterministic | deterministic | full | holds | `knowledge-organization.the-listing` | `check_catalog_order` tests README first, the meta lead, directories only, name order, and the verbatim sentence; okf-lint owns membership. |
| `standard.no-shadowing` | A repo-scoped Standard directory's name is one no directory dev-playbook publishes under `standards/` carries; | deterministic | deterministic | full | holds | none | Vacuous here: the rule is consumer-scoped and `audit` runs it only outside dev-playbook mode. `check_shadows_upstream` tests it as written. |

## Escalations

### `standard.read-only` — A detector leaves everything git tracks as it found it. — breaks

The predicate: "A detector leaves everything git tracks as it found it."

The population is "a check the verifier table names, first-party at
`scripts/<name>` or a dependency by its address", so `ruff-format` and `shfmt`
are members. `standards/boundaries.yaml:10` and `:25` put both at `commit`,
`push`, and `ci`. At the commit gate they are the pre-commit hooks of
`.pre-commit-config.yaml:14` and `:22`, wired with no arguments, so each runs
in its rewriting mode over tracked files. `.github/workflows/ci.yml:13` passes
`--show-diff-on-failure`, a flag that only means something for hooks that
modify files.

Two first-party members write too:
`src/dev_playbook/verifier_table.py:449` and
`src/dev_playbook/boundary_table.py:345` write `standards/verifiers.yaml` and
`standards/boundaries.yaml` under `--write`. Neither gate passes that flag,
and `tests/dev_playbook/test_verifier_table.py:297`
(`test_lint_mode_never_writes`) guards the default mode.

The counter-reading is in the family's own Explanation, "A formatter has two
modes" (`standards/standard/explanation.md:40-46`): the write mode "is
enforcement, never an audit". If that carve-out is meant to reach the
population, the predicate does not say so — the population names the address,
and the address is what runs at the gate.

On the kind: I propose stochastic because `ruff-format`, `shfmt`, `mypy`,
`shellcheck`, and `pre-commit validate-manifest` have no source in this repo.
A script reading only repo files can test the first-party half by AST and must
guess at the rest.

### `standard.thin-shims` — The script holds no rule logic of its own: — breaks

The predicate: "The script holds no rule logic of its own: it puts the host
repo's package on the import path and calls that package's entry point."

Eight of the 13 first-party detectors obey — `scripts/testing-lint` (24
lines), `decisions-lint` (26), `loop-lint` (26), `workspace-lint` (27),
`verifier-table` (28), `standards-lint` (29), `boundary-table` (29),
`prose-lint` (32). Five do not, and hold their rule logic in the script file:

- `scripts/repo-lint` — 801 lines, its own `Finding` class and rule constants
  (`scripts/repo-lint:74`), `check_dogfood_mirror` at line 685.
- `scripts/okf-lint` — 842 lines.
- `scripts/harness-files-lint` — 668 lines, its own `main` at line 579.
- `scripts/ref-lint` — 287 lines, its own `main` at line 216.
- `scripts/python-lint` — 182 lines, importing `argparse`, `ast`, and
  `dataclass` directly.

`tests/test_rule_registry.py:40-51` confirms the split from the other side: it
lists `scripts/okf-lint`, `scripts/python-lint`, `scripts/repo-lint`, and
`scripts/harness-files-lint` as source files carrying `Finding` constructions,
next to the `src/dev_playbook/*.py` modules.

The verifier row is null, and no other rule under `standards/` states the shim
shape — `standards/build/explanation.md:189` ("Package-backed scripts are
shims") is Explanation prose with no rule behind it.

### `standard.the-hosting-pattern` — A first-party detector is published as a hook in its repo's `.pre-commit-hooks.yaml` and has a row in the validation table of `scripts/README.md` where the repo has that file. — breaks, weak

The predicate: "A first-party detector is published as a hook in its repo's
`.pre-commit-hooks.yaml` and has a row in the validation table of
`scripts/README.md` where the repo has that file."

`.pre-commit-hooks.yaml:20` publishes exactly one hook, `playbook-lint`. None
of the 13 `scripts/` addresses in `standards/verifiers.yaml` is published as a
hook. `scripts/README.md` states the design plainly: "the manifest and the
local block carry only the aggregate hook and never change." The predicate's
first clause therefore fails for every member, and it contradicts
`distribution.one-published-id` (`standards/distribution/channel.md:23-28`),
which requires exactly the one published hook.

The check is weak because `check_hook_surfaces`
(`src/dev_playbook/standards_lint.py:525-588`) tests a different predicate. It
emits `standard.the-hosting-pattern` for two things only:

1. Set inequality between the manifest's `scripts/`-entry hook ids and the
   local `repo: local` block's (lines 561-564). Both sets are
   `{playbook-lint}` today, so the leg is green.
2. A roster name missing from a `scripts/README.md` table row (lines 583-587),
   where in dev-playbook mode the set scanned is `DETECTORS`, the
   playbook-lint roster, not the published hooks.

Neither leg asks whether a detector is a published hook. Leg 1 also duplicates
`distribution.a-publisher-dogfoods-its-manifest`
(`standards/distribution/channel.md:30-35`), which
`standards/verifiers.yaml:46` assigns to `scripts/repo-lint`, whose
`check_dogfood_mirror` (`scripts/repo-lint:685-720`) tests the same manifest ⊆
local containment.

### `standard.offered-by-the-canonical-template` — A first-party detector in the repo that carries `standards/build/canonical/` is a hook of that canonical `.pre-commit-config.yaml`'s pinned block. — breaks, weak

The predicate: "A first-party detector in the repo that carries
`standards/build/canonical/` is a hook of that canonical
`.pre-commit-config.yaml`'s pinned block."

The pinned block is
`standards/build/canonical/.pre-commit-config.yaml:3-6`, and it holds one
hook, `playbook-lint`. None of the 13 first-party detectors is a hook of it,
so the predicate fails for every member — and, as above, it cannot hold
alongside `distribution.one-published-id`.

The check is weak for the same reason as the hosting rule.
`check_hook_surfaces` (`src/dev_playbook/standards_lint.py:568-581`) compares
`manifest_all` — every id `.pre-commit-hooks.yaml` publishes — against
`_canonical_dev_hook_ids`, the ids in the canonical template's pinned
dev-playbook block. Both are `{playbook-lint}`, so the leg is green. It never
enumerates the detectors, so nothing tests the predicate as written.

### `standard.directory-layout` — Every immediate subdirectory of `standards/` is a Standard directory: — breaks, weak

The predicate: "Every immediate subdirectory of `standards/` is a Standard
directory: it holds at least one file typed `Standard`, and every other `.md`
file under it, `index.md` aside, is typed `Standard` or `Explanation`; the
only flat files under `standards/` are `README.md` and `index.md`;
standards-lint reports a departure."

The third clause breaks in this tree. `git ls-files standards` returns four
flat files:

    standards/README.md
    standards/boundaries.yaml
    standards/index.md
    standards/verifiers.yaml

`standards/verifiers.yaml` and `standards/boundaries.yaml` are neither
`README.md` nor `index.md`. The same family mandates them at exactly those
paths: `standards/standard/detectors.md:41-48` ("carries
`standards/verifiers.yaml`") and `:74-88` ("carries
`standards/boundaries.yaml`"). The rule and the two table rules contradict
each other.

The check is weak because `_flat_strays`
(`src/dev_playbook/standards_lint.py:196-205`) filters the flat candidates to
names ending in `.md`:

    and parts[1].endswith(".md")

so a flat non-Markdown file is never a finding, and the detector stays green
over the two YAML tables. `tests/dev_playbook/test_standards_lint.py:125`
(`test_flat_standards_file_is_flagged_as_a_stray`) fixtures
`standards/build.md`, confirming the `.md`-only reach.

The first two clauses hold: the 13 tracked subdirectories each carry a file
typed `Standard`, and every non-index `.md` under them is typed `Standard` or
`Explanation`. `standards/references/` exists on disk but holds no tracked
file, so it is outside `_standard_dirs` and outside the predicate.

## Detectors

**`scripts/standards-lint`** (`src/dev_playbook/standards_lint.py`, 691 lines)
decides five of this family's rules plus `doc-type.the-population`. It walks
`git ls-files` for `standards/`, flags flat `.md` strays, directories with no
file typed `Standard`, and members typed outside `{Standard, Explanation}`
(`standard.directory-layout`); checks the catalog's order and each row's
verbatim opening sentence (`standard.the-catalog`); compares the published
manifest, the local `repo: local` block, the canonical template's pinned
block, and the `scripts/README.md` table
(`standard.the-hosting-pattern`, `standard.offered-by-the-canonical-template`);
and in consumer mode flags a directory name the pinned dev-playbook clone
already uses (`standard.no-shadowing`). It runs in two modes, keyed on the
presence of `standards/build/canonical/.pre-commit-config.yaml`.

**`scripts/verifier-table`** (`src/dev_playbook/verifier_table.py`, 511 lines)
derives `standards/verifiers.yaml` and is its own lint. `declared_rules` reads
every trailer under `standards/<name>/`, raising rather than tabling when a
trailer disagrees with its heading, has no heading, or repeats an id. It then
asks each roster detector `--list-rules` in parallel and reads
`DEPENDENCY_RULES` for the six dependency addresses, flagging an id no rule
declares, an id a rule declares stochastic, and an id two checks claim
(`standard.an-emitted-id-is-a-rule-heading`), a dependency address the repo
carries nowhere (`standard.an-address-exists`), and in consumer mode a row
naming an upstream rule (`standard.a-consumer-adds-only-its-own-rules`).
Finally it byte-compares the rendered table with the committed file
(`standard.the-verifier-table`).

**`scripts/boundary-table`** (`src/dev_playbook/boundary_table.py`, 402 lines)
derives `standards/boundaries.yaml` from the wiring and is its own lint. It
reads each pre-commit hook's stages into the `commit` and `push` columns,
expanding `playbook-lint` to `DETECTORS` plus the manifest check and a `make`
entry through `make -n`, and reads the `ci` column from each workflow's `run`
steps under their `SKIP`. An address at no gate is `on-demand` when
`playbook_lint.UNGATED_AUDITS` registers it and a finding otherwise, and a
registered audit a gate runs is a finding too
(`standard.every-address-runs-somewhere`); the rendered table is then
byte-compared with the committed file (`standard.the-boundary-table`).

**`src/dev_playbook/findings.py`** (34 lines) is not a detector but is the
single implementation of `standard.finding-format`: `render` builds
`location[:line]: <rule id> message`, and `print_rules` is the shared body of
every detector's `--list-rules`. All 13 first-party detectors call both.
