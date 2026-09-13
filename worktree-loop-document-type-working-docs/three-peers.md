---
type: General-Sheet
title: Three Peers
description: Runbook, Standard, and Loop as peer doc-types — their one-sentence definitions, the parallel structure between them, and what is settled about Loop so far
---

# Three Peers

Runbook, Standard, and Loop are three doc-types under one kind,
[Doc-Type](/doc-types/doc-type.md): operations plus a composition rule,
fixing a shape every instance fills. This member records the parallel
between them. It is speculative, per
[ROOT.md](/worktree-loop-document-type-working-docs/ROOT.md).

## The three sentences

Each doc-type is one sentence. Runbook's and Standard's are the ones
their bundles carry today; Loop's is new.

> A **runbook** is an invocable command written as documentation: a
> skill or an agent definition.

> A **Standard** describes a state: one class of object as its
> population, plus named rules, each a predicate over one member's
> state.

> A **loop** drives a state toward a target state by iteratively taking
> prescribed actions and validating against prescribed standards.

The verbs are the contrast: a runbook is *invoked*, a standard
*describes*, a loop *drives*. A standard describes its state twice, in
prose and in checkers, and has no notion of moving toward it; that is
what a loop's check composes.

## The idealized parallel

What each peer looks like when fully built, from the two existing
bundles ([Doc-Type System](/doc-types/doc-type-system.md#the-bundle)):

| | Runbook | Standard | Loop |
|---|---|---|---|
| Family | every skill and agent definition | files typed `Standard` under `standards/` | files typed `Loop` under `loops/` |
| Definition | `definition.md` | `definition.md` | `definition.md` |
| Operations | read, write, do, override, never, args, report | population, rule | act, check, yield |
| Shape | the Reference chain: nodes and labeled edges | one population and its rules | acts, checks, and yields, iterated |
| Composition rule | any number of edges, coarsely ordered | one population, any number of rules, unordered | any number of acts and checks, ordered by the iteration; a set of yield conditions |
| Grain | instance-level | instance-level | instance-level |
| Encoding | `{Read …}` `{Run …}` `{If …, {…}}` spans in prose | frontmatter `population`; H2 rule, H2+H3 condition | one Mermaid block; H2 Acts, Checks, Yields, one entry per node |
| Generator and view | `scripts/chaingen` → `chains.txt` | `scripts/rulegen` → `standards.txt` | none; the Mermaid block in each instance is the view |
| Residual ledger | `residual-ledger.md` | `residual-ledger.md` | `residual-ledger.md` |
| Obligation card | `harness/runbook-conventions` | the Standard-Card catalog | `knowledge-organization/loop-conventions` |

## Where the peers are not yet parallel

Findings about the peers themselves, more important than the parked
items in Stale Findings and fixed as part of this work or right after.

- **Standard's operations are nouns.** Runbook's operations are seven
  verbs, Standard-Card's are four (define, audit, enforce, adopt), and
  Loop's are four (target, act, check, yield). Standard's are two nouns,
  population and rule. Every doc-type should be defined by a short list
  of simple verbs; overlap between doc-types is allowed.
- **Standard has no self-standing definition.** Fixed:
  [standard/definition.md](/doc-types/standard/definition.md) now opens
  with *a Standard describes a state*, in prose and in checkers, and
  the card pointer follows. The "question" idea still sits only on
  [Standard-Card](/doc-types/standard-card/definition.md#named-by-the-question),
  which is the card's concern, not the Standard's.
- **Audit and enforce are fused in practice.** Every auditor runs at
  pre-commit and every failure blocks, so no standard is aspirational
  today. A loop needs the audit cell without the gate; unfusing them is
  what makes "compose with standards" right.
- **Adopt is a loop.** The card's adopt cell, the helpers that bring a
  repo into compliance, is a loop by another name, rarely used because
  the system had no loop primitive. Once Loop exists, adopt should point
  at a Loop instance or leave the card.
- **The card's cells are two kinds of pointer.** Define and audit
  point inside the doc-type system, at the Standard and its auditors.
  Enforce points outside it, at a harness position, the hooks registry
  in `standards/harness/files.md`, where an audit runs as a gate;
  pre-commit and CI are runtimes, not loops, the way a workflow script
  is a JS file. Adopt points at a Loop instance when one exists and is
  empty otherwise. No Gate primitive is needed. A candidate for the
  checker loop, not a decision.
- **`Object` is a base nobody defines.** Every contract-shape
  pseudocode block writes `class Runbook(Object)`, `class
  Standard(Object)`, `class StandardCard(Object)`, and now `class
  Loop(Object)`, and no file defines `Object`. The pseudocode is one
  view of the system and must agree with itself across every bundle.
- **"Contract" is overloaded.** [Doc-Type](/doc-types/doc-type.md#contract)
  defines a contract as "everything a caller of an instance may rely
  on", yet a Standard is never called and a Loop is driven, not called.
  Either the word is widened or it is Runbook's word only.

## The first instance's standard

The doc-type system checker needs a standard for the target state of
the doc-type system, aspirational, audited, not gated. What it must
say, so far:

- **Minimal verbs.** The system is expressed in the fewest verbs and
  operations that suffice. Every doc-type added makes the system less
  comprehensible; the loop's job is to find the minimum set.
- **Two views that agree.** The simple verbs are one view of the world
  and the contract-shape pseudocode is another. They need not match one
  to one, but every pseudocode object across every bundle must make
  sense when put together, one `Object`, one `Condition`, one set of
  pointers between them.
- **Both forms in the doc-type, the graph in the instance.** A loop's
  bundle carries pseudocode and graph; a loop instance is drawn as a
  graph.

## What is settled about Loop

- **The definition** is the sentence above. Shorter is better; the
  definition carries the kind, the shape carries the parts. Runbook's
  sentence names no reports or effects for the same reason.
- **Yield is an operation, programmed, not derived.** An instance
  writes "yields when …"; the when is the instance's, and the doc-type
  says nothing about it: never, once at the end, periodically, every
  turn are all instances. Yield is a *set* of conditions, not a list:
  the loop yields when any one is met, where a list would be iterated
  through. Measurement is always possible, by
  deterministic code or by a model returning a value, so "yields when it
  cannot measure" was wrong and is dropped.
- **No rule on when a loop is worth writing.** Every piece of work can
  repeat; the user decides which loops to build. This conversation is a
  loop that yields every turn and will not run again, so it is not an
  instance.
- **Three verbs.** Loop's operations are read off its sentence: *act*,
  a prescribed action, a pointer at a runbook; *check*, a prescribed
  standard, a pointer at `Standard.audit`; *yield*, a programmed
  exit. Composition: any number of acts and checks, ordered by the
  iteration, and a set of yield conditions.
- **No target operation.** A target state is "this population passes
  these checks", so the checks carry it and population is already
  Standard's word. The description an acting agent needs is the
  standard's definition, the same standard whose audit the check runs:
  define tells the act what the target looks like, audit tells the
  check how far off it is. The findings an audit returns are the distance and
  the direction: each names a member and the rule it fails. This holds
  for indefinite targets too: an ideation loop's check is a model-judge
  standard with a rubric, and its findings are still findings.
- **A check composes `Standard.audit`, not the Standard.** A card's
  four cells are separable, and what a check points at is the audit
  cell: the auditors that measure a population against the Standard's
  rules and return findings. A check never points at the Standard
  document, which only defines, and never at the enforce cell, which
  gates. So a standard that is defined and audited but not gated is
  aspirational, which is what most loop targets are; a loop is out of
  standard until its last step, and many never get there.
- **Loop composes the other two peers, by pointer.** An act points at
  a runbook, whole: a runbook is one move. A check points at a
  standard's audit, `Standard.audit`, the one cell of the four: an audit
  is one measurement. A loop is moves and measurements iterated toward
  a target. This is the seed of the shape, and a guess about the
  encoding: an instance may be written largely as pointers, the way a
  card is, and the generator may stitch its view from the existing
  chains and rules tables.
- **A Loop instance is a document, not code.** A `.js` workflow file is
  a JS file. The Loop doc-type sits one level of abstraction above any
  runtime. When the `.claude/workflows/*.js` row of the registry is
  ruled, it is a runtime that runs loops, not the Loop family.
- **The family mirrors Standard's.** Instances are files typed `Loop`
  under a reserved root tree, `loops/`, flat until an instance needs a
  directory. Three edits register it, and they must agree: a `Loop`
  row in the Types table of
  [Document Types](/standards/knowledge-organization/document-types.md),
  a "Typed Loop → Under loops/" rule beside the Standard one, and a
  `Loop | loops` row in the rulings table of
  [Doc-Type System](/doc-types/doc-type-system.md#registry-rulings).
  A reserved root tree is not the general rule for doc-types; it is
  earned only when consumer repos reach for the instances by path, as
  they do for standards. Consumers keep their own `loops/` the way they
  keep their own `standards/`.

## Example instances

Held to test the shape, not to build:

- The software factory: a briefed GitHub issue in, a mergeable PR out,
  one yield to the user at the end.
- A repo-conversion loop: drive the Markdown tree toward smaller,
  one-concern, well-linked files; yield when the verifiers pass.
- A code-quality loop: drive modules toward a complexity bound checked
  by deterministic counts or stochastic agents.
- An ideation loop: seeded with a vision, generate and self-evaluate
  ideas, yield to the user periodically, resume on their feedback.

The first instance, built after the doc-type, is a **doc-type system
checker**. It describes the intended world, every doc-type as a few
simple verbs plus a composition rule, and checks that world against the
one we live in, dev-playbook and its workspace. Through the three verbs:
act is sending out agents to find inconsistencies, the kind the peer
section above already holds, and ideating fixes; check is a
self-consistency standard applied by the loop's own judgment; yield is
{every K rounds}, to the user, resuming on their feedback. Its goal at
this level is not to transform the system but to align with the user on
a self-consistent target end state. Chosen over a Markdown complexity
loop because that would open a new front; this one stays on the work at
hand. Not the software factory: as specified today it needs a loop to
clean it up, which is a different loop from the one that runs it, and
either is too big for a first test.

## Prior art

Act and check are industry-standard under other names: control loops
and Kubernetes reconciliation (desired state, observed state, a
controller closing the gap; desired state written as a spec, which
agrees with dropping target), evaluator-optimizer and generator-critic
patterns, PDCA, OODA, red-green-refactor. Yield is where the field has
no consensus (interrupt, checkpoint, a person in the loop); the generator
sense, hand control out and resume at the same point, is the most
precise word available. One difference on purpose: industry loops are
code; a Loop instance is a document that points at runbooks and
standards, and the runtime is whatever runs it. From memory, not a
fresh search.

## Acronyms

None.
