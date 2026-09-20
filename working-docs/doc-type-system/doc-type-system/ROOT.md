---
type: General-Sheet
title: Doc-Type System
description: The root of the doc-type system strand — the language of doc-types, verbs, and predicates, its principles and terms, and the worklist from the Standard's new shape through the first instance
---

# Doc-Type System

The strand that holds the language: what a doc-type is, its verbs, its
rules as predicates, its encodings as grammar. Speculative, per
[Synthesis Working Root](/working-docs/doc-type-system/ROOT.md).
It defines Loop, one of its three doc-types
([Loop](/working-docs/doc-type-system/loop/ROOT.md)), and each
encoding it writes defines an extractor of the fact base
([Fact Base Strand](/working-docs/doc-type-system/fact-base/ROOT.md)).
The user's own words on the work are kept verbatim in
[Personal Notes](/working-docs/doc-type-system/doc-type-system/personal-notes.md)
for use outside the set.

## Goal

Three DocTypes, ten verbs, in
[Reference Model](/working-docs/doc-type-system/doc-type-system/reference-model.md),
the picture of the target state;
[Doc-Type Specification](/working-docs/doc-type-system/doc-type-system/specification/doc-type.md)
is the same state as predicates, with one file per doc-type beside it.
The refactor that reaches them, then one loop that grows the
specification.

## Principles

- **Peers first.** Wherever a choice is open, pick the one that keeps
  the three doc-types parallel.
  [Reference Model](/working-docs/doc-type-system/doc-type-system/reference-model.md)
  holds the parallel structure, and each peer has its conventions
  Standard: `harness/runbook-conventions` for Runbook, the
  Meta-Standard under `standard/` for Standard, and
  `knowledge-organization/loop-conventions` for Loop.
- **Verbs.** Each doc-type is defined by a short list of simple verbs,
  its operations. Overlap between doc-types is allowed.
