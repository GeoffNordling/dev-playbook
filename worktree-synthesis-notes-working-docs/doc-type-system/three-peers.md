---
type: General-Sheet
title: Three Peers
description: Runbook, Standard, and Loop as peer doc-types — their one-sentence definitions, the parallel between them in the target state, and where Loop stands
---

# Three Peers

Runbook, Standard, and Loop are three doc-types under one kind,
[Doc-Type](/doc-types/doc-type.md): operations plus a composition rule,
fixing a shape every instance fills. This member records the parallel
between them. It is speculative, per
[Doc-Type System](/worktree-synthesis-notes-working-docs/doc-type-system/ROOT.md).

## The three sentences

Each doc-type is one sentence, quoted from its directory:
[Runbook](/doc-types/runbook/definition.md),
[Standard](/doc-types/standard/definition.md),
[Loop](/doc-types/loop/definition.md).

> A **runbook** is an invocable command written as documentation: a
> skill or an agent definition.

> A **standard** is a normative target: a state some class of object
> is held to, that a reviewer or a lint could cite to reject work.

> A **loop** drives a state toward a target state by iteratively taking
> prescribed actions and validating against prescribed standards.

The verbs are the contrast: a runbook is *invoked*, a standard is
*held to*, a loop *drives*. A standard holds and has no notion of
moving toward its state; a loop's check audits against it.

## The parallel

What each peer looks like on disk in the target state, per
[Reference Model](/worktree-synthesis-notes-working-docs/doc-type-system/reference-model.md),
each directory laid out as
[Doc-Type System](/doc-types/doc-type-system.md) says:

| | Runbook | Standard | Loop |
|---|---|---|---|
| Family | `skills/<name>/SKILL.md`, `agents/<name>.md` | `standards/<name>/<topic>.md` | `loops/<name>.md` |
| Operations | read, write, do, override, accept, report | hold | act, check, yield |
| Parts | Edge: operation, target, condition, banned | Rule: id, kind, predicate, condition | Act, Check, Yield: pointer, condition |
| Composition rule | any number of edges, coarsely ordered | one population, any number of rules | any number of steps, in iteration order |
| Encoding | `{Read …}` `{Run …}` `{If …, {…}}` spans in prose | frontmatter `population`; H2 rule; H3 rule under its condition; id and kind after the predicate | one Mermaid block; H2 Acts, Checks, Yields, one entry per step |
| Conventions Standard | `harness/runbook-conventions` | `standard/`, the Meta-Standard | `knowledge-organization/loop-conventions` |

## The first instance's standard

The
[specification](/worktree-synthesis-notes-working-docs/doc-type-system/specification/index.md)
is the first instance's standard, written as working-set members
until Standard has its new shape. What it does not hold, because a
spec is predicates only: the objective, complexity minimized,
lexicographic, residuals then doc-types then verbs then shared verbs.
Whether Loop gains a part for it is open, in
[ROOT.md](/worktree-synthesis-notes-working-docs/loop/ROOT.md#planned).

## Loop today

- **The definition is the sentence above.** Shorter is better; the
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
  standard, a pointer at a Standard; *yield*, a programmed
  exit. Composition: any number of acts, checks, and yields, in
  iteration order.
- **No target operation.** A target state is "this population passes
  these checks", so the checks carry it. The findings an audit returns
  are the distance and the direction: each names a member and the rule
  it fails, and the applying act reads nothing else
  ([Specifying a Loop](/worktree-synthesis-notes-working-docs/loop/specifying-a-loop.md#the-loop-that-proposes)).
- **A check points at a Standard; the toolchain audits.** The Standard
  holds the rules; `audit` is the toolchain's, and it routes each rule
  id to its verifier and returns findings. Which boundaries also run
  those ids is the boundaries' wiring, so a Standard no repo boundary
  runs is aspirational, which is what most loop targets are; a loop is
  out of standard until its last step, and many never get there.
- **Loop composes the other two peers, by pointer.** An act points at
  a runbook, whole: a runbook is one move. A check points at a
  Standard, whole: an audit is one measurement. A loop is moves and
  measurements iterated toward a target.
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
[Doc-Type System](/worktree-synthesis-notes-working-docs/doc-type-system/ROOT.md#planned).

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
