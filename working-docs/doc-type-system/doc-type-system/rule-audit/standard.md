---
type: General-Sheet
title: Standard Family Rule Audit
description: The rule audit over the standards/standard/ family — every rule's kind, detector coverage, repo state, and overlap, with escalations for what breaks or is weakly checked
---

# Standard Family Rule Audit

The `standards/standard/` family declares 21 rules across two Standards,
[Detectors](/standards/standard/detectors.md) (17) and
[The Standards Tree](/standards/standard/tree.md) (4). Two rules move from
deterministic to stochastic, `standard.read-only` and
`standard.an-absent-surface-is-clean`, whose predicates ask what a program
does at run time rather than what a file holds; none moves the other way.
Six rules break in this repo: `standard.read-only`, because
`scripts/verifier-table --write` and `scripts/boundary-table --write` write
two tracked files; `standard.thin-shims`, because five detector scripts hold
their rule logic in the script; `standard.the-hosting-pattern` and
`standard.offered-by-the-canonical-template`, because no detector is
published in `.pre-commit-hooks.yaml` or listed in the canonical template —
the one published hook is `playbook-lint`, which
`distribution.one-published-id` demands; `standard.a-first-party-detector`,
which is a condition written as an obligation and is false of the six
dependency addresses; and `standard.directory-layout`, which admits only
`README.md` and `index.md` as flat files while `standards/verifiers.yaml`
and `standards/boundaries.yaml` sit there. Four rules are weakly checked,
`standard.the-boundary-table`, `standard.the-hosting-pattern`,
`standard.offered-by-the-canonical-template`, and
`standard.directory-layout`. One rule is low value,
`standard.a-first-party-detector`. Ten rules have no check at all. Two rules
are unknown, `standard.a-consumer-adds-only-its-own-rules` and
`standard.no-shadowing`, because both fire in consumer mode only and no
consumer repo is visible from here. Three scripts decide the family:
`scripts/standards-lint`, `scripts/verifier-table`, and
`scripts/boundary-table`.

## Rules

