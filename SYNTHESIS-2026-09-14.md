---
type: General-Sheet
title: Synthesis Notes
description: The record of one synthesis session across the loop and cloa branches — the branches are one theory, ontology solvers against pseudocode, and deterministic separation of stochastic chains — with what was decided and what was left open
---

# Synthesis Notes

The record of a session on 2026-09-14 that read every important
document on two branches at once and talked through how they fit.
The branches: `worktree-loop-document-type`, the doc-type language,
three DocTypes and ten verbs in
[Reference Model](/worktree-loop-document-type-working-docs/reference-model.md)
and one meaning per word in
[Glossary](/worktree-loop-document-type-working-docs/glossary.md);
and `worktree-cloa-viewer-tool-2`, the fact base in
`worktree-cloa-viewer-tool-2-working-docs/fact-base.md`. Both descend
from [System Legibility](/docs/system-legibility.md). Where a file
existed on both branches the loop branch's copy was newer on every
one, and that copy was the one read.

Three topics, in the order discussed. Nothing here is decided beyond
what the Decided sections say.

## 1. The two branches are one theory

The loop branch is the language: doc-types, verbs, rules as
predicates, encodings as grammar. The cloa branch is what the language
compiles to: extractors are the parsers, the fact base is the symbol
table, views are selections over it. The reference model says the CLOA
is a view derived deterministically from structure embedded in the
files; the fact base says every view is a selection from the fact
base. Two sessions that never saw each other wrote the same sentence.

### Decided

- **Stochasticity is a continuous scale per file.** A markdown file
  with no declared structure sits at one; code sits at zero; a file
  with embedded structure sits between. A file's stochasticity is what
  lies outside its declared structure, which is what the doc-type
  build loop already calls the residual. The bedrock of determinism is
  a threshold on content, not a line between file kinds. System
  Legibility's sentence that documentation is the stochastic thing and
  code the deterministic one is imprecise and needs one clause to say
  this.
- **A fully deterministic runbook or loop still gets a doc-type.**
  Shape is orthogonal to stochasticity. Every loop gets a Loop
  document, even one a workflow runs, because the document is the
  legible form. The one requirement that follows is a drift check
  between the Loop document and its substrate, the same deterministic
  rule chaingen applies to a runbook and its chain.
- **No fundamental incompatibility.** What the reading found was
  vocabulary drift and gaps left by work not yet done.
- **An encoding defines an extractor; it is not a spec.** Under the
  glossary a spec is a set of predicates. `encoding.md` is mostly a
  function, the primitive map from written form to rows, which is the
  extractor's definition. The well-formedness predicates buried in it,
  a span nests at most two deep, one link names a target, belong in
  the Standard whose verifier is the drift check, or in the one coarse
  rule every grammar induces: the file parses.

### Gaps to close, not conflicts

- **Audit and Enforce need a declared home.** The loop branch moved
  the card's Audit into a verifier table and Enforce into boundary
  wiring. The fact base extracts declared files and bedrock only. The
  rule id to verifier map and the rule id to boundary map must be
  declared data in a fixed shape with an extractor, wherever they
  live, so the solver can read them.
- **The fact base holds declarations and state, never findings.**
  Findings are a separate stamped artifact. Deterministic ones are
  recomputable from the fact base; stochastic ones are cached with
  commit, judge, and time. This is the seam the glossary draws
  between a set and a distribution.
- **"Rule" splits.** The fact base's rows-to-rows function with no
  judgment is a derivation. Its rows-to-violations function is a
  verifier keyed by rule id. Standard keeps "rule."
- **Three conditions, two representations.** A runbook edge's and a
  loop step's condition are strings; a Standard rule's condition is a
  reference to another rule. Option: every condition is a Rule with a
  kind, so all three unify and the fact base gets one guarded-by edge.
  Cost: runbook prose conditions would need ids. Open.
- **The loop's Mermaid block is encoding.** A loop extractor reads
  it; the view is drawn from rows. The loop contract shape's "no
  generator, the graph is the view" gives way to that.
- **Small.** Standard rules are unordered in `contract-shape.md` and
  in file order in the reference model. "Kind" carries three meanings:
  view-file kind, registry kind, `Rule.kind`. The reference model's
  `External` catch-all target sits against the fact base's total
  accounting.

## 2. Ontology solvers

### Source

