---
type: General-Sheet
title: Synthesis Working Root
description: The root of the unified working set — four strands, doc-type system, Loop, fact base, and viewer, the plan-dependency edges between them, the cross-strand decisions and open questions, and the order the strands run in
---

# Synthesis Working Root

This set is speculative: every member writes a guess as a guess, and
every member inherits that voice. It unifies the working sets of two
branches, `worktree-loop-document-type` and
`worktree-cloa-viewer-tool-2`, which one reading found to be one
theory. The set is four strands, each with its own root and its own
worklist
([Worklist](/standards/knowledge-organization/documentation-sets/working-documentation-sets.md#worklist)).
This root holds only what crosses strands.

## Goal

- **Doc-type system**, the language: doc-types, verbs, rules as
  predicates, encodings as grammar. Root:
  [Doc-Type System](/worktree-synthesis-notes-working-docs/doc-type-system/ROOT.md).
- **Loop**, the driver: the third doc-type, a full peer of Runbook and
  Standard. Root: [Loop](/worktree-synthesis-notes-working-docs/loop/ROOT.md).
- **Fact base**, the compiled object: one deterministic object of nodes
  and edges per checkout, every view a selection from it. Root:
  [Fact Base](/worktree-synthesis-notes-working-docs/fact-base/ROOT.md).
- **Viewer**, a selection on screen: cloa-viewer, the local visual IDE
  that draws registered views of the fact base. Root:
  [CLOA Viewer](/worktree-synthesis-notes-working-docs/viewer/ROOT.md).

## The four strands

An edge is a plan dependency, what one strand's plan needs from
another's, never a runtime data flow. There are three: the doc-type
system defines Loop, one of its three doc-types; each encoding the
doc-type system writes defines an extractor of the fact base; every
view the viewer draws is a selection of the fact base. Loop is a leaf.

```
                             glossary.md
                      one meaning per word, all four
                                  │
  ┌───────────────────────────────┴────────────────────────────────┐
  │  DOC-TYPE SYSTEM · the language                                │
  │  picture ······· reference-model.md                            │
  │  predicates ···· specification/ doc-type · runbook · standard  │
  │  method ········ writing-predicates.md                         │
  │  parallel ······ three-peers.md                                │
  │  theory ········ ontology-solvers.md                           │
  │  user's words ·· personal-notes.md                             │
  │  drained ······· doc-types/{doc-type, runbook, standard}       │
  │  plan: refactor steps 1–8 · vocabulary pass · /write-predicates│
  │        · first instance, a loop that proposes predicates       │
  └────────────┬──────────────────────────────────┬────────────────┘
  Loop is one  │                                  │  each encoding
  of its three │                                  │  defines an
  doc-types    ▼                                  ▼  extractor
  ┌────────────────────────────┐   ┌──────────────────────────────┐
  │  LOOP · the driver         │   │  FACT BASE · the compiled    │
  │  predicates · specification│   │  object                      │
  │                 /loop.md   │   │  theory ····· fact-base.md   │
  │  how it is told            │   │  evidence ··· fact-base-     │
  │     · specifying-a-loop.md │   │      ralph.md · ralph.json   │
  │  standing · three-peers.md │   │  planned view                │
  │  drained · doc-types/loop/ │   │     · deterministic-         │
  │     · loop-lint · loops/   │   │       separation.md          │
  │  plan: the objective part, │   │  plan: simulations by hand · │
  │        if any · then it is │   │   extractors chain, standard,│
  │        used by the two     │   │   loop · verifier table and  │
  │        loops above and     │   │   boundary config as declared│
  │        right               │   │   data · findings as a       │
  └────────────────────────────┘   │   stamped artifact · the     │
                                   │   simulation as a loop       │
                                   └──────────────┬───────────────┘
                                                  │  a selection
                                   ┌──────────────▼───────────────┐
                                   │  VIEWER                      │
                                   │  root ······· ROOT.md        │
                                   │  on disk ···· contract.md    │
                                   │  kinds ······ registry.md    │
                                   │  panels ····· design.md ·    │
                                   │               viewer.md      │
                                   │  program ···· server.md      │
                                   │  built ······ stack.md       │
                                   │  plan: runbook design ·      │
                                   │   CLOA kinds · pinning ·     │
                                   │   stale badge                │
                                   └──────────────────────────────┘
```

## Terms

Every strand uses the words of
[Glossary](/worktree-synthesis-notes-working-docs/glossary.md), one
meaning each. A word a strand coins for itself is in that strand's
root.

## Decided

- **The two branches are one theory.** The loop branch is the
  language: doc-types, verbs, rules as predicates, encodings as
  grammar. The cloa branch is what the language compiles to:
  extractors are the parsers, the fact base is the symbol table, views
  are selections over it. The reference model says the CLOA is a view
  derived deterministically from structure embedded in the files; the
  fact base says every view is a selection from the fact base. Two
  sessions that never saw each other wrote the same sentence. What the
  reading found was vocabulary drift and gaps left by work not yet
  done, no fundamental incompatibility. Each gap is filed in one
  strand's root, under Decided, Open, or Planned.

## Open

- **Whether every condition is a Rule.** A runbook edge's and a loop
  step's condition are strings; a Standard rule's condition is a
  reference to another rule. Option: every condition is a Rule with a
  kind, so all three unify and the fact base gets one guarded-by edge.
  Cost: runbook prose conditions would need ids. Crosses the doc-type
  system and the fact base.
- **Whether one solver or two.** Mypy over the pseudocode, an engine
  over the fact base and a domain layer, or one of them. The case is in
  [Ontology Solvers](/worktree-synthesis-notes-working-docs/doc-type-system/ontology-solvers.md).
  The user is not convinced two are needed. Crosses the doc-type
  system and the fact base.

## Order

The edges give the order. The doc-type system's refactor runs first,
because Loop's predicates and the fact base's extractors bind to what
it produces. Loop and the fact base then run beside each other. The
viewer's next kinds wait on the fact base, since each is a selection
from it.

## Acronyms

- **CLOA** — Correct Level of Abstraction.
- **IDE** — Integrated Development Environment.
