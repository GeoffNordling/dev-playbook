---
type: General-Sheet
title: Standard
description: The rewrite of the standard family's eight deterministic rules left after phase 2 — five checks over the model, four restated and one gaining a check, three deleted per their escalations, two Standards edited to the triage, and nothing retired
---

# Standard

The step built `src/dev_playbook/checks/standard.py` and
`tests/dev_playbook/checks/test_standard.py` from
[the standard triage](/working-docs/doc-type-system/detector-rewrite/triage/standard.md).
The six table rules the triage deletes by the two-tables ruling left
`standards/standard/detectors.md` in phase 2, so this step found eight
of the fourteen. `scripts/standards-lint` still runs
`check_directory_layout`, `check_catalog_order`, `check_hook_surfaces`,
and `check_shadows_upstream`, and still emits the deleted
`standard.every-detector-is-reachable-and-listed`; it retires in
Step 10. A repo is dev-playbook, for the catalog's lead slot, the
shadow rule, and the canonical compare, where it tracks
`standards/build/canonical/.pre-commit-config.yaml`, the probe
`standards-lint` used.

## Built

- `standard.every-subdirectory-a-standard-directory`: function
  `every_subdirectory_a_standard_directory`, ported from
  `check_directory_layout`. The body in `standards/standard/tree.md`
  is the triage blockquote. The `population` half stays with
  `standards-lint` for the doc-type family.
- `standard.directory-index-opens-with-the-governing-sentence`:
  function `opens_with_the_governing_sentence`, gaining a check per
  escalation 4. The body in `tree.md` is the ruling's blockquote. The
  first sentence after the H1 of each `standards/<name>/index.md`
  matches `^\S.* governs \S.* — \S.*$`; 12 of 12 pass.
- `standard.the-catalog-lists-every-directory`: function
  `the_catalog_lists_every_directory`, ported from
  `check_catalog_order` with membership added. The body in `tree.md`
  is the triage blockquote. One finding per stray entry and per
  unlisted directory index; the order is judged only when the listed
  set is right; an entry's wording is judged against its index's first
  sentence, and an index with none is the governing-sentence rule's
  finding.
- `standard.no-shadowing`: function `no_shadowing`, ported from
  `check_shadows_upstream`. The body in `tree.md` is the triage
  blockquote. The upstream names ship as
  `sources.STANDARD_DIRECTORIES`, pinned to `standards/` by a new test
  in `tests/dev_playbook/test_sources.py`.
- `standard.offered-by-the-canonical-template`: function
  `offered_by_the_canonical_template`, ported from the canonical leg
  of `check_hook_surfaces`. The body in
  `standards/standard/detectors.md` is the triage blockquote. Both sets
  are `{playbook-lint, playbook-check}` today, not `{playbook-lint}`
  as the triage says.

`detectors.md`'s `description` and its row in
`standards/standard/index.md` now name what the file holds: read-only,
the machine-state skip, and the canonical template's offer.

## Deleted

- `standard.the-script-holds-no-rule-logic`, escalation 1.
- `standard.git-runs-against-the-given-root`, escalation 2, with its
  Why. In `guides/consuming.md` step 2, the sentence that linked it
  was dropped.
- `standard.every-detector-is-reachable-and-listed`, escalation 3. In
  `guides/consuming.md` step 3, the parenthetical link was dropped.

The condition heading `A first-party detector` keeps
`Offered by the canonical template`, so it stays.

## Retired

None.

## Set aside

None.

## Measured

- `uv run playbook check .`: 0.41 s, 46 checks over 460 files, zero
  findings.
- `scripts/playbook-lint .`: 0.21 s, clean.

## Acronyms

None.
