---
type: General-Sheet
title: Check Rewrite
description: The root of the check rewrite strand — one pass over the checking system against the settled Standards, its principles and constraints, the state it left the tree in, the eight design rulings, and what remains
---

# Check Rewrite

The strand that rewrote the checking system: the Python checks,
the two tables they feed, and the hook that runs them. Speculative,
per
[Synthesis Working Root](/working-docs/doc-type-system/ROOT.md).
It depends on the doc-type system strand
([Doc-Type System](/working-docs/doc-type-system/doc-type-system/ROOT.md)),
whose step 11 settled the rules the checks answer to; no strand's
plan waits on it. Its input was a survey of the fourteen rules whose
check tested less than the sentence, consumed by the triage.

## Goal

One holistic pass over the checking system: refactor, reconsider,
redesign. The checks grew one at a time over months and were never
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
  per check; `--select` and `--ignore` by rule id with one config
  surface; one test per rule id with a meta-test over the registry.
- **Delete is the default.** Per the doc-type system's three working
  policies: no credit for rule count, and a check never keeps a
  rule alive.
- **Simple.** Fewer moving parts beats a clever one.
- **Plain rules.** On exit every rule body reads plain, direct, and
  concrete: it names the file, the value, and the comparison, so the
  user understands it on first reading. A body that does not is
  restated with its meaning held and its heading fixed, since the
  heading is the id and every heading is approved. Unclear wording is
  never a reason to delete. A proposal on screen states how it
  differs from today's sentence and from today's check.

## Constraints

- **At least as fast as the hooks today.** The number is measured
  before the design is judged against it.
- **Deterministic rules only.** Stochastic rules, a judge, and any
  runner for one are out. The trailer's kind is the only slot they
  keep.
- **No GitHub checks.** `scripts/workspace-lint` and everything it
  decides over `gh api` is untouched.
- **The null rows are in.** The 52 deterministic rules with no check
  gain one on this pass, or are deleted.
- **This repo only.** The design is judged in dev-playbook. A generic
  repo on this machine bumps its pin and refactors itself to meet the
  new checks, as it does today; nothing else about consumer repos
  is held.

## Current state

The rewrite is built and cut over at `b2f8815`; what follows is the
tree as it stands.

- One published hook, `playbook-check`, whose entry is the console
  script `playbook check` in `src/dev_playbook/check_cli.py`. It
  builds one `Repo` model from `git ls-files`, runs every registered
  check, then two steps that are not functions over the model:
  `loop_lint.main` and `pre-commit validate-manifest` where a manifest
  exists. `SKIP=workspace` leaves out the checks tagged as reading
  other repos under `~/workspace/`, and the skip is announced.
- Twelve check modules under `src/dev_playbook/checks/`, one per
  directory under `standards/`, with 107 check functions and 24
  registrations of a rule a tool decides. A consumer repo's own checks
  in `src/<package>/checks/` load beside them. The layer test holds
  both directions over a repo's own checks: every one is a
  deterministic heading under `standards/` with its test, and every
  deterministic heading is registered.
- One test per rule id under `tests/dev_playbook/checks/`; 763 tests
  in 7.6 s where 988 took 10.0 s.
- No check script is left under `scripts/`: the loop checks run as
  `playbook check`'s `loop_lint` step, kept for the loop workstream, and
  `workspace-lint` runs at no gate by ruling. The two tables and their
  scripts are gone.

## Terms