| id | rule | kind | proposed | check | state | overlap | value | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `standard.read-only` | "A detector leaves everything git tracks as it found it." | deterministic | stochastic | none | breaks | none | high | Proving that arbitrary code never writes needs judgment. `verifier_table.py:449` and `boundary_table.py:345` write the two tables under `--write`. |
| `standard.an-absent-surface-is-clean` | "A detector whose surface is optional, a `skills/`, `standards/`, or `loops/` tree, exits 0 and reports no finding in a repo that has no such surface." | deterministic | stochastic | none | holds | none | high | Which surface is optional, and what a detector does where it is absent, both need judgment. `standards_lint.py:649` returns early; `loop_lint.py:31` and `scripts/README.md:77` state the same for the other two. |
| `standard.the-verifier-table` | "A repo that declares a rule under `standards/` carries `standards/verifiers.yaml`, byte-identical to what `scripts/verifier-table` writes: one row per declared rule id, sorted, each carrying the address of the one check that decides it or null." | deterministic | deterministic | full | holds | none | high | Test: the committed text equals a fresh render (`verifier_table.py:456`). 284 trailers under `standards/`, 284 rows in the file. |
| `standard.an-emitted-id-is-a-rule-heading` | "Every id a check claims, a first-party detector under `--list-rules` or a dependency in the generator's dependency map, is the id of a rule declared deterministic under `standards/`, and no two checks claim the same id." | deterministic | deterministic | full | holds | none | high | Test: each claimed id is in `declared_rules`, is `deterministic`, and is unclaimed (`verifier_table.py:359-390`). All three legs run. |
| `standard.an-address-exists` | "Every dependency address the table names resolves in the repo: a hook id of its `.pre-commit-config.yaml`, or a dependency its `pyproject.toml` declares, or `pre-commit` itself where that config file exists." | deterministic | deterministic | full | holds | none | high | Test: `address.split()[0]` is in hook ids, `pyproject` names, or `pre-commit` (`verifier_table.py:344-357`). `ruff-check`, `ruff-format`, `shellcheck`, `shfmt` are hook ids; `mypy` is `pyproject.toml:32`. |
| `standard.a-consumer-adds-only-its-own-rules` | "In a repo other than dev-playbook, no row of the table names a rule dev-playbook's shipped table carries; the two tables union at read time." | deterministic | deterministic | full | unknown | none | high | Test: `set(rows) & set(upstream)` in consumer mode (`verifier_table.py:392-401`). No consumer repo is visible from this one, so no member can be checked. |
| `standard.the-boundary-table` | "A repo that asks any check, dev-playbook or a consumer whose `.pre-commit-config.yaml` wires a `scripts/` hook, carries `standards/boundaries.yaml`, byte-identical to what `scripts/boundary-table` writes: one row per address the verifier table names, sorted, each carrying the gates that run it in a fixed order drawn from `commit`, the pre-commit stage at `git commit`; `push`, the pre-push stage at `git push`, which runs `make check`; `ci`, a workflow under `.github/workflows/`; and `on-demand`, no gate." | deterministic | deterministic | weak | holds | none | high | The code never reads `standards/verifiers.yaml`; it rebuilds the address set from the roster and the dependency map (`boundary_table.py:131-141`). |
| `standard.every-address-runs-somewhere` | "Every address the verifier table names runs at a gate or is a registered ungated audit, and no registered ungated audit runs at a gate." | deterministic | deterministic | full | holds | none | high | Test: both directions against `UNGATED_AUDITS` (`boundary_table.py:296-315`). Every row of `standards/boundaries.yaml` carries a gate; `scripts/workspace-lint` carries `on-demand`. |
| `standard.a-skip-is-machine-state` | "A detector is skipped at a gate only where its input is machine-local rather than held in the repository." | stochastic | stochastic | none | holds | none | high | Whether an input is machine-local is a judgment. The one skip is `SKIP: ref-lint` at `.github/workflows/ci.yml:16`; ref-lint resolves `~/workspace` Citations against sibling clones. |
| `standard.a-first-party-detector` | "The detector is a script the audited repo hosts at `scripts/<name>`." | deterministic | deterministic | none | breaks | none | low | A condition written as an obligation. False of the six dependency addresses the verifier table names, `mypy`, `ruff-check`, `ruff-format`, `shellcheck`, `shfmt`, `pre-commit validate-manifest`. |
| `standard.thin-shims` | "The script holds no rule logic of its own: it puts the host repo's package on the import path and calls that package's entry point." | deterministic | deterministic | none | breaks | none | high | Test: the file defines no function or class and calls one imported entry point. `scripts/okf-lint` (842 lines), `scripts/repo-lint` (801), `scripts/harness-files-lint` (668), `scripts/ref-lint` (287), `scripts/python-lint` (182) all define their own. |
| `standard.git-runs-against-the-given-root` | "A first-party detector that runs git addresses the repository it was given even when its environment carries an absolute `GIT_DIR` that names another repository." | deterministic | deterministic | none | holds | none | high | Test: every `subprocess` call whose argv starts with `git` passes `env=gitrepo.no_git_env()`. No detector script runs git itself; `gitrepo.py:82,106`, `md.py:340`, `pyast.py:67`, `workspace_lint.py:323,357` all scrub. |
| `standard.the-hosting-pattern` | "A first-party detector is published as a hook in its repo's `.pre-commit-hooks.yaml` and has a row in the validation table of `scripts/README.md` where the repo has that file." | deterministic | deterministic | weak | breaks | `distribution.a-publisher-dogfoods-its-manifest` | high | `.pre-commit-hooks.yaml:20` publishes `playbook-lint` alone, and `scripts/workspace-lint` has no validation-table row. The code tests neither; it compares two id sets and the roster's README rows. |
| `standard.offered-by-the-canonical-template` | "A first-party detector in the repo that carries `standards/build/canonical/` is a hook of that canonical `.pre-commit-config.yaml`'s pinned block." | deterministic | deterministic | weak | breaks | `distribution.one-published-id` | high | The pinned block lists `playbook-lint` alone (`standards/build/canonical/.pre-commit-config.yaml:3-6`). The code compares the manifest with that block and never asks about a detector. |
| `standard.list-rules` | "A first-party detector answers `--list-rules` by printing every rule id it can emit, one per line, and exiting 0." | deterministic | deterministic | none | holds | none | high | Test: the `--list-rules` branch calls `findings.print_rules` over the module's `RULES`, and every emission site names a member of it. All 13 detectors do. |
| `standard.finding-format` | "A finding is one line, `location:line: <rule id> message`: a colon after the location, single spaces, the location a repo-relative path, or the member's name where the member is not a file, and `:line` omitted for a finding on the whole member." | deterministic | deterministic | none | holds | none | high | Test: every finding line comes from `findings.render` (`findings.py:14`) and no detector formats one itself. All 13 import and call it. |
| `standard.exit-codes` | "A first-party detector exits 0 when clean, 1 when it has findings, and 2 when it cannot run." | deterministic | deterministic | none | holds | none | high | Test: the detector's `main` returns or exits 0, 1, and 2 on the three paths. All 13 carry an exit-2 path beside the 0/1 split. |
| `standard.directory-layout` | "Every immediate subdirectory of `standards/` is a Standard directory: it holds at least one file typed `Standard`, and every other `.md` file under it, `index.md` aside, is typed `Standard` or `Explanation`; the only flat files under `standards/` are `README.md` and `index.md`; standards-lint reports a departure." | deterministic | deterministic | weak | breaks | none | high | `standards/verifiers.yaml` and `standards/boundaries.yaml` are flat files the predicate does not admit. `_flat_strays` (`standards_lint.py:201-210`) filters to `.md`, so it cannot see them. |
| `standard.the-statement` | "Every Standard directory's `index.md` opens with one sentence, `<Name> governs <what> — <the things>`: the Standard's name, the question it governs, and the things its rules cover; the catalog row repeats that sentence." | deterministic | deterministic | none | holds | `standard.the-catalog` | high | Test: the sentence after the H1 matches `<Name> governs <what> — <the things>`. All 13 Standard-directory indexes do. `standard.the-catalog` already owns the repeat clause; the form is checked nowhere. |
| `standard.the-catalog` | "A repo carrying a `standards/` tree has a `standards/index.md` listing `README.md` first and then every directory, in dev-playbook the meta-standard's `standard/` next, the rest alphabetical by name, each row carrying its directory index's opening sentence verbatim less the period; standards-lint reports the order and a row's wording, and okf-lint the membership ([The listing](/standards/knowledge-organization/indexes.md#the-listing))." | deterministic | deterministic | full | holds | `knowledge-organization.the-listing` | high | Test: order, directory-only rows, and each row's wording (`standards_lint.py:342-418`). The catalog lists README, `standard/`, then 12 directories in name order, each row verbatim. Membership is the listing rule's, as the predicate says. |
| `standard.no-shadowing` | "A repo-scoped Standard directory's name is one no directory dev-playbook publishes under `standards/` carries; standards-lint reports the collision at the consumer's commit gate." | deterministic | deterministic | full | unknown | none | high | Test: local directory names against the pinned clone's (`standards_lint.py:599-625`). The leg is skipped in dev-playbook mode (`standards_lint.py:656`), and no consumer repo is visible from here. |

