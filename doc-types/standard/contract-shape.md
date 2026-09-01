---
type: General-Sheet
title: Standard Card
description: The card — Standard's contract shape — four pointer cells that catalog every standard for one-hop lookup
---

# Standard Card

The card is Standard's contract shape. Returning to a topic months
later should not require re-deriving shared understanding over several
turns of conversation. Each standard therefore gets a **standard
card**: a small fixed-format record that tells a user or agent where
to look. The files it points at define the standard; the card
aggregates pointers so a thought that originates at the abstract level
("how do we do X here?") resolves to concrete files in one hop.

## The card

A card is a markdown file at `standards/<name>.md` with
`type: Standard-Card` frontmatter: a heading, one sentence naming the
governed question, then exactly four cells as sections. That sentence
opens `Governs how`, names the territory its define cell covers, and runs
about a breath; the frontmatter `description` repeats it verbatim less the
period, so the catalog row and the card state the same remit.
standards-lint's `standard.card-question` checks the pairing. Each cell holds
annotated pointers; an empty cell states an explicit "none" so gaps stay
visible. Cards are thin — often just a handful of pointers — and never
restate the content of their targets.

- **Define** — the contract: prose documents and canonical reference
  files.
- **Audit** — read-only deviation detection: the detectors that report
  nonconformance without blocking anything.
- **Enforce** — blocking gates: the rungs where nonconformance stops the
  path to main, cited by fixed name (**commit gate**, **push gate**,
  **CI gate**), defined in [enforcement.md](/standards/build/enforcement.md).
  A cell cites the single rung where the detector is stationed — where its
  wiring lives (pre-commit hooks → the commit gate; tools that run only inside
  `make check` / `make check-judgments-cache` → the push gate); the hook pattern in enforcement.md's Map
  implies the echoes at the other rungs. Enforcement is automatic and
  continuously in effect; a code review is a one-time checkpoint, never an
  Enforce pointer.
- **Adopt** — anything that helps bring a repository into conformance,
  such as templates or migration procedures. Often "none": the generic
  path is an agent reading the define cell and fixing the repository.

The cards themselves are the examples: [Build](/standards/build.md) and
[Meta-Standard](/standards/standard.md) — the latter is the card of the
standard that governs cards, since the meta-standard is an instance of
the format it defines.