Frank Coyle, "Agents and Ontologies," recorded in mission-control at
`ideas/ontology-guardrails.md` on 2026-07-27. No link or venue was
recorded. The claim: a formal ontology outside the model as logical
guardrails, probabilistic reasoning inside, logic outside. Pydantic at
the door, ontology at the ledger; a failed check loops back to the
model or escalates to the owner. That last sentence is act, check,
yield.

### The theory, in industry terms

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

### Pseudocode and type checkers

A type checker is an ontology solver over program text. Mypy reads
class declarations as a TBox and every expression as an assertion,
and a type error is a consistency violation with a line number. The
difference from an ontology engine is what the assertions range over:
mypy checks the source, the engine checks the data.

Route proposed for the pseudocode: the fenced block in
`reference-model.md` becomes real Python that never runs. The bare
names, `operations = {read, write, do}` and
`kind: deterministic | stochastic`, become an `Enum` or `Literal`, and
the block is a module of dataclasses with no bodies. Mypy checks the
declarations against themselves. A script introspects the classes with
`typing.get_type_hints` and emits the OWL classes, properties, and
cardinality shapes. The `# rules:` lines become predicates, as Python
functions over loaded instances or as shapes. A bedrock extractor
pulls the fence out of the markdown the way doctest pulls examples out
of a docstring. The words around the block are the stochastic
remainder; the block sits at zero.

### The loop the solver enables

Check: extract the fact base, run the solver, findings are
inconsistencies and violations. Act: fix what a finding names. Yield:
when a finding needs a judgment. Which thing the act fixes is the
fork: the repo, which is the adopt loop with the ontology as its
Standard; or the pseudocode, which is the doc-type build loop with the
findings the user rules the model's fault as its residual. The solver
never reports a missing class. That comes from residuals, as today.

### Two ontologies

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

### Decided

- Nothing. The user is not convinced two solvers, mypy and an
  engine, are needed, and stays open. Not decided now.

## 3. Deterministic separation of the system

The question: can parts of the system be provably separated under
determinism, so that the worst case of stacked stochasticity is
bounded. Well-formed once stated per predicate rather than per
system.

Take one predicate P over the final state. Each stochastic step has
some probability of breaking P, and along a chain those compound: the
chance P survives is a product, and the tail grows with chain length.
A deterministic verifier of P at step k is a containment boundary:
everything downstream runs conditional on P holding, so P's violation
probability at the end depends only on the stochastic steps after k.
Predicates nobody verifies compound across the whole chain. The
system's worst case is one number per predicate: the compounded error
of the stochastic steps after that predicate's last deterministic
check. Stochastic rules are the ones whose tails still run the length
of the chain.

Miniature. Runbook A, a model, writes `data.json`. Script S reads it,
transforms it to `out.json`, and fails loud on malformed input.
Runbook B, a model, reads `out.json` and writes a report.

- "out.json is well-formed": S verifies it, A is contained, B does not
  write the file. Effectively deterministic.
- "the report cites every record in out.json": nobody verifies it. A
  can drop a record and S passes it through; B can miss one. Tail
  length two, compounding.
- A script that diffs the report's citations against `out.json` after
  B drops that predicate's tail to zero.

The provable part is a graph question: for each rule id, which
stochastic nodes lie between its last verifier and the end. That is a
query over the fact base, and it is deterministic. The probabilities
stay estimates; the structure that bounds them is proven. This and
"the target is a ruleset of predicates" are one question: every rule
given a script verifier shortens its own tail to the segment after its
gate.

## Standing reminder

Describe a target state as falsifiable predicates, never as a linear
description plus actions. The reference model is the witness; the
predicates are the spec; both are kept.

## Open

- Whether every condition is a Rule.
- Where the verifier map and the boundary map are declared.
- Whether one solver or two: mypy over the pseudocode, an engine over
  the fact base and the domain layer.
- Whether the fenced pseudocode becomes real Python.
- The per-predicate tail query as a view over the fact base.

## Acronyms

- **ABox** — Assertion box: the facts of a knowledge base.
- **CLOA** — Correct Level of Abstraction.
- **MIP** — Mixed-Integer Programming.
- **OWL** — Web Ontology Language.
- **RDFS** — Resource Description Framework Schema.
- **SHACL** — Shapes Constraint Language.
- **TBox** — Terminology box: the schema of a knowledge base.
