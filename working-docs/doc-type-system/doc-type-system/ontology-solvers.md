---
type: General-Sheet
title: Ontology Solvers
description: Ontology solvers against the doc-type system — the fact base as an ABox, the doc-types as a TBox, a Standard's rules as shapes, a type checker as the same solver over program text, the route from the fenced pseudocode to real Python, and the document and domain ontologies another repository splits into, none of it decided
---

# Ontology Solvers

The record of one topic from a synthesis session on 2026-09-14: what
an ontology solver is in industry terms, how the doc-type system and
the fact base map onto one, the route that turns the reference
model's pseudocode into something a solver reads, and the two
ontologies, document and domain, that extending the system to another
repository shows. Speculative, per
[Doc-Type System](/working-docs/doc-type-system/doc-type-system/ROOT.md).
Nothing here is decided; the one question it raises is in the top
root's [Open](/working-docs/doc-type-system/ROOT.md#open).

## Source

Frank Coyle, "Agents and Ontologies," recorded in mission-control at
`ideas/ontology-guardrails.md` on 2026-07-27. No link or venue was
recorded. The claim: a formal ontology outside the model as logical
guardrails, probabilistic reasoning inside, logic outside. Pydantic at
the door, ontology at the ledger; a failed check loops back to the
model or escalates to the owner. That last sentence is act, check,
yield.

## The theory, in industry terms

- **ABox.** The facts, each a triple: subject, predicate, object. The
  fact base is an ABox.
- **TBox.** The schema: classes, properties with a domain and a range,
  a class hierarchy. RDFS. The doc-types are a TBox: `Runbook`,
  `Standard`, `Loop` are classes; the ten verbs are properties with
  domains and ranges.
- **Axioms.** OWL adds what the schema cannot say: functional
  properties (an order has at most one refund), disjoint classes
  (customer and support rep), enumerated classes (a status is one of
  three values), transitive properties. All of these sit in OWL RL,
  the polynomial profile.
- **The reasoner.** Computes the closure and checks consistency. Its
  base answer is one boolean; a justification, the minimal axiom set
  behind a contradiction, is available and slower.
- **SHACL.** Closed-world validation, a shape per node type, a report
  naming node, shape, property, and message per violation. A Standard's
  rules are shapes; audit is the SHACL run; a violation is a finding
  with a receipt.
- **The open-world caveat.** An OWL reasoner treats an unstated fact
  as unknown, not false, and infers around a missing field. Checks
  that must report a missing thing go in shapes.
- **Cost.** Sub-second at this scale. Rules plus fixpoint, not
  search; nothing like a MIP.

## Pseudocode and type checkers

A type checker is an ontology solver over program text. Mypy reads
class declarations as a TBox and every expression as an assertion,
and a type error is a consistency violation with a line number. The
difference from an ontology engine is what the assertions range over:
mypy checks the source, the engine checks the data.

Route proposed for the pseudocode: the fenced block in
[Reference Model](/working-docs/doc-type-system/doc-type-system/reference-model.md)
becomes real Python that never runs. The bare names,
`operations = {read, write, do}` and
`kind: deterministic | stochastic`, become an `Enum` or `Literal`, and
the block is a module of dataclasses with no bodies. Mypy checks the
declarations against themselves. A script introspects the classes with
`typing.get_type_hints` and emits the OWL classes, properties, and
cardinality shapes. The `# rules:` lines become predicates, as Python
functions over loaded instances or as shapes. A bedrock extractor
pulls the fence out of the markdown the way doctest pulls examples out
of a docstring. The words around the block are the stochastic
remainder; the block sits at zero.

## The loop the solver enables

Check: extract the fact base, run the solver, findings are
inconsistencies and violations. Act: fix what a finding names. Yield:
when a finding needs a judgment. Which thing the act fixes is the
fork: the repo, which is the loop that brings a repo to a Standard,
with the ontology as that Standard; or the pseudocode, which is
[the doc-type build loop](/doc-types/doc-type.md#the-doc-type-build-loop)
with the findings the user rules the model's fault as its residual.
The solver never reports a missing class. That comes from residuals,
as today.

## Two ontologies

The extension to other repositories, a job search, a lemonade stand,
shows two ontologies, not one. The **document ontology** is the
doc-type system: what kinds of files exist and how they relate, the
same in every repo, declared once in dev-playbook. A **domain
ontology** is per repo: `Job`, `Company`, `Application`, `Interview`.
A Standard's population ranges over domain classes; a loop's checks
read domain facts. dev-playbook has no domain layer because its domain
is itself.

The agent's proposal: Python and mypy author the document ontology,
emitting OWL and SHACL by introspection the way Pydantic emits JSON
Schema; domain ontologies are declared files in the emitted form from
the start, since an agent writes them from a conversation and the
generic toolchain must read them without importing code; one engine
checks both over one fact base per checkout. The case for the engine
at the domain layer: schema as data, existing vocabularies such as
schema.org's `JobPosting` and `Organization`, and open-world fit for
partial domain knowledge.

## Acronyms

- **ABox** — Assertion box: the facts of a knowledge base.
- **MIP** — Mixed-Integer Programming.
- **OWL** — Web Ontology Language.
- **RDFS** — Resource Description Framework Schema.
- **SHACL** — Shapes Constraint Language.
- **TBox** — Terminology box: the schema of a knowledge base.
