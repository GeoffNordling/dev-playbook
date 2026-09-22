---
type: General-Sheet
title: Detector Rewrite
description: The root of the detector rewrite strand — one pass over the checking system against the settled Standards, its principles and constraints, the current state it starts from, the open design questions, and the worklist
---

# Detector Rewrite

The strand that rewrites the checking system: the Python detectors,
the two tables they feed, and the hook that runs them. Speculative,
per
[Synthesis Working Root](/working-docs/doc-type-system/ROOT.md).
It depends on the doc-type system strand
([Doc-Type System](/working-docs/doc-type-system/doc-type-system/ROOT.md)),
whose step 11 settled the rules the detectors answer to; no strand's
plan waits on it. Its input is
[Detector Fixes](/working-docs/doc-type-system/detector-rewrite/detector-fixes.md).

## Goal

One holistic pass over the checking system: refactor, reconsider,
redesign. The detectors grew one at a time over months and were never
refactored together, so the pass rewrites the whole suite against the
settled rules, from scratch where that is cleaner, into
`src/dev_playbook/`, grouped by module. On exit, every deterministic
rule stated under `standards/` has a check that decides it, every
check decides a stated rule, and every Standard the rewrite touches
is one the repo complies with.

## Principles

- **Greenfield.** Every rule stated today is an intention, not a
  contract. A rule that no longer makes sense is deleted; one that
  needs changing is changed; none is implemented because it is
  stated. The one invariant is that what is stated on exit is
  complied with on exit.
- **Professional practice where it is an easy win.** The suite was
  built by one developer and one model over months. Where a
  well-known pattern — how ruff, flake8, and the pre-commit mirrors
  do it — replaces a local invention, take it. The five in hand:
  `language: python` with a console script instead of a self-
  bootstrapping file; a registry of checks keyed by rule id instead
  of hand-kept id tuples; one parsed repo model instead of one walk
  per detector; `--select` and `--ignore` by rule id with one config
  surface; one test per rule id with a meta-test over the registry.
- **Delete is the default.** Per the doc-type system's three working
  policies: no credit for rule count, and a detector never keeps a
  rule alive.
- **Simple.** Fewer moving parts beats a clever one.

## Constraints

- **At least as fast as the hooks today.** The number is measured
  before the design is judged against it.
- **Deterministic rules only.** Stochastic rules, a judge, and any
  runner for one are out. The trailer's kind is the only slot they
  keep.
- **No GitHub auditing.** `scripts/workspace-lint` and everything it
  decides over `gh api` is untouched.
- **The null rows are in.** The 52 deterministic rules with no check
  gain one on this pass, or are deleted.
- **This repo only.** The design is judged in dev-playbook. A generic
  repo on this machine bumps its pin and refactors itself to meet the
  new detectors, as it does today; nothing else about consumer repos
  is held.

## Current state

- 217 rules carry a trailer; 119 have no check. By family:
  knowledge-organization 37 of 60 null, doc-type 26 of 42, prose 14
  of 18, decisions 7 of 9; `python` alone is fully covered.
- 18 addresses: 12 detectors in the `playbook-lint` roster,
  `workspace-lint` ungated, and 5 dependencies (`ruff-check`,
  `ruff-format`, `shellcheck`, `shfmt`, `pre-commit validate-manifest`).
- The detectors split two ways. Five carry their logic in the script
  itself — `okf-lint` 808 lines, `repo-lint` 781, `harness-files-lint`
  677, `ref-lint` 287, `python-lint` 182 — against
  `standard.the-script-holds-no-rule-logic`. The other seven are
  24–32-line shims over `src/dev_playbook/`. Their tests split the
  same way: 212 subprocess tests over the five, package tests over the
  rest.
- Dispatch is twelve subprocesses from `dev_playbook.playbook_lint`,
  each a `uv run --script` start, each running its own `git ls-files`
  and parsing the same markdown again. Rule ids are string constants
  in each source; `verifier-table` learns them by spawning every
  detector with `--list-rules`, and `tests/test_rule_registry.py`
  guards the hand-kept tuples against the emit sites by parsing the
  source.
- The hook is `language: script`: pre-commit builds no environment,
  so `scripts/playbook-lint` bootstraps itself through its
  `uv run --script` shebang and a `sys.path` insert of `src/`.
