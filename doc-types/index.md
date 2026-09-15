---
okf_version: "0.1"
---

# doc-types/ — index

The documentation type system: what a doc-type is, this repo's
instantiation, and one directory per built doc-type.

- [Doc-Type](/doc-types/doc-type.md) — The doc-type kind — operations plus a composition rule, fixing a contract shape — and the doc-type build loop that produces one from a documentation family
- [Doc-Type System](/doc-types/doc-type-system.md) — This repo's doc-type instantiation — the registry rulings, the roster of built doc-types, and the import surface for consumer repos

## Directories

- [loop/](/doc-types/loop/index.md) — The Loop doc-type — definition, contract shape, encoding, and residual ledger for the documents that drive a state toward a target state
- [runbook/](/doc-types/runbook/index.md) — The Runbook doc-type — definition, contract shape, encoding, and residual ledger for the repo's invocable commands
- [standard/](/doc-types/standard/index.md) — The Standard doc-type — definition, contract shape, encoding, the two generated views, and residual ledger for the cards and rulesets under standards/
