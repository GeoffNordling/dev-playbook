---
type: General-Sheet
title: Card Cells
description: The four cells — Standard-Card's contract shape — and the one relation every card collapses to, card × cell × pointer
---

# Card Cells

The four cells are Standard-Card's contract shape
([Doc-Type](/doc-types/doc-type.md)): the form every card's contract
takes. Returning to a topic months later should not require re-deriving
shared understanding over several turns of conversation. Each standard
therefore gets a **standard card**: a small fixed-format record that tells
a user or agent where to look. The files it points at define the
standard; the card aggregates pointers so a thought that originates at
the abstract level ("how do we do X here?") resolves to concrete files in
one hop.

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

- **Define** — the Standards: documents typed `Standard`, each one
  population and its rules.
- **Audit** — read-only deviation detection: the detectors that report
  nonconformance without blocking anything. A formatter is a detector by
  its check mode ([Detectors](/standards/standard/detectors.md#detectors)).
- **Enforce** — what compels conformance, in one of two modes. At a
  gate: the rung where nonconformance stops the path to main, cited by
  fixed name (**commit gate**, **push gate**, **CI gate**), defined in
  [Gates](/standards/standard/gates.md). A cell cites the single rung
  where the detector is stationed — where its wiring lives (pre-commit
  hooks → the commit gate; tools that run only inside `make check` /
  `make check-judgments-cache` → the push gate); the hook pattern in Gates
  implies the echoes at the other rungs. On demand: a script or skill the
  user, a schedule, or a process step invokes, which rewrites the object
  into conformance and leaves the result for review, marked
  **on demand** beside its link. A code review is a one-time checkpoint,
  never an Enforce pointer.
- **Adopt** — what brings a repository into conformance the first time:
  a scaffold, a template, a migration procedure, a first-pickup recipe.
  Often "none": the generic path is an agent reading the define cell and
  fixing the repository.

The cards themselves are the examples: [Build](/standards/build.md) and
[Meta-Standard](/standards/standard.md) — the latter is the card of the
standard that governs cards, since the meta-standard is an instance of
the format it defines. The shape in pseudocode:

```python
class StandardCard(Object):
    """One card per standard. Points; never restates."""

    question: str                       # "Governs how ..." — one breath

    # four cells; a cell is a list of pointers, or the literal word "none"
    define:  list[Pointer[Standard]]                # required, at least one
    audit:   list[Pointer[Detector]] | None
    enforce: list[Pointer[Gate | OnDemand]] | None  # Gate = commit | push | CI; OnDemand = a tool that rewrites
    adopt:   list[Pointer[Adoption]] | None

    # rules: each a predicate over one card's state
    location    = path == f"standards/{name}.md"            # flat, never nested
    frontmatter = type == "Standard-Card" and description == question
    layout      = h2s == ["Define", "Audit", "Enforce", "Adopt"]
```

## The view

Every card in the catalog collapses to rows of one relation,
`card, cell, pointer`. `scripts/cardgen` writes the whole catalog to
`doc-types/standard-card/cards.txt` and, with `--check`, fails on drift:

```
card     cell     pointer
build    define   /standards/build/canonical.md
build    audit    /scripts/repo-lint
build    enforce  commit gate
modules  audit    none
```

A Define, Audit, or Adopt pointer is the file a bullet leads with, or the
bare name of a third-party detector cited by its pin. An Enforce pointer
is one of the three gate names, or the file of a tool marked on demand.
An empty cell is one `none` row, so the
gap stays visible in the view as it does in the card. Cards sort
alphabetically, cells keep the card's order, and pointers keep their
bullet order. The annotation after each pointer stays below the collapse,
in the card.
