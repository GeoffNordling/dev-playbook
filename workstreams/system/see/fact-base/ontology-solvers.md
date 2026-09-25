---
type: General-Sheet
title: Ontology Solvers
description: The ontology of the fact base in industry terms — the fact base as an ABox, the doc-types as a TBox, a Standard's rules as shapes, the one solver that checks them, and the document and domain ontologies another repository splits into, none of it decided
---

# Ontology Solvers

The record of one topic from a synthesis session on 2026-09-14: what
an ontology solver is in industry terms, how the doc-type system and
the fact base map onto one, and the two ontologies, document and
domain, that extending the system to another repository shows. The
ontology is part of the fact base, and the doc-type system enables it:
without doc-types there is no ontology to solve. Speculative, per
[Fact Base Workstream](/workstreams/system/see/fact-base/WORKSTREAM.md).
Nothing here is decided.

## The source is one recorded talk

Frank Coyle, "Agents and Ontologies," recorded in mission-control at
`ideas/ontology-guardrails.md` on 2026-07-27. No link or venue was
recorded. The claim: a formal ontology outside the model as logical
guardrails, probabilistic reasoning inside, logic outside. Pydantic at
the door, ontology at the ledger; a failed check loops back to the
model or escalates to the owner. That last sentence is act, verify,
yield.

## The theory, in industry terms

- **ABox** ([Terms](/workstreams/system/see/fact-base/WORKSTREAM.md#terms)).
  The fact base is an ABox.
- **TBox** ([Terms](/workstreams/system/see/fact-base/WORKSTREAM.md#terms)).
  RDFS. The doc-types are a TBox: `Runbook`, `Standard`, `Guide`,
  `Loop`, and `Workstream` are classes; the twelve verbs are properties
  with domains and ranges.
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
  rules are shapes; verification is the SHACL run; a violation is a finding
  with a receipt.
- **The open-world caveat.** An OWL reasoner treats an unstated fact
  as unknown, not false, and infers around a missing field. Checks
  that must report a missing thing go in shapes.
- **Cost.** Sub-second at this scale. Rules plus fixpoint, not
  search; nothing like a MIP.

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

One engine checks both ontologies over one fact base per checkout. The
document ontology is declared once in dev-playbook; a domain ontology is
a declared file in the same form from the start, since an agent writes
it from a conversation and the generic toolchain must read it without
importing code. The case for the engine at the domain layer: schema as
data, existing vocabularies such as schema.org's `JobPosting` and `Organization`, and open-world fit for
partial domain knowledge.
