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
  1. *Standard takes its new shape.* Done 2026-09-20; the entry is in
     [Completed](#completed).
  2. *The verifier table.* A generator writes the table and is the lint.
     - The table is a map: one row per rule id, and the address of the
       thing that decides it, a homegrown script by path, a dependency
       by its pinned pre-commit hook id, a judge by its file, or null.
     - The generator reads the rule headings under `standards/<name>/`,
       asks each check which ids it emits, and writes the table; it
       fails on an emitted id that is no rule heading, on an address
       that does not exist, and on a consumer row that names a
       dev-playbook rule.
     - Null is allowed: for a stochastic rule, and for the seventy-one
       deterministic rules no script has ever checked. No step writes
       those scripts; a rule unchecked before this plan stays unchecked.
     - dev-playbook's table ships in the package; a consumer's generator
       adds rows only for the rules that repo declares, the way the
       type registry unions.
     - The generated table is committed, and the commit gate regenerates
       it and fails on a difference.
     - The checks change the ids they emit to the rule headings: seventy
       of seventy-nine differ today, listed in the Emitted ids table of
       [Verifiers and Boundaries](/working-docs/doc-type-system/doc-type-system/verifiers-and-boundaries.md#emitted-ids).
       Where one id covers several rules the check splits it; where
       several ids are one rule the check merges them.
     - Four ids get a decision, not a rename: `prose.banned-word` gets
       a deterministic rule in `prose/conventions.md`, which needs
       prose-lint to allow the one mention that states it;
       `knowledge-organization.doc-shape` splits into README Content's
       `h1` and CONTEXT.md Content's `the-language-section`;
       `tracking.no-blocked-label` retires into `tracking.valid-labels`;
       `registry-location` is kept under `local-declaration` or dropped.
     - `standard/detectors.md` is rewritten: its population is "a check
       the table names", and its id rule is what the generator
       enforces, replacing standards-lint's `rule-matrix`.
     - No `audit()` function; a judge, when one is built, reads the table.
     - Progress, 2026-09-20: the renames and splits are done across all
       eleven detectors and green, uncommitted. Reading the code showed
       the worksheet overclaimed six rules no check decides, so they stay
       null: `an-act-links-a-runbook`, `harness.tool-fields`,
       `row-description`, `resource`, `ticket-parentage`, and
       `epic-headings`. `registry-location` is kept under
       `local-declaration`; an unreachable issues read is filed under
       `tracking.build-labels`. Still to do: the generator and its table,
       the gate wiring, the `detectors.md` rewrite, deleting `rule-matrix`,
       and correcting the worksheet's Emitted ids table.
     Reason: the table is the one place the Standard files and the
     checks meet, and a generator that fails cannot drift from either.
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
     same fact base item as step 2's. `standard/gates.md` retires at
     this step: its Three rungs is the table's own schema, with a
     loop's check the fourth boundary the file today denies; its Skips
     is a per-machine entry of that table; its Installed in every
     clone is already `build/bootstrap.md`'s step 4; and its A red CI
     run is never merged binds the user, not a gate, and moves to
     `docs/guides/standard.md`, repointing `docs/guides/tracking.md`,
     `docs/machines.md`, and the comment in `playbook_lint.py`. The
     closure standards-lint's `hook-surfaces` checks today, that every
     detector a card cites is in the commit gate's roster or
     registered ungated, becomes the table's rule: every rule id with
     a verifier is named by some boundary or listed as ungated on
     purpose. Two facts the boundary table of
     [Verifiers and Boundaries](/working-docs/doc-type-system/doc-type-system/verifiers-and-boundaries.md#boundary-table)
     carries into this step: the canonical `ci.yml`'s `SKIP` removes
     `ref-lint` from CI in every governed repo, which the config
     states as that detector's boundaries rather than as an
     environment variable, and the same `SKIP` names `web-typecheck`,
     a hook only dev-playbook has, which leaves the canonical file.
     Step 2 filed standards-lint's closure leg, a cited detector that is
     neither in the playbook-lint roster nor a registered ungated audit,
     under `standard.the-hosting-pattern`; this step moves it to the
     boundary table.
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
     runbook already covers it, or moved where it is neither.
     `docs/guides/<name>.md` is the destination for a guide that is
     teaching, the reasoning and vocabulary behind a Standard, as
     `docs/guides/modules.md` is for modules; a guide that is a
     procedure an agent performs becomes a runbook; a procedure only
     the user performs by hand, the GitHub settings an administrator
     sets, is documentation and lives in the guide, since a runbook is
     for work an agent is intended to do; the rule for where each of
     the six goes is decided case by case at this step, not before. `standards/references/okf-spec.md`, the one `type: Reference`
     mirror under the tree, and its `index.md` leave with them, to
     `docs/references/okf-spec.md`, since a vendored upstream spec is
     supporting material a Standard cites and not a Standard; the
     citation in `knowledge-organization/indexes.md` and the row in
     `standards/index.md` move with it. Six of standards-lint's seven
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
     by that repo at its next pin bump. `standard/cards.md` retires
     with the card, and the rules that outlive it are written as the
     successor Standard, population "a repo's `standards/` tree":
     one directory per Standard at `standards/<name>/<topic>.md`, the
     directory index carrying the description, the catalog order, no
     shadowing of an upstream directory name, and the rule shape
     itself, an H2 with a predicate and a `<name>.<slug> · kind`
     trailer and H3s only under a condition, which no Standard states
     today. `standard/consuming.md` is rewritten as the post-card
     recipe, not moved, since its steps name cards, Audit cells, and
     standards-lint's consumer mode. `standard/detectors.md`'s
     `the-hosting-pattern` loses its Audit-cell leg here, and
     Document Types' `typed-standard-card-or-standard-ruleset`
     becomes the rule for the one type `Standard`. Of the six
     Guides leaving `standards/`, `harness/files.md` and
     `harness/writing-for-agents.md` have `docs/guides/harness.md`
     to fold into and `knowledge-organization/file-roles.md` has
     `docs/guides/knowledge-organization.md`, where each is
     teaching; the case-by-case rule above still decides.
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
  9. *Scrub `docs/`.* Every file under `docs/` other than
     `docs/decisions/` and `docs/guides/` is read and given its
     long-term home: a guide behind a Standard moves to
     `docs/guides/<name>.md`, a procedure an agent performs becomes a
     runbook, a decision becomes a Decision Record, supporting material
     a Standard cites sits under `docs/references/`, and a working
     paper that is none of these either stays as a working paper or is
     deleted. Reason: step 1 sent everything a drain displaced to
     `docs/` as a holding place, and the PR merges only once each file
     under `docs/` is where it belongs, never in a temporary home.
  10. *Verify every predicate.* After step 2, every rule in every
     Standard is run against this repo once, and the outcome is
     recorded, never assumed: a rule with a script verifier by running
     the script; a rule with a null row by hand or by an agent reading
     the population with the predicate; a stochastic rule by a judge
     over a sample of members. A predicate that is not true of the
     repo today is either fixed in this PR where the fix is small or
     becomes an issue that names the rule id and the failing members,
     `standard.thin-shims` and the five detectors that hold their own
     logic, `okf-lint`, `repo-lint`, `harness-files-lint`, `ref-lint`,
     and `python-lint`, being the first, and the four rules the
     holistic pass wrote or restored, `decisions.immutable-after-merge`,
     `knowledge-organization.skill-invocation`,
     `distribution.a-valid-manifest`, and the renamed
     `knowledge-organization.mapping-entry-shape`, being next, since
     no run has confirmed them. A predicate that turns out
     undecidable as written is rewritten or deleted. Reason: step 1's
     kind tags are aspirational, deterministic meaning a script could
     decide the rule and not that one does, and the drains were
     verified only against the detector code that exists; a Standard
     that states what the repo does not do, with no issue that says
     so, is the slop this work exists to remove.
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

- **Standard takes its new shape, 2026-09-20.** Step 1 of The system.
  Every rule in the 25 drained rulesets is a heading, a predicate, and
  a trailer `` `<name>.<slug>` · deterministic|stochastic ``, 251 rules
  in all, drained one ruleset at a time by the
  [Body Drain](/working-docs/doc-type-system/doc-type-system/body-drain.md)
  rubric; `standard/cards.md` and `standard/gates.md` stay undrained
  for steps 4 and 3. Teaching the drains displaced is a guide at
  `docs/guides/<name>.md`, twelve in all, one per Standard directory.
  The closing pass drew the verifier and boundary tables by hand,
  read the rulesets across each other, and left its findings and
  every deferral in
  [Verifiers and Boundaries](/working-docs/doc-type-system/doc-type-system/verifiers-and-boundaries.md),
  each deferral also named at the step that owns it. Reason: a loop
  cannot route a rule without an id and a kind, and text no verifier
  reads is text the state is not held to.

## Acronyms

- **CI** — Continuous Integration.
- **PR** — Pull Request.
