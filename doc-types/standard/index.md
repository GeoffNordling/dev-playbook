---
okf_version: "0.1"
---

# doc-types/standard/ — index

The Standard doc-type: the object that is defined, audited, enforced,
and adopted, written across a card and its rulesets — its definition,
contract shape, encoding, and residual ledger. The two generated views
also live here: `cards.txt`, every card's cells, one row per pointer,
written and checked by `scripts/cardgen`; `standards.txt`, every
ruleset's population and rules, written and checked by `scripts/rulegen`.
The rules a card, a ruleset, and the catalog obey, and the detector
contract behind an Audit cell, stay with the Meta-Standard, under
[standards/standard/](/standards/standard/index.md).

- [Cells and Rulesets](/doc-types/standard/contract-shape.md) — Standard's contract shape — four cells, one per verb, each a pointer list, with the ruleset a Define pointer reaches, one population and its rules — in prose, one screen of pseudocode, and the relations every Standard collapses to
- [Cells and Rulesets Encoding](/doc-types/standard/encoding.md) — The layer below the shape — how a card's cells encode pointers for cardgen, how a ruleset writes its population, rules, and conditions for rulegen, where each file sits, how it is named, and the catalog that lists it
- [Standard](/doc-types/standard/definition.md) — What a standard is — a normative target that is defined, audited, enforced, and adopted — its four verbs, the two file kinds it is written across, the family it serves, how it is named and scoped, and where it lives
- [Standard Residual Ledger](/doc-types/standard/residual-ledger.md) — Standard's residual record — what four cells and a ruleset cannot express, one entry per card or ruleset that has one
