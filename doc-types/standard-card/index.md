---
okf_version: "0.1"
---

# doc-types/standard-card/ — index

The Standard-Card doc-type. `cards.txt` also lives here: the generated view
of every card's cells, one row per pointer, written and checked by
`scripts/cardgen`. The obligation machinery — the detector contract and
drift — stays with the Meta-Standard card, under
[standards/standard/](/standards/standard/detectors.md).

- [Card Cells](/doc-types/standard-card/contract-shape.md) — The four cells — Standard-Card's contract shape — and the one relation every card collapses to, card × cell × pointer
- [Card Cells Encoding](/doc-types/standard-card/encoding.md) — The layer below the card — how a cell's bullets encode pointers for cardgen, where a card lives, how it is named, and the catalog that lists it
- [Standard-Card](/doc-types/standard-card/definition.md) — What a standard card is — the catalog record for one standard, named by the question it governs — its scope axis, and what a standard is not
- [Standard-Card Residual Ledger](/doc-types/standard-card/residual-ledger.md) — Standard-Card's residual record — what the four cells cannot express, one entry per card that has one
