# scripts/ — index

The dev scripts the repo keeps for itself, with the logic behind them in
`src/dev_playbook/`. Start at [Scripts](/scripts/README.md).

- [Scripts](/scripts/README.md) — The local dev scripts, thin shims over the library code in src/dev_playbook/, and how the published playbook hook relates to them

`labelgen` regenerates the label table in
`standards/tracking/github/label-scheme.md`, rendered from `label_scheme.json`,
and fails on drift via `--check`.
