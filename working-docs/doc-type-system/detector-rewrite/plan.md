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
- **The registry.** `src/dev_playbook/check_registry.py`: the `@check` decorator
  writing one dict entry, the `needs=WORKSPACE` tag, and registration
  of a rule by hook name for the ones ruff, shellcheck, shfmt, and the
  manifest validator decide. The two tool-decided shell entries land
  here; the shell family's three other rules are phase 3's last step.
- **The runner and the console script.** `playbook check` builds the
  model once, runs every registered function, stamps the id on each
  finding, and honours `--without workspace`. `playbook checks` prints
  the dict. Both under `[project.scripts]` in `pyproject.toml`.
- **The hook.** A second entry in `.pre-commit-hooks.yaml`,
  `language: python`, next to `playbook-lint`. Both entries in the
  canonical `.pre-commit-config.yaml` and in this repo's.
- **The sources module.** `sources.py` with its first constants and
  the test that pins each to its heading.
- **The meta-test.** `tests/dev_playbook/test_check_registry.py`: every
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
| 12 | shell | nothing; its two tool-decided rules landed in phase 1 |

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

A Ralph loop ([Ralph loop](/harness-recipes/recipes/ralph-loop.md)),
one segment per one to four steps. `PLAN.md` at the checkout root
holds the twelve tasks with checkpoint markers after steps 1, 2, 3,
5, 9, and 11, and after every step from 12 on, the rework steps the
Step 11 audit added included; `PROGRESS.md` is the log. Each launch
runs up to four Opus iterations, one per step, and stops at the next
marker. Each
iteration's task line points it at
[Rewrite Family Prompt](/working-docs/doc-type-system/detector-rewrite/prompts/rewrite-family.md):
the family's triage report is the specification, the scaffold is read
before any code is written, the report goes to
`rewrite/<family>.md`, and the iteration commits its family as one
commit, as the loop requires. The launch, the same for every step:

```
Workflow({ name: "ralph-loop", args: { model: "opus", maxIters: 4, planFile: "PLAN.md", progressFile: "PROGRESS.md", checkCmd: "make check" } })
```

At each checkpoint, three things in order, the third a stop:

1. **The fork verifies.** `/ralph-checkpoint` forks the session; the
   fork runs the Guardrails below against the tree, writes a fix task
   at the front of the next segment where one fails, checks the
   marker off, and commits the two loop files.
2. **The session relays.** The fork's report, the report file, and
   the range to diff, in a few lines.
3. **The session ranks and releases.** The session sorts the
   segment's deviations, judgment calls and Guardrail misses alike,
   by how much they matter, shows the user the top two, and launches
   the next segment. A deviation the session cannot rule on itself
   stops the run for the user's word, and a rejected segment is
   reverted or fixed by hand before the next launch.

### Guardrails

What the fork checks, each against the tree, with the segment's
commits as the range:

- **No heading drifted.** The heading lines added and removed under
  `standards/<family>/` in the range are exactly the report's deleted
  and new rules.
- **Bodies match.** Each restated rule's body equals its blockquote
  in `triage/<family>.md`.
- **The repo passes.** `make check`, `scripts/playbook-lint .`, and
  `uv run playbook check .` are all clean.
- **Coverage.** `uv run playbook checks --family <family>` lists
  exactly the deterministic trailers under `standards/<family>/`; the
  meta-test in `make check` says every function has its test.
- **The retirement happened.** Each script the step retires is gone
  from `git ls-files`, and its name appears nowhere outside
  `working-docs/`.
- **The worklist moved.** `rewrite/<family>.md` exists and its index
  row is in.
- **No drift.** The judgment calls in `PROGRESS.md` are each a gap the
  report left, not a departure from it; a call that overrode the
  report is a fix task.

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

## Progress

- **Phase 1, 2026-09-23.** The scaffold is in the tree: `model.py`,
  `check_registry.py`, `check_cli.py`, `sources.py`, `checks/shell.py`
  with the two tool-decided shell rules, the `playbook-check` hook in
  the manifest and both configs, and the four test files with the
  meta-test. The empty run, model build included, is 0.25 s on this
  repo; the old gate is 0.47 s. One word, check, names the concern at
  every level: the term, the `playbook check` and `playbook checks`
  commands, the hook id, the two modules, the `@check` decorator, and
  the `Check` entry. The placeholders `cli.py` and `registry.py` could
  not stand because the viewer's tests already own those basenames and
  pytest refuses two test files of one name.
- **Phase 2, 2026-09-23.** The dead weight is gone: the two tables,
  their two scripts, `verifier_table.py`, `boundary_table.py`, their
  two tests, and the two roster lines. The rules deleted from
  `standards/standard/detectors.md` are six, not three, as the
  standard family's triage read the ruling: the two H2 table rules
  and the four H3 rules under them, each stating a property of a
  table row or an address. The two stochastic rules stay; the skip
  rule moves up to H2 with its parent gone, its id unchanged. The
  dead `UNGATED_AUDITS` set left `playbook_lint.py` with the boundary
  table, its only reader. Fourteen files outside the working set
  named the tables or linked the deleted headings, and each sentence
  was repointed at Detectors or dropped, so `ref-lint` and the index
  check stay clean. The three gates are green with 42 fewer tests.
- **Phase 3 set up, 2026-09-23.** The loop is ready and unlaunched:
  `PLAN.md` with the twelve tasks and a checkpoint after each, shell
  last since its three function-decided rules had no step,
  `PROGRESS.md` empty,
  [Rewrite Family Prompt](/working-docs/doc-type-system/detector-rewrite/prompts/rewrite-family.md)
  written, and `rewrite/` waiting for the reports. One scaffold fix
  on the way: the registry maps a family to its module with hyphens
  as underscores, since `doc-type` and `knowledge-organization`
  cannot name a module.

## Finish line

The Planned entry for the rewrite is done when the tree holds: no
detector under `scripts/` except `loop-lint`, one check module per
Standards directory, the meta-test green in both directions, the
tables gone, and every check clean on the repo. The tests item is
done in the same tree. The Standards-and-docs item and scripts under
ruff follow as their own work.

## Acronyms

None.