## Escalations

### `standard.read-only` — "A detector leaves everything git tracks as it found it."

The predicate is absolute: a detector changes nothing git tracks. Two
detectors do. `scripts/verifier-table --write` writes
`standards/verifiers.yaml` at `src/dev_playbook/verifier_table.py:449`, and
`scripts/boundary-table --write` writes `standards/boundaries.yaml` at
`src/dev_playbook/boundary_table.py:345`. Both files are tracked, and both
scripts are addresses the verifier table names, so both are members of this
Standard's population.

The repo knows about the split: a formatter has two modes, and `shfmt -d`
is a detector where `shfmt -w` is enforcement. The two table generators are the same shape: the default run
compares and prints findings, `--write` regenerates. The predicate carries
none of that, so it reads as false of the two scripts the meta-standard
itself defines.

Proposal: rewrite. The new sentence: "A detector leaves everything git
tracks as it found it, in the mode a gate runs it in; a second, explicitly
requested write mode, `shfmt -w` or `verifier-table --write`, is enforcement
and not a detector run." The repo's state is deliberate — a generator that
is also its own lint is the design the explanation argues for — and the
explanation already states the carve-out, so only the predicate is behind.

### `standard.the-boundary-table` — "A repo that asks any check, dev-playbook or a consumer whose `.pre-commit-config.yaml` wires a `scripts/` hook, carries `standards/boundaries.yaml`, byte-identical to what `scripts/boundary-table` writes: one row per address the verifier table names, sorted, each carrying the gates that run it in a fixed order drawn from `commit`, the pre-commit stage at `git commit`; `push`, the pre-push stage at `git push`, which runs `make check`; `ci`, a workflow under `.github/workflows/`; and `on-demand`, no gate."

