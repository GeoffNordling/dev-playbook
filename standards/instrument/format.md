---
type: Standard
title: Instruments and Instrument Specs
description: What an instrument is and the Instrument Spec contract every instrument carries
---

# Instruments and Instrument Specs

An **instrument** is a purpose-built device: an artifact format together
with the tooling that produces or checks it. Where a standard governs a
question a repository must answer, an instrument *is* an answer — a device
that standards, skills, and rituals employ.

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

## Employed by

Every Instrument Spec carries an **`## Employed by`** section naming the
standard, skill, or ritual that demands its readings. An instrument is an
answer only because something asks the question; the section records who
asks, so an orphaned instrument — one no live consumer names — reads as
orphaned rather than indistinguishable from a working device.

Reading cadence belongs to the consumer, never to this standard. On demand is
the device's contract — an instrument is regenerated when someone asks for a
fresh reading (see Readings below), and no instrument is bound to the weekly
loop by this standard. A ritual that wants its readings refreshed on a
schedule states that cadence in the ritual's own doc, and the Employed-by
section points at that ritual; the cadence lives there, not here.

## Executors

The tooling behind a spec may be deterministic code
(the file graph — `scripts/file-graph`), an agent executing the spec
directly (the datasheet), or a mix. The spec states which, and what the
executor needs: inputs, scope, and where the artifact lands.

## Readings

An instrument's artifacts land under `readings/<instrument>/<subject>.<ext>`
— one subdirectory per instrument, named for its spec (`instruments/<X>.md`
⇒ `readings/<X>/`). Readings are regenerated **manually, on demand** — by
re-running the instrument when someone wants a fresh one, never by
hand-editing the output and never on an automatic sync. A committed reading
may lag the code or repository it describes until it is next regenerated;
that staleness is expected, not a defect to chase. On demand means a human
asks for a fresh reading. A change that stales a committed reading — moved
files, renamed paths, refactors — is not a demand: exclude `readings/`
from reference sweeps and leave the reading lagging. Readings carry no OKF
frontmatter (they are outputs, not concept docs). A repository that consumes
an instrument grows only a `readings/` directory; the spec and its tooling
stay in dev-playbook.