- **Both forms.** A target state is written twice: as a reference
  model, the picture the user thinks in, and as a specification,
  falsifiable predicates that describe the whole set and not one member
  of it, never as a linear description plus actions. The reference
  model is the witness; the predicates are the spec; both are kept.
  Both use the words of
  [Terms](/working-docs/doc-type-system/ROOT.md#terms), one
  meaning each.
- **Predicates are written one way.**
  [Writing Predicates](/working-docs/doc-type-system/doc-type-system/writing-predicates.md)
  is how; it may become the Standard that governs it.
- **Stochasticity is a continuous scale per file.** A markdown file
  with no declared structure sits at one; code sits at zero; a file
  with embedded structure sits between. A file's stochasticity is what
  lies outside its declared structure, which is what
  [the doc-type build loop](/doc-types/doc-type.md#the-doc-type-build-loop)
  already calls the residual. The bedrock of determinism is a
  threshold on content, not a line between file kinds.
- **Shape is orthogonal to stochasticity.** A fully deterministic
  runbook or loop still gets its doc-type document, because the
  document is the legible form. The one requirement that follows is
  a drift check between the document and its substrate, the same
  deterministic rule chaingen applies to a runbook and its chain. The
  loop half is in the Loop strand
  ([Principles](/working-docs/doc-type-system/loop/ROOT.md#principles)).

## Terms

- **DocType** — the base class of
  [Reference Model](/working-docs/doc-type-system/doc-type-system/reference-model.md):
  a class extends it when its instance is one markdown file of that
  type. `Object`, its earlier name, is retired.
- **Part** — a class nested inside a DocType: an Edge, a Rule, an
  Act, a Check, a Yield. A part has no verbs.

## Open

- **Rule order.** Standard rules are unordered in
  [Population and Rules](/doc-types/standard/contract-shape.md) and in
  file order in the reference model. One must give.
- **The `External` target.** The reference model's `External`
  catch-all target sits against the fact base's total accounting.
- **Whether the fenced pseudocode becomes real Python.**
  [Ontology Solvers](/working-docs/doc-type-system/doc-type-system/ontology-solvers.md)
  proposes the route: a module of dataclasses with no bodies, checked
  by mypy, introspected into an ontology.

## Planned

- **The system.** The refactor toward the reference model and the
  specification. The target shape of one rule, decided 2026-09-20: a heading,
  the predicate, and a trailer line, nothing else. The predicate is
  everything between the heading and the trailer, a list of exemptions
  included when the check needs one, and it is written so that
  deterministic code lifts it verbatim into a judge's prompt, alone or
  concatenated with other stochastic rules for one judge call. A body
  after the trailer is not part of the target: what the 232 bodies
  hold today is enforcement wiring, which step 3 removes, pointers to
  other Standards, which the fact base carries, and exemptions, which
  belong inside the predicate. Reason: text that no verifier reads is
  text the state is not held to, and the split between a checked first
  paragraph and an unchecked body is where the prose and the verifier
  drift apart.
  1. *Standard takes its new shape.* Every rule gets an id,
     `<name>.<slug>`, the `standards/<name>/` directory then the
     heading's GitHub slug, `build.uvlock-and-python-version`, and a
     kind, deterministic or stochastic, on a trailer line after its
     predicate, `` `build.uvlock-and-python-version` · deterministic ``,
     the form the specification files already use. A condition is a
     rule and carries both; the rules under it name it as their
     condition. Reason: a loop's check routes each rule to a verifier
     by id and kind, so a rule without both cannot be checked, and a
     stochastic rule is one an LLM judge decides, using the predicate
     as its prompt. The directory as prefix keeps every id the
     detectors emit today valid; a detector id that matches no
     heading slug is renamed to the slug in step 2, where the table
     makes the mismatch a finding. The same step drains the bodies, one
     ruleset at a time and the pace rising as the results earn trust,
     never all 29 at once: one Opus agent owns one ruleset and returns
     one row per rule and nothing else, the rule id, a verdict, and for
     fold or split the exact new text. The verdicts, from a fixed
     rubric: enforcement wiring, a pointer to another Standard, or a
     reason is deleted; an exemption or definition that changes what
     passes is folded into the predicate; a body sentence that is
     itself a constraint is split into a rule of its own; a rule
     another rule in the same directory already decides is redundant
     and goes; anything a detector that emits the rule's id already
     honors is folded, never deleted, and any clause the detector does
     not decide is cut or split into a rule with no verifier yet, so a
     deterministic predicate says exactly what its script decides. The
     session decides every row and puts only the ambiguous ones to the
     user, each with its pick, and a no is kept with its reason. The
     prompt is [Body Drain](/working-docs/doc-type-system/doc-type-system/body-drain.md).
     Reason: a rule tagged and left with its body is orphaned
     work, and a loop that begins with 232 findings across 29 files has
     no small first move; this is the first instance run by hand, an
     act that drafts, a yield per rule, an act that applies.
  2. *The verifier table and `audit`.* One table maps every rule id to
     a script, a judge, or null, one row per id, keyed by id; dev-playbook
     holds the rows for its own rules and a consumer repo holds rows for
     the rules it invents, unioned in downhill only, the pattern the type
     registry already uses. Null is allowed: the table's job is the map,
     not the fill, and a null row is a gap the view shows rather than a
     failure. One `audit(standard, state)` function in the package parses
     the file, skips a rule whose condition fails on the member, skips a
     null row, runs a script for a deterministic rule, batches the
     stochastic rules' predicates into one judge prompt, and returns
     findings, each one member and one rule id. Reason: this is the one
     place the Standard files and the code meet, so a table row naming
     no rule, a rule with no row, or a consumer row naming a dev-playbook
     id is a lint failure, not a silent gap. The table's shape as declared
     data the fact base extracts is the fact base strand's item
     ([Planned](/working-docs/doc-type-system/fact-base/ROOT.md#planned)).
  3. *Boundaries read ids from config.* A second table, one per repo and
     never inherited, names the rule ids each boundary runs: the commit
     hook, `make check`, CI, and a loop's check. Every id it names
     resolves in the verifier union. Reason: which boundary runs a rule
     is wiring, and a Standard that states its own enforcement cannot be
     audited by a loop without also being gated; the same rule is gated
     in one repo and aspirational in another, which one shared table
     could not say. The two tables are two files because they have two
     owners, the verifier map workspace-wide and the boundary map one
     repo's; both live under `standards/` as plain data, format decided
     when step 2 is built. The config's shape as declared data is the
     same fact base item as step 2's.
  4. *Retire the card.* Delete `Standard-Card`, its four cells, Define,
     Audit, Enforce, Adopt, `cardgen`, `rulegen`, and the `.txt`
     files, retire `Standard-Ruleset`, and bind the type `Standard` to
     `standards/<name>/<topic>.md`. The directory's `index.md` carries
     the one-line description the card's question sentence carried, and
     the catalog row reads it from there. The six Guides under
     `standards/` today, `build/bootstrap.md`, `standard/consuming.md`,
     `tracking/linking-issues.md`, `harness/files.md`,
     `harness/writing-for-agents.md`, and
     `knowledge-organization/file-roles.md`, leave the tree, each one
     converted to a runbook where it is a procedure, deleted where a
     runbook already covers it, or moved where it is neither; `docs/` is
     not a destination, since it holds the high-level intentional
     documents, and the rule for where such a file goes is decided case
     by case at this step, not before. Six of standards-lint's seven
     rules go with the card; `rule-matrix` is superseded by step 2's
     table lint. Reason: the reference model places every cell elsewhere,
     Define is the Standard file, Audit is the verifier table, Enforce is
     the boundary config, and Adopt was never a primitive; and viewing is
     out of scope for this work.
     [Reference Model](/working-docs/doc-type-system/doc-type-system/reference-model.md#what-goes-where)
     lists each disposition. The fact base's extractors item strikes
     the card extractor for this reason. `rulegen` goes as a script
     with its `.txt` file; its logic moves into the package as the
     `standard` extractor, per that item
     ([Planned](/working-docs/doc-type-system/fact-base/ROOT.md#planned)).
     A consumer repo's cards, story-forge's five among them, are deleted
     by that repo at its next pin bump.
  5. *`Object` becomes `DocType`, and the one-module lint.* The
     pseudocode left the three `contract-shape.md` files in PR #491 and
     sits whole in
     [Reference Model](/working-docs/doc-type-system/doc-type-system/reference-model.md#the-language),
     so this step splits it back: `DocType`, `Target`, and `Finding` to
     `doc-type.md`, each doc-type's class with its nested parts to its
     own `contract-shape.md`, and the reference model keeps the toolchain
     half and the fit. The `Standard` class is written in the shape
     steps 1 to 4 produce: location `standards/<name>/<topic>.md`,
     frontmatter `type`, `title`, `description`, `population`, a `Rule`
     of id, kind, predicate, and condition, and no pointer to a script or
     a gate. Then add the linter that concatenates the four fences and
     parses them as one Python module. Reason: the parts, Edge, Rule,
     Act, Check, Yield, are not doc-types and must not extend the base;
     the linter is the first verifier for the specification, whose
     `one-base` and `one-module` rules name `contract-shape.md`, and is
     what makes the three contract shapes one design instead of three.
  6. *Runbook's two edits.* `accept` replaces `args` as the verb for
     an input edge, and `never write` becomes a `banned` polarity on a
     write edge. Reason: every operation on an edge must be one of the
     doc-type's verbs, and `args` was a noun and `never` a negation,
     neither a verb.
  7. *The specification becomes a Standard.* Move
     [specification/](/working-docs/doc-type-system/doc-type-system/specification/index.md)
     under `standards/` in the shape step 1 produces, bound to no
     boundary, and add one rule to the Standard file:
     `doc-type-system.standard.no-body`, deterministic, nothing follows
     a rule's trailer. Reason: the first loop's checks point at it, and
     a loop must not bind to the Standard shape that step 4 deletes; the
     no-body rule holds on the day it lands because step 1 drained the
     bodies, and it keeps them drained.
  8. *Ban the word guard.* See the banned words below.
- **First instance.** One loop, `loops/<name>.md`, over the doc-type
  system, after step 7: its checks point at the specification as a
  Standard, and the loop grows it. In iteration order: an act drafts
  candidate predicates, each with its citation or marked invented and
  the members that fail it today; a yield to the user, yes or no per
  predicate; an act applies the accepted ones; a check audits; a yield
  to the user with the diff. A no is kept with its reason, and the
  reason is a candidate predicate itself. The design behind it is
  [Specifying a Loop](/working-docs/doc-type-system/loop/specifying-a-loop.md).
  Whether Loop gains a part for the scalar this loop descends is the
  Loop strand's item
  ([Planned](/working-docs/doc-type-system/loop/ROOT.md#planned)).
- **The `/write-predicates` skill.** A runbook that points at
  [Writing Predicates](/working-docs/doc-type-system/doc-type-system/writing-predicates.md);
  after the guide settles. Also improve writing-predicates.md; it's
  a rough first draft user does not endorse it yet.
- **Banned words in prose-lint.** One entry for each retired word,
  guard, generator, and adopt, each message naming the word to use
  instead, so a habit in the model's weights is caught at the commit
  boundary rather than by the user. The three doc-type directories
  and `CONTEXT.md` take the set's terms when the strand drains.
- **One clause in System Legibility.** Its sentence that
  documentation is the stochastic thing and code the deterministic
  one is imprecise; one clause says that stochasticity is a scale per
  file ([Principles](/working-docs/doc-type-system/doc-type-system/ROOT.md#principles)).

## Completed

- **One meaning per word, one home per word, 2026-09-15.** Every
  word the four strands use is defined once, in the Terms bucket of
  the set's root where more than one strand uses it and of a strand's
  root where one does, and every other use links to it. Reason: the
  same word carried two senses more than once in this work, guard
  beside condition, evaluator beside verifier, bundle beside
  directory, and each cost a round of correction; a loop reading these
  files cannot ask which sense was meant. The words are in the set's
  [Terms](/working-docs/doc-type-system/ROOT.md#terms).
- **One doc-type for Standard.** Merged into one directory,
  [doc-types/standard/](/doc-types/standard/index.md), with Contract
  defined by the cut in [Doc-Type](/doc-types/doc-type.md). The shape
  it carries there is the one the refactor replaces with
  [Reference Model](/working-docs/doc-type-system/doc-type-system/reference-model.md)'s.

## Acronyms

- **CI** — Continuous Integration.
- **PR** — Pull Request.