- Four layers name the same rules, and no two of them agree:

  | Layer | What it is | Where it lives |
  | --- | --- | --- |
  | Family | the directory, and the id's namespace | 12 of them |
  | Standard | the file, and the population a rule binds | 31 rule-carrying files |
  | Detector | the script that decides the rule | 18 addresses over 98 rules; 119 rules have none |
  | Gate | when the detector runs | commit, push, ci, or on-demand |

  Family and Standard part company in 6 of the 12 families:
  `knowledge-organization.` spans 8 files, `doc-type.` 5, `tracking.`
  4, `build.` 3, `harness.` and `standard.` 2 each. A detector crosses
  both — `repo-lint` decides 20 rules from 3 families and 6 files,
  `harness-files-lint` 12 rules from 2 families. The gate is a fourth
  cut again: `workspace-lint` holds 14 rules and runs at no gate.

## Terms

- **Address** — the right-hand side of a row in
  `standards/verifiers.yaml`: the name of the one check that decides
  a rule, and the key `standards/boundaries.yaml` joins on to say
  which gates run it. Today a first-party script by path, a pinned
  pre-commit hook id, or a `pyproject.toml` dependency plus its
  subcommand. What it is on exit is the design's.
- **Detector**, **verifier table**, **boundary table** — per
  [Detectors](/standards/standard/detectors.md), until the rewrite
  restates them.

## Open

- **The hook mechanism.** Proposed, not ruled: the suite is one
  console script under `[project.scripts]`, and the published hook is
  `language: python` with that script as its entry, so pre-commit
  installs the package into a venv it caches once per pin, as ruff
  and shellcheck-py reach the canonical config. No detector file
  under `scripts/`, no `sys.path` insert, and no shim or hosting rule
  in Detectors. The script's name is the design's; `playbook check`
  is the placeholder.
- **The registry and the model.** How a check is declared and keyed,
  and what parsed-repo object it reads.
- **The id schema.** An id is `<family>.<slug>`, the directory and the
  heading's slug, so the namespace is coarser than the population it
  binds. `<standard>.<slug>` was proposed and measured, and the
  evidence is against it: it moves 210 of the 217 ids, only 7 match
  their file; it drops the word that carries the meaning
  (`build.ciyml-byte-identical-to-canonical` becomes `canonical.ciyml-…`);
  and it lands `prose/conventions.md`, `shell/conventions.md` and
  `testing/conventions.md` on one `conventions.` namespace. There are
  no slug collisions, so nothing is broken. The design rules on the
  schema, leaving it alone included, with the layer table in front of
  it, because what names a group of rules and what module owns them
  are the same question.
- **A check that keys on something that is not an id.** `okf-lint`
  finds the type registry by that heading's slug, so a rename of the
  heading lands in the detector; the slug is a named constant since
  step 11 wave 5. The design gives every such coupling one named
  place.
- **The two tables under one process.** `verifier-table` and
  `boundary-table` are detectors today, with `--write`. Where every
  check is in one process, whether they stay separate addresses or
  become subcommands, and what the boundary table still records when
  every in-process check runs at every gate.

## Planned

- **The design.** Rule on the open questions in order — the hook
  mechanism, the registry and model, the id schema, the two tables —
  then triage the 217 rules family by family with the greenfield eye,
  producing the exit list: keep, rewrite, delete. The exit list is
  the specification the package is written to.
- **The measurement.** Time `playbook-lint` on this repo and on a
  consumer, and the test suite, before any code moves.
- **The rewrite.** The package, module by module, against the exit
  list; the console script; the two tables regenerated; the detector
  files under `scripts/` deleted.
- **The tests.** One test per rule id in `tests/dev_playbook/`, a
  meta-test that every registered id has one and names a heading
  under `standards/`, the 212 subprocess tests retired once the
  package tests cover them, `tests/test_rule_registry.py` deleted with
  the tuples it guards.
- **The Standards and the docs.** `standards/standard/detectors.md`,
  `standards/distribution/channel.md`,
  `guides/writing-a-detector.md`, `scripts/README.md`, and the
  canonical `.pre-commit-config.yaml`, each rewritten to the state the
  repo is then in.

## Completed

Nothing yet.

## Acronyms

None.
