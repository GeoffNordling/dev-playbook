---
type: Vocabulary
title: Vocabulary
description: The workspace's established vocabulary — the canonical terms to use exactly
---

# Vocabulary

The workspace's established vocabulary — the canonical terms every doc uses exactly, so shared language stays consistent. Extensible: terms are added here as they're pinned down.

## Language

### Legibility

The words the user and the AI meet on
([System Legibility](/docs/system-legibility.md)).

**Slop**
Output that diverges from the user's intent, or that the user cannot read.

### Governance

How a Standard's rules are decided, in the terms of the Standard's
shape ([Population and Rules](/doc-types/standard/contract-shape.md)).

**Rule**
One heading of a Standard, its predicate, and its trailer: an id, `<family>.<slug>`, and a kind, deterministic or stochastic.

**Verifier**
What decides one rule over a member and returns findings: a check or a judge. It reads and never writes.

**Check**
A verifier for a deterministic rule: a function registered under the rule's id, which `playbook check` runs, or a tool such as ruff registered by its hook.
_Avoid_: detector, lint.

**Judge**
A verifier for a stochastic rule: a model prompted with the rule's predicate.

**Finding**
What a verifier returns for a member that fails a rule: the member, the rule's id, and a message.

**Gate**
A point where findings block work: pre-commit, pre-push, or CI.
_Avoid_: audit, enforcement, venue.

**Draft Standard**
A file typed Standard inside a leaf workstream, whose rule ids take the workstream's directory name as their family. It is wired to a stint's `--check` and never to a gate, so its rules may fail at any time. It is the workstream's target; on accept it is deleted, or moved under `standards/` and wired to a gate.
_Avoid_: candidate Standard, proto-Standard.

**Zero findings**
Every verifier of a specification, run against a state, returns nothing: the state is in the target state, up to judge error.

### Specification

How a target is written down, as predicates and as one state that
satisfies them
([Doc-Type](/standards/doc-type/doc-type.md)).

**Predicate**
A statement about one member at one moment that is true or false. It defines a set: the states where it holds.

**Condition**
The predicate under which a part applies: for a rule, the rule it sits under; for a runbook edge or a loop step, when it fires. Where the condition is false, the part is not evaluated.
_Avoid_: guard.

**Population**
The class of targets a Standard's rules range over.

**Specification**
A set of predicates taken together, which defines the intersection of their sets; a Standard is a specification written as a file over a population. Short form: spec.

**Target state**
The set of states that satisfy a specification: a set, never one state.

**Objective**
A scalar to minimize, such as the fewest verbs, that ranks the states which satisfy the predicates and is never one of them. It is descended one proposed step at a time, each step accepted or vetoed by the user.

**Reference model**
One state that satisfies a specification, drawn out: a witness, as an example is to a property in property-based testing. The doc-type system's is [Reference Model](/doc-types/reference-model.md).

### Doc-types

The parts of the doc-type system
([Reference Model](/doc-types/reference-model.md)).

**Doc-type**
A contract for one kind of file: a directory `doc-types/<name>/` whose parts a check reads out of each instance. The [Doc-Type Registry](/registries/doc-types.md) joins each one to the OKF type or harness members its instances are.
_Avoid_: document type.

**DocType**
The base class of the reference model: a class extends it when its instance is one markdown file of that type.

**Part**
A class nested inside a DocType, such as a runbook's Edge or a Standard's Rule. A part has no verbs.

**Why**
A block that opens `> **Why.**`: the argument for the rule whose trailer it follows, or for the file when it ends the opening prose. It holds no predicate.

**Encoding**
A doc-type's map from written form to rows: which marks in a file of that type carry which primitives. It defines the doc-type's extractor.

**Primitive**
One named node type or relation type that a doc-type owns, such as the runbook's `reads`, or a bedrock relation such as `contains`.