The predicate says "one row per address the verifier table names". The code
never opens `standards/verifiers.yaml`. `addresses` at
`src/dev_playbook/boundary_table.py:131-141` rebuilds the set from
`playbook_lint.DETECTORS`, `playbook_lint.UNGATED_AUDITS`, and
`verifier_table.DEPENDENCY_RULES` — the same sources the verifier table
draws on, but read a second time rather than read back.

The two sets can differ. The verifier table names an address only where that
address claims a rule id the trailers declare deterministic
(`verifier_table.py:380-390`). A roster detector whose every claimed id is
rejected, or one that claims none, gets no address in
`standards/verifiers.yaml` but still gets a row in
`standards/boundaries.yaml`. Today no detector is in that state: all 13
`scripts/` addresses appear in both files, so the gap is latent.

### `standard.a-first-party-detector` — "The detector is a script the audited repo hosts at `scripts/<name>`."

The population is "a check the verifier table names, first-party at
`scripts/<name>` or a dependency by its address". Six of the 19 addresses in
`standards/verifiers.yaml` are dependencies: `mypy`, `ruff-check`,
`ruff-format`, `shellcheck`, `shfmt`, and `pre-commit validate-manifest`.
None is a script at `scripts/<name>`, so the predicate is false of nearly a
third of the population.

