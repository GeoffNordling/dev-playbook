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

## Locations, drawn

Three placement rules carry every location:

1. **A kind's definition lives one level up, in `types/<kind>/`** —
   cards are defined in `types/standard/`, not among the cards.
   THEORY.md is where the recursion terminates: "type" is the kind of
   `types/`' own members, no level exists above, so it sits
   self-hosted at the root.
2. **Instances live where their populations live**, and an instance
   contract rides inside the instance file itself — a runbook's spans
   are its contract; no separate contract location exists.
3. **Construct and obligation stay separate.** A type's shape is
   declared in `types/`; the rule binding instances to use it is a
   Standard card. The two never merge, so Standard and Runbook remain
   peers at the type layer.

```
dev-playbook/
  types/
    index.md
    THEORY.md                  what a type is — defined once, never copied
    TYPE-SYSTEM.md             this repo's registry rulings + roster
    runbook/                   one dir per type, true peers
      contract-shape.md        the Reference chain — chain shape
      encoding.md              the encoding layer: grammar, spans
      RESIDUAL-LEDGER.md
    standard/
      contract-shape.md        define · audit · enforce · adopt — struct
      encoding.md              the card format
      RESIDUAL-LEDGER.md       empty at birth — no residuals is a record

  dotfiles/dot-claude/…        Runbook instances; each one's spans are
                               its contract
  standards/                   Standard instances — cards and index,
                               nothing but population
  scripts/chaingen             bedrock; chains.txt a generated view

consumer-repo/
  types/
    index.md
    TYPE-SYSTEM.md             "import Runbook, Standard from dev-playbook"
                               + local rulings
    <local-type>/              only if this repo declares its own type
      contract-shape.md · encoding.md · RESIDUAL-LEDGER.md
  standards/  .claude/…        its own instance populations, same rules
```

The import row is the Standard system's own move, one level up: a
consumer repo never copies THEORY.md or a shape, it imports them
abstractly and declares only what is local.

The obligation lives in **runbook-conventions**: its Define cites
`types/runbook/`, its audit runs `chaingen --check`, its enforce is the
gate. The chain itself is never a Standard, and the obligation is not
independently adoptable.

## Pinned ambiguities

- The base directory is `types/`, not `theory/` — the per-type dirs are
  concrete implementations derived from the theory, not theory; the
  theory still lives inside, at the root, by placement rule 1.
