---
type: General-Sheet
title: Standard
description: The triage of the standard family's fourteen deterministic rules — none kept as written, four restated plain, six table rules deleted under the two-tables ruling, and four escalated
---

# Standard

Fourteen deterministic rules over two Standards under
`standards/standard/`, per
[Triage](/working-docs/doc-type-system/detector-rewrite/triage.md).
Two stochastic rules are skipped: `read-only-without-a-write-flag`
and `a-skip-is-machine-state`.

## detectors.md

Kept as written: none.

The six rules below are the verifier-table and boundary-table rules.
The two-tables ruling in
[Decided](/working-docs/doc-type-system/detector-rewrite/ROOT.md#decided)
deletes both tables, their two scripts, and "the three Detectors
rules that require them". Six deterministic rules have a table file,
a table row, or an address as their member, not three. This report
reads the ruling as all six: the two H2 rules require a table file,
and each of the four H3 rules under them states a property of a
table row or an address, which the ruling dissolves. Each row also
gives a reason of its own, so the verdict holds if the ruling meant
only three.

- **`a-declaring-repo-carries-the-generated-verifier-table`**,
  `standards/standard/detectors.md:35`. Delete, by the two-tables
  ruling: `standards/verifiers.yaml` is deleted. Today's check is
  `verifier_table.audit`, `src/dev_playbook/verifier_table.py:424`.
- **`an-emitted-id-is-a-rule-heading`**,
  `standards/standard/detectors.md:50`. Delete, by the two-tables
  ruling. Reason of its own: the member is dev-playbook's own checking
  code. What survives, that every registered id names a deterministic
  heading and no id is registered twice, is the registry meta-test in
  Planned. Today's check is `verifier_table.derive`,
  `src/dev_playbook/verifier_table.py:317`.
- **`an-address-exists`**, `standards/standard/detectors.md:59`.
  Delete, by the two-tables ruling. Reason of its own: the term
  address dissolves. A rule a tool decides is registered with the
  hook's name, and the meta-test covers that name. Today's check is
  `verifier_table.audit`, `src/dev_playbook/verifier_table.py:424`.
- **`a-consumer-adds-only-its-own-rules`**,
  `standards/standard/detectors.md:67`. Delete, by the two-tables
  ruling. Reason of its own: with no table, a consumer has no rows to
  add, so the rule binds nothing. Today's check is
  `verifier_table.audit`, `src/dev_playbook/verifier_table.py:424`.
- **`the-boundary-table-generated-from-the-wiring`**,
  `standards/standard/detectors.md:74`. Delete, by the two-tables
  ruling: `standards/boundaries.yaml` is deleted. The weak-check row
  in
  [Detector Fixes](/working-docs/doc-type-system/detector-rewrite/detector-fixes.md)
  closes with it. Today's check is `boundary_table.audit`,
  `src/dev_playbook/boundary_table.py:331`.
- **`every-address-runs-somewhere`**,
  `standards/standard/detectors.md:94`. Delete, by the two-tables
  ruling. Reason of its own: addresses dissolve, and an untagged check
  runs at every gate, so the rule binds nothing. Today's check is
  `boundary_table.audit`, `src/dev_playbook/boundary_table.py:331`,
  over `addresses`, `:131`.
- **`the-script-holds-no-rule-logic`**,
  `standards/standard/detectors.md:112`. Escalated, item 1. Proposed
  delete.
- **`git-runs-against-the-given-root`**,
  `standards/standard/detectors.md:121`. Escalated, item 2. Proposed
  delete.
- **`every-detector-is-reachable-and-listed`**,
  `standards/standard/detectors.md:134`. Escalated, item 3. Proposed
  delete.
- **`offered-by-the-canonical-template`**,
  `standards/standard/detectors.md:144`. Rewrite, `wording only`.

  > The hook ids in the dev-playbook `repo:` block of
  > `standards/build/canonical/.pre-commit-config.yaml` are the same
  > set as the hook ids in `.pre-commit-hooks.yaml`.

  Check: the canonical leg of `check_hook_surfaces`,
  `src/dev_playbook/standards_lint.py:567`, compares every manifest
  id (`_manifest_ids`, `:504`) with the pinned-block ids
  (`_canonical_dev_hook_ids`, `:467`) in both directions. It runs only
  where the canonical file exists (`_dev_playbook_mode`, `:207`). Set
  equality already implies the old first clause, that each published
  detector is a hook of the block. Today both sets are
  `{playbook-lint}`.

## tree.md

Kept as written: none.

- **`every-subdirectory-a-standard-directory`**,
  `standards/standard/tree.md:24`. Rewrite, `wording only`.

  > Every `.md` file under a directory in `standards/`, at any depth
  > and except a file named `index.md`, has `type: Standard`, and each
  > directory directly in `standards/` has at least one such file. The
  > only `.md` files directly in `standards/` are `README.md` and
  > `index.md`.

  Check: `check_directory_layout`, `src/dev_playbook/standards_lint.py:229`,
  decides all three clauses through `_flat_strays` (`:195`),
  `_members` (`:183`), and `_standard_dirs` (`:170`). The same
  function also emits `doc-type.the-frontmatter-names-the-population`,
  which belongs to the doc-type family.
- **`directory-index-opens-with-the-governing-sentence`**,
  `standards/standard/tree.md:33`. Escalated, item 4. Proposed
  rewrite, `meaning changed`, gaining a check.
- **`the-catalog-lists-every-directory`**,
  `standards/standard/tree.md:42`. Rewrite, `wording only`. The
  clause that names the detectors is dropped. It says where the rule
  is checked, not what the repo is, and "No Standard says where it
  runs" (`standards/standard/detectors.md:24`).

  > `standards/index.md` lists `README.md` first, then the `index.md`
  > of every directory directly in `standards/`, and nothing else. The
  > directories are in alphabetical order by name, except that in
  > dev-playbook `standard/` comes first. Each directory's entry has,
  > after its link, the first sentence of that directory's `index.md`
  > without its final period.

  Check: `check_catalog_order`, `src/dev_playbook/standards_lint.py:336`,
  decides "nothing else" (`:358`), the order (`:369`), and each row's
  wording against `_opening_sentence` (`:287`, compared at `:402`).
  It does not decide "every directory". Today okf-lint decides that,
  under `knowledge-organization.one-entry-per-concept-document-and-child-directory`.
  The new check adds membership: the listed directory indexes equal
  the set of `standards/*/index.md`.
- **`no-shadowing`**, `standards/standard/tree.md:54`. Rewrite,
  `wording only`. The clause that names standards-lint and the commit
  gate is dropped for the same reason as the catalog row.

  > In a repo other than dev-playbook, no directory directly in
  > `standards/` has the name of a directory directly in `standards/`
  > of the dev-playbook version the repo pins.

  Check: `check_shadows_upstream`, `src/dev_playbook/standards_lint.py:593`,
  reads the upstream names from `HOOK_REPO_ROOT` (`:67`), the pinned
  clone, and runs in consumer mode only (`:650`). On the rewrite the
  model holds only the audited repo, and a `language: python` hook
  runs from an installed package, not the clone's tree. So the
  upstream directory names must ship in the package, for example as
  a constant in `sources.py` that a test pins to `standards/`.

## Escalations

Ruled 2026-09-23 under the general rulings in
[Triage](/working-docs/doc-type-system/detector-rewrite/triage.md#rulings-that-calibrate-the-rest).
Items 1 to 3: deleted; consumers are no reason to keep a rule. Item
4: built, the shape check, 12 of 12 pass.

Items 1 to 3 share one question. The calibration ruling "a rule
about the checker itself is a test, not a rule" covers dev-playbook's
own checking code only. After the rewrite, dev-playbook has no
detector under `scripts/` (Hook mechanism, Decided). But two
consumer repos host their own first-party detectors and are bound
by these three rules today: `mission-control` wires `ideas-lint`,
and `story-forge` wires five, `interview-prep-lint`, `stories-lint`,
`role-postings-lint`, `unemployment-lint`, and `resume-lint`. Each
is a `scripts/` entry in both `.pre-commit-hooks.yaml` and the
`repo: local` block of `.pre-commit-config.yaml`. The question is
whether the Detectors Standard keeps governing a consumer's own
detector scripts once dev-playbook has none.

1. **`the-script-holds-no-rule-logic`**,
   `standards/standard/detectors.md:112`.
   - Means: a detector script under `scripts/` is only a launcher. It
     puts the repo's package on `sys.path`, imports one entry point,
     and calls it. All logic is in the package.
   - Proposal: delete. In dev-playbook the member stops existing on
     the rewrite. A consumer's detector is that repo's own checking
     code, which its own tests cover.
   - Alternative: keep it for consumers, restated with the statements
     a shim really has, `meaning changed`: "Apart from its shebang,
     inline metadata block, and docstring, a detector script under
     `scripts/` has only `import sys`, `from pathlib import Path`, one
     `sys.path.insert` of the repo's `src/`, one import from the
     repo's package, and one `if __name__ == "__main__":` block that
     calls the imported name."
   - Difference from today's sentence: delete removes the rule. The
     alternative names the five statements every shim has. Read
     literally, the current sentence fails every shim, because each
     shim also has `import sys`, `from pathlib import Path`, a
     docstring, and an `if __name__` guard. Example:
     `scripts/standards-lint`.
   - Difference from today's enforcement: none. The verifier row is
     `null` (`standards/verifiers.yaml:192`).
   - Measured: in dev-playbook, five scripts fail today, all removed
     by the rewrite: `scripts/okf-lint` 808 lines, `scripts/repo-lint`
     781, `scripts/harness-files-lint` 677, `scripts/ref-lint` 287,
     `scripts/python-lint` 182. In consumers,
     `mission-control/scripts/ideas-lint` fails (482 lines). The five
     `story-forge` scripts are 27 to 30 line shims, which pass the
     alternative.

2. **`git-runs-against-the-given-root`**,
   `standards/standard/detectors.md:121`.
   - Means: when a detector starts a `git` child process, it removes
     every variable that `git rev-parse --local-env-vars` lists from
     that process's environment. This stops an exported `GIT_DIR`
     from redirecting the child to another repo.
   - Proposal: delete. After the rewrite, dev-playbook's only git call
     is the model builder's one `git ls-files`. A test that builds
     the model under a foreign `GIT_DIR` covers it: dev-playbook's
     own checker, per the calibration ruling. A consumer's detector
     is that repo's own code.
   - Alternative: keep it for consumers, with an `ast` check that every
     `subprocess` call whose argv starts `"git"` passes an `env=`
     argument. This is a weaker test than the sentence, because the
     check cannot see what the `env` mapping contains. That gap is a
     `meaning changed` narrowing.
   - Difference from today's sentence: delete removes the rule, and
     the Why moves to the test's docstring.
   - Difference from today's enforcement: none. The verifier row is
     `null` (`standards/verifiers.yaml:186`). The practice lives in
     `gitrepo.no_git_env`, `src/dev_playbook/gitrepo.py:47`.
     `mission-control/scripts/ideas-lint:84` has its own copy.
   - Measured: no check exists, so no count of failing call sites.

3. **`every-detector-is-reachable-and-listed`**,
   `standards/standard/detectors.md:134`.
   - Means: some hook path runs every detector script: the
     `playbook-lint` roster, a `scripts/` hook in both
     `.pre-commit-config.yaml` and `.pre-commit-hooks.yaml`, or the
     ungated-audit list. Each detector also has a row in a table of
     `scripts/README.md` where that file exists.
   - Proposal: delete. After the rewrite, dev-playbook has no roster
     and no detector scripts, and the registry meta-test covers
     reachability of every check. For consumers, the manifest-to-local
     half is `distribution.a-publisher-dogfoods-its-manifest`
     (`standards/distribution/channel.md:31`).
   - Alternative: keep it for consumers, `meaning changed` because the
     roster and ungated-audit branches dissolve: "Every hook in the
     `repo: local` block of `.pre-commit-config.yaml` whose `entry`
     starts `scripts/` is also in `.pre-commit-hooks.yaml`, and it
     has a row in a table of `scripts/README.md` where that file
     exists."
   - Difference from today's sentence: delete removes the rule. The
     alternative drops the roster and ungated-audit branches.
   - Difference from today's enforcement: `check_hook_surfaces`,
     `src/dev_playbook/standards_lint.py:524`, checks less than the
     sentence. Its mirror leg (`:559`) compares the `scripts/`-entry
     ids of the manifest and the local block, and its README leg
     (`:582`) matches the roster, or the consumer's local detector
     hooks, against any backticked first cell of any table in
     `scripts/README.md` (`_readme_table_names`, `:490`). It never
     lists the detectors that `verifiers.yaml` names, so it does not
     flag a detector script that no hook reaches.
     `every-address-runs-somewhere` flags that case today.
   - Measured: both consumers pass today. `story-forge` has 5 of 5
     detectors mirrored and `mission-control` has 1 of 1. Neither
     repo has `scripts/README.md`, so the README leg does not apply
     to them.

4. **`directory-index-opens-with-the-governing-sentence`**,
   `standards/standard/tree.md:33`.
   - Means: the first sentence of each Standard directory's
     `index.md` names the Standard, the question it governs, and what
     its rules cover, in the pattern `<Name> governs <what> — <the
     things>`. The catalog row repeats that sentence.
   - Proposal: rewrite, `meaning changed`, gaining a check:

     > The first sentence after the H1 of each `standards/<name>/index.md`
     > has the form `<Name> governs <what> — <the things>`: the
     > Standard's name, the word `governs`, the question it governs, an
     > em dash, and the things its rules cover.

     Check: take `_opening_sentence`
     (`src/dev_playbook/standards_lint.py:287`) of each directory
     index and match `^\S.* governs \S.* — \S.*$`.
   - Difference from today's sentence: the clause "the catalog row
     repeats that sentence" is dropped because it restates
     `the-catalog-lists-every-directory`, which requires each row to
     have that sentence verbatim. This is not a cut at an "and", so
     the meaning changes for this rule alone. The two rules together
     still decide the same states. The check decides the shape only.
     Whether `<Name>` is the Standard's name and `<what>` is its
     question is not decidable: no file records a Standard's name.
     For example, `standards/testing/index.md` opens "Python Testing
     governs", and no title, directory name, or frontmatter field has
     "Python Testing".
   - Difference from today's enforcement: the verifier row is `null`
     (`standards/verifiers.yaml:182`), so the rule gains its first
     check.
   - Measured: 12 of 12 Standard directory indexes match the pattern
     today, and `standards_lint.audit` reports 0 findings, so every
     catalog row repeats its sentence.

## New rules

None.

## Acronyms

None.
