# working-docs/doc-type-system/detector-rewrite/ — index

The detector rewrite strand: one pass over the checking system against
the settled Standards, and the survey of what the detectors miss that
it starts from. Start at the root.

Ordering: the root, then reading order.

- [Detector Rewrite](/working-docs/doc-type-system/detector-rewrite/ROOT.md) — The root of the detector rewrite strand — one pass over the checking system against the settled Standards, its principles and constraints, the current state it starts from, the seven design rulings, and the worklist
- [Rewrite Plan](/working-docs/doc-type-system/detector-rewrite/plan.md) — The implementation plan of the detector rewrite — four phases, the family order and which old script each family retires, how each phase is delegated and checked, and the finish line
- [Triage](/working-docs/doc-type-system/detector-rewrite/triage.md) — The method of the detector rewrite's triage — the verdicts, how a row is escalated, the user's rulings that calibrate every family, and the one report per family
- [triage/](/working-docs/doc-type-system/detector-rewrite/triage/index.md) — One triage report per family: every deterministic rule of the family kept, rewritten, or deleted, with its escalations
- [rewrite/](/working-docs/doc-type-system/detector-rewrite/rewrite/index.md) — One rewrite report per family: what the family's step built, deleted, retired, and set aside, and the wall time it measured
- [prompts/](/working-docs/doc-type-system/detector-rewrite/prompts/index.md) — The launch prompts the rewrite hands to its agents, one file per agent role
- [Detector Fixes](/working-docs/doc-type-system/detector-rewrite/detector-fixes.md) — The rewrite's input — the fourteen rules whose detector tests less than the sentence, the survey of what each detector misses, the thin-shim moves, and the one-base check, none of them touched by step 11