Read as a condition it is exact. The six rules below it — `thin-shims`,
`git-runs-against-the-given-root`, `the-hosting-pattern`,
`offered-by-the-canonical-template`, `list-rules`, `finding-format`,
`exit-codes` — each speak of "a first-party detector" or "the script", and
each is the subset this heading names.
[Population and Rules](/doc-types/standard/contract-shape.md) defines a
condition as "what must hold of a member for the rule to bind it, named as a
subset of the population", and
[Standard Conventions](/standards/doc-type/standard-conventions.md#the-rule-shape)
says a level-three heading sits only under a level-two heading that is a
condition. The trailer makes this heading a rule as well, which is what puts
it in the population it means to narrow.

Proposal: delete the trailer and leave the heading as the condition its
level-three rules already read it as. Nothing is lost: the sentence stays on
the page as the subset's definition, `scripts/verifier-table` stops carrying
a null row for it, and the seven rules under it keep the same subject. Two
other headings in the file, "The verifier table" and "The boundary table",
carry both a trailer and level-three rules; those two state real
obligations, so only this one is pure definition.

### `standard.thin-shims` — "The script holds no rule logic of its own: it puts the host repo's package on the import path and calls that package's entry point."

Eight of the 13 first-party detectors obey. `scripts/standards-lint` (29
lines) is the shape the predicate describes: a docstring, a `sys.path`
insert, `from dev_playbook.standards_lint import main`, and
`raise SystemExit(main())`.

Five do not. `scripts/okf-lint` is 842 lines, `scripts/repo-lint` 801,
`scripts/harness-files-lint` 668, `scripts/ref-lint` 287, and
`scripts/python-lint` 182. Each defines its own rule logic in the script:
`scripts/repo-lint:256` defines `check_precommit_config`,
`scripts/okf-lint:280` defines `check_registry`,
`scripts/harness-files-lint:163` defines `check_required_fields`,
`scripts/python-lint:94` defines `check_no_future`, and
`scripts/ref-lint:154` defines `scan_file`. None of the five has a module
under `src/dev_playbook/` to call.

`scripts/README.md:10` states the same thing the predicate does — "Each file
here is a thin shim over the library code in `src/dev_playbook/`" — so the
README is wrong about the repo in the same five places. The verifier row is
null, so nothing reports it.

Proposal: change the repo — move the five scripts' logic into
`src/dev_playbook/`, leaving each script the shape the other eight already
have. The repo plainly wants this: the predicate states it, `scripts/README.md`
states it as fact, `standards/modules/design.md` puts the logic behind an
importable interface, and eight of 13 detectors are already there, including
the three newest (`standards-lint`, `verifier-table`, `boundary-table`). The
five are the leftovers of an earlier shape, not a decision. The files that
change are `scripts/okf-lint`, `scripts/repo-lint`,
`scripts/harness-files-lint`, `scripts/ref-lint`, and `scripts/python-lint`,
each paired with a new module under `src/dev_playbook/` and its tests under
`tests/`. This is the expensive way out, so the cheaper alternative is worth
stating: narrow the predicate to the eight that already comply, which buys
nothing, since the rule then stops binding the five files it exists for.

### `standard.the-hosting-pattern` — "A first-party detector is published as a hook in its repo's `.pre-commit-hooks.yaml` and has a row in the validation table of `scripts/README.md` where the repo has that file."

The first clause is false of every member. `.pre-commit-hooks.yaml:20`
publishes exactly one hook, `playbook-lint`, and
`distribution.one-published-id` requires exactly that: "The hook
repository's `.pre-commit-hooks.yaml` publishes exactly one hook,
`playbook-lint`." `playbook-lint` is not itself a detector — the population
is "a check the verifier table names", and `standards/verifiers.yaml` names
`scripts/playbook-lint` nowhere. So no first-party detector is published in
the manifest, by design:
`src/dev_playbook/playbook_lint.py:40-44` states it, "Adding a detector here
IS enrolling it workspace-wide — there is no per-consumer step."

The second clause is false of one member. `scripts/workspace-lint` is an
address of `standards/verifiers.yaml`, so it is a first-party detector, and
its only `scripts/README.md` row is in the Utility scripts table at line
131, not the validation table at lines 60-73.

The code tests neither clause. `check_hook_surfaces` at
`src/dev_playbook/standards_lint.py:530-593` runs two legs under this id: it
compares the manifest's `scripts/`-entry hook ids with the local block's in
both directions, and it requires a `scripts/README.md` table row for each
name in `roster`. The first leg is not the predicate — it is
`distribution.a-publisher-dogfoods-its-manifest`, "A repo whose root holds
`.pre-commit-hooks.yaml` lists every hook id that file publishes under a
`repo: local` block of its `.pre-commit-config.yaml`", which
`scripts/repo-lint` already decides at
`scripts/repo-lint:685` (`check_dogfood_mirror`). The second leg reads
`roster`, which defaults to `playbook_lint.DETECTORS` — the 12 gated
detectors — so `workspace-lint` is never asked for a row, and
`_readme_table_names` (`standards_lint.py:496-507`) collects backticked
cells from every table in the file, so it could not tell the validation
table from the utility one anyway.

Proposal: rewrite. The new sentence: "A first-party detector is reachable
from its repo's published hook — named in the `playbook-lint` roster, or
published as its own hook in `.pre-commit-hooks.yaml` — and has a row in the
validation table of `scripts/README.md` where the repo has that file." The
repo's single-hook channel is deliberate and
`distribution.one-published-id` states it, so the predicate, not the repo,
is what is behind. The rewrite also leaves `workspace-lint` outside the
roster and outside the validation table, which is correct — it is ungated —
so the second clause should say "validation table, or the utility table for
a registered ungated audit".

### `standard.offered-by-the-canonical-template` — "A first-party detector in the repo that carries `standards/build/canonical/` is a hook of that canonical `.pre-commit-config.yaml`'s pinned block."

`standards/build/canonical/.pre-commit-config.yaml:3-6` pins one
dev-playbook hook, `playbook-lint`. The other 12 first-party detectors are
not hooks of that block and never will be: the whole point of the aggregate
hook is that a consumer's config enumerates nothing
(`.pre-commit-hooks.yaml:11-14`). So the predicate is false of every member
except none, for the same reason `standard.the-hosting-pattern` is.

The code checks a different thing. `check_hook_surfaces` at
`src/dev_playbook/standards_lint.py:568-586` compares `manifest_all`, every
id `.pre-commit-hooks.yaml` publishes, with `_canonical_dev_hook_ids`, the
ids in the template's pinned dev-playbook block, in both directions. That is
a real check nothing else runs — a stale hook id in the template that a
consumer would copy fails here — but it says nothing about a detector.

Proposal: rewrite so the predicate states the compare the code runs and the
repo wants. The new sentence: "In the repo that carries
`standards/build/canonical/`, the canonical `.pre-commit-config.yaml`'s
pinned dev-playbook block offers exactly the hook ids
`.pre-commit-hooks.yaml` publishes." The repo's state is deliberate and
`distribution.one-published-id` fixes it, so the predicate is what must
move; the rewrite also moves the rule out of the "a first-party detector"
condition, which is not its subject.

### `standard.directory-layout` — "Every immediate subdirectory of `standards/` is a Standard directory: it holds at least one file typed `Standard`, and every other `.md` file under it, `index.md` aside, is typed `Standard` or `Explanation`; the only flat files under `standards/` are `README.md` and `index.md`; standards-lint reports a departure."

The first two clauses hold. All 13 tracked directories under `standards/`
hold at least one file typed `Standard`, and all 43 non-index Markdown files
under them are typed `Standard` or `Explanation`.

The third clause breaks. `standards/` holds four flat files:
`README.md`, `index.md`, `verifiers.yaml`, and `boundaries.yaml`. The last
two are not admitted, and they are not strays — this same Standard requires
them at exactly those paths.
[The verifier table](/standards/standard/detectors.md#the-verifier-table)
says a repo that declares a rule "carries `standards/verifiers.yaml`", and
[The boundary table](/standards/standard/detectors.md#the-boundary-table)
says the same of `standards/boundaries.yaml`.

The check cannot see the fault. `_flat_strays` at
`src/dev_playbook/standards_lint.py:201-210` keeps only paths whose second
part ends in `.md`, so a flat file of any other extension passes by
construction. A stray `standards/notes.txt` would go unreported for the same
reason.

One more thing the check cannot see: `standards/references/` exists on disk
as an empty directory and holds no tracked or untracked file, so
`_standard_dirs` (`standards_lint.py:176-186`) never sees it and the catalog
does not list it. It is a leftover of the doc-type refactor rather than a
rule fault, since the predicate's population is the repo's tree and git
carries no empty directory.

Proposal: rewrite the third clause to name the two tables. The new sentence
ends: "…; the only flat files under `standards/` are `README.md`,
`index.md`, `verifiers.yaml`, and `boundaries.yaml`; standards-lint reports
a departure." The repo's state is deliberate — the two tables are required
at those paths by two rules of this same family — and the rewrite lets
`_flat_strays` drop its `.md` filter and report any other flat file, which
is what the clause was for.

## Detectors

**`scripts/standards-lint`** (`src/dev_playbook/standards_lint.py`, 691
lines) decides five of this family's rules and one of `doc-type`'s. It walks
the `standards/` tree for flat strays and unadmitted member types
(`standard.directory-layout`, `doc-type.the-population`), checks the
catalog's order and each row's wording against the target index's opening
sentence (`standard.the-catalog`), compares the published manifest, the
local `repo: local` block, the canonical template's pinned block, and the
`scripts/README.md` tables (`standard.the-hosting-pattern`,
`standard.offered-by-the-canonical-template`), and in consumer mode flags a
local directory whose name reuses an upstream one
(`standard.no-shadowing`). It runs in two modes, keyed on the presence of
`standards/build/canonical/.pre-commit-config.yaml`, and returns no finding
at all where the repo carries neither a catalog nor a Standard directory.

**`scripts/verifier-table`** (`src/dev_playbook/verifier_table.py`, 511
lines) both writes `standards/verifiers.yaml` and is its lint. It reads
every rule trailer under `standards/`, asks each roster detector
`--list-rules` in a subprocess, adds the hand-kept `DEPENDENCY_RULES` map,
and renders one sorted row per declared id. It reports a claimed id no
trailer declares, a claimed id a trailer declares stochastic, an id two
checks both claim (`standard.an-emitted-id-is-a-rule-heading`), a dependency
address the repo's hooks and `pyproject.toml` do not carry
(`standard.an-address-exists`), a consumer row naming an upstream rule
(`standard.a-consumer-adds-only-its-own-rules`), and a committed file that
differs from a fresh render (`standard.the-verifier-table`). A trailer whose
id does not match its heading's slug is exit 2, not a finding.

**`scripts/boundary-table`** (`src/dev_playbook/boundary_table.py`, 402
lines) both writes `standards/boundaries.yaml` and is its lint. It derives
each address's gates from the wiring: the pre-commit config's hooks by
stage, with `playbook-lint` expanded to its roster and a `make` entry
expanded through `make -n`, and each workflow step's `run` lines less that
step's `SKIP`. It reports an address at no gate that is not a registered
ungated audit, a registered audit that a gate runs after all
(`standard.every-address-runs-somewhere`), and a committed file that differs
from a fresh render (`standard.the-boundary-table`). Its row set comes from
the roster and the dependency map rather than from
`standards/verifiers.yaml`.
