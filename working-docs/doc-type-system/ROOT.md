---
type: General-Sheet
title: Synthesis Working Root
description: The root of the unified working set — six strands and their plan dependencies, the terms every strand uses, the open cross-strand questions, and the run order
---

# Synthesis Working Root

This set is speculative: every member writes a guess as a guess, and
every member inherits that voice. It unifies the working sets of two
branches, `worktree-loop-document-type` and
`worktree-cloa-viewer-tool-2`, which describe one theory. The set is
six strands, each with its own root and its own worklist
([One list of items, state by section](/standards/knowledge-organization/documentation-sets/working-documentation-sets.md#one-list-of-items-state-by-section)).
This root holds only what crosses strands.

## Goal

- **Doc-type system**, the language: doc-types, verbs, rules as
  predicates, encodings as grammar. Root:
  [Doc-Type System](/working-docs/doc-type-system/doc-type-system/ROOT.md).
- **Loop**, the driver: the third doc-type, a full peer of Runbook and
  Standard. Root: [Loop](/working-docs/doc-type-system/loop/ROOT.md).
- **Fact base**, the compiled object: one deterministic object of nodes
  and edges per checkout, every view a selection from it. Root:
  [Fact Base](/working-docs/doc-type-system/fact-base/ROOT.md).
- **Viewer**, a selection on screen: cloa-viewer, the local visual IDE
  that draws registered views of the fact base. Root:
  [CLOA Viewer](/working-docs/doc-type-system/viewer/ROOT.md).
- **Check rewrite**, the checking system: one pass over the Python
  checks, the two tables, and the hook, against the rules the
  doc-type system settled. Root:
  [Check Rewrite](/working-docs/doc-type-system/check-rewrite/ROOT.md).
- **Story-forge simulation**, the trial: the doc-type system and the
  fact base tried by hand on one consumer repo before any extractor is
  coded. Root:
  [Story-Forge Simulation](/working-docs/doc-type-system/story-forge-simulation/ROOT.md).

## The six strands

A dependency is what one strand's plan needs from another's, never a
runtime data flow. There are six: the doc-type system defines Loop,
one of its four doc-types; each encoding the doc-type system writes
defines an extractor of the fact base; every view the viewer draws is
a selection of the fact base; the check rewrite binds to the rules
the doc-type system's step 11 settled; the story-forge simulation
takes its language from the doc-type system and its method from the
fact base. Loop, the check rewrite, and the simulation are
leaves.

```
                            ROOT.md#terms
                      one meaning per word, all five
                                  │
  ┌───────────────────────────────┴────────────────────────────────┐
  │  DOC-TYPE SYSTEM · the language                                │
  │  picture ······· reference-model.md                            │
  │  predicates ···· standards/doc-type/doc-type.md                │
  │  method ········ guides/writing-predicates.md                  │
  │  theory ········ ontology-solvers.md                           │
  │  user's words ·· personal-notes.md                             │
  │  drained ······· doc-types/{doc-type, runbook, standard}       │
  │  plan: refactor steps 1–10 · banned words · /write-predicates │
  │        · first instance, a loop that proposes predicates       │
  └────────────┬──────────────────────────────────┬────────────────┘
  Loop is one  │                                  │  each encoding
  of its four  │                                  │  defines an
  doc-types    ▼                                  ▼  extractor
  ┌────────────────────────────┐   ┌──────────────────────────────┐
  │  LOOP · the driver         │   │  FACT BASE · the compiled    │
  │  predicates · specification│   │  object                      │
  │                 /loop.md   │   │  theory ····· fact-base.md   │
  │  how it is told            │   │  evidence ··· fact-base-     │
  │     · specifying-a-loop.md │   │      ralph.md · ralph.json   │
  │                            │   │  planned view                │
  │  drained · doc-types/loop/ │   │     · deterministic-         │
  │     · loop_lint · loops/   │   │       separation.md          │
  │  plan: the objective part, │   │  plan: simulations by hand · │
  │        if any · its use by │   │   extractors chain, standard,│
  │        the two loops above │   │   loop · verifier table and  │
  │        and right           │   │   gate config as declared    │
  └────────────────────────────┘   │   data · findings as a       │
                                   │   stamped artifact · the     │
  ┌────────────────────────────┐   │   simulation as a loop       │
  │  CHECK REWRITE · the       │   └──────────────┬───────────────┘
  │  checking system           │                  │  a selection
  │  root ······· ROOT.md      │   ┌──────────────▼───────────────┐
  │  binds to the rules the    │   │  VIEWER                      │
  │  doc-type system settled   │   │  root ······· ROOT.md        │
  │  built: playbook check     │   │  on disk ···· contract.md    │
  │  plan: repeated fixes to   │   │                              │
  │        predicates skill    │   │  kinds ······ registry.md    │
  │                            │   │  panels ····· design.md ·    │
  │                            │   │               viewer.md      │
  └────────────────────────────┘   │  program ···· server.md      │
                                   │  built ······ stack.md       │
                                   │  plan: runbook design ·      │
                                   │   CLOA kinds · pinning ·     │
                                   │   stale badge                │
                                   └──────────────────────────────┘
```

## Terms

The words of the set, one meaning each, used in these senses by every
strand. This is the conceptual model, what domain-driven design calls
the ubiquitous language: the level above the pseudocode of
[Reference Model](/working-docs/doc-type-system/doc-type-system/reference-model.md)
and above the predicates that describe the same target. Three levels,
top down: these terms are the words; the reference model is one
witness in pseudocode; the specification is the predicates. A word
one strand coins for itself is in that strand's root. The entries are
the seed of the system's eventual context file.

### Logic

- **State** — everything a predicate may read at one moment: the repo
  tree and the targets outside it.
- **Predicate** — a statement about one member at one moment that is
  true or false. It defines a set: the states where it holds.
- **Rule** — a predicate as it lives in a Standard: an id, a kind, the
  predicate text, and an optional condition. A rule is about one
  member; the Standard lifts it to the state: every member of the
  population satisfies it.
- **Condition** — the predicate under which a part applies: for a
  rule, the rule it is under; for a runbook edge or a loop step, when
  it fires. Where the condition is false the part is not evaluated,
  so a rule's set widens to include those states. The word is
  condition, never guard.
- **Population** — the class of targets a Standard's rules range over.
- **Specification** — a set of predicates taken together. It defines
  the intersection of their sets. A Standard is a spec written as a
  file over a population. Short form: spec.
- **Target state** — the set of states that satisfy a spec. Not one
  state; a set.
- **Objective** — a scalar to minimize, "the fewest verbs". It ranks
  the states that satisfy the predicates; it is never one of them, and
  it is descended one proposed step at a time, each accepted or
  vetoed by the user.
- **Reference model** — one state that satisfies the spec, drawn out.
  A witness. Model checking writes the relation as M ⊨ φ: the model
  satisfies the formula. Property-based testing calls the same pair
  example and property. Model and spec are the two written forms of
  one target.

### Verification

- **Verifier** — per [CONTEXT.md](/CONTEXT.md#governance): what decides a rule for a member. A check for a
  deterministic rule, a judge for a stochastic one.
- **Deterministic rule** — its verifier is a function. Same input,
  same answer. Hard set membership.
- **Stochastic rule** — its verifier is a judge with an error rate. A
  noisy classifier of membership. This is the one place statistics
  enters the logic.
- **Kind** — a rule's, deterministic or stochastic: which verifier
  decides it.
- **Finding** — one member and the rule it fails. Evidence that the
  state is outside the set. What a loop carries from one step to the
  next: a verification ([Loop](/doc-types/loop/definition.md)) returns
  findings and the acts read them.
- **Zero findings** — every verifier of a spec, run against a state,
  returns nothing: the state is in the set, up to judge error.
- **Gate** — per [CONTEXT.md](/CONTEXT.md#governance): pre-commit,
  pre-push, or CI, blocking on its checks' findings. A loop's
  verification runs verifiers and never gates.

### Extraction

- **Encoding** — a doc-type's map from written form to rows: which
  marks in a file of that type carry which primitives. It defines
  the doc-type's extractor and is not a spec: the well-formedness
  predicates in it, a span nests at most two deep, one link names a
  target, belong in a Standard whose verifier is the drift check, or
  in the one coarse rule every grammar induces, the file parses.
- **Extractor** — a deterministic function from one artifact to rows.
  It reads a file and yields nodes and edges. A bedrock extractor
  parses a format someone else fixed; a doc-type extractor is the
  function that doc-type's encoding defines. The word is extractor,
  never generator.
- **Fact base** — the one object underneath every view: a set of nodes
  and a set of edges, written by code to one file per checkout.
- **Node** — one thing with an identity, a node type, a provenance, and
  attributes. An identity is a repo-relative path
  ([Contract](/working-docs/doc-type-system/viewer/contract.md#identities));
  an imported node has a name instead, and a bucket is named
  `bucket:<name>`.
- **Edge** — one relation from a source node to a target node, with a
  relation type, and, where the source declares them, an order, a
  condition, and a detail quoted from the source. The detail is what
  the runbook encoding calls annotation
  ([Nodes and Edges Encoding](/doc-types/runbook/encoding.md)).
- **Derivation** — a deterministic function from rows to rows. It
  reads the fact base and derives new rows from existing ones, with
  no judgment, and never touches a file. Not a rule: a rule is a
  Standard's.
- **View** — a selection of nodes and edges from the fact base, plus a
  renderer. A view drops rows; it never adds or converts one.
- **Residual** — what a doc-type's selected primitives cannot express
  about one of its documents, recorded in that doc-type's ledger
  ([Doc-Type](/doc-types/doc-type.md#the-doc-type-build-loop)).

### Statistics

- **Distribution** — the states an act could leave behind, each
  weighted by how likely it is, given the state it starts from and the
  prompt it is given. Some of the weight falls inside the target set,
  some outside. A distribution is not a set and a set is not a
  distribution.
- **Sample** — one state an act did leave behind: one draw from its
  distribution.
- **Loop** — the one sentence of [Loop](/doc-types/loop/definition.md).
  In these terms: a trajectory of samples that ends when one lands
  in the set or when a yield's condition holds first. Each sample
  starts from the last, with its findings in the prompt, so the
  samples are not independent: the trajectory is a path through state
  space. Verify tests the sample, act draws the next one, yield exits
  to the user or another loop.

Logic and statistics meet at one seam. Predicates define a set, with
no probabilities attached. An act is a draw from a distribution over
states, and the draw lands in the set or outside it. A loop does not
change the LLM; it changes what the next draw is given:
check finds where the last sample fell outside, act draws again with
those findings in the prompt, so successive samples land in the set
more often. Deterministic rules decide membership exactly; stochastic
rules decide it with an error rate.

## Open

- **Whether every condition is a Rule.** A runbook edge's and a loop
  step's condition are strings; a Standard rule's condition is a
  reference to another rule. Option: every condition is a Rule with a
  kind, so all three unify and the fact base gets one guarded-by edge.
  Cost: runbook prose conditions would need ids. Crosses the doc-type
  system and the fact base.
- **Whether one solver or two.** Mypy over the pseudocode, an engine
  over the fact base and a domain layer, or one of them. The case is in
  [Ontology Solvers](/working-docs/doc-type-system/doc-type-system/ontology-solvers.md).
  The user is not convinced two are needed. Crosses the doc-type
  system and the fact base.

## Order

The dependencies give the order. The doc-type system's refactor runs
first, because Loop's predicates, the fact base's extractors, and the
check rewrite bind to what it produces. Loop, the fact base, and
the check rewrite then run beside each other. The viewer's next kinds wait on the fact base, since each is a
selection from it.

## Acronyms

- **CLOA** — Correct Level of Abstraction.
- **IDE** — Integrated Development Environment.
- **JSON** — JavaScript Object Notation.
- **LLM** — Large Language Model.
