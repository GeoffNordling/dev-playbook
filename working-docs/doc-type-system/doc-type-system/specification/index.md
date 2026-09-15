# working-docs/doc-type-system/doc-type-system/specification/ — index

The specification of the doc-type system: the general file every
doc-type satisfies, then one file per known doc-type with what it
alone satisfies. Start at
[Doc-Type Specification](/working-docs/doc-type-system/doc-type-system/specification/doc-type.md).

Ordering: the general specification, then one file per doc-type.

- [Doc-Type Specification](/working-docs/doc-type-system/doc-type-system/specification/doc-type.md) — The doc-type system's target state as a specification — the predicates any doc-type satisfies, so a loop can propose a new one; the files beside it hold each known doc-type's own
- [Runbook Specification](/working-docs/doc-type-system/doc-type-system/specification/runbook.md) — What the Runbook doc-type satisfies beyond Doc-Type Specification — its six verbs, and every edge landing on a Target
- [Standard Specification](/working-docs/doc-type-system/doc-type-system/specification/standard.md) — What the Standard doc-type satisfies beyond Doc-Type Specification — one verb, every rule identified and decidable, a population naming a class, one verifier per id, boundaries that name ids, and an audit that returns findings
- [Loop Specification](/working-docs/doc-type-system/doc-type-system/specification/loop.md) — What the Loop doc-type satisfies beyond Doc-Type Specification — three verbs, steps that only point, nothing landing on a loop, and zero findings as the one pass
