---
type: General-Sheet
title: Distribution
description: The triage of the distribution family's three deterministic rules — two kept, one deleted as a rule about dev-playbook's own manifest that a test covers
---

# Distribution

Three rules in one Standard, `standards/distribution/channel.md`,
triaged per
[Triage](/working-docs/doc-type-system/detector-rewrite/triage.md).
[Detector Fixes](/working-docs/doc-type-system/detector-rewrite/detector-fixes.md)
has no survey row for this family.

## channel.md

Kept as written, the check matching the sentence:
`a-publisher-dogfoods-its-manifest`, `the-manifest-validates`. Their
checks today:

- `a-publisher-dogfoods-its-manifest`,
  `standards/distribution/channel.md:31`. Today
  `check_dogfood_mirror`, `scripts/repo-lint:665`, runs when
  `.pre-commit-hooks.yaml` exists (`scripts/repo-lint:713`). It gives a
  finding for each published id that is not in a `repo: local` block.
  An absent `.pre-commit-config.yaml` counts as an empty block. The
  rule has members outside dev-playbook: `mission-control` publishes
  `ideas-lint` and `story-forge` publishes five hooks. All three
  publishers pass today. The rewrite reads both files through the
  model, not through the two line regexes at `scripts/repo-lint:676`
  and `scripts/repo-lint:624`. The mirror leg of `check_hook_surfaces`,
  `src/dev_playbook/standards_lint.py:559`, also finds a missing
  `scripts/` id, under `standard.every-detector-is-reachable-and-listed`.
  That leg is for the `standard` family's triage to decide.
- `the-manifest-validates`, `standards/distribution/channel.md:38`.
  Today `playbook_lint.main` adds the step only when
  `.pre-commit-hooks.yaml` exists (`src/dev_playbook/playbook_lint.py:120`)
  and runs `uvx pre-commit validate-manifest`
  (`src/dev_playbook/playbook_lint.py:81`). `DEPENDENCY_RULES`,
  `src/dev_playbook/verifier_table.py:85`, gives it its address. Per the
  Decided ruling "Rules a tool decides", the registry lists it under
  pre-commit's manifest validator and asks for no test. The check keeps
  the same condition: it runs only where the manifest exists.

The remaining rule:

- **`one-published-hook-id`**, `standards/distribution/channel.md:20`.
  Delete: its member is dev-playbook's own checking code, which a test
  covers. Only dev-playbook is "the hook repository". The other two
  publishers publish their own ids, one and five, so the rule applies
  to no other governed repo. The Standard's `population`, "a governed
  repo's share", does not include it. No check exists today
  (`standards/verifiers.yaml:35` is `null`). The Why is decision record
  `docs/decisions/0012-one-published-hook.md`, which keeps it. A test
  in `tests/dev_playbook/` reads `.pre-commit-hooks.yaml` and asserts
  one hook with the id the rewrite publishes. The rewrite changes that
  entry to the `language: python` console script, so the test goes in
  with it.

## Escalations

None.

## New rules

None.

## Acronyms

None.
