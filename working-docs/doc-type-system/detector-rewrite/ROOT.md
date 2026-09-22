---
type: General-Sheet
title: Detector Rewrite
description: The root of the detector rewrite strand — one pass over the checking system against the settled Standards, its principles and constraints, the current state it starts from, the six design rulings, the one open question, and the worklist
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
- **Plain rules.** On exit every rule body reads plain, direct, and
  concrete: it names the file, the value, and the comparison, so the
  user understands it on first reading. A body that does not is
  restated with its meaning held and its heading fixed, since the
  heading is the id and every heading is approved. Unclear wording is
  never a reason to delete. A proposal on screen states how it
  differs from today's sentence and from today's enforcement.

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
  subcommand. Dissolves on exit: a rule's check is a function in a
  module.
- **Detector**, **verifier table**, **boundary table** — per
  [Detectors](/standards/standard/detectors.md), until the rewrite
  restates them.
- **Check** — one Python function that decides one rule, registered
  under that rule's id.
- **Model** — the `Repo` object: the repo read once into memory, in
  parsed form, that every check reads.

## Decided

- **Hook mechanism, 2026-09-22.** A `language: python` hook whose
  entry is a console script under `[project.scripts]`; pre-commit
  builds and caches the venv once per pin. No detector under
  `scripts/`, no `sys.path` insert. Placeholder name: `playbook check`.
- **Repo model, 2026-09-22.** One in-memory `Repo` object per run,
  built from one `git ls-files`, holding each file's parsed form:
  frontmatter, headings with slugs and line numbers, trailers, links,
  lines outside fences; Python files as `ast` trees. Every check
  reads the model and never touches disk or git. Plain dataclasses,
  no framework; tests build it through the same constructor. Whether
  markdown parsing stays hand-rolled or moves to a CommonMark library
  is open, below.
- **Mirrored grouping, 2026-09-22.** One check module per
  `standards/` directory, named for it: `build/` ↔ `checks/build.py`.
  The id keeps `<family>.<slug>`, so module and namespace coincide.
  Where the tree cannot mirror, the tree is a candidate for change,
  and the exception is written down.
- **Registry, 2026-09-22.** `@rule("<id>")` on each check function
  writes one dict entry, id to function; the runner stamps the id on
  every finding the function yields. The rule list and the meta-test
  read the dict. No hand-kept tuple, no `--list-rules`, no AST guard.
- **The two tables, 2026-09-22.** `verifiers.yaml`, `boundaries.yaml`,
  their two scripts, and the three Detectors rules that require them
  are deleted; no code read either file. The term address dissolves.
  - The user's view is `playbook rules`: id, module, environment tag,
    computed live, with `--family` and `--without` filters.
  - A boundary is a tag on the check, `@rule(id, needs=WORKSPACE)`,
    for a check that reads sibling repos on this machine. CI runs
    `playbook check --without workspace` in place of `SKIP: ref-lint`.
    Untagged checks run at every gate.
- **Data read out of a Standard, 2026-09-22.** Where a check consumes
  data a Standard's body holds, such as the type registry table
  under one heading of `document-types.md` or the canonical files
  under `standards/build/canonical/`, the path and heading are named
  constants in one module, placeholder `sources.py`. A test pins
  each constant to its document: the path exists, the heading is
  present. A check reads the section through the model, never by
  scanning for the heading itself.
- **Rules a tool decides, 2026-09-22.** A rule ruff, shellcheck,
  shfmt, or pre-commit's manifest validator decides is registered
  with the hook's name in place of a function: `playbook rules`
  lists it with that hook, and the meta-test asks no test of it.
  Every id in a Standard is in the registry, one way or the other.

## Open

- **The markdown parser.** `md.py` is a hand-rolled line scanner. A
  CommonMark library such as `markdown-it-py` gives a tested parse
  with line numbers. Decide on the rewrite, with the dependency cost.

## Planned

- **The triage.** The 150 deterministic rules family by family with
  the greenfield eye, each kept, rewritten, or deleted, the hard rows
  escalated and ruled on, in
  [Triage](/working-docs/doc-type-system/detector-rewrite/triage.md).
  `build` and `python` done by hand as the calibration sample; the
  other ten families by one Opus agent each, launched with
  [Triage Family Prompt](/working-docs/doc-type-system/detector-rewrite/prompts/triage-family.md).
  The exit list is the specification the package is written to.
- **The measurement.** Time `playbook-lint` on this repo and the
  test suite, before any code moves.
- **The rewrite.** The package, module by module, against the exit
  list; the console script; the markdown parser decided; the two
  tables, their scripts, and the detector files under `scripts/`
  deleted.
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

- **The design, 2026-09-22.** Six rulings in one session, recorded
  under Decided: hook mechanism, repo model, mirrored grouping,
  registry, the two tables, data read out of a Standard. The
  markdown parser is the one item left open, for the rewrite.

## Acronyms

None.
