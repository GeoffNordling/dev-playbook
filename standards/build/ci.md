---
type: Standard
title: Thin CI
description: Thin CI — the byte-identical workflow that runs exactly the hook suite on every push and PR
---

# Thin CI

Every repo carries the identical workflow, byte-for-byte the canonical
[ci.yml](/standards/build/canonical/ci.yml): one job, one real step —
`pre-commit run --all-files` with `SKIP: ref-check` — on every push and PR
to `main`.

`SKIP: ref-check` because `ref-check` validates cross-repo Citations
(`~/workspace/<repo>/…`), and a CI runner checks out only the one repo, so
those citations can never resolve there. Local pre-commit remains the strict
reference gate. `okf-lint` runs in CI — everything it checks is in-repo.

## Tests run locally, not in CI

CI runs the hook suite and nothing else. Two hard reasons tests stay local:
this workspace is local-first (no headless cloud agents, ever), and test
suites depend on dev-playbook as a local path dependency that does not exist
on a cloud runner. The pre-push-stage hook does not fire under
`pre-commit run`, so CI stays test-free automatically — nothing to
configure, nothing to drift.
