---
type: General-Sheet
title: Types
description: Theory additions — contract, shape, composition rule — and the long-term types/ tree they settle into
---

# Types

Theory additions and location decisions for types and their contracts.
Same speculative-voice conventions as the branch plan.

## Theory additions

- A thing *has* a contract; it isn't one. Grain is an axis: type-level
  or instance-level.

  ```
  Standard   same contract for every card  naming-conventions and modules/design
                                           answer different questions, same four
                                           operations
  Runbook    one contract per instance     /intake's chain ≠ /commit's chain
  ```

- Type = operations + composition rule. Shape = the contract form those
  two fix. Contract = shape filled with instance detail.

  ```
             operations                        composition rule    shape
  Standard   define audit enforce adopt        one of each         struct
  Runbook    reads writes does overrides       any number,         chain — the
             args reports (mods: if, never)    coarsely ordered    Reference chain
  ```

- "The Reference chain" names Runbook's shape; "a runbook's Reference
  chain" names one instance contract.

  ```
  shape      every chain is edges from the six labels, rooted at one runbook
  instance   /commit's chain: args in, reads the commit standard,
             writes git(commit, push), reports outcome: str
  ```

- Freer composition rule ⇒ deeper machinery.

  ```
  Standard   struct    headings suffice; its determinism is in its audit
                       linters and enforcement gates
  Runbook    chain     needs grammar ({Read …}, {If …, {…}}) + chaingen.py + --check
  ```

- The Contract organizes the type layer: per documentation family, the
  theory's deliverable is a contract shape.

  ```
  delivered  Standard → struct        Runbook → chain
  future     each new family ruled important gets its shape from the loop
  ```

## The type layer, drawn

The type layer is the stack's top layer; its primitives are types, one
per documentation family the registry rules important. Each type exists
to hand its family a contract shape — that is the deliverable every
time, and it is what "the Contract organizes the type layer" means.

```
general:

  family ──the loop──► type = operations + composition rule
                         │
                         └──► shape ───filled per instance───► contract


implemented, one deep and one sparse:

  runbooks    ──the loop──►  Runbook
  (skills,                     operations:   reads writes does
   agents)                                   overrides args reports
                               composition:  any number, coarsely ordered
                                 │
                                 └──► shape: the chain — the Reference chain
                                        │
                                        ├─ /intake's chain     one contract
                                        └─ /commit's chain     another

  cards       ──predates ──►  Standard
                the loop        operations:   define audit enforce adopt
                                composition:  one of each
                                  │
                                  └──► shape: the struct
                                         │
                                         ├─ the harness card — its four
                                         │  sections filled (its Define
                                         │  citing detail files like
                                         │  files.md)
                                         └─ the build card — its four
                                            sections filled (Define citing
                                            distribution.md)
```

A card is to Standard what `/intake` is to Runbook: one instance, one
filled shape, one contract. The detail files under a card sit below its
contract, the way a runbook's prose body sits below its chain.

## Decisions

- The chain does not become a Standard; it gets one — construct and
  obligation stay separate, so Standard and Runbook remain peers at the
  type layer.

  ```
  construct    types/runbook/contract-shape.md       what a chain IS
  obligation   runbook-conventions (extended)        "every runbook declares one":
                                                     define cites types/runbook/,
                                                     audit = chaingen --check,
                                                     enforce = the gate
  ```

  No separate standard; the obligation is not independently adoptable.

- The base directory is `types/` — each subdirectory is one type,
  TYPE-SYSTEM.md names the roster, THEORY.md is the theory of types.
  Rejected: `theory/` (the per-type dirs are concrete implementations,
  not theory), `contracts/` (the tree holds more than contracts),
  `core-abstractions/` ("abstraction" is declined as a term of art, and
  "core" adds nothing the registry rulings don't already say).

- The general theory lives at the root of `types/`, by the Standard
  precedent: each population directory carries its kind's definition at
  its root. `standards/standard.md` is the general definition of a card,
  at the root of the card population; THEORY.md is the general
  definition of a type, at the root of the type population. `types/` is
  a population directory whose population is types.

- The long-term tree, with true peerage:

  ```
  dev-playbook/types/
    index.md
    THEORY.md                    what a type is — defined once, never copied
    TYPE-SYSTEM.md               dev-playbook's registry rulings + roster
    runbook/
      contract-shape.md          the Reference chain — chain shape
      encoding.md                the encoding layer: grammar, spans
      RESIDUAL-LEDGER.md
    standard/
      contract-shape.md          define · audit · enforce · adopt — struct shape
      encoding.md                the card format (today's standards/standard/format.md)
      RESIDUAL-LEDGER.md         empty at birth, deliberately
  ```

- Greenfield moves, completing the pattern: `standards/standard/format.md`
  was Standard's encoding layer all along and relocates to
  `types/standard/encoding.md`; `standards/standard.md` (the general
  Standard definition) migrates into `types/standard/` too. `standards/`
  becomes pure instance population + index — exactly how consumer repos'
  `standards/` directories already look. The old mixed state (definition
  living among instances) was the only irregularity, and consumers never
  copied it.

- Instances live where populations live; instance contracts ride inside
  instance files.

  ```
  Runbook    dotfiles/dot-claude/…    spans in the prose are the contract
  Standard   standards/…              the cards
  bedrock    scripts/chaingen         chains.txt a generated view, untended
  ```

- Residual ledgers split per type. Standard's is created empty — the
  absence of residuals is itself a record.

- Types are extensible across repos by the same abstract import the
  Standard system uses. A consumer repo's TYPE-SYSTEM.md states its
  imports and any local rulings; local types are declared only there.

  ```
  consumer-repo/types/
    index.md
    TYPE-SYSTEM.md               "import Runbook, Standard from dev-playbook"
                                 + local rulings
    <local-type>/                only if this repo declares its own type
      contract-shape.md · encoding.md · RESIDUAL-LEDGER.md
  ```

## Pinned ambiguities

- "Is Standard a contract?" — resolved by grain: it has one, type-level.
- **Struct**, not record, for Standard's shape.
- The theory belongs inside `types/`, at the root — settled by the
  population-directory precedent, not by "general things live elsewhere."
