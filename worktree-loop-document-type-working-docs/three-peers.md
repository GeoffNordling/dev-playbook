---
type: General-Sheet
title: Three Peers
description: Runbook, Standard, and Loop as peer doc-types — their one-sentence definitions, the parallel structure between them, and what is settled about Loop so far
---

# Three Peers

Runbook, Standard, and Loop are three doc-types under one kind,
[Doc-Type](/doc-types/doc-type.md): operations plus a composition rule,
fixing a shape every instance fills. This member records the parallel
between them and what the Loop design has settled, so the work survives a
context reset. It is speculative, per
[ROOT.md](/worktree-loop-document-type-working-docs/ROOT.md).

## The three sentences

Each doc-type is one sentence. Runbook's and Standard's are the ones
their bundles carry today; Loop's is new.

> A **runbook** is an invocable command written as documentation: a
> skill or an agent definition.

> A **Standard** is the kind a card's Define cell points at: one class
> of object as its population, plus named rules, each a predicate over
> one member's state.

> A **loop** drives a state toward a target state by iteratively taking
> prescribed actions and validating against prescribed standards.

The verbs are the contrast: a runbook is *invoked*, a standard *binds*
(or, in the intended sentence, *answers*), a loop *drives*. Standard's
sentence is the weak one: it defers to the card instead of standing
alone; see
[Stale Findings](/worktree-loop-document-type-working-docs/stale-findings.md).

## The idealized parallel

What each peer looks like when fully built, from the two existing
bundles ([Doc-Type System](/doc-types/doc-type-system.md#the-bundle)):

| | Runbook | Standard | Loop |
|---|---|---|---|
| Family | every skill and agent definition | files typed `Standard` under `standards/` | files typed `Loop` under `loops/` |
| Definition | `definition.md` | `definition.md` | `definition.md` |
| Operations | read, write, do, override, never, args, report | population, rule | target, act, check, yield |
| Shape | the Reference chain: nodes and labeled edges | one population and its rules | open |
| Composition rule | any number of edges, coarsely ordered | one population, any number of rules, unordered | one target, any number of acts, checks, and yields, ordered by the iteration |
| Grain | instance-level | instance-level | open |
| Encoding | `{Read …}` `{Run …}` `{If …, {…}}` spans in prose | frontmatter `population`; H2 rule, H2+H3 condition | open |
| Generator and view | `scripts/chaingen` → `chains.txt` | `scripts/rulegen` → `standards.txt` | `scripts/loopgen` → open |
| Residual ledger | `residual-ledger.md` | `residual-ledger.md` | `residual-ledger.md` |
| Obligation card | `harness/runbook-conventions` | the Standard-Card catalog | open |

## Where the peers are not yet parallel

Findings about the peers themselves, more important than the parked
items in Stale Findings and fixed as part of this work or right after.

- **Standard's operations are nouns.** Runbook's operations are seven
  verbs, Standard-Card's are four (define, audit, enforce, adopt), and
  Loop's are four (target, act, check, yield). Standard's are two nouns,
  population and rule. Every doc-type should be defined by a short list
  of simple verbs; overlap between doc-types is allowed.
- **Standard has no self-standing definition.**
  [standard/definition.md](/doc-types/standard/definition.md) opens by
  deferring to the card ("the kind a card's Define cell points at").
  The intended sentence, *a standard answers a question about how a
  specific thing is done*, lives nowhere; the "question" idea sits only
  on [Standard-Card](/doc-types/standard-card/definition.md#named-by-the-question).
  Add the sentence and let population-and-rules be the shape's sentence.
- **"Contract" is overloaded.** [Doc-Type](/doc-types/doc-type.md#contract)
  defines a contract as "everything a caller of an instance may rely
  on", yet a Standard is never called and a Loop is driven, not called.
  Either the word is widened or it is Runbook's word only.

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
- **Four verbs.** Loop's operations are read off its sentence: *target*,
  the state driven toward, one per loop; *act*, a prescribed action, a
  pointer at a runbook; *check*, a prescribed standard, a pointer at a
  Standard; *yield*, a programmed exit. Composition: one target, any
  number of acts, checks, and yields, ordered by the iteration.
- **Loop composes the other two peers.** *Prescribed actions* are what
  runbooks are; *prescribed standards* are what Standards are. A runbook
  is one move, a standard is one measurement, a loop is moves and
  measurements iterated toward a target. This is the seed of the shape,
  and a guess about the encoding: an instance may be written largely as
  pointers, the way a card is, and the generator may stitch its view
  from the existing chains and rules tables.
- **A Loop instance is a document, not code.** A `.js` workflow file is
  a JS file. The Loop doc-type sits one level of abstraction above any
  runtime.
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

The first instance, built after the doc-type, is a small Markdown
complexity loop: deterministic and model-judge detectors, run to clean
up this repo's Markdown. Not the software factory: as specified today it
needs a loop to clean it up, which is a different loop from the one that
runs it, and either is too big for a first test.

Only the definiteness of the target state varies across them, and that
sets the rest: the kind of check and the yield policy. The autonomy
scale of [Working in Loops](/docs/working-in-loops.md#the-autonomy-scale)
falls out of one property of the instance.

## Open questions

- The shape: the four verbs and the composition rule in prose and one
  screen of pseudocode.

## Acronyms

None.
