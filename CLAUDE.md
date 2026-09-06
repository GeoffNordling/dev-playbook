# dev-playbook

## Rules

- This is a meta repo: what is authored here governs the population of
  ~/workspace repos, most of which are not visible from this one. Write
  standards for that audience, never around this repo's internals.
- Before changing the published hooks (the `scripts/` entry points or
  `.pre-commit-hooks.yaml`), read
  [Distribution Channel](/standards/distribution/channel.md) — consumer repos pin a
  `rev` and need a bump after hook changes.
