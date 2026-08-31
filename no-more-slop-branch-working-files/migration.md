---
type: General-Sheet
title: Migration
description: The move plan that takes the working files to their long-term homes — the path table, the standards/ split, and the wiring that lands with it
---

# Migration

Branch overflow: the instruction sheet for moving the working files
to their long-term homes. It dies once the move lands. Same
speculative-voice conventions as the branch plan.

## The path table

Every working file, flat in this directory today, moves verbatim to
its future path; nothing is rewritten at move time except links.

| Working file | Future home |
|---|---|
| `system-legibility.md` | `docs/system-legibility.md` |
| `doc-type.md` | `doc-types/doc-type.md` |
| `doc-type-system.md` | `doc-types/doc-type-system.md` |
| `runbook-definition.md` | `doc-types/runbook/definition.md` |
| `runbook-contract-shape.md` | `doc-types/runbook/contract-shape.md` |
| `runbook-encoding.md` | `doc-types/runbook/encoding.md` |
| `runbook-residual-ledger.md` | `doc-types/runbook/residual-ledger.md` |
| `parser/chaingen.py` | `scripts/chaingen` |
| `parser/chains.txt` | a generated view; final location set by where `chaingen` writes |

Link rewrites ride the move: every
`/no-more-slop-branch-working-files/<file>` reference repoints to the
future path, mechanically. Index entries move with their files —
each future directory's `index.md` lists what lands in it, and this
directory's index shrinks as files leave.

## The standards/ split

[format.md](/standards/standard/format.md) mixes four jobs; the move
splits it along the five-file roster:

- **definition** — "What a standard is", "What a standard is not",
  and "Scope" → `doc-types/standard/definition.md`. Scope sits with
  the definition because it says what population a standard governs;
  its no-shadowing rule is detector-backed and may belong with the
  obligation material instead — decide at split time.
- **contract shape** — "The card" → `doc-types/standard/contract-shape.md`.
- **encoding** — "Where a standard lives", "Naming", "The catalog" →
  `doc-types/standard/encoding.md`.
- **obligation** — "Detectors" and "Drift" stay under `standards/`:
  they are the Meta-Standard card's machinery, not shape
  declaration.
- `doc-types/standard/residual-ledger.md` is created empty — no
  residuals is a record.

[standard.md](/standards/standard.md) is the Meta-Standard card. It
stays a card at `standards/standard.md` and does not migrate; its
Define cell repoints from format.md to the split files.

## Repoints

- `doc-type-system.md`'s Standard links (definition and shape, both
  at format.md today) repoint to `doc-types/standard/definition.md`
  and `doc-types/standard/contract-shape.md`.
- Runbook's obligation rides
  [runbook-conventions](/standards/harness/runbook-conventions.md):
  its Define cites `doc-types/runbook/`, its Audit runs
  `chaingen --check`, its Enforce is the gate that check is
  stationed at.

## New files at move time

Per the five-file roster, each doc-type directory carries
`index.md`, `definition.md`, `contract-shape.md`, `encoding.md`,
`residual-ledger.md`:

- `doc-types/index.md` — lists `doc-type.md`, `doc-type-system.md`,
  and the two directories.
- `doc-types/runbook/index.md` — its five files, four of which move
  in from this directory.
- `doc-types/standard/index.md` — its five files, born in the
  split.

## Observations

- The workspace inheritance pattern — dev-playbook declares a system
  once, consumers inherit it, a repo declares only what is local —
  is stated per-system in `CLAUDE.md`, format.md's Scope, and
  document-types.md's Local extensions, with no single home. A
  candidate for [System Legibility](/no-more-slop-branch-working-files/system-legibility.md)
  or a standard of its own; recorded here so the move does not lose
  it.
