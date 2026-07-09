---
type: Standard Card
title: Instruments
description: Card for the instrument standard — how purpose-built devices are specified and kept conformant
---

# Instruments

Governs how purpose-built devices — artifact formats with tooling — are
specified and kept conformant.

## Define

- [instrument/format.md](/standards/instrument/format.md) — the contract:
  what an instrument is, the Instrument Spec, executors, readings

## Audit

- [okf-lint](/scripts/okf-lint) — every spec typed `Instrument Spec`, the
  [instruments catalog](/instruments/index.md) complete and fresh

## Enforce

- the canonical
  [.pre-commit-config.yaml](/standards/build/canonical/.pre-commit-config.yaml)
  — okf-lint in every repo's suite

## Adopt

- none
