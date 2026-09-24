---
type: General-Sheet
title: System Brief
description: The doc-type system and the fact base as one reader holds them after one pass through the workstream — the doctrine, the four doc-types and their pseudocode, the two written forms, the encoding, the fact base and its views, the build loop, and the two ontologies a consumer repo splits into, each with the file that carries it
---

# System Brief

What one session learned of the doc-type system before turning to
story-forge, kept so the next session reads this file and the files
it names instead of the whole workstream again. Speculative, per
[Story-Forge Simulation](/workstreams/doc-type-system/story-forge-simulation/WORKSTREAM.md).
Every claim below is the named file's, restated in one clause; where
the two differ, the named file is right.

## The doctrine

[System Legibility](/docs/system-legibility.md) is the why. The user
understands the systems they own without reading all of them. Slop
defeats that, in two forms: output that diverges from intent, and
output that is right but illegible, greppable by a model and opaque to
the user. Natural-language instruction is stochastic, so the remedy is
deterministic forcing functions at the CLOA, the Correct Level of
Abstraction: the highest level at which the user can trust the AI and
the lowest at which the AI needs the user, moving per system and per
goal. Too low is rubber-stamping; too high is vibe coding. Two ideas
from that file carry the rest: documentation is code, a markdown file
being fuzzy code with the LLM as its stochastic compiler; and the
bedrock of determinism is where documentation stops and code begins,
with declared abstractions descending toward it layer by layer.

## The four doc-types

A doc-type gives a markdown file what code has: a type, a contract, an
API of verbs, and a shape ([Doc-Type](/doc-types/doc-type.md)). Four
are built, each one directory under `doc-types/` with the same four
files, `definition.md`, `contract-shape.md`, `encoding.md`, and
`residual-ledger.md`
([Doc-Type System](/doc-types/doc-type-system.md)):

| DocType | Verbs | Instances live in |
| --- | --- | --- |
| Runbook, invoked | read, write, do, override, accept, report | skills and agent definitions |
| Standard, held to | hold | `standards/` |
| Guide, instructs | instruct | `guides/` |
| Loop, drives | act, check, yield | `loops/` |

The whole picture is one block of pseudocode,
[Reference Model](/workstreams/doc-type-system/doc-type-system/reference-model.md#the-language):
each doc-type a Python class extending `DocType`, its parts nested
inside it (`Runbook.Edge`, `Standard.Rule`, `Loop.Act`), the
toolchain four lines below it. The block is pinned to the four
`contract-shape.md` files by `tests/test_pseudocode_sync.py`.
[Ontology Solvers](/workstreams/doc-type-system/doc-type-system/ontology-solvers.md)
proposes making it real Python that never runs, checked by mypy and
introspected into a TBox. The rules every doc-type is held to are the
Standard [Doc-Type](/standards/doc-type/doc-type.md).

## Both written forms

A target state is written twice, never as a linear description plus
actions: as a reference model, one witness state in pseudocode, the
picture the user thinks in; and as a specification, falsifiable
predicates over the whole set of states. The user's words, in
[Personal Notes](/workstreams/doc-type-system/doc-type-system/personal-notes.md):
a reference model shows one point in the distribution, the predicates
describe the distribution. A Standard is a spec written as a file over
a population; each rule is a predicate with an id in the form
`<family>.<slug>`, a kind, deterministic where a script decides it and
stochastic where a judge with an error rate does, an optional
condition, and a why. The words are the synthesis workstream's
[Terms](/workstreams/doc-type-system/WORKSTREAM.md#terms), one meaning
each, and the seam between logic and statistics is drawn there: a
predicate defines a set, an act is a draw from a distribution, a loop
changes what the next draw is given.

## The encoding

The seam between prose and parser is
[Nodes and Edges Encoding](/doc-types/runbook/encoding.md). In a
runbook, braces mark the one machine-readable unit in a sentence:
`{Read [issue shapes](…); the brief formats…}` yields one `reads` edge,
and everything past the first `;` is annotation for the executing
agent. One sentence serves both readers. Unbraced prose is never an
edge. That rule is the bedrock made concrete.

## The fact base

[Fact Base](/workstreams/doc-type-system/fact-base/fact-base.md)
turns the encodings into one deterministic object per checkout: nodes
and edges, every row with a receipt, the extractor and the line that
yielded it. Two kinds of fact only. Extractable, a parser settles it:
a file exists, a link points somewhere, a module imports a module.
Declared, an author wrote it in a fixed shape: a frontmatter field, a
chain span, a rule, an index row. Anything a model would infer is
neither. Views are pure selections, seven of them: containment tree,
catalog, dependency graph, control flow, data flow, cross-reference
matrix, interface card. The record is not the behavior: a `reads` edge
says the text instructs a read, not that the agent obeyed. The one
hand simulation so far is
[Ralph Fact Base](/workstreams/doc-type-system/fact-base/fact-base-ralph.md),
nineteen nodes and forty-one edges in `fact-base-ralph.json`, whose
payoff was its five gaps: the facts the question needed that no
extractor reached, one of them a prompt string inside `ralph-loop.js`,
whose fix is structural, code carries no prose.

## The build loop

The doc-type build loop is EM
([The build loop runs over every object](/workstreams/doc-type-system/fact-base/fact-base.md#the-build-loop-runs-over-every-object)).
E-step: re-express the family in the current primitives. Residual:
what will not fit, written to that doc-type's ledger. M-step: propose
one primitive that shrinks it. Stop at the inflection point, as with k
in k-means. Above the bedrock the M-step invents a primitive and costs
a contract shape and a parser; below it the M-step maps one from a
vocabulary the language already fixes, `open(path, "w")` becoming
`writes`, and costs one extractor. The method for a new subsystem is
the fact base head file's Planned item
[Simulations by hand](/workstreams/doc-type-system/fact-base/WORKSTREAM.md#planned):
enumerate the questions a person asks, hand-write one fact base in the
viewer's envelope with a receipt on every row, firm the views, record
the residuals, and write no code until the simulations cover the use
cases.

## Two ontologies

[Ontology Solvers](/workstreams/doc-type-system/doc-type-system/ontology-solvers.md#two-ontologies)
shows that extending the system to another repository splits it in
two. The document ontology is the doc-type system, the same in every
repo, declared once in dev-playbook. A domain ontology is per repo,
`Job`, `Company`, `Application`; a Standard's population ranges over
its classes and a loop's checks read its facts. dev-playbook has no
domain layer because its domain is itself.
[Across the workspace](/workstreams/doc-type-system/fact-base/fact-base.md#across-the-workspace)
gives the rule: a consumer repo imports the schema and the bedrock
extractors unchanged and adds its own node types, its own file-format
extractors, and any doc-type of its own; it never redefines a
primitive dev-playbook owns. Who owns a residual a consumer raises is
open.

## Reading order for a new session

1. This file.
2. [Synthesis Workstream](/workstreams/doc-type-system/WORKSTREAM.md),
   for the terms.
3. [Ralph Fact Base](/workstreams/doc-type-system/fact-base/fact-base-ralph.md)
   and its JSON, for the row shape a simulation writes.
4. [Story-Forge Survey](/workstreams/doc-type-system/story-forge-simulation/story-forge-survey.md),
   for the specimen.

## Acronyms

- **API** — Application Programming Interface.
- **CLOA** — Correct Level of Abstraction.
- **EM** — Expectation-Maximization.
- **LLM** — Large Language Model.
- **TBox** — Terminology box: the schema of a knowledge base.
