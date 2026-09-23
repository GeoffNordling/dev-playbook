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
The number is the one the rows above cite.

1. `the-script-holds-no-rule-logic`,
   `standards/standard/detectors.md:112`: deleted; consumers are no
   reason to keep a rule.
2. `git-runs-against-the-given-root`,
   `standards/standard/detectors.md:121`: deleted, the same reason.
3. `every-detector-is-reachable-and-listed`,
   `standards/standard/detectors.md:134`: deleted, the same reason.
4. `directory-index-opens-with-the-governing-sentence`,
   `standards/standard/tree.md:33`: built, the shape check, 12 of 12
   pass today. The body:

   > The first sentence after the H1 of each `standards/<name>/index.md`
   > has the form `<Name> governs <what> — <the things>`: the
   > Standard's name, the word `governs`, the question it governs, an
   > em dash, and the things its rules cover.

   Check: the opening sentence of each directory index matches
   `^\S.* governs \S.* — \S.*$`. The clause "the catalog row repeats
   that sentence" is dropped; `the-catalog-lists-every-directory`
   already requires it.

## New rules

None.

## Acronyms

None.