- **Rule**, **Verifier**, **Check**, **Judge**, **Finding**, **Gate**
  — per [Vocabulary](/CONTEXT.md#governance). Detector, lint, audit,
  and enforcement are retired.
- **Model** — the `Repo` object: the repo read once into memory, in
  parsed form, that every check reads.

## Decided

- **Hook mechanism, 2026-09-22.** A `language: python` hook whose
  entry is a console script under `[project.scripts]`; pre-commit
  builds and caches the venv once per pin. No check script under
  `scripts/`, no `sys.path` insert. The console script is
  `playbook check`.
- **Repo model, 2026-09-22.** One in-memory `Repo` object per run,
  built from one `git ls-files`, holding each file's parsed form:
  frontmatter, headings with slugs and line numbers, trailers, links,
  lines outside fences; Python files as `ast` trees. Every check
  reads the model and never touches disk or git. Plain dataclasses,
  no framework; tests build it through the same constructor.
- **Mirrored grouping, 2026-09-22.** One check module per
  `standards/` directory, named for it: `build/` ↔ `checks/build.py`.
  The id keeps `<family>.<slug>`, so module and namespace coincide.
  Where the tree cannot mirror, the tree is a candidate for change,
  and the exception is written down.
- **Registry, 2026-09-22.** `@check("<id>")` on each check function
  writes one dict entry, id to function; the runner stamps the id on
  every finding the function yields. The rule list and the meta-test
  read the dict. No hand-kept tuple, no `--list-rules`, no AST guard.
- **The two tables, 2026-09-22.** `verifiers.yaml`, `boundaries.yaml`,
  their two scripts, and the three rules of Checks that require them
  are deleted; no code read either file. The term address dissolves.
  - The user's view is `playbook checks`: id, module, environment tag,
    computed live, with `--family` and `--without` filters.
  - A machine dependency is a tag on the check, `@check(id, needs=WORKSPACE)`,
    for a check that reads sibling repos on this machine. CI sets
    `SKIP: workspace` in place of `SKIP: ref-lint`, and `playbook
    check` reads the tag from `SKIP`.
    Untagged checks run at every gate.
- **Data read out of a Standard, 2026-09-22.** Where a check consumes
  data a Standard's body holds, such as the type registry table
  under one heading of `document-types.md` or the canonical files
  under `standards/build/canonical/`, the path and heading are named
  constants in one module, `sources.py`. A test pins
  each constant to its document: the path exists, the heading is
  present. A check reads the section through the model, never by
  scanning for the heading itself.
- **Rules a tool decides, 2026-09-22.** A rule ruff, shellcheck,
  shfmt, or pre-commit's manifest validator decides is registered
  with the hook's name in place of a function: `playbook checks`
  lists it with that hook, and the meta-test asks no test of it.
  Every id in a Standard is in the registry, one way or the other.
- **The markdown parser, 2026-09-23.** The hand-rolled scanner in
  `md.py` stays, with one fix: a link whose text wraps across a line
  break is found, which today hides five targets from `ref-lint`. A
  spike by one Opus agent parsed all 254 tracked markdown files with
  `markdown-it-py` and got the same headings, trailers, frontmatter,
  and fenced lines, at 0.27 s against 0.03 s, two dependencies, and a
  private-attribute hook for link line numbers. Not an easy win. The
  parser sits behind one function, so the swap stays cheap.

## Open

None.

## Planned

- **Signal to noise in `ralph-setup`, before the merge to main.** The
  reading-chain review done by hand for this loop, where dropping
  `ROOT.md` and the triage method and trimming each report's
  Escalations halved what one iteration reads, becomes a step of the
  `ralph-setup` skill. After the plan is designed, the agent walks
  everything the plan tells an iteration to read, weighs each file
  as signal for that task or noise around it, and where the noise is
  a significant share, partners with the user to redesign the plan
  and refactor the documents until the iteration reads mostly signal.
- **The checkpoint fork checks quality, not just completion, before
  the merge to main.** At the Step 12a checkpoint the fork ticked every
  item as done and the gates green, and a read-only Opus review run
  beside it found four rules whose sentence and check disagreed, one
  check stricter than its sentence and three sentences silent on what
  the code reads. The fork verified that the work was done, not that it
  was right. The `ralph-checkpointer` agent definition under
  `dotfiles/dot-claude/agents/` gains a quality pass: for each unit the
  segment landed, the fork reads the specification and the result side
  by side and names one case the two would treat differently, or
  states there is none, before ticking the marker. This strand's copy
  of that pass was the Sentence equals code Guardrail of its plan: for
  each check function the segment adds or edits, the fork reads the
  rule's sentence and the function side by side and names one input
  the two would judge differently, or states there is none; a
  difference is a fix task that reduces the sentence to what the code
  tests, never one that grows the code. The case is one a repo writes
  today or a Standard names, never one constructed to break the code:
  at the Step 12c checkpoint the Opus review returned eight findings,
  frontmatter with no final newline and a two-character `==` underline
  among them, and the user ruled every one a hypothetical and the review
  a bug hunt. An agent asked for bugs finds bugs; the pass asks for
  use cases that break, or will soon.
- **A skill that turns repeated fixes into predicates.** Invoked in
  any session, it reads the session's history and finds the fixes that
  repeat: the user sees stale state, asks, and the agent brings that
  state back into line by hand. Each such fix is a sign of a missing
  predicate. For each one, the skill proposes a rule in a Standard,
  existing or new, that states the more abstract property, so that a
  check stops the problem at a gate, or at least an agent can bring the
  state back into line with the rule with no user in the loop. Example
  from this strand: "detector" was swept out of 68 files by hand; the
  rule "no authored document uses a word `CONTEXT.md` lists under
  _Avoid_" would have caught every one at commit. Fixes with the user
  in the loop, all day, do not scale; predicates do.

## Completed

- **Scripts under ruff, 2026-09-23.** Ruff picks a file's language by
  its extension, so it never opened the extensionless uv scripts under
  `scripts/`. The root cause was that an extensionless file does not
  say its language, so a new rule states it:
  [scripts/ holds only scripts](/standards/build/skeleton.md#scripts-holds-only-scripts),
  where a name with no dot is a uv Python script and every other file
  is `.py`, `.sh`, or `.md`. On that rule the canonical
  `pyproject.toml` pins `extend-include = ["scripts/*"]` less `.sh`
  and `.md`, and the two canonical ruff hooks run over the repo by
  that config, `pass_filenames: false` and `always_run: true`, since
  pre-commit hands them only files it tags as Python and CI runs only
  pre-commit. The scripts stay extensionless, as commands run by name.
  Eight docstrings and one reformat made them clean.
  `scripts/loop-lint` was deleted, since `playbook check` calls its
  module directly. `bayes-lab-sim`'s `scripts/vulcan_system1.png`
  breaks the rule, to be deleted there.

- **A consumer's checks, 2026-09-23.** A consumer repo writes its
  checks where dev-playbook keeps its own, `src/<package>/checks/` and
  `tests/<package>/checks/`, importing `@check`, `Finding`, and `Repo`
  from `dev_playbook`; the `playbook-check` hook it already pins loads
  them beside dev-playbook's, so it publishes no hook of its own. The
  meta-test's directions became the layer test, which `playbook check`
  runs over the repo's own checks and exits 2 on. Chosen over each
  consumer copying the registry, model, and command, since every repo
  runs dev-playbook's checks and only adds its own, as with Standards;
  one layer of consumers, no deeper. The wheel item was dropped:
  pre-commit builds from a clone at the pinned rev, which holds no
  gitignored directory, and that wheel is 189 KB in 101 files; the
  108 MB came only from building this working checkout.

- **The terms and the docs, 2026-09-23.** One vocabulary from the
  Standard pseudocode: rule, verifier, check, judge, finding, gate, in
  `CONTEXT.md`; detector, lint, audit, and enforcement retired
  everywhere but proper names and Decision Records. Detectors became
  [Checks](/standards/standard/checks.md), the guide
  [Writing a Check](/guides/writing-a-check.md) with the shape of a
  consumer's own checks, Loop's `check` became `verify`, and this
  strand became the check rewrite.

- **The rewrite and the tests, 2026-09-23.** Four phases, `8877f74` to
  `b2f8815`, the state under Current state. Phase 1, by hand: the
  scaffold, `model.py`, `check_registry.py`, `check_cli.py`,
  `sources.py`, the hook in the manifest and both configs, the
  meta-test; one word, check, at every level. Phase 2, by hand: the
  two tables, their scripts, modules, tests, and the six table rules
  of Checks deleted. Phase 3, a Ralph loop of twelve family steps
  and six rework steps, twelve checkpoints, each released by a fork
  and the last four reviewed beside it by a read-only Opus agent; nine
  scripts retired; ten rule sentences reduced to their checks under
  the Sentence equals code Guardrail, added when the Step 12a review
  found four such differences and bounded to inputs a repo writes
  today when the Step 12c review returned eight hypotheticals. Phase 4,
  by hand: the cut over, `playbook-lint` and its module, tests, and
  `tests/test_rule_registry.py` deleted, `SKIP: workspace` in the
  canonical CI and the secondary machine, the one-published-hook test
  in. The stopwatch: `pytest` under its baseline, `pre-commit` 0.16 s
  over, ruled not worth closing. The loop's plan, progress log,
  prompts, and the twelve triage and twelve rewrite reports were
  deleted at certification.
- **The measurement, 2026-09-23.** Wall time on this repo at
  `66b1e6b`, uv cache warm, before any code moves: `playbook-lint .`
  0.47 s, the median of three runs; `pre-commit run --all-files`
  0.89 s; `pytest` 10.0 s over 988 tests on 12 workers. The rewrite
  is judged against these.
- **The triage, 2026-09-23.** The 150 deterministic rules family by
  family, each kept, rewritten, or deleted: `build` and `python` by
  hand, the other ten families by one Opus agent each, the agents' 27
  escalations ruled by the general rulings now under the
  Standards-and-docs Planned item. The twelve reports were the
  specification the package was written to.
- **The plan, 2026-09-23.** The parser ruled and the plan written:
  four phases, the family order, the old script each family retires,
  and the checkpoint guardrails.
- **The design, 2026-09-22.** Six rulings in one session, recorded
  under Decided: hook mechanism, repo model, mirrored grouping,
  registry, the two tables, data read out of a Standard. The
  markdown parser was left open, and ruled the day after.

## Acronyms

None.
