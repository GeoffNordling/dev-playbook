---
type: Standard
title: Instruments and Instrument Specs
description: What an instrument is and the Instrument Spec contract every instrument carries
---

# Instruments and Instrument Specs

An **instrument** is a purpose-built device: an artifact format together
with the tooling that produces or checks it. Where a standard governs a
question a repository must answer, an instrument *is* an answer — a device
that standards, skills, and workflows employ.

## What makes a device an instrument

- **It defines an artifact format.** Invoking an instrument yields a
  concrete artifact with a prescribed form.
- **It carries a prescriptive contract.** The contract — the Instrument
  Spec — is the source of truth; implementations must satisfy it, and a
  reviewer rejects nonconforming output by citing the spec.
- **It is invoked, not adopted.** A caller points the instrument at a
  subject and receives the artifact. The caller chooses the scope; the
  instrument never decides its own.

## The Instrument Spec

Each instrument's contract is a document typed `Instrument Spec` under
`instruments/` — a single file, or a directory of single-concern documents
with an `index.md`. The spec is self-sufficient: an executor handed the
spec and the caller's inputs produces a conformant artifact with no other
instruction. [instruments/index.md](/instruments/index.md) is the catalog;
every instrument is listed there.

## Executors

The tooling behind a spec may be deterministic code
(the file graph — `scripts/file-graph`), an agent executing the spec
directly (the datasheet), or a mix. The spec states which, and what the
executor needs: inputs, scope, and where the artifact lands.