**Residual**
What a doc-type's selected primitives cannot express about one of its documents, recorded in that doc-type's residual ledger ([the doc-type build loop](/workstreams/system/see/fact-base/WORKSTREAM.md#terms)).

### Fact base

The one object that every view of a checkout is selected from
([the See workstream](/workstreams/system/see/WORKSTREAM.md)).

**Fact base**
A set of nodes and a set of edges, written by code to one file per checkout. Every view is a selection from it.

**Extractor**
A deterministic function from one artifact to rows of the fact base. A bedrock extractor parses a format someone else fixed; a doc-type extractor is the function that the doc-type's encoding defines.
_Avoid_: generator.

**Node**
One thing in the fact base, with an identity, a node type, a provenance, and attributes.

**Edge**
One relation in the fact base from a source node to a target node, with a relation type and, where the source declares them, an order, a condition, and a detail quoted from the source.

**View**
A selection of nodes and edges from the fact base, plus a renderer. A view drops rows and never adds or converts one.

### Workstreams and loops

How work advances, with the user present or not
([Running a Stint](/guides/running-a-stint.md)).

**Workstream**
One line of work, an intent and its history, kept in a directory whose head file is typed Workstream. It ends when the user accepts or deletes it.

**Loop**
A shape of act, verification, and yield steps, defined once in a file typed Loop under `loops/`. It holds no goal and no history, and one loop drives many workstreams.

**Yield**
A loop's programmed exit to a receiver: another loop, the principal, or the user.

**Stint**
A bounded spend of effort that advances one leaf workstream, with a loop and a driver chosen for it, toward the rules of the workstream's draft Standards it targets, if any. An attended stint has the user in it; an unattended stint runs in sealed containers with no user, by the `stint` command, and ends by yielding to the user.

**Driver**
The program that runs a stint's loop: it starts each iteration, reads what the iteration reports, and stops the stint.

**Principal**
The top-level entity of a stint, which owns the plan and rules on the reports of the iterations and the reviewer. In an attended stint it is the user and the top-level agent together; in an unattended stint, the top-level agent alone.

**Iteration**
One fresh-context agent that does one task of a stint's plan, commits, and exits.

**Segment**
The tasks of a stint's plan from one checkpoint to the next.

**Checkpoint**
The review point at the end of a segment: a reviewer reads the segment's work against the plan, and the principal revises the plan.

### Documentation sets

How concept documents group
([Documentation Sets](/standards/knowledge-organization/documentation-sets/documentation-sets.md)).

**Documentation set**
The concept documents one `index.md` owns, related as a set by the index's listing; a directory with its own `index.md` is a set nested in its parent's.

**Concern**
The boundary a document or a set declares: a document's frontmatter `description`, a set's index introduction. A body is judged against it.

### File roles

The two axes a repository file sits on, its role and its content
([OKF Frontmatter](/standards/knowledge-organization/okf-frontmatter.md)).

**Concept document**
Prose a reader loads to understand something. It carries OKF frontmatter, and a check reads its type.

**OKF type**
The `type` value in a concept document's frontmatter, a label from the [OKF Type Registry](/registries/okf-types.md) or a repo's local declaration. It is not a doc-type: an OKF type names a kind of document, and only some kinds have a doc-type.
_Avoid_: document type.

**Harness-owned file**
A file a tool consumes as configuration or runs as code or instructions: every non-`.md` file, plus the Claude Code file set the [Harness File Registry](/registries/harness-files.md#members) enumerates. It carries no OKF frontmatter.

**Procedure**
The steps of one job: its trigger, its target, the order of the steps, the conditions it branches on, the commands it issues, when it stops, what it reports. It binds one actor for the length of one run.

**Runbook**
An invocable command written as documentation: a skill or an agent definition. It is invoked by name, args in, a report out, effects on state in between, and its body is natural imperative English commanding the executing agent ([Runbook](/doc-types/runbook/definition.md)).

**Context file**
Prose the harness injects into agent context, read and never invoked: a `CLAUDE.md` at any scope and every `rules/*.md` ([Claude Code Files](/standards/harness/files.md)).
