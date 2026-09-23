---
type: General-Sheet
title: Distribution
description: The rewrite of the distribution family's three deterministic rules — one check over the model, one registered to the validate-manifest step, one deleted as a rule about dev-playbook's own manifest, one Standard edited to the triage, and nothing retired
---

# Distribution

The step built `src/dev_playbook/checks/distribution.py` and
`tests/dev_playbook/checks/test_distribution.py` from
[the distribution triage](/working-docs/doc-type-system/detector-rewrite/triage/distribution.md).
`scripts/repo-lint` still runs its `check_dogfood_mirror`; it retires
with `repo-lint` in Step 11.

## Built

- `distribution.a-publisher-dogfoods-its-manifest`: function
  `dogfoods_its_manifest`, kept as written. It reads
  `.pre-commit-hooks.yaml` and `.pre-commit-config.yaml` as YAML
  through the model, in place of the two line regexes in
  `scripts/repo-lint`. It runs only where the manifest exists; an
  absent config counts as an empty `repo: local` block. dev-playbook
  publishes two ids today, `playbook-lint` and `playbook-check`, and
  its local block lists both: 0 findings.
- `distribution.the-manifest-validates`: hook `validate-manifest`, the
  step `playbook-lint` runs with `uvx pre-commit validate-manifest`
  only where the manifest exists. Kept as written.

## Deleted

- `distribution.one-published-hook-id`: heading, body, trailer, and
  Why removed from `standards/distribution/channel.md`. No link
  pointed at the heading. Its Why stays in decision record
  `docs/decisions/0012-one-published-hook.md`. The Standard's
  `description`, the intro and row in `standards/distribution/index.md`,
  and the row in `standards/index.md` no longer name the published hook
  id. The test the triage names, one hook with the id the rewrite
  publishes, is not added here: the manifest publishes two ids until
  the cutover changes the entry.

## Retired

None.

## Set aside

None.

## Measured

- `uv run playbook check .`: 0.39 s, 17 checks over 451 files, zero
  findings.
- `scripts/playbook-lint .`: 0.24 s, clean.

## Acronyms

None.
