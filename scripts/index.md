# scripts/ — index

Everything the repo can run: the hook entry points it publishes to consumer
repos and the dev scripts it keeps for itself, with the logic behind both in
`src/dev_playbook/`. Start at [Scripts](/scripts/README.md).

- [Scripts](/scripts/README.md) — The executable surface of published hook entry points and local dev scripts, with shared library code in src/dev_playbook/

`chaingen` regenerates `doc-types/runbook/chains.txt` — every runbook's
Reference chain — and fails on drift via `--check`. `cardgen` does the
same for `doc-types/standard/cards.txt` — every standard card's
cells as rows of `card, cell, pointer`. `rulegen` does the same for
`doc-types/standard/standards.txt` — every ruleset's population and
rules as two tables, `card, standard, population` and
`card, standard, rule, when`. `labelgen` does the same for the label table in
`standards/tracking/label-scheme.md`, rendered from `label_scheme.json`.
`verifier-table` does the same for `standards/verifiers.yaml`, the map from
every rule id to the check that decides it, and runs in the commit gate.
`boundary-table` does the same for `standards/boundaries.yaml`, the gates
that run each of those checks, read from the wiring itself.
