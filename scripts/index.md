# scripts/ — index

Everything the repo can run: the hook entry points it publishes to consumer
repos and the dev scripts it keeps for itself, with the logic behind both in
`src/dev_playbook/`. Start at [Scripts](/scripts/README.md).

- [Scripts](/scripts/README.md) — The executable surface of published hook entry points and local dev scripts, with shared library code in src/dev_playbook/

`chaingen` regenerates `doc-types/runbook/chains.txt` — every runbook's
Reference chain — and fails on drift via `--check`. `cardgen` does the
same for `doc-types/standard-card/cards.txt` — every standard card's
cells as rows of `card, cell, pointer`.
