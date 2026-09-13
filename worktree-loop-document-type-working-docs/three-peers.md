---
type: General-Sheet
title: Three Peers
description: Runbook, Standard, and Loop as peer doc-types — their one-sentence definitions, the parallel between them today, and where Loop stands
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

> A **standard** is a normative target: a state some class of object
> is held to, that a reviewer or a lint could cite to reject work.

> A **loop** drives a state toward a target state by iteratively taking
> prescribed actions and validating against prescribed standards.

The verbs are the contrast: a runbook is *invoked*, a standard is
*held to*, a loop *drives*. A standard is defined, audited, enforced,
and adopted, and has no notion of moving toward its state; its audit is
what a loop's check composes.

## The parallel today

What each peer looks like on disk, from the three bundles ([Doc-Type System](/doc-types/doc-type-system.md#the-bundle)):

| | Runbook | Standard | Loop |
|---|---|---|---|
| Family | every skill and agent definition | one directory per Standard under `standards/` | files typed `Loop` under `loops/` |
| Definition | `definition.md` | `definition.md` | `definition.md` |
| Kinds | Skill, Agent definition | Standard-Card, Standard-Ruleset | Loop |
| Operations | read, write, do, override, never, args, report | define, audit, enforce, adopt | act, check, yield |
| Shape | the Reference chain: nodes and labeled edges | four cells; under Define, one population and its rules | acts, checks, and yields, iterated |
| Composition rule | any number of edges, coarsely ordered | one cell each, any number of pointers; one population, any number of rules per ruleset | any number of acts, checks, and yields, in iteration order |
| Encoding | `{Read …}` `{Run …}` `{If …, {…}}` spans in prose | card: H2 per cell, one pointer per bullet; ruleset: frontmatter `population`, H2 rule, H2+H3 condition | one Mermaid block; H2 Acts, Checks, Yields, one entry per node |
| Generator and view | `scripts/chaingen` → `chains.txt` | `scripts/cardgen` → `cards.txt`; `scripts/rulegen` → `standards.txt` | none; the Mermaid block in each instance is the view |
| Residual ledger | `residual-ledger.md` | `residual-ledger.md` | `residual-ledger.md` |
| Obligation card | `harness/runbook-conventions` | `standard/`, the Meta-Standard | `knowledge-organization/loop-conventions` |

## The first instance's standard

The first instance needs a standard for the target state of
the doc-type system, aspirational, audited, not gated. What it must
say, so far:

- **Minimal verbs.** An objective, not a predicate: the fewest verbs
  and operations that suffice, descended one accepted merge at a time.
- **Two views that agree.** The simple verbs are one view of the world
  and the contract-shape pseudocode is another. They need not match one
  to one, but every pseudocode object across every bundle must make
  sense when put together, one `Object`, one `Condition`, one set of
  pointers between them.
- **Both forms in the doc-type, the graph in the instance.** A loop's
  bundle carries pseudocode and graph; a loop instance is drawn as a
  graph.

## Loop today

- **The definition** is the sentence above. Shorter is better; the
  definition carries the kind, the shape carries the parts. Runbook's
  sentence names no reports or effects for the same reason.
- **Yield is an operation, programmed, not derived.** An instance
  writes "yields when …"; the when is the instance's, and the doc-type
  says nothing about it: never, once at the end, periodically, every
  turn are all instances. Measurement is always possible, by
  deterministic code or by a model returning a value.
- **No rule on when a loop is worth writing.** Every piece of work can
  repeat; the user decides which loops to build. This conversation is a
  loop that yields every turn and will not run again, so it is not an
  instance.
- **Three verbs.** Loop's operations are read off its sentence: *act*,
  a prescribed action, a pointer at a runbook; *check*, a prescribed
  standard, a pointer at `Standard.audit`; *yield*, a programmed
  exit. Composition: any number of acts, checks, and yields, in
  iteration order.
- **No target operation.** A target state is "this population passes
  these checks", so the checks carry it. The findings an audit returns
  are the distance and the direction: each names a member and the rule
  it fails, and the applying act reads nothing else
  ([Specifying a Loop](/worktree-loop-document-type-working-docs/specifying-a-loop.md#the-loop-that-proposes)).
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
  a target.
- **A Loop instance is a document, not code.** A `.js` workflow file is
  a JS file. The Loop doc-type sits one level of abstraction above any
  runtime. When the `.claude/workflows/*.js` row of the registry is
  ruled, it is a runtime that runs loops, not the Loop family.
- **The family mirrors Standard's.** Instances are files typed `Loop`
  under `loops/`, registered in
  [Document Types](/standards/knowledge-organization/document-types.md)
  and [Doc-Type System](/doc-types/doc-type-system.md#registry-rulings).
  Consumers keep their own `loops/` the way they keep their own
  `standards/`.

## Example instances

Held to test the shape, not to build:

- The software factory: a briefed GitHub issue in, a mergeable PR out,
  one yield to the user at the end.
- A repo-conversion loop: drive the Markdown tree toward smaller,
  one-concern, well-linked files; yield when the verifiers pass.
- A code-quality loop: drive modules toward a complexity bound checked
  by deterministic counts or stochastic agents.

The first instance is a loop over the doc-type system; its design is
[ROOT.md](/worktree-loop-document-type-working-docs/ROOT.md#planned).

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
