---
type: General-Sheet
title: Rewrite Plan
description: The implementation plan of the detector rewrite — four phases, the family order and which old script each family retires, how each phase is delegated and checked, and the finish line
---

# Rewrite Plan

How the Planned items of
[Detector Rewrite](/working-docs/doc-type-system/detector-rewrite/ROOT.md)
get built. The design is the seven rulings under its Decided; the
specification is the twelve reports under
[Triage](/working-docs/doc-type-system/detector-rewrite/triage.md).
This file adds the one thing neither has: the order of the work and
what is true of the repo after each step.

## The shape

Four phases. The gate is green after every commit, because the old
scripts and the new package run side by side until the old ones are
empty.

1. **Scaffold.** The package with no checks in it.
2. **Delete the dead weight.** The two tables and the three rules
   that required them.
3. **One family at a time.** Twelve units of the same work, one
   commit each, big scripts retired as their last family lands.
4. **Cut over.** The old entry point goes; the stopwatch runs.

Then the last two Planned items in their own turn: the Standards and
docs, and scripts under ruff.

## Phase 1: scaffold

Done in session, by hand, since every later step builds on its shape.
Lands in one commit:

- **The model.** `src/dev_playbook/model.py`: plain dataclasses for
  the repo, a markdown file, a heading, a trailer, a link, a Python
  file. One constructor builds it from one `git ls-files`. The
  markdown parser is the hand-rolled scanner from `md.py`, kept, with
  one fix: a link whose text wraps across a line break is found. The
  Python half is the standard library's `ast`.
- **The registry.** `src/dev_playbook/registry.py`: the `@rule` decorator
  writing one dict entry, the `needs=WORKSPACE` tag, and registration
  of a rule by hook name for the ones ruff, shellcheck, shfmt, and the
  manifest validator decide. Those tool-decided entries land here,
  so the `shell` family has no step in phase 3.
- **The runner and the console script.** `playbook check` builds the
  model once, runs every registered function, stamps the id on each
  finding, and honours `--without workspace`. `playbook rules` prints
  the dict. Both under `[project.scripts]` in `pyproject.toml`.
- **The hook.** A second entry in `.pre-commit-hooks.yaml`,
  `language: python`, next to `playbook-lint`. Both entries in the
  canonical `.pre-commit-config.yaml` and in this repo's.
- **The sources module.** `sources.py` with its first constants and
  the test that pins each to its heading.
- **The meta-test.** `tests/dev_playbook/test_registry.py`: every
  registered function has a test named for its id, and every
  registered id is a heading under `standards/`. The reverse
  direction, every deterministic trailer is registered, is written
  now and marked expected-to-fail until cut over.

Exit check: `playbook check` runs clean with zero findings, and its
wall time on this repo, model build included, is on record. The
parser alone is 0.03 s, so the number should sit far under the 0.47 s
baseline.

## Phase 2: the dead weight

One commit, by hand: `standards/verifiers.yaml`,
`standards/boundaries.yaml`, `scripts/verifier-table`,
`scripts/boundary-table`, `verifier_table.py`, `boundary_table.py`,
their two tests, their two roster lines, and the three rules in
`standards/standard/detectors.md` that required them. Nothing reads
the tables, and their scripts demand a row per rule id, so every
family in phase 3 would otherwise maintain a dead file.

## Phase 3: one family at a time

The repeatable unit. For one family, in one commit:

1. Write `checks/<family>.py`: one function per rule the family's
   report keeps, restates, or builds, each reading the model.
2. Write one test per rule id in `tests/dev_playbook/checks/`.
3. Edit the family's Standards to the report: restated bodies pasted
   from the report's blockquotes, deleted rules removed, new rules
   added, the one stochastic conversion made. Headings never change.
4. Delete the family's old detector where this family was its last:
   the script, its package module, its tests, its roster line.
5. Run the gate, run `make check`, and confirm `playbook check` is
   clean on the repo as it stands.

The order, smallest first, with what each step retires:

| Step | Family | Retires |
| --- | --- | --- |
| 1 | python | `python-lint` |
| 2 | testing | `testing-lint` |
| 3 | decisions | `decisions-lint` |
| 4 | prose | `prose-lint` |
| 5 | tracking | nothing; `workspace-lint` is untouched |
| 6 | distribution | nothing yet |
| 7 | build | nothing yet |
| 8 | harness | nothing yet |
| 9 | standard | nothing yet |
| 10 | doc-type | `harness-files-lint`, `standards-lint` |
| 11 | knowledge-organization | `okf-lint`, `ref-lint`, `repo-lint` |

A name in the last column means the script under `scripts/`, its
package module where it has one, its tests, and its roster line.

A rule checked by both an old script and a new function between
steps is harmless: both pass. The three monoliths go at the end
because their last family is the largest.

The loop family is not in the table. Its module `loop_lint.py` and
shim stay as they are for the next workstream; at cut over the new
runner calls that module as one legacy step, so the loop checks keep
their gate.

### Delegation

A Ralph loop, one segment per step, an Opus agent per segment
launched from `prompts/rewrite-family.md`, written before step 1 in
the pattern of the triage prompt: the family's report is the
specification, the model and registry are read before any code is
written, the report is written to a file, and the agent commits
nothing itself. The checkpoint agent between segments verifies the
segment before releasing the next.

### Guardrails

What the checkpoint agent checks, all mechanical:

- **No heading drifted.** The diff of heading lines under
  `standards/` is exactly the report's deleted and new rules.
- **Bodies match.** Every restated body equals its report blockquote.
- **The repo passes.** `playbook check` and the old gate are both
  clean; `make check` is green; no check was added that fails.
- **Coverage.** Every deterministic trailer in the family's Standards
  is a registered id, and every registered id has its test.
- **The retirement happened.** The old script named in the table for
  this step is gone, with its tests and roster line.
- **The worklist moved.** The step is recorded in this file's
  progress and in the ROOT.

## Phase 4: cut over

One commit, by hand, once the roster of `scripts/playbook-lint` holds
only `loop-lint`:

- The `playbook-lint` entries go from `.pre-commit-hooks.yaml`, the
  canonical `.pre-commit-config.yaml`, and this repo's; the new hook
  is the only one.
- `scripts/playbook-lint` and `playbook_lint.py` go, with their tests,
  and `tests/test_rule_registry.py` with the tuples it guards.
- `SKIP: ref-lint` in the canonical `ci.yml` becomes
  `playbook check --without workspace`.
- The meta-test's reverse direction stops being expected-to-fail.
- The stopwatch: `pre-commit run --all-files` and `pytest` against
  0.89 s and 10.0 s. A miss is a finding, not a pass.

## Finish line

The Planned entry for the rewrite is done when the tree holds: no
detector under `scripts/` except `loop-lint`, one check module per
Standards directory, the meta-test green in both directions, the
tables gone, and every check clean on the repo. The tests item is
done in the same tree. The Standards-and-docs item and scripts under
ruff follow as their own work.

## Acronyms

None.
