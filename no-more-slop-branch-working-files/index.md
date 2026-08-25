---
okf_version: "0.1"
---

# no-more-slop-branch-working-files — bundle index

Temporary tracking files for the `no-more-slop` branch. The whole folder is
deleted when the branch merges; material drains out of it into long-term
locations as it settles.

- [CLOA Abstractions](/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md) — The noun-and-verb abstractions that make documentation understandable at the CLOA, and the loop that generates them
- [CLOA Chains](/no-more-slop-branch-working-files/CLOA-CHAINS.md) — The ledger of finalized reference chains — one recorded entry per unit, written down as it is ruled
- [Edge Encoding](/no-more-slop-branch-working-files/EDGE-ENCODING.md) — The one-to-one primitive map from Reference chain to skill prose — the ruled encodings, the holes, and the residual ledger
- [Factory Survey](/no-more-slop-branch-working-files/FACTORY-SURVEY.md) — One session's full read of the software factory — a classification of its files, the intent they carry, and sketches for a possible native rewrite
- [No More Slop](/no-more-slop-branch-working-files/NO-MORE-SLOP.md) — The branch plan — goal, principles, the two tracks, and the current step

The `edge-examples/` subtree holds the exemplar skills and agents for the
edge-encoding design. The committed state is the verbatim snapshot; the
encoding under design lives as uncommitted edits on top, so the IDE diff
against HEAD shows exactly what the encoding changes. A settled edge's
edit is committed once ruled. The tree mirrors the `skills/` and `agents/`
source layout so the lints treat the copies exactly as they treat the
sources. The live skill files are untouched until the design settles.
